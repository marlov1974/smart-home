"""Compose the atomic Mode+Service+Debug-command EFFECT v4 update.

This is an offline artifact operation.  It never contacts a Shelly or Procon.
The three chunks are inseparable: Mode and Service share the private effect
model ABI, while Debug Command owns the exact-UID gain-seed command consumed by
the new controller.  Every input and the completed output is cross-checked
against its chunk files, sizes.json, manifest.bin, and install.bin.
"""

import argparse
import binascii
import hashlib
import json
import shutil
import struct
from pathlib import Path


IMAGE_BASE = 0x08008000
MANIFEST_SIZE = 64
MANIFEST_MAGIC = 0x50384D46
MANIFEST_VERSION = 1
MANIFEST_COMMIT = 0x434F4D54
EXPECTED_SLOT_IDS = list(range(8))
CHANGED = ("mode", "service", "debug_command")
EXPECTED_OTA_SLOTS = [2, 4, 5]
ARTIFACT_EXTENSIONS = ("S", "ld", "raw.bin", "bin", "elf", "map")


def crc(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _require_int(mapping: dict, key: str, label: str) -> int:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"invalid {key} in {label}")
    return value


def validate_directory(directory: Path, label: str) -> dict:
    """Return validated metadata and bytes for one complete build directory."""
    sizes = load_json(directory / "sizes.json")
    layout = _require_int(sizes, "layout", label)
    manifest_address = _require_int(sizes, "manifest_address", label)
    slots = sizes.get("slots")
    if not isinstance(slots, list) or len(slots) != len(EXPECTED_SLOT_IDS):
        raise ValueError(f"invalid slot count in {label}")
    if [_require_int(slot, "id", label) for slot in slots] != EXPECTED_SLOT_IDS:
        raise ValueError(f"non-canonical slot ids in {label}")
    names = [slot.get("name") for slot in slots]
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError(f"invalid or duplicate slot names in {label}")

    manifest = (directory / "manifest.bin").read_bytes()
    if len(manifest) != MANIFEST_SIZE:
        raise ValueError(f"invalid manifest length in {label}")
    words = struct.unpack("<16I", manifest)
    if words[0] != MANIFEST_MAGIC or words[1] != MANIFEST_VERSION:
        raise ValueError(f"invalid manifest header in {label}")
    if words[2] != layout:
        raise ValueError(f"manifest/layout mismatch in {label}")
    if any(words[11:14]):
        raise ValueError(f"nonzero reserved manifest words in {label}")
    if words[14] != crc(manifest[:56]) or words[15] != MANIFEST_COMMIT:
        raise ValueError(f"invalid manifest checksum or commit marker in {label}")

    image = (directory / "install.bin").read_bytes()
    manifest_offset = manifest_address - IMAGE_BASE
    if manifest_offset < 0 or manifest_offset + MANIFEST_SIZE > len(image):
        raise ValueError(f"manifest outside install image in {label}")
    if image[manifest_offset : manifest_offset + MANIFEST_SIZE] != manifest:
        raise ValueError(f"manifest/install slice mismatch in {label}")

    chunks = {}
    occupied = []
    for slot in slots:
        name = slot["name"]
        size = _require_int(slot, "size", f"{label}:{name}")
        address = _require_int(slot, "address", f"{label}:{name}")
        expected_crc = _require_int(slot, "crc32", f"{label}:{name}")
        if size <= 0:
            raise ValueError(f"invalid chunk size in {label}:{name}")
        chunk = (directory / f"{name}.bin").read_bytes()
        if len(chunk) != size:
            raise ValueError(f"chunk length mismatch in {label}:{name}")
        if crc(chunk) != expected_crc:
            raise ValueError(f"chunk CRC mismatch in {label}:{name}")
        expected_sha = slot.get("sha256")
        if expected_sha is not None and expected_sha != sha256(chunk):
            raise ValueError(f"chunk SHA-256 mismatch in {label}:{name}")
        offset = address - IMAGE_BASE
        if offset < 0 or offset + size > len(image):
            raise ValueError(f"chunk outside install image in {label}:{name}")
        if image[offset : offset + size] != chunk:
            raise ValueError(f"chunk/install slice mismatch in {label}:{name}")
        if slot["id"] > 0 and words[3 + slot["id"]] != expected_crc:
            raise ValueError(f"chunk/manifest CRC mismatch in {label}:{name}")
        occupied.append((offset, offset + size, name))
        chunks[name] = chunk

    occupied.sort()
    for (_, previous_end, previous_name), (start, _, name) in zip(occupied, occupied[1:]):
        if start < previous_end:
            raise ValueError(f"overlapping chunks in {label}: {previous_name}/{name}")
    if any(start < manifest_offset + MANIFEST_SIZE and end > manifest_offset for start, end, _ in occupied):
        raise ValueError(f"manifest overlaps a chunk in {label}")

    install_json = load_json(directory / "install.json")
    if install_json.get("sha256") != sha256(image):
        raise ValueError(f"install SHA-256 mismatch in {label}")
    return {
        "sizes": sizes,
        "slots": slots,
        "manifest": manifest,
        "manifest_words": words,
        "image": image,
        "chunks": chunks,
        "manifest_prefix_crc": crc(manifest[:56]),
    }


