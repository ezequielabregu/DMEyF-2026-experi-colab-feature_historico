"""Espera el fin de la cola, calcula ganancia y respalda tablas agregadas."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--data',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--bucket',required=True)
    p.add_argument('--exporter',type=Path,required=True)
    args=p.parse_args()
    for _ in range(1440):
        state=json.loads((args.root/'batch_status.json').read_text())
        if state.get('status') in ['complete','completed_with_errors']:
            break
        time.sleep(60)
    else:
        raise RuntimeError('La cola no terminó dentro del plazo de un día')
    here=Path(__file__).resolve().parent
    subprocess.run([sys.executable,str(here/'evaluate_profit.py'),'--root',str(args.root),
                    '--data',str(args.data),'--out',str(args.out)],check=True)
    archive=args.out/'tutoria_con_ganancia.zip'
    subprocess.run([sys.executable,str(args.exporter),'--root',str(args.root),
                    '--profit',str(args.out),'--out',str(archive)],check=True)
    subprocess.run(['gcloud','storage','cp',str(archive),args.bucket.rstrip('/')+'/tutoria_con_ganancia.zip'],check=True)
    print('Evaluación económica y respaldo completos',flush=True)


if __name__=='__main__':
    main()
