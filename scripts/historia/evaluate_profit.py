"""Ganancia descriptiva en agosto usando predicciones existentes, sin entrenar."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

FAMILIES = ['historia_reciente', 'cambios_relativos', 'persistencia', 'rankings_cero_fijo']
HIT, MISS = 1072500, -27500


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def profit(probabilities, positive):
    prob = np.asarray(probabilities)
    y = np.asarray(positive)
    if prob.ndim != 1 or y.shape != prob.shape or len(prob) < 6000:
        raise ValueError('Forma de predicciones/etiquetas inválida')
    if not np.isfinite(prob).all() or ((prob < 0) | (prob > 1)).any():
        raise ValueError('Probabilidades inválidas')
    order = np.argsort(-prob, kind='stable')
    curve = np.cumsum(np.where(y[order], HIT, MISS), dtype=np.int64)
    return {'gain_4000_M': float(curve[3999] / 1e6),
            'gain_band_3000_6000_M': float(curve[2999:6000].mean() / 1e6),
            'hits_4000': int(y[order[:4000]].sum())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True, help='Carpeta nueva')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'month': 201908,
                'positive': 'BAJA+2', 'hit': HIT, 'miss': MISS, 'fixed_N': 4000,
                'band': [3000, 6000], 'band_inclusive': True,
                'interpretation': 'Exploratorio en validación; sin optimizar N, no es test independiente.',
                'data_sha256': digest(args.data), 'script_sha256': digest(__file__),
                'input_hashes': {}}
    with duckdb.connect() as con:
        labels = con.execute('SELECT numero_de_cliente, foto_mes, clase_ternaria FROM read_parquet(?) WHERE foto_mes=201908', [str(args.data)]).df()
    records, skipped = [], []
    for family in FAMILIES:
        folder = args.root / family
        state = folder / 'status.json'
        if not state.exists() or json.loads(state.read_text()).get('status') != 'complete':
            skipped.append(family)
            continue
        keys_path = folder / 'validation_keys.csv'
        keys = pd.read_csv(keys_path)
        joined = keys.merge(labels, on=['numero_de_cliente', 'foto_mes'], how='left', sort=False, validate='one_to_one')
        if len(keys) != 131775 or len(joined) != len(labels) or not keys.equals(joined[keys.columns]):
            raise ValueError(f'Claves desalineadas en {family}')
        if not joined.clase_ternaria.isin(['BAJA+1', 'BAJA+2', 'CONTINUA']).all():
            raise ValueError('Clases faltantes o desconocidas')
        y = (joined.clase_ternaria == 'BAJA+2').to_numpy()
        if int(y.sum()) != 543:
            raise ValueError('Cantidad de positivos distinta de la réplica')
        config = json.loads((folder / 'config.json').read_text())
        seeds = config['seeds_used']
        if len(seeds) != 10 or len(set(seeds)) != 10:
            raise ValueError('Se requieren diez semillas por brazo')
        previous = pd.read_csv(folder / 'metrics.csv').set_index(['variant', 'seed'])
        manifest['input_hashes'][str(keys_path)] = digest(keys_path)
        outputs = args.out / family
        outputs.mkdir()
        family_records = []
        for variant in ['baseline', family]:
            predictions = []
            for seed in seeds:
                path = folder / f'{variant}_{seed}_201908.npy'
                prob = np.load(path, allow_pickle=False)
                auc = float(roc_auc_score(y, prob))
                if abs(auc - float(previous.loc[(variant, seed), 'auc'])) > 1e-10:
                    raise ValueError(f'AUC distinta: {variant} {seed}; revisar alineación')
                manifest['input_hashes'][str(path)] = digest(path)
                row = dict(family=family, variant=variant, kind='seed', seed=seed, auc=auc, **profit(prob, y))
                family_records.append(row)
                predictions.append(prob)
            prob = np.mean(predictions, axis=0)
            family_records.append(dict(family=family, variant=variant, kind='ensemble', seed=None,
                                       auc=float(roc_auc_score(y, prob)), **profit(prob, y)))
        table = pd.DataFrame(family_records)
        table.to_csv(outputs / 'profit_metrics.csv', index=False)
        summary = {}
        for metric in ['gain_4000_M', 'gain_band_3000_6000_M']:
            paired = table[table.kind == 'seed'].pivot(index='seed', columns='variant', values=metric)
            delta = paired[family] - paired.baseline
            ensemble = table[table.kind == 'ensemble'].set_index('variant')[metric]
            summary[metric] = dict(baseline_mean=float(paired.baseline.mean()), variant_mean=float(paired[family].mean()),
                                   mean_delta=float(delta.mean()), wins=int((delta > 0).sum()), seeds=len(delta),
                                   baseline_ensemble=float(ensemble['baseline']), variant_ensemble=float(ensemble[family]),
                                   ensemble_delta=float(ensemble[family] - ensemble['baseline']))
        (outputs / 'profit_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
        records += family_records
        print(family, json.dumps(summary), flush=True)
    pd.DataFrame(records).to_csv(args.out / 'profit_metrics.csv', index=False)
    manifest['skipped_incomplete'] = skipped
    manifest['completed'] = [f for f in FAMILIES if f not in skipped]
    (args.out / 'config.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (args.out / 'status.json').write_text('{"status":"complete"}', encoding='utf-8')
    print('Pendientes:', skipped, flush=True)


if __name__ == '__main__':
    main()
