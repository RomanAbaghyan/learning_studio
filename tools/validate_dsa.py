#!/usr/bin/env python3
"""Validate an authored DSA revision before publishing; never writes learner data."""
from collections import Counter
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastapi import HTTPException
from backend.dsa_api import ContentStore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content-dir', type=Path, default=ROOT / 'backend' / 'content' / 'dsa')
    args = parser.parse_args()
    try:
        catalog, lessons = ContentStore(args.content_dir).load()
    except HTTPException as error:
        print(error.detail, file=sys.stderr)
        return 1
    print(json.dumps({
        'valid': True,
        'topics': len(catalog['topics']),
        'status': dict(Counter(item['status'] for item in catalog['topics'])),
        'lessonDocuments': len(lessons),
        'resources': len(catalog.get('resources', [])),
        'comparisons': len(catalog.get('comparisons', [])),
        'note': 'Schema validation does not certify educational completeness or algorithm correctness.',
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
