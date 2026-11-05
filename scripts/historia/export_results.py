"""Snapshot de tablas y metadatos; excluye IDs, modelos y predicciones."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import zipfile

FAMILIES = ['historia_reciente', 'cambios_relativos', 'persistencia', 'rankings_cero_fijo']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('snapshot.json', json.dumps({'captured_utc': datetime.now(timezone.utc).isoformat()}, indent=2))
        for name in ['batch_status.json', 'tutoria/deployment.json']:
            file = args.root / name
            if file.exists():
                z.write(file, file.name)
        for family in FAMILIES:
            for name in ['config.json', 'metrics.csv', 'summary.json', 'status.json', 'extra_coverage.csv']:
                file = args.root / family / name
                if file.exists():
                    z.write(file, f'{family}/{name}')
    print(args.out)


if __name__ == '__main__':
    main()
