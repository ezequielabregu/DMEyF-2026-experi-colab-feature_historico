"""Optuna sobre PAQ_P3, con cache por configuración y reanudación de modelos."""
import gc
import hashlib
import json
import os
from pathlib import Path
import pickle
import sqlite3
import sys
import time
import traceback

os.chdir(Path(__file__).resolve().parent)
import numpy as np
import optuna
import pandas as pd
from sklearn.metrics import roc_auc_score
import funciones as F
import parametros as P
import optuna_config as C

ROOT = Path.cwd().parent
OUT = ROOT / 'resultados/optuna'
RUNTIME = ROOT / 'runtime'
CHECKPOINT = ROOT / 'exp/checkpoint'
STATE_FILE = ROOT / 'estado_optuna.json'
for folder in (OUT, RUNTIME, CHECKPOINT):
    folder.mkdir(parents=True, exist_ok=True)


def write_json(path, value):
    F.escribir_texto(path, json.dumps(value, indent=2, default=str))


class Experiment:
    def __init__(self):
        previous = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
        if previous:
            write_json(ROOT / f"estado_intento_{previous['attempt']}.json", previous)
        self.state = {'status': 'running', 'phase': 'preflight',
                      'started': previous.get('started', time.time()),
                      'attempt': previous.get('attempt', 0) + 1,
                      'new_models': previous.get('new_models', 0),
                      'configuration_commit': (ROOT / 'source_commit.txt').read_text().strip(),
                      'source_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                                        for f in [Path('funciones.py'), Path('parametros.py'),
                                                  Path('optuna_config.py'), Path('optuna_paq.py')]}}
        if previous:
            for name in ('funciones.py', 'parametros.py', 'optuna_config.py'):
                assert previous['source_sha256'][name] == self.state['source_sha256'][name], name
            self.state['previous_source_sha256'] = previous['source_sha256']
        self.seeds = F.semillas(P, 10)
        self.search_seeds = [self.seeds[i] for i in C.SEARCH_SEED_INDICES]
        self.reeval_seeds = [self.seeds[i] for i in C.REEVALUATION_SEED_INDICES]
        assert not set(self.search_seeds) & set(self.reeval_seeds)
        self.info = F.leer_filas(P)
        self.table = F.Tabla(P, P.BLOQUES_PAQ_P3)
        self.datasets = {}
        self.eval_x = {}
        self.study = None
        self.sampler = None
        self.save()

    def save(self):
        self.state['updated'] = time.time()
        write_json(STATE_FILE, self.state)

    def phase(self, name):
        self.state['phase'] = name
        self.save()
        print('FASE', name, flush=True)

    def snapshot(self):
        if self.sampler is not None:
            target = RUNTIME / 'sampler.pkl'
            temporary = target.with_suffix('.tmp')
            temporary.write_bytes(pickle.dumps(self.sampler))
            os.replace(temporary, target)
            (CHECKPOINT / 'sampler.pkl.tmp').write_bytes(target.read_bytes())
            os.replace(CHECKPOINT / 'sampler.pkl.tmp', CHECKPOINT / 'sampler.pkl')
        database = RUNTIME / 'study.sqlite'
        if database.exists():
            temporary = CHECKPOINT / 'study.tmp.sqlite'
            with sqlite3.connect(database) as source, sqlite3.connect(temporary) as destination:
                source.backup(destination)
            os.replace(temporary, CHECKPOINT / 'study.sqlite')
        self.save()

    def preflight(self):
        assert self.table.columnas == F.Tabla(P, P.MAIN['bloques']).columnas
        assert len(self.table.columnas) == 1653 and P.MAIN['peso_b2'] == 3
        expected = pd.read_csv(ROOT / 'referencia/main_huellas_pred.csv')
        assert len(expected) == 50
        assert F.revisar_config(P, P.MAIN, crear=False) == '786f0055d685f102'
        for row in expected.itertuples():
            prediction = np.load(F.ruta_pred(P, 'main', row.foto_mes, row.semilla))
            self.validate(prediction, row.foto_mes)
            assert F.huella(prediction) == row.huella
        blocks = pd.read_csv(ROOT / 'referencia/huellas_bloques.csv').set_index('bloque')
        for block in P.BLOQUES_PAQ_P3:
            values, _ = F.leer_bloque(P, block)
            assert F.huella(values) == blocks.loc[block, 'huella'], block
        print('PREFLIGHT OK: ocho bloques y cincuenta predicciones de MAIN', flush=True)

    def validate(self, prediction, month):
        assert prediction.dtype == np.float32
        assert prediction.shape == ((self.info['mes_fila'] == month).sum(),)
        assert np.isfinite(prediction).all()

    def config(self, params, anchor=False):
        hiper = {key: value for key, value in params.items() if key != 'arboles'}
        name = ('anchor_' if anchor else 'opt_') + F.firma(params)
        return {**P.MAIN, 'nombre': name, 'hiper': hiper, 'arboles': int(params['arboles']),
                'eligio_entre_varias': True}

    def dataset(self, month):
        if month not in self.datasets:
            train_months = F.ventana(P.MAIN, month, P)
            assert max(train_months) <= month - P.DISTANCIA
            train = np.isin(self.info['mes_fila'], train_months)
            self.datasets[month] = F.dataset(self.table, train, self.info['clase'][train], 3, P)
            self.eval_x[month] = self.table.filas(self.info['mes_fila'] == month)
        return self.datasets[month]

    def prediction(self, config, month, seed):
        F.revisar_config(P, config)
        path = F.ruta_pred(P, config['nombre'], month, seed)
        if path.exists():
            prediction = np.load(path)
        else:
            started = time.time()
            dataset = self.dataset(month)
            model = F.entrenar(dataset, config, seed, P)
            prediction = model.predict(self.eval_x[month], num_threads=P.N_HILOS).astype(np.float32)
            self.validate(prediction, month)
            F.guardar_npy(path, prediction)
            self.state['new_models'] += 1
            self.state['last_model'] = {'config': config['nombre'], 'month': month, 'seed': seed,
                                        'seconds': round(time.time() - started, 2)}
            print('MODELO', self.state['last_model'], flush=True)
            del model
        self.validate(prediction, month)
        sidecar = path.with_suffix('.json')
        metadata = {'huella': F.huella(prediction), 'month': month, 'seed': seed,
                    'config': config['nombre']}
        if sidecar.exists():
            assert json.loads(sidecar.read_text()) == metadata, str(path)
        else:
            write_json(sidecar, metadata)
        self.snapshot()
        return prediction

    def metrics(self, config, months, seeds, anchor=False):
        rows = []
        for month in months:
            y = self.info['clase'][self.info['mes_fila'] == month] == 'BAJA+2'
            for seed in seeds:
                prediction = self.prediction(config, month, seed)
                if anchor:
                    baseline = np.load(F.ruta_pred(P, 'main', month, seed))
                    assert np.array_equal(prediction, baseline), ('Anchor distinto de MAIN', month, seed)
                rows.append({'config': config['nombre'], 'foto_mes': month, 'semilla': seed,
                             'ganancia_banda_M': float(F.banda(F.curva(prediction, y, P), P) / 1e6),
                             'auc': roc_auc_score(y, prediction)})
        return pd.DataFrame(rows)

    def baseline_metrics(self, months, seeds):
        return self.metrics(P.MAIN, months, seeds)

    def setup_study(self):
        sampler_path = RUNTIME / 'sampler.pkl'
        self.sampler = pickle.loads(sampler_path.read_bytes()) if sampler_path.exists() else \
            optuna.samplers.TPESampler(seed=P.SEMILLA_PRIMIGENIA, n_startup_trials=C.N_STARTUP_TRIALS)
        self.study = optuna.create_study(study_name='paq_p3_optuna_20261113',
                                         storage=f'sqlite:///{(RUNTIME / "study.sqlite").as_posix()}',
                                         direction='maximize', sampler=self.sampler, load_if_exists=True)
        protocol = {'space': C.SPACE, 'search_seeds': self.search_seeds, 'reeval_seeds': self.reeval_seeds,
                    'search_months': C.SEARCH_MONTHS, 'final_months': C.FINAL_MONTHS, 'n_trials': C.N_TRIALS}
        protocol = json.loads(json.dumps(protocol))
        stored = self.study.user_attrs.get('protocol')
        if stored:
            assert stored == protocol
        else:
            self.study.set_user_attr('protocol', protocol)
        for trial in self.study.get_trials(deepcopy=False):
            if trial.state == optuna.trial.TrialState.RUNNING:
                self.study.tell(trial.number, state=optuna.trial.TrialState.FAIL)
                if set(trial.params) == set(C.SPACE):
                    self.study.enqueue_trial(trial.params, user_attrs={'recovered_trial': trial.number})
        if not self.study.get_trials():
            self.study.enqueue_trial({**P.HIPER_03, 'arboles': P.ARBOLES_03}, user_attrs={'anchor': True})
        self.snapshot()

    def search(self):
        self.phase('busqueda')
        complete = optuna.trial.TrialState.COMPLETE

        def objective(trial):
            params = {}
            for name, (low, high, logarithmic, integer) in C.SPACE.items():
                params[name] = trial.suggest_int(name, low, high, log=logarithmic) if integer else \
                    trial.suggest_float(name, low, high, log=logarithmic)
            self.state['trial'] = trial.number
            self.snapshot()
            anchor = params == {**P.HIPER_03, 'arboles': P.ARBOLES_03}
            config = self.config(params, anchor=anchor)
            trial.set_user_attr('config', config['nombre'])
            frame = self.metrics(config, C.SEARCH_MONTHS, self.search_seeds, anchor=anchor)
            value = float(frame.ganancia_banda_M.mean())
            trial.set_user_attr('auc', float(frame.auc.mean()))
            frame.to_csv(OUT / f'trial_{trial.number:03d}_metricas.csv', index=False)
            return value

        def callback(study, trial):
            finished = [t for t in study.trials if t.state == complete]
            self.state['trials_complete'] = len(finished)
            study.trials_dataframe().to_csv(OUT / 'busqueda.csv', index=False)
            self.snapshot()
            print('PRUEBA COMPLETA', trial.number, trial.value, 'total', len(finished), flush=True)

        finished = [t for t in self.study.trials if t.state == complete]
        remaining = C.N_TRIALS - len(finished)
        if remaining > 0:
            self.study.optimize(objective, n_trials=remaining, callbacks=[callback], n_jobs=1)
        trials = [t for t in self.study.trials if t.state == complete]
        assert len(trials) == C.N_TRIALS
        return sorted(trials, key=lambda trial: (-trial.value, trial.number))[:C.N_CANDIDATES]

    def selection(self, candidates):
        self.phase('reevaluacion')
        base = self.baseline_metrics(C.SEARCH_MONTHS, self.reeval_seeds)
        base_mean = float(base.ganancia_banda_M.mean())
        rows = []
        frames = [base]
        for trial in candidates:
            anchor = trial.params == {**P.HIPER_03, 'arboles': P.ARBOLES_03}
            config = P.MAIN if anchor else self.config(trial.params)
            frame = base if anchor else self.metrics(config, C.SEARCH_MONTHS, self.reeval_seeds)
            frames.append(frame)
            rows.append({'trial': trial.number, 'params': trial.params, 'config': config,
                         'search_M': trial.value, 'reevaluation_M': float(frame.ganancia_banda_M.mean()),
                         'delta_M': float(frame.ganancia_banda_M.mean() - base_mean)})
            pd.DataFrame(rows).to_csv(OUT / 'reevaluacion.csv', index=False)
        pd.concat(frames).drop_duplicates(['config', 'foto_mes', 'semilla']).to_csv(OUT / 'reevaluacion_metricas.csv', index=False)
        selected = sorted(rows, key=lambda row: (-row['reevaluation_M'], row['trial']))[0]
        choice = {'candidate': selected, 'baseline_M': base_mean,
                  'advance_to_final': bool(selected['delta_M'] > 0 and selected['config']['nombre'] != 'main'),
                  'candidates': [trial.number for trial in candidates]}
        frozen = ROOT / 'eleccion.json'
        if frozen.exists():
            assert json.loads(frozen.read_text()) == choice, 'Cambió la elección al reanudar'
        else:
            write_json(frozen, choice)
        self.snapshot()
        print('ELECCION CONGELADA', choice, flush=True)
        return choice

    def final(self, choice):
        if not choice['advance_to_final']:
            self.state['conclusion'] = 'Ninguna candidata supera MAIN en reevaluación'
            return
        self.phase('evaluacion_final')
        self.datasets.clear()
        self.eval_x.clear()
        gc.collect()
        config = choice['candidate']['config']
        candidate = self.metrics(config, C.FINAL_MONTHS, self.seeds)
        baseline = self.baseline_metrics(C.FINAL_MONTHS, self.seeds)
        pd.concat([candidate, baseline]).to_csv(OUT / 'evaluacion_final_metricas.csv', index=False)
        evaluation = F.Evaluacion(P, self.info, self.seeds)
        for name in (config['nombre'], 'main'):
            evaluation.leer(name, C.FINAL_MONTHS)
        result = evaluation.comparar(config['nombre'], 'main', C.FINAL_MONTHS, P.SEMILLA_BOOTSTRAP)
        paired = candidate.merge(baseline, on=['foto_mes', 'semilla'], suffixes=('_candidato', '_main'), validate='one_to_one')
        paired['delta_auc'] = paired.auc_candidato - paired.auc_main
        paired['delta_banda_M'] = paired.ganancia_banda_M_candidato - paired.ganancia_banda_M_main
        paired.to_csv(OUT / 'evaluacion_final_pares.csv', index=False)
        by_seed = paired.groupby('semilla')[['delta_banda_M', 'delta_auc']].mean()
        by_seed.to_csv(OUT / 'evaluacion_final_por_semilla.csv')
        result['delta_auc'] = float(by_seed.delta_auc.mean())
        result['auc_semillas_a_favor'] = int((by_seed.delta_auc > 0).sum())
        result['n_semillas'] = len(self.seeds)
        result['trial'] = choice['candidate']['trial']
        result['exploratorio'] = True
        pd.DataFrame([result]).to_csv(OUT / 'evaluacion_final_comparacion.csv', index=False)
        self.state['result'] = result
        print('RESULTADO FINAL', result, flush=True)

    def run(self):
        self.preflight()
        if '--check-only' in sys.argv:
            self.state['status'] = 'preflight_passed'
            self.save()
            return
        self.setup_study()
        candidates = self.search()
        choice = self.selection(candidates)
        self.final(choice)
        self.state['status'] = 'complete'
        self.state['finished'] = time.time()
        self.snapshot()


if __name__ == '__main__':
    experiment = None
    try:
        experiment = Experiment()
        experiment.run()
    except BaseException:
        traceback.print_exc()
        if experiment is not None:
            experiment.state['status'] = 'failed'
            experiment.state['error'] = traceback.format_exc()
            experiment.save()
        raise
