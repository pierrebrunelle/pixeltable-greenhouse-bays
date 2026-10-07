"""Seed five bays, three readings and two plantings.

Usage:
    python seed.py            # seeds the local `greenhouse` catalog directory
    python seed.py my_dir     # or another directory you passed to `pxt schema update`
"""
import sys
from pathlib import Path

import pixeltable as pxt

target = sys.argv[1] if len(sys.argv) > 1 else 'greenhouse'
HERE = Path(__file__).resolve().parent

SEED = {
    'bays': [
        {'bay_id': 'A-12', 'zone': 'north', 'crop': None, 'status': 'open'},
        {'bay_id': 'A-14', 'zone': 'north', 'crop': None, 'status': 'open'},
        {'bay_id': 'A-15', 'zone': 'north', 'crop': 'basil', 'status': 'planted'},
        {'bay_id': 'B-02', 'zone': 'south', 'crop': 'tomato', 'status': 'planted'},
        {'bay_id': 'B-05', 'zone': 'south', 'crop': None, 'status': 'resting'},
    ],
    'readings': [
        {'bay_id': 'A-15', 'taken_at': '2026-10-04T06:00', 'temp_c': 18.5, 'humidity_pct': 70.0},
        {'bay_id': 'B-02', 'taken_at': '2026-10-04T06:00', 'temp_c': 24.0, 'humidity_pct': 78.0},
        {'bay_id': 'B-02', 'taken_at': '2026-10-04T14:00', 'temp_c': 33.0, 'humidity_pct': 88.0},
    ],
    'plantings': [
        {'bay_id': 'A-15', 'crop': 'basil', 'planted_on': '2026-09-12', 'status': 'growing'},
        {'bay_id': 'B-02', 'crop': 'tomato', 'planted_on': '2026-08-20', 'status': 'fruiting'},
    ],
}

for table_name, rows in SEED.items():
    t = pxt.get_table(f'{target}/{table_name}')
    if t.count() > 0:
        print(f'{target}/{table_name} already has {t.count()} rows; skipping')
        continue
    for row in rows:
        for k, v in row.items():
            if isinstance(v, str) and v.startswith('data/'):
                row[k] = str(HERE / v)   # local sample media file
    t.insert(rows)
    print(f'inserted {len(rows)} rows into {target}/{table_name}')
