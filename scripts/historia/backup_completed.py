"""Respalda cada familia terminada sin modificar los procesos de entrenamiento."""
import argparse
import json
from pathlib import Path
import subprocess
import time

FAMILIES = ['historia_reciente', 'cambios_relativos', 'persistencia', 'rankings_cero_fijo']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--bucket', required=True)
    args = p.parse_args()
    backed_up = set()
    # Un día como límite; la cola sigue ejecutándose aunque termine este respaldo.
    for _ in range(1440):
        state_file = args.root / 'batch_status.json'
        state = json.loads(state_file.read_text()) if state_file.exists() else {}
        for family in FAMILIES:
            if family in backed_up or not (args.root / family / 'status.json').exists():
                continue
            command = ['gcloud', 'storage', 'rsync', '--recursive', str(args.root / family), args.bucket.rstrip('/') + '/' + family]
            result = subprocess.run(command)
            if result.returncode == 0:
                backed_up.add(family)
                (args.root / f'{family}_backup.json').write_text(json.dumps({'status': 'complete', 'bucket': command[-1]}))
                print(f'RESPALDADO {family}', flush=True)
            else:
                print(f'REINTENTAR {family}', flush=True)
        final = state.get('status') in ['complete', 'completed_with_errors']
        if final and set(state.get('completed', [])) <= backed_up:
            subprocess.run(['gcloud', 'storage', 'cp', str(state_file), args.bucket.rstrip('/') + '/batch_status.json'])
            return
        time.sleep(60)
    print('Límite de espera alcanzado. Revisar logs de respaldo.', flush=True)


if __name__ == '__main__':
    main()
