"""P0069: validate ELF load addresses/vectors and create padded candidate BIN."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import sys
from elftools.elf.elffile import ELFFile

BASE, LIMIT, RAM, RAM_END = 0x08008000, 0x0800C000, 0x20000000, 0x20004000

def check(path, objcopy):
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        assert elf['e_machine'] == 'EM_ARM' and elf.little_endian
        vec = elf.get_section_by_name('.isr_vector')
        assert vec['sh_addr'] == BASE and vec['sh_size'] == 99 * 4
        words = struct.unpack('<99I', vec.data())
        assert words[0] == RAM_END
        text = elf.get_section_by_name('.text')
        for entry in words[1:]:
            assert entry & 1 and text['sh_addr'] <= (entry & ~1) < text['sh_addr'] + text['sh_size']
        assert elf['e_entry'] == words[1]
        for seg in elf.iter_segments():
            if seg['p_type'] != 'PT_LOAD':
                continue
            if seg['p_filesz']:
                assert BASE <= seg['p_paddr'] < seg['p_paddr'] + seg['p_filesz'] <= LIMIT
            if seg['p_memsz']:
                start, end = seg['p_vaddr'], seg['p_vaddr'] + seg['p_memsz']
                assert (BASE <= start < end <= LIMIT) or (RAM <= start < end <= RAM_END - 2048)
    raw = path.with_suffix('.raw.bin')
    subprocess.run([objcopy, '-O', 'binary', str(path), str(raw)], check=True)
    content = raw.read_bytes()
    assert struct.unpack_from('<II', content) == words[:2]
    size = (len(content) + 2047) // 2048 * 2048
    assert 0 < size <= LIMIT - BASE
    candidate = path.with_suffix('.bin')
    candidate.write_bytes(content + b'\xff' * (size - len(content)))
    info = {'package': 'P0069', 'status': 'experimental-unverified-on-hardware',
            'mcu_assumption': 'STM32L433xx, exact package/density unverified',
            'base': hex(BASE), 'end_exclusive': hex(BASE + size),
            'initial_sp': hex(words[0]), 'reset_vector': hex(words[1]),
            'raw_bytes': len(content), 'padded_bytes': size,
            'sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
            'serial': '9600 8N1', 'slave_id': 1, 'function': 4, 'address': 0, 'value': 888,
            'bootloader_verification': 'device bootloader absent; vendor host protocol analyzed only'}
    candidate.with_suffix('.json').write_text(json.dumps(info, indent=2) + '\n')
    print('PASS image bounds/vectors:', json.dumps(info))

if __name__ == '__main__':
    check(Path(sys.argv[1]), sys.argv[2])
