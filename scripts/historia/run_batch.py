"""Cola secuencial de las cuatro familias y paquete agregado para tutoría."""
import argparse
import csv
from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

EXPERIMENTS = ['historia_reciente', 'cambios_relativos', 'persistencia', 'rankings_cero_fijo']
EXPORT_FILES = ['config.json', 'metrics.csv', 'summary.json', 'status.json', 'extra_coverage.csv']


def write_status(path, **fields):
    fields['updated_utc'] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(fields, indent=2), encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--broken', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--wait-pid', type=int)
    p.add_argument('--bucket', help='Prefijo gs:// de respaldo del paquete agregado')
    p.add_argument('--reuse-complete', type=Path, help='Reutiliza solo familias completas y verificadas de una cola anterior')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    status = args.out / 'batch_status.json'
    package = args.out / 'tutoria'
    package.mkdir()
    here = Path(__file__).resolve().parent
    deployment = here.parents[1] / 'deployment.json'
    if deployment.exists():
        shutil.copy2(deployment, package / deployment.name)
    write_status(status, status='waiting', experiments=EXPERIMENTS, waiting_pid=args.wait_pid)
    if args.wait_pid:
        proc = Path(f'/proc/{args.wait_pid}/cmdline')
        while proc.exists():
            try:
                command = proc.read_bytes()
            except FileNotFoundError:
                break
            if b'comparar_historia.py' not in command:
                break
            print(f'Esperando corrida anterior PID {args.wait_pid}', flush=True)
            time.sleep(30)
    completed, failed = [], []
    for experiment in EXPERIMENTS:
        write_status(status, status='running', current=experiment, completed=completed, failed=failed)
        out = args.out / experiment
        previous = args.reuse_complete / experiment if args.reuse_complete else None
        reuse = previous is not None and (previous / 'status.json').exists()
        if reuse:
            if json.loads((previous / 'status.json').read_text()).get('status') != 'complete':
                raise ValueError(f'Estado previo inválido: {experiment}')
            config = json.loads((previous / 'config.json').read_text())
            # No reutilizar resultados si cambiaron entrada, código o parámetros.
            for filename, expected in config['hashes'].items():
                digest = hashlib.file_digest(open(filename, 'rb'), 'sha256').hexdigest()
                if digest != expected:
                    raise ValueError(f'Cambió el archivo de la corrida completa: {filename}')
            if Path(config['data']).resolve() != args.data.resolve() or Path(config['broken']).resolve() != args.broken.resolve():
                raise ValueError('Las rutas de entrada no coinciden con la corrida anterior')
            with (previous / 'metrics.csv').open() as f:
                metrics = list(csv.DictReader(f))
            pairs = {(r['variant'], int(r['seed'])) for r in metrics}
            seeds = set(config['seeds_used'])
            if len(seeds) != 10 or len(metrics) != 20 or pairs != {(v, s) for v in ['baseline', experiment] for s in seeds}:
                raise ValueError('Corrida completa sin los diez pares esperados')
            shutil.copytree(previous, out)
            old_log = args.reuse_complete / f'{experiment}.log'
            if old_log.exists():
                shutil.copy2(old_log, args.out / old_log.name)
            else:
                (args.out / f'{experiment}.log').write_text('Reutilizado de ' + str(previous))
            result = subprocess.CompletedProcess([], 0)
            print(f'REUTILIZADO {experiment}: {previous}', flush=True)
        command = [sys.executable, '-u', str(here / f'exp_{experiment}.py'),
                   '--data', str(args.data.resolve()), '--broken', str(args.broken.resolve()),
                   '--hyper', str(here / 'baseline07.json'), '--out', str(out.resolve()),
                   '--seeds', '10', '--threads', '8']
        if not reuse:
            print(f'INICIO {experiment}', flush=True)
            with (args.out / f'{experiment}.log').open('w', encoding='utf-8') as log:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode == 0 and (out / 'status.json').exists():
            completed.append(experiment)
        else:
            failed.append(experiment)
        destination = package / experiment
        destination.mkdir()
        for name in EXPORT_FILES:
            if (out / name).exists():
                shutil.copy2(out / name, destination / name)
        shutil.copy2(args.out / f'{experiment}.log', destination / 'execution.log')
        write_status(status, status='running', current=None, completed=completed, failed=failed)
        shutil.copy2(status, package / status.name)
        archive = args.out / 'tutoria_resultados.zip'
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for file in package.rglob('*'):
                if file.is_file():
                    z.write(file, file.relative_to(package).as_posix())
        if args.bucket:
            backup = subprocess.run(['gcloud', 'storage', 'cp', str(archive), args.bucket.rstrip('/') + '/tutoria_resultados.zip'])
            if backup.returncode:
                print('AVISO: respaldo falló; los resultados locales se conservaron.', flush=True)
        print(f'FIN {experiment}: codigo={result.returncode}', flush=True)
    write_status(status, status='complete' if not failed else 'completed_with_errors', completed=completed, failed=failed)
    shutil.copy2(status, package / status.name)
    with zipfile.ZipFile(args.out / 'tutoria_resultados.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for file in package.rglob('*'):
            if file.is_file():
                z.write(file, file.relative_to(package).as_posix())
    if args.bucket:
        subprocess.run(['gcloud', 'storage', 'cp', str(args.out / 'tutoria_resultados.zip'), args.bucket.rstrip('/') + '/tutoria_resultados.zip'])
    print(json.dumps(dict(completed=completed, failed=failed)), flush=True)
    return bool(failed)


if __name__ == '__main__':
    sys.exit(main())
