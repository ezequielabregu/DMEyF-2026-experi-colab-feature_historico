"""Exploración en agosto: disponibilidad de historia y ceros observados."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import time

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

SEEDS = [294103, 342929, 161093, 677561, 431077, 330679, 511579,
         312773, 118147, 567529]
ANCHORS = ['ctrx_quarter', 'mpayroll', 'mcaja_ahorro', 'cpayroll_trx',
           'ctarjeta_visa_transacciones']
TRAIN = [201903, 201904, 201905, 201906]


def fingerprint(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def features(base):
    """Construye originales y lags/deltas por calendario exacto, sin imputar."""
    variables = [c for c in base if c not in ['numero_de_cliente', 'foto_mes', 'clase_ternaria']]
    if len(variables) != 152:
        raise ValueError('Se esperan los 152 predictores originales')
    base = base.sort_values(['foto_mes', 'numero_de_cliente']).reset_index(drop=True)
    period = (base.foto_mes // 100) * 12 + base.foto_mes % 100
    index = pd.MultiIndex.from_arrays([base.numero_de_cliente, period])
    if not index.is_unique:
        raise ValueError('Claves duplicadas')
    rows = np.flatnonzero(base.foto_mes.isin(TRAIN + [201908]))
    x = base[variables].to_numpy(dtype=np.float32)
    positions = {k: index.get_indexer(pd.MultiIndex.from_arrays([
        base.numero_de_cliente.iloc[rows], period.iloc[rows] - k])) for k in [1, 2]}
    current = x[rows]
    parts = [current]
    names = list(variables)
    for k in [1, 2]:
        pos = positions[k]
        previous = x[np.maximum(pos, 0)].copy()
        previous[pos < 0] = np.nan
        parts += [previous, current - previous]
        names += [f'{v}_lag{k}' for v in variables] + [f'{v}_delta{k}' for v in variables]
    frame = pd.DataFrame(np.column_stack(parts), columns=names)
    frame = frame.replace([np.inf, -np.inf], np.nan)
    return base.iloc[rows][['numero_de_cliente', 'foto_mes', 'clase_ternaria']].reset_index(drop=True), frame, None, None


def run(experiment, build_extra, experiment_file):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--broken', type=Path, required=True)
    p.add_argument('--hyper', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True, help='Carpeta nueva')
    p.add_argument('--seeds', type=int, default=10, choices=range(1, 11))
    p.add_argument('--threads', type=int, default=8)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    config = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}
    config.update(seeds_used=SEEDS[:args.seeds], experiment=experiment, train=TRAIN, validation=201908,
                  hashes={str(f): fingerprint(f) for f in [args.data, args.broken, args.hyper, Path(__file__), Path(__file__).with_name('transforms.py'), Path(experiment_file)]},
                  versions={name: importlib.metadata.version(name) for name in
                            ['pandas', 'numpy', 'duckdb', 'lightgbm', 'scikit-learn']})
    (args.out / 'config.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    with duckdb.connect() as con:
        # Septiembre y octubre no se cargan; el parquet de entrada ya tiene etiquetas.
        base = con.execute('SELECT * FROM read_parquet(?) WHERE foto_mes BETWEEN 201901 AND 201908', [str(args.data)]).df()
    if base.duplicated(['numero_de_cliente', 'foto_mes']).any():
        raise ValueError('Claves duplicadas')
    if set(base.foto_mes.unique()) != set(range(201901, 201909)):
        raise ValueError('Faltan fotos de enero a agosto')
    broken = pd.read_csv(args.broken)
    for variable, month in broken[['variable', 'foto_mes']].itertuples(index=False):
        if month <= 201908:
            base.loc[base.foto_mes == month, variable] = np.nan
    ids, control, availability, behavior = features(base)
    variables = list(control.columns[:152])
    extra = build_extra(base, ids, control, variables)
    assert len(extra) == len(control) and extra.index.equals(control.index)
    assert not set(extra.columns) & set(control.columns)
    assert extra.columns.is_unique
    extra = extra.astype(np.float32).replace([np.inf, -np.inf], np.nan)
    del base, availability, behavior
    assert control.shape[1] == 760
    train = ids.foto_mes.isin(TRAIN).to_numpy()
    valid = (ids.foto_mes == 201908).to_numpy()
    if (int(train.sum()), int(valid.sum())) != (506871, 131775):
        raise ValueError('Los conteos no coinciden con la réplica')
    if not ids.clase_ternaria.isin(['BAJA+1', 'BAJA+2', 'CONTINUA']).all():
        raise ValueError('Etiquetas desconocidas o faltantes')
    ytrain = ids.clase_ternaria.isin(['BAJA+1', 'BAJA+2']).to_numpy()[train]
    yvalid = (ids.clase_ternaria == 'BAJA+2').to_numpy()[valid]
    hyper = json.loads(args.hyper.read_text())
    fixed = dict(objective='binary', metric='auc', boosting='gbdt', max_bin=31,
                 bagging_freq=1, lambda_l1=0., lambda_l2=0., min_gain_to_split=0.,
                 feature_pre_filter=False, num_threads=args.threads, deterministic=True,
                 force_col_wise=True, verbose=-1, **hyper['params'])
    ids.loc[valid, ['numero_de_cliente', 'foto_mes']].to_csv(args.out / 'validation_keys.csv', index=False)
    pd.DataFrame({'feature': list(extra.columns), 'missing_fraction': extra.loc[valid].isna().mean().to_numpy()}).to_csv(args.out / 'extra_coverage.csv', index=False)
    records = []
    predictions = {}
    for name, blocks in [('baseline', [control]), (experiment, [control, extra])]:
        x = pd.concat(blocks, axis=1)
        (args.out / f'{name}_features.json').write_text(json.dumps(list(x.columns)), encoding='utf-8')
        dataset = lgb.Dataset(x.loc[train], label=ytrain, free_raw_data=False)
        predictions[name] = []
        for seed in SEEDS[:args.seeds]:
            start = time.time()
            model = lgb.train(dict(fixed, seed=seed), dataset, num_boost_round=hyper['arboles'])
            prob = model.predict(x.loc[valid], num_threads=args.threads)
            auc = roc_auc_score(yvalid, prob)
            predictions[name].append(prob)
            # Solo predicciones de validación. Nunca se consulta octubre.
            np.save(args.out / f'{name}_{seed}_201908.npy', prob)
            record = dict(variant=name, seed=seed, auc=auc, features=x.shape[1], seconds=time.time()-start)
            records.append(record)
            pd.DataFrame(records).to_csv(args.out / 'metrics.csv', index=False)
            print(f'{name} seed={seed} AUC={auc:.9f} features={x.shape[1]}', flush=True)
        del dataset
    metrics = pd.DataFrame(records)
    table = metrics.pivot(index='seed', columns='variant', values='auc')
    summary = {}
    for candidate, reference in [(experiment, 'baseline')]:
        d = table[candidate] - table[reference]
        summary[f'{candidate}-{reference}'] = dict(mean_delta=float(d.mean()), wins=int((d > 0).sum()), seeds=len(d))
    summary['ensemble_auc'] = {name: float(roc_auc_score(yvalid, np.mean(prob, axis=0))) for name, prob in predictions.items()}
    (args.out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    (args.out / 'status.json').write_text('{"status": "complete"}', encoding='utf-8')
    print(json.dumps(summary, indent=2), flush=True)