def changed_slots(old: dict, new: dict) -> list[int]:
    return [
        index
        for index, (before, after) in enumerate(zip(old["slots"][1:], new["slots"][1:]))
        if old["chunks"][before["name"]] != new["chunks"][after["name"]]
    ]


def _validate_abi(before: dict, after: dict) -> None:
    old_sizes = before["sizes"]
    new_sizes = after["sizes"]
    if old_sizes.get("ota_protocol") != 2 or new_sizes.get("ota_protocol") != 2:
        raise ValueError("OTA protocol 2 is required")
    if old_sizes["layout"] != new_sizes["layout"]:
        raise ValueError("layout mismatch")
    if old_sizes["manifest_address"] != new_sizes["manifest_address"]:
        raise ValueError("manifest address mismatch")
    if before["chunks"]["bl2"] != after["chunks"]["bl2"]:
        raise ValueError("BL2 mismatch")
    for old_slot, new_slot in zip(before["slots"], after["slots"]):
        keys = ("id", "name", "address", "size", "ram", "ram_size", "exports")
        if any(old_slot.get(key) != new_slot.get(key) for key in keys):
            raise ValueError(f"slot ABI mismatch: {old_slot['name']}")


def compose(base: Path, candidate: Path, destination: Path) -> dict:
    before = validate_directory(base, f"base:{base}")
    after = validate_directory(candidate, f"candidate:{candidate}")
    _validate_abi(before, after)

    selected = {slot["name"]: slot for slot in after["slots"] if slot["name"] in CHANGED}
    if set(selected) != set(CHANGED):
        raise ValueError("candidate is missing Mode, Service, or Debug Command")

    manifest = bytearray(before["manifest"])
    image = bytearray(before["image"])
    for name in CHANGED:
        slot = selected[name]
        chunk = after["chunks"][name]
        struct.pack_into("<I", manifest, 16 + 4 * (slot["id"] - 1), slot["crc32"])
        offset = slot["address"] - IMAGE_BASE
        image[offset : offset + len(chunk)] = chunk

    struct.pack_into("<I", manifest, 56, crc(manifest[:56]))
    manifest_offset = before["sizes"]["manifest_address"] - IMAGE_BASE
    image[manifest_offset : manifest_offset + MANIFEST_SIZE] = manifest

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
    composed_sizes = dict(before["sizes"], slots=composed_slots)
    (destination / "sizes.json").write_text(json.dumps(composed_sizes, indent=2) + "\n")
    install = load_json(base / "install.json")
    install.update(
        status="offline-composed-unverified-candidate",
        profile="production",
        sha256=sha256(image),
    )
    (destination / "install.json").write_text(json.dumps(install, indent=2) + "\n")

    final = validate_directory(destination, f"final:{destination}")
    slots = changed_slots(before, final)
    if slots != EXPECTED_OTA_SLOTS:
        raise ValueError(f"unexpected OTA slots: {slots}")
    for slot in before["slots"]:
        name = slot["name"]
        if name not in CHANGED and before["chunks"][name] != final["chunks"][name]:
            raise ValueError(f"preserved chunk changed: {name}")
    for name in CHANGED:
        if final["chunks"][name] != after["chunks"][name]:
            raise ValueError(f"selected candidate chunk changed during composition: {name}")

    return {
        "base_manifest": f"{before['manifest_prefix_crc']:08x}",
        "candidate_manifest": f"{final['manifest_prefix_crc']:08x}",
        "changed_ota_slots": slots,
        "changed_modules": list(CHANGED),
        "mode_used": selected["mode"]["used"],
        "mode_capacity": selected["mode"]["size"],
        "service_used": selected["service"]["used"],
        "service_capacity": selected["service"]["size"],
        "debug_command_used": selected["debug_command"]["used"],
        "debug_command_capacity": selected["debug_command"]["size"],
        "install_sha256": sha256(image),
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
        "atomic_modules": list(CHANGED),
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
