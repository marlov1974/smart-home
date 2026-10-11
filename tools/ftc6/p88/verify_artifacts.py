"""P0088 public-artifact consistency checks; no private image or network needed."""
import csv
import json
from pathlib import Path


def verify(directory):
    directory = Path(directory)
    atlas = json.loads((directory / 'command-atlas.json').read_text())
    rows = atlas['rows']
    identifiers = [r['id'] for r in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError('duplicate atlas ID')
    with (directory / 'command-atlas.csv').open(newline='') as source:
        csv_rows = list(csv.DictReader(source))
    if [r['id'] for r in csv_rows] != identifiers:
        raise ValueError('CSV IDs differ')
    for original, encoded in zip(rows, csv_rows):
        for key, value in original.items():
            actual = json.loads(encoded[key]) if isinstance(value, (dict, list)) else encoded[key]
            expected = value if isinstance(value, (dict, list)) else '' if value is None else str(value)
            if actual != expected:
                raise ValueError('CSV content differs: ' + original['id'] + '/' + key)
    ledger = (directory / 'atlas-ledger.md').read_text().splitlines()
    # The separator has no spaces, so only the header precedes data rows.
    ledger_ids = [line.split(' | ')[0][2:] for line in ledger if line.startswith('| ')][1:]
    if ledger_ids != identifiers:
        raise ValueError('human ledger IDs differ')
    coverage = json.loads((directory / 'coverage.json').read_text())
    if coverage['semantic']['inventoried_rows'] != len(rows):
        raise ValueError('stale coverage row count')
    descriptors = json.loads((directory / 'source-tx-descriptors.json').read_text())
    fields = sum(len(d['fields']) for d in descriptors)
    if coverage['structural']['source_tx_descriptors'] != len(descriptors) or coverage['structural']['source_tx_fields'] != fields:
        raise ValueError('stale source coverage')
    inventory = json.loads((directory / 'structural-inventory.json').read_text())
    if [{k: v for k, v in d.items() if k != 'qualified_call_sites'} for d in descriptors] != inventory['source_tx_descriptors']:
        raise ValueError('source descriptor copies differ')
    return {'result': 'PASS', 'json_rows': len(rows), 'csv_rows': len(csv_rows),
            'human_ledger_all_ids_present': True, 'source_fields': fields}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.directory), indent=2))
