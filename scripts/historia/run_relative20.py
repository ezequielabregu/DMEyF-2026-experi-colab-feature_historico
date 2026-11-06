"""Corrida fija de veinte semillas de cambios relativos y ganancia posterior."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--wait-batch',type=Path,required=True)
    p.add_argument('--data',type=Path,required=True)
    p.add_argument('--broken',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--bucket',required=True)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    state=args.out/'batch_status.json'
    def status(value, **fields):
        state.write_text(json.dumps({'status':value,'experiment':'cambios_relativos','seeds':20,**fields},indent=2))
    status('waiting')
    for _ in range(1440):
        previous_state=json.loads(args.wait_batch.read_text())
        if previous_state.get('status') in ['complete','completed_with_errors']:
            break
        time.sleep(60)
    else:
        raise RuntimeError('La cola previa no terminó dentro del plazo')
    here=Path(__file__).resolve().parent
    status('running')
    command=[sys.executable,'-u',str(here/'exp_cambios_relativos.py'),
             '--data',str(args.data),'--broken',str(args.broken),'--hyper',str(here/'baseline07.json'),
             '--out',str(args.out/'cambios_relativos'),'--seeds','20','--threads','8']
    try:
        with (args.out/'training.log').open('w') as f:
            subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,check=True)
        import numpy as np
        import pandas as pd
        current=args.out/'cambios_relativos'
        metrics=pd.read_csv(current/'metrics.csv')
        old=pd.read_csv(args.previous/'metrics.csv')
        matched=metrics.merge(old,on=['variant','seed'],suffixes=('_20','_original'),validate='one_to_one')
        if len(matched)!=20:
            raise ValueError('Faltan las diez semillas originales por brazo')
        np.testing.assert_allclose(matched.auc_20,matched.auc_original,rtol=0,atol=1e-10)
        identical=[]
        for r in old.itertuples():
            name=f'{r.variant}_{r.seed}_201908.npy'
            identical.append(np.array_equal(np.load(current/name),np.load(args.previous/name)))
        (args.out/'original_seed_check.json').write_text(json.dumps({'auc_match':True,'all_predictions_identical':bool(all(identical))}))
        table=metrics.pivot(index='seed',columns='variant',values='auc')
        old_seeds=set(old.seed)
        groups={'original10':table.loc[table.index.isin(old_seeds)],'new10':table.loc[~table.index.isin(old_seeds)],'total20':table}
        summary={}
        for name,frame in groups.items():
            d=frame.cambios_relativos-frame.baseline
            summary[name]={'mean_delta':float(d.mean()),'wins':int((d>0).sum()),'seeds':len(d)}
        (args.out/'seed_groups.json').write_text(json.dumps(summary,indent=2))
        subprocess.run([sys.executable,str(here/'evaluate_profit.py'),'--root',str(args.out),'--data',str(args.data),
                        '--out',str(args.out/'economia'),'--families','cambios_relativos'],check=True)
        status('complete',completed=['cambios_relativos'])
    except Exception as e:
        status('failed',error=str(e))
        raise
    package=args.out/'resumen_20semillas.zip'
    with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for file in args.out.rglob('*'):
            if file.is_file() and file.suffix in ['.json','.csv'] and file.name!='validation_keys.csv':
                z.write(file,file.relative_to(args.out).as_posix())
    subprocess.run(['gcloud','storage','rsync','--recursive',str(current),args.bucket.rstrip('/')+'/archivos_completos'],check=True)
    subprocess.run(['gcloud','storage','cp',str(package),args.bucket.rstrip('/')+'/resumen_20semillas.zip'],check=True)
    print('COMPLETO: veinte semillas y evaluación económica',flush=True)


if __name__=='__main__':
    main()
