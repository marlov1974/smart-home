import json
import struct
import tempfile
import unittest
from pathlib import Path

from tools.compose_effect_energy_v4 import (
    CHANGED,
    EXPECTED_OTA_SLOTS,
    IMAGE_BASE,
    MANIFEST_COMMIT,
    MANIFEST_MAGIC,
    compose,
    crc,
    sha256,
    validate_directory,
)


NAMES = (
    "bl2",
    "common",
    "dispatcher",
    "mode",
    "drift",
    "service",
    "debug_command",
    "debug_telemetry",
)


def make_fixture(path: Path, changed=()) -> None:
    slot_size = 32
    manifest_address = IMAGE_BASE + len(NAMES) * slot_size
    image = bytearray(b"\xff" * 384)
    slots = []
    chunks = {}
    for slot_id, name in enumerate(NAMES):
        marker = slot_id + (64 if name in changed else 0)
        if name == "bl2":
            marker = slot_id
        chunk = bytes([marker]) * slot_size
        chunks[name] = chunk
        address = IMAGE_BASE + slot_id * slot_size
        image[address - IMAGE_BASE : address - IMAGE_BASE + slot_size] = chunk
        slots.append(
            {
                "id": slot_id,
                "name": name,
                "address": address,
                "size": slot_size,
                "ram": 0x20000000 + slot_id * 64,
                "ram_size": 64,
                "exports": [f"export_{name}"],
                "ram_used": 0,
                "used": slot_size,
                "free": 0,
                "crc32": crc(chunk),
                "sha256": sha256(chunk),
            }
        )
    prefix = struct.pack(
        "<14I",
        MANIFEST_MAGIC,
        1,
        0x12345678,
        1,
        *(crc(chunks[name]) for name in NAMES[1:]),
        0,
        0,
        0,
    )
    manifest = prefix + struct.pack("<II", crc(prefix), MANIFEST_COMMIT)
    offset = manifest_address - IMAGE_BASE
    image[offset : offset + len(manifest)] = manifest
    path.mkdir()
    for name, chunk in chunks.items():
        (path / f"{name}.bin").write_bytes(chunk)
    (path / "manifest.bin").write_bytes(manifest)
    (path / "install.bin").write_bytes(image)
    (path / "layout.h").write_text("/* fixture */\n")
    (path / "sizes.json").write_text(
        json.dumps(
            {
                "ota_protocol": 2,
                "layout": 0x12345678,
                "manifest_address": manifest_address,
                "slots": slots,
            }
        )
    )
    (path / "install.json").write_text(json.dumps({"sha256": sha256(image)}))


class ComposeEffectEnergyV4Test(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.base = self.root / "base"
        self.candidate = self.root / "candidate"
        make_fixture(self.base)
        make_fixture(self.candidate, CHANGED)

    def tearDown(self):
        self.temporary.cleanup()

    def test_composes_exact_atomic_slots_and_preserves_all_others(self):
        destination = self.root / "final"
        result = compose(self.base, self.candidate, destination)
        self.assertEqual(result["changed_modules"], list(CHANGED))
        self.assertEqual(result["changed_ota_slots"], EXPECTED_OTA_SLOTS)
        final = validate_directory(destination, "test-final")
        before = validate_directory(self.base, "test-base")
        candidate = validate_directory(self.candidate, "test-candidate")
        for name in NAMES:
            expected = candidate if name in CHANGED else before
            self.assertEqual(final["chunks"][name], expected["chunks"][name])

    def test_rejects_chunk_crc_mismatch(self):
        path = self.candidate / "mode.bin"
        data = bytearray(path.read_bytes())
        data[0] ^= 1
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "chunk CRC mismatch"):
            compose(self.base, self.candidate, self.root / "final")

    def test_rejects_install_slice_mismatch(self):
        path = self.candidate / "install.bin"
        image = bytearray(path.read_bytes())
        image[3 * 32] ^= 1
        path.write_bytes(image)
        install = json.loads((self.candidate / "install.json").read_text())
        install["sha256"] = sha256(image)
        (self.candidate / "install.json").write_text(json.dumps(install))
        with self.assertRaisesRegex(ValueError, "chunk/install slice mismatch"):
            compose(self.base, self.candidate, self.root / "final")

    def test_rejects_manifest_crc_that_disagrees_with_sizes(self):
        manifest = bytearray((self.candidate / "manifest.bin").read_bytes())
        struct.pack_into("<I", manifest, 16 + 4 * (3 - 1), 0xCAFEBABE)
        struct.pack_into("<I", manifest, 56, crc(manifest[:56]))
        (self.candidate / "manifest.bin").write_bytes(manifest)
        image_path = self.candidate / "install.bin"
        image = bytearray(image_path.read_bytes())
        offset = 8 * 32
        image[offset : offset + 64] = manifest
        image_path.write_bytes(image)
        install = json.loads((self.candidate / "install.json").read_text())
        install["sha256"] = sha256(image)
        (self.candidate / "install.json").write_text(json.dumps(install))
        with self.assertRaisesRegex(ValueError, "chunk/manifest CRC mismatch"):
            compose(self.base, self.candidate, self.root / "final")

    def test_rejects_non_atomic_candidate(self):
        base_debug = (self.base / "debug_command.bin").read_bytes()
        candidate_sizes = json.loads((self.candidate / "sizes.json").read_text())
        debug = candidate_sizes["slots"][6]
        debug["crc32"] = crc(base_debug)
        debug["sha256"] = sha256(base_debug)
        (self.candidate / "debug_command.bin").write_bytes(base_debug)
        image_path = self.candidate / "install.bin"
        image = bytearray(image_path.read_bytes())
        offset = debug["address"] - IMAGE_BASE
        image[offset : offset + len(base_debug)] = base_debug
        manifest = bytearray((self.candidate / "manifest.bin").read_bytes())
        struct.pack_into("<I", manifest, 16 + 4 * (debug["id"] - 1), debug["crc32"])
        struct.pack_into("<I", manifest, 56, crc(manifest[:56]))
        (self.candidate / "manifest.bin").write_bytes(manifest)
        manifest_offset = candidate_sizes["manifest_address"] - IMAGE_BASE
        image[manifest_offset : manifest_offset + 64] = manifest
        image_path.write_bytes(image)
        (self.candidate / "sizes.json").write_text(json.dumps(candidate_sizes))
        install = json.loads((self.candidate / "install.json").read_text())
        install["sha256"] = sha256(image)
        (self.candidate / "install.json").write_text(json.dumps(install))
        with self.assertRaisesRegex(ValueError, r"unexpected OTA slots: \[2, 4\]"):
            compose(self.base, self.candidate, self.root / "final")


if __name__ == "__main__":
    unittest.main()
