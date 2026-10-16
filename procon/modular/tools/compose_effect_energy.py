"""Compose the paired Mode+Service EFFECT update over installed device images.

This is an offline artifact operation.  It never contacts a Shelly or Procon.
The two chunks are inseparable because Mode calls the private effect-model
veneers hosted by Service.
"""

import argparse
import binascii
import hashlib
import json
import shutil
import struct
from pathlib import Path


IMAGE_BASE = 0x08008000
CHANGED = ("mode", "service")
EXPECTED_OTA_SLOTS = [2, 4]
ARTIFACT_EXTENSIONS = ("S", "ld", "raw.bin", "bin", "elf", "map")


def crc(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def manifest_prefix_crc(directory: Path) -> int:
    manifest = (directory / "manifest.bin").read_bytes()
    if len(manifest) != 64 or struct.unpack_from("<I", manifest, 56)[0] != crc(manifest[:56]):
        raise ValueError(f"invalid manifest: {directory}")
    return crc(manifest[:56])


def changed_slots(old: Path, new: Path) -> list[int]:
    before = load_json(old / "sizes.json")
    after = load_json(new / "sizes.json")
    result = []
    for index, (a, b) in enumerate(zip(before["slots"][1:], after["slots"][1:])):
        if (old / f"{a['name']}.bin").read_bytes() != (new / f"{b['name']}.bin").read_bytes():
            result.append(index)
    return result


def compose(base: Path, candidate: Path, destination: Path) -> dict:
    before = load_json(base / "sizes.json")
    after = load_json(candidate / "sizes.json")
    if before["layout"] != after["layout"]:
        raise ValueError("layout mismatch")
    if (base / "bl2.bin").read_bytes() != (candidate / "bl2.bin").read_bytes():
        raise ValueError("BL2 mismatch")
    if len(before["slots"]) != len(after["slots"]):
        raise ValueError("slot count mismatch")
    for old_slot, new_slot in zip(before["slots"], after["slots"]):
        keys = ("id", "name", "address", "size", "ram", "ram_size", "exports")
        if any(old_slot[key] != new_slot[key] for key in keys):
            raise ValueError(f"slot ABI mismatch: {old_slot['name']}")

    base_manifest_crc = manifest_prefix_crc(base)
    manifest = bytearray((base / "manifest.bin").read_bytes())
    image = bytearray((base / "install.bin").read_bytes())
    selected = {slot["name"]: slot for slot in after["slots"] if slot["name"] in CHANGED}
    if set(selected) != set(CHANGED):
        raise ValueError("candidate is missing Mode or Service")

    for name in CHANGED:
        slot = selected[name]
        chunk = (candidate / f"{name}.bin").read_bytes()
        if len(chunk) != slot["size"] or crc(chunk) != slot["crc32"]:
            raise ValueError(f"invalid candidate chunk: {name}")
        struct.pack_into("<I", manifest, 16 + 4 * (slot["id"] - 1), slot["crc32"])
        offset = slot["address"] - IMAGE_BASE
        image[offset : offset + len(chunk)] = chunk

    struct.pack_into("<I", manifest, 56, crc(manifest[:56]))
    manifest_address = before["manifest_address"] - IMAGE_BASE
    image[manifest_address : manifest_address + 64] = manifest

    destination.mkdir(parents=True, exist_ok=True)
    for old_slot in before["slots"]:
        source = candidate if old_slot["name"] in CHANGED else base
        for extension in ARTIFACT_EXTENSIONS:
            artifact = source / f"{old_slot['name']}.{extension}"
            if artifact.exists():
                shutil.copyfile(artifact, destination / artifact.name)
    shutil.copyfile(base / "layout.h", destination / "layout.h")
    (destination / "manifest.bin").write_bytes(manifest)
    (destination / "install.bin").write_bytes(image)

    composed_slots = [selected.get(slot["name"], slot) for slot in before["slots"]]
    composed_sizes = dict(before, slots=composed_slots)
    (destination / "sizes.json").write_text(json.dumps(composed_sizes, indent=2) + "\n")
    install = load_json(base / "install.json")
    install.update(
        status="offline-composed-unverified-candidate",
        profile="production",
        sha256=hashlib.sha256(image).hexdigest(),
    )
    (destination / "install.json").write_text(json.dumps(install, indent=2) + "\n")

    slots = changed_slots(base, destination)
    if slots != EXPECTED_OTA_SLOTS:
        raise ValueError(f"unexpected OTA slots: {slots}")
    for old_slot in before["slots"]:
        if old_slot["name"] not in CHANGED:
            if (base / f"{old_slot['name']}.bin").read_bytes() != (destination / f"{old_slot['name']}.bin").read_bytes():
                raise ValueError(f"preserved chunk changed: {old_slot['name']}")

    return {
        "base_manifest": f"{base_manifest_crc:08x}",
        "candidate_manifest": f"{crc(manifest[:56]):08x}",
        "changed_ota_slots": slots,
        "changed_modules": list(CHANGED),
        "mode_used": selected["mode"]["used"],
        "mode_capacity": selected["mode"]["size"],
        "service_used": selected["service"]["used"],
        "service_capacity": selected["service"]["size"],
        "install_sha256": hashlib.sha256(image).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--vp1-base", required=True, type=Path)
    parser.add_argument("--vp2-base", required=True, type=Path)
    parser.add_argument("--vp1-out", required=True, type=Path)
    parser.add_argument("--vp2-out", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()
    summary = {
        "physical_install": False,
        "device_specific": True,
        "private_service_veneers": ["0x08012069", "0x0801206d"],
        "devices": {
            "1": compose(args.vp1_base, args.candidate, args.vp1_out),
            "2": compose(args.vp2_base, args.candidate, args.vp2_out),
        },
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n")
    for device, result in summary["devices"].items():
        print(
            f"VP{device}: {result['base_manifest']} -> {result['candidate_manifest']} "
            f"slots {result['changed_ota_slots']}"
        )


if __name__ == "__main__":
    main()
