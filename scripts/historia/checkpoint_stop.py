"""Corte solicitado entre checkpoints de predicciones; no apaga la VM."""
import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def verified_signal(pid, expected, sig):
    proc=Path(f'/proc/{pid}/cmdline')
    if not proc.exists():
        return False
    command=proc.read_bytes().replace(b'\0',b' ').decode(errors='replace')
    if expected not in command:
        raise RuntimeError(f'PID {pid} no corresponde al proceso esperado')
    os.kill(pid,sig)
    return True


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--queued-root',type=Path,required=True)
    p.add_argument('--worker',type=int,required=True)
    p.add_argument('--wrapper',type=int,required=True)
    p.add_argument('--queued',type=int,required=True)
    p.add_argument('--target',type=int,default=10)
    p.add_argument('--bucket',required=True)
    args=p.parse_args()
    # Primero impedir que se inicie el siguiente experimento o se interprete el corte como fallo científico.
    verified_signal(args.queued,'run_rankings20.py',signal.SIGSTOP)
    verified_signal(args.wrapper,'run_relative20.py',signal.SIGSTOP)
    folder=args.root/'cambios_relativos'
    metric=folder/'metrics.csv'
    deadline=time.monotonic()+600
    rows=[]
    while time.monotonic()<deadline:
        try:
            before=metric.stat()
            rows=list(csv.DictReader(metric.open()))
            after=metric.stat()
            if before.st_mtime_ns!=after.st_mtime_ns or before.st_size!=after.st_size:
                time.sleep(1)
                continue
            valid=[r for r in rows if r.get('variant')=='baseline' and r.get('seed')]
            if len(valid)>=args.target:
                if not all((folder/f'baseline_{r["seed"]}_201908.npy').exists() for r in valid):
                    raise RuntimeError('Falta predicción de una semilla registrada')
                break
        except (FileNotFoundError,KeyError):
            pass
        time.sleep(2)
    else:
        print('Límite de espera: guardar los checkpoints disponibles sin esperar otra semilla.',flush=True)
    verified_signal(args.worker,'exp_cambios_relativos.py',signal.SIGSTOP)
    record={'status':'interrupted_at_checkpoint','reason':'Usuario solicita apagar VM dentro de veinte minutos',
            'saved_utc':datetime.now(timezone.utc).isoformat(), 'metrics_rows':len(rows),
            'baseline_seeds':sum(r.get('variant')=='baseline' for r in rows),
            'variant_seeds':sum(r.get('variant')=='cambios_relativos' for r in rows),
            'target_seeds':20,'automatic_resume':False}
    (args.root/'checkpoint_stop.json').write_text(json.dumps(record,indent=2))
    (args.root/'batch_status.json').write_text(json.dumps(record,indent=2))
    (args.queued_root/'batch_status.json').write_text(json.dumps({'status':'not_started_user_shutdown','experiment':'rankings_cero_fijo','seeds':20},indent=2))
    # No quedan escrituras de entrenamiento después de congelar al worker.
    for pid, expected in [(args.worker,'exp_cambios_relativos.py'),(args.wrapper,'run_relative20.py'),(args.queued,'run_rankings20.py')]:
        verified_signal(pid,expected,signal.SIGKILL)
    subprocess.run(['sync'],check=True)
    print(json.dumps(record),flush=True)
    for root,name in [(args.root,'relativos20_20261106'),(args.queued_root,'rankings20_20261106')]:
        subprocess.run(['gcloud','storage','rsync','--recursive',str(root),args.bucket.rstrip('/')+'/'+name],check=True,timeout=180)
    print('CHECKPOINT_Y_RESPALDO_COMPLETOS',flush=True)


if __name__=='__main__':
    main()
