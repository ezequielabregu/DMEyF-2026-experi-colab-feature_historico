"""Ejecuta y registra el baseline 2019 con DuckDB, Parquet, LightGBM y Optuna."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import logging
from pathlib import Path
import platform
import sqlite3
import traceback
import uuid

import lightgbm as lgb
import optuna
import pandas as pd
from sklearn.metrics import roc_auc_score

try:
    from .baseline_data import BaselineData, parquet_source, sha256
except ImportError:
    from baseline_data import BaselineData, parquet_source, sha256

TRAIN, VALID, TEST = [201903, 201904, 201905, 201906], 201908, 201910


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False))


def register(path, run_id, status, out, config, metrics=None, error=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY, status TEXT, updated_utc TEXT, output_dir TEXT,
            config_json TEXT, metrics_json TEXT, error TEXT)''')
        con.execute('INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?)',
                    (run_id, status, now(), str(out.resolve()), json.dumps(config),
                     json.dumps(metrics) if metrics else None, error))


def execute(args, config):
    logging.info('Preparando cache Parquet y verificando claves/clases')
    path, fingerprint = parquet_source(args.data, args.cache, args.threads)
    config.update(source_sha256=fingerprint, parquet=str(path.resolve()), parquet_sha256=sha256(path))
    write_json(args.out / 'config.json', config)
    data = BaselineData(path, args.threads)
    try:
        xtrain, ytrain, _ = data.split(TRAIN)
        xvalid, yvalid, _ = data.split([VALID])
        logging.info('Entrenamiento: %s filas; validación: %s; features: %s', len(ytrain), len(yvalid), xtrain.shape[1])
        train = lgb.Dataset(xtrain, label=ytrain, free_raw_data=False)
        valid = lgb.Dataset(xvalid, label=yvalid, reference=train, free_raw_data=False)
        fixed = dict(objective='binary', metric='auc', verbosity=-1,
                     bagging_freq=1, seed=args.seed, num_threads=args.threads,
                     deterministic=True, force_col_wise=True, feature_pre_filter=False)
        study = optuna.create_study(direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=args.seed),
            storage=f'sqlite:///{args.out.resolve() / "optuna.db"}', study_name='baseline')

        def objective(trial):
            params = dict(fixed,
                          num_leaves=trial.suggest_int('num_leaves', 16, 128),
                          learning_rate=trial.suggest_float('learning_rate', .01, .15, log=True),
                          min_data_in_leaf=trial.suggest_int('min_data_in_leaf', 100, 4000, log=True),
                          feature_fraction=trial.suggest_float('feature_fraction', .5, 1.),
                          bagging_fraction=trial.suggest_float('bagging_fraction', .5, 1.))
            model = lgb.train(params, train, num_boost_round=args.max_rounds,
                              valid_sets=[valid], valid_names=['validation'],
                              callbacks=[lgb.early_stopping(args.patience, verbose=False)])
            trial.set_user_attr('best_iteration', model.best_iteration)
            auc = model.best_score['validation']['auc']
            previous = [t.value for t in study.get_trials() if t.state == optuna.trial.TrialState.COMPLETE]
            if not previous or auc > max(previous):
                model.save_model(str(args.out / 'model.txt'))
            return auc

        def checkpoint(study, trial):
            study.trials_dataframe().to_csv(args.out / 'trials.csv', index=False)
            logging.info('Trial %s/%s: AUC=%s, rondas=%s', trial.number + 1, args.trials,
                         trial.value, trial.user_attrs.get('best_iteration'))

        study.optimize(objective, n_trials=args.trials, callbacks=[checkpoint])
        best = study.best_trial
        write_json(args.out / 'selection.json', dict(trial=best.number, validation_auc=best.value,
                   best_iteration=best.user_attrs['best_iteration'], params=dict(fixed, **best.params)))
        logging.info('Selección cerrada. Evaluando octubre una vez.')
        model = lgb.Booster(model_file=str(args.out / 'model.txt'))
        xtest, ytest, ids = data.split([TEST])
        predictions = model.predict(xtest, num_threads=args.threads)
        ids.assign(prob_baja=predictions).to_parquet(args.out / 'predictions_201910.parquet', index=False)
        metrics = dict(validation_auc=best.value, test_auc=roc_auc_score(ytest, predictions),
                       best_trial=best.number, best_iteration=best.user_attrs['best_iteration'],
                       rounds_at_limit=best.user_attrs['best_iteration'] == args.max_rounds,
                       params=dict(fixed, **best.params), rows_by_month=data.counts,
                       features=xtrain.shape[1], train_rows=len(ytrain), validation_rows=len(yvalid),
                       test_rows=len(ytest), train_positives=int(ytrain.sum()),
                       validation_positives=int(yvalid.sum()), test_positives=int(ytest.sum()))
        write_json(args.out / 'metrics.json', metrics)
        pd.DataFrame({'feature': model.feature_name(), 'gain': model.feature_importance('gain')})\
            .sort_values('gain', ascending=False).to_csv(args.out / 'importance.csv', index=False)
        return metrics
    finally:
        data.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path('datasets/competencia_02_con_clase.csv.gz'))
    parser.add_argument('--cache', type=Path, default=Path('datasets/baseline_2019.parquet'))
    parser.add_argument('--out', type=Path, help='Carpeta nueva; por defecto exp/baseline_FECHA_ID')
    parser.add_argument('--registry', type=Path, default=Path('exp/experiments.sqlite'))
    parser.add_argument('--summary-dir', type=Path, default=Path('resultados/baseline'))
    parser.add_argument('--trials', type=int, default=30)
    parser.add_argument('--seed', type=int, default=2026)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--max-rounds', type=int, default=3000)
    parser.add_argument('--patience', type=int, default=100)
    args = parser.parse_args()
    if min(args.trials, args.max_rounds, args.patience, args.threads) < 1:
        parser.error('trials, max-rounds, patience y threads deben ser positivos')
    run_id = 'baseline_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ_') + uuid.uuid4().hex[:8]
    args.out = args.out or Path('exp') / run_id
    args.out.mkdir(parents=True, exist_ok=False)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.StreamHandler(), logging.FileHandler(args.out / 'run.log')])
    optuna.logging.enable_propagation()
    optuna.logging.disable_default_handler()
    config = {k: str(v.resolve()) if isinstance(v, Path) else v for k, v in vars(args).items()}
    config.update(run_id=run_id, started_utc=now(), train=TRAIN, validation=VALID, test=TEST,
                  python=platform.python_version(),
                  code_sha256={p.name: sha256(p) for p in [Path(__file__), Path(__file__).with_name('baseline_data.py')]},
                  versions={p: importlib.metadata.version(p) for p in
                            ['pandas', 'numpy', 'lightgbm', 'optuna', 'scikit-learn', 'duckdb', 'pyarrow']})
    write_json(args.out / 'config.json', config)
    write_json(args.out / 'status.json', dict(status='running', run_id=run_id, started_utc=config['started_utc']))
    register(args.registry, run_id, 'running', args.out, config)
    try:
        metrics = execute(args, config)
        register(args.registry, run_id, 'complete', args.out, config, metrics)
        args.summary_dir.mkdir(parents=True, exist_ok=True)
        write_json(args.summary_dir / f'{run_id}.json', dict(config=config, metrics=metrics))
        write_json(args.out / 'status.json', dict(status='complete', run_id=run_id, finished_utc=now()))
        logging.info('Finalizado: validación AUC %.6f; test AUC %.6f; salida %s',
                     metrics['validation_auc'], metrics['test_auc'], args.out)
    except BaseException:
        error = traceback.format_exc()
        register(args.registry, run_id, 'failed', args.out, config, error=error)
        write_json(args.out / 'status.json', dict(status='failed', run_id=run_id, finished_utc=now(), error=error))
        logging.exception('Corrida fallida; diagnóstico registrado')
        raise


if __name__ == '__main__':
    main()
