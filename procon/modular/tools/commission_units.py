"""P0076: pure offline validation of two expected Procon SID/UID mappings.

No bus scan, transmission, configuration, provisioning or control occurs here.
Matching saved observations does not prove isolation, collision freedom or wiring.
"""
import argparse
import json
from pathlib import Path
import re
from control_command import validate_slave


def normalize_uid(uid):
    if not isinstance(uid, str) or not re.fullmatch(r'[0-9a-fA-F]{24}', uid):
        raise ValueError('UID must be exactly 24 hexadecimal digits in register word order')
    uid = uid.lower()
    if uid in ('0' * 24, 'f' * 24):
        raise ValueError('All-zero/all-FF UID is invalid')
    return uid


def decode_identity(words, requested_slave=None):
    if not isinstance(words, list) or len(words) != 12 or any(type(word) is not int or not 0 <= word <= 65535 for word in words):
        raise ValueError('Identity requires 12 uint16 words from input72..83')
    schema, effective, configured, source, valid, uid_valid = words[:6]
    if schema != 1 or valid != 1 or uid_valid != 1:
        raise ValueError('Unsupported identity schema or invalid configuration/UID')
    validate_slave(effective)
    if effective != configured or source not in (1, 2, 3) or (source == 1 and effective != 1):
        raise ValueError('Inconsistent effective/configured slave or configuration source')
    if source == 3 and effective > 30:
        raise ValueError('Hardware DIP addressing supports only slave1..30')
    if requested_slave is not None and effective != validate_slave(requested_slave):
        raise ValueError('Returned identity does not match the requested slave address')
    uid_words = [(words[6 + index * 2] << 16) | words[7 + index * 2] for index in range(3)]
    uid = normalize_uid(''.join(f'{word:08x}' for word in uid_words))
    return {'schema': schema, 'slave_id': effective, 'configured_slave_id': configured,
            'source': source, 'source_name': {1: 'default', 2: 'image-profile', 3: 'hardware-dip'}[source],
            'config_valid': True, 'uid_valid': True, 'uid96': uid, 'uid_words': uid_words,
            'words_72_83': words}


def decode_dip(words, identity):
    if not isinstance(words, list) or len(words) != 3 or any(type(v) is not int for v in words):
        raise ValueError('DIP verification requires input84..86 raw/stable/reason words')
    raw, stable, reason = words
    if not 0 <= raw <= 255 or stable != 1 or reason != 0 or (raw & 0x60) != 0x60:
        raise ValueError('DIP samples unstable, rejected or outside supported SW6/SW7 mode')
    if not 1 <= (raw & 31) <= 30 or (raw & 31) != identity['slave_id']:
        raise ValueError('DIP low-five-bit address disagrees with the physical identity')
    return {'raw': raw, 'stable': True, 'rejection_reason': reason, 'words_84_86': words}


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or type(manifest.get('schema')) is not int or manifest.get('schema') != 1:
        raise ValueError('Expected commissioning manifest schema1')
    units = manifest.get('units')
    if not isinstance(units, list) or len(units) != 2:
        raise ValueError('Exactly two independently identified units are required')
    result, names, addresses, uids = [], set(), set(), set()
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError('Each unit must be an object')
        name = unit.get('name')
        if not isinstance(name, str) or not name.strip() or name != name.strip() or len(name) > 80 or name in names:
            raise ValueError('Unit names must be nonempty and unique')
        address = validate_slave(unit.get('slave_id'))
        uid = normalize_uid(unit.get('uid96'))
        if address in addresses:
            raise ValueError('Duplicate slave address: do not join these units')
        if uid in uids:
            raise ValueError('Duplicate UID: these are not two independently identified units')
        names.add(name);addresses.add(address);uids.add(uid)
        result.append({'name': name, 'slave_id': address, 'uid96': uid})
    return result


def validate_commissioning(manifest, observations):
    expected = validate_manifest(manifest)
    if not isinstance(observations, list) or len(observations) != 2:
        raise ValueError('Exactly two saved identity observations are required')
    observed = {}
    for item in observations:
        if not isinstance(item, dict) or not isinstance(item.get('name'), str) or item.get('name') in observed:
            raise ValueError('Observed unit names must be unique strings')
        address = validate_slave(item.get('slave_id'))
        decoded = decode_identity(item.get('identity_words_72_83'), requested_slave=address)
        if decoded['source'] == 3:
            decoded['dip'] = decode_dip(item.get('dip_words_84_86'), decoded)
        observed[item['name']] = decoded
    if len({item['slave_id'] for item in observed.values()}) != 2 or len({item['uid96'] for item in observed.values()}) != 2:
        raise ValueError('Duplicate observed slave address or UID; bus join is blocked')
    for unit in expected:
        actual = observed.get(unit['name'])
        if actual is None or actual['slave_id'] != unit['slave_id'] or actual['uid96'] != unit['uid96']:
            raise ValueError('Expected physical unit SID/UID mapping does not match observations: ' + unit['name'])
    return {'schema': 1, 'status': 'OFFLINE_IDENTITY_MATCH', 'units': expected,
            'control_authorized': False, 'physical_isolation_verified': False, 'shared_bus_verified': False,
            'note': 'Saved identity words match the expected mapping. Isolated physical reads, wiring and interleaved collision-free dual polling still require separate verification.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('observations', type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(validate_commissioning(json.loads(args.manifest.read_text()),
                                               json.loads(args.observations.read_text())), indent=2))
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
