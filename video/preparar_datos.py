"""Arma video/datos/: las tablas chicas que leen las figuras del video, cada una con su fuente.

Se corre una vez desde video/ (con el venv del proyecto): python preparar_datos.py [ruta_al_clon_de_ExperimentoVH]
- Copia, con `git show` (solo lectura), los resultados de otros branches de este repo.
- Copia la tabla de cierre del v10 desde un clon local de https://github.com/ClariRZ/ExperimentoVH.
- Calcula la banda del ensemble por mes de AC, A-consigna y PAQ_P3 a partir de las predicciones guardadas
  del pipeline (exp/pipeline/, no versionado). Si no están, deja el CSV que ya existe.
No entrena nada ni cambia ningún resultado.
"""
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
DATOS = AQUI / 'datos'

# (branch, archivo en ese branch, destino en datos/)
DESDE_GIT = [
    # pipeline del main con los hiperparámetros del 03 (PAQ_P3), antes del merge de Optuna
    ('b09397e', 'resultados/pipeline/main_comparacion.csv', 'paq_p3_comparacion.csv'),
    ('b09397e', 'resultados/pipeline/main_ganancias.csv', 'paq_p3_ganancias.csv'),
    ('b09397e', 'resultados/pipeline/AC_ganancias.csv', 'ac_ganancias.csv'),
    ('origin/rango', 'resultados/pipeline/rango_comparacion.csv', 'rango_comparacion.csv'),
    ('origin/feat/optuna-paq-p3', 'resultados/optuna/evaluacion_final_comparacion.csv', 'optuna_comparacion.csv'),
] + [('origin/ezequiel/etapa-1', f'resultados/{n}.csv', f'exploratorio/{n}.csv')
     for n in ['04_regla', '04_dosis', '05_d2_comparacion', '06_comparacion', '12_comparacion', '12_semillas',
               '15_comparacion', '17_comparacion', '20_comparacion', '22_comparacion', '23_comparacion',
               '23_reevaluacion', '24_comparacion']]


def copiar_de_git():
    for ref, archivo, destino in DESDE_GIT:
        texto = subprocess.run(['git', '-C', str(REPO), 'show', f'{ref}:{archivo}'],
                               check=True, capture_output=True, text=True).stdout
        (DATOS / destino).parent.mkdir(parents=True, exist_ok=True)
        (DATOS / destino).write_text(texto)
        print(f'{destino:38s} <- {ref}:{archivo}')


def copiar_v10(clon):
    origen = Path(clon) / 'v10' / 'cierre' / 'resultados.csv'
    (DATOS / 'v10_resultados.csv').write_text(origen.read_text())
    print(f'{"v10_resultados.csv":38s} <- ClariRZ/ExperimentoVH:v10/cierre/resultados.csv')


def bandas_ensemble():
    """Banda (3.000 a 6.000 envíos) del ensemble de 5 semillas, con la ganancia de la consigna."""
    sys.path.insert(0, str(REPO / 'pipeline'))
    import parametros as P
    import funciones as F
    import os
    os.chdir(REPO / 'pipeline')                      # las rutas de parametros.py son relativas a pipeline/
    carpetas = {'AC': 'AC', 'A_CONSIGNA': 'A_CONSIGNA', 'PAQ_P3': 'main'}
    if not (P.EXP / 'main' / 'pred').exists():
        print('bandas_ensemble.csv: no hay predicciones en exp/pipeline; queda el CSV versionado')
        return
    fi = F.leer_filas(P)
    es_b2 = np.asarray(fi['clase'] == 'BAJA+2')
    filas = []
    for mes in P.MESES_EVALUADOS:
        y = es_b2[np.asarray(fi['mes_fila'] == mes)]
        for nombre, carpeta in carpetas.items():
            d = P.EXP / carpeta / 'pred' / str(mes)
            if not d.exists():
                continue
            X = np.stack([np.load(a) for a in sorted(d.glob('*.npy'))])
            orden = np.argsort(-X.mean(0), kind='stable')
            g = np.cumsum(np.where(y[orden], P.GANANCIA_ACIERTO, -P.COSTO_ESTIMULO)) / 1e6
            filas.append({'config': nombre, 'foto_mes': mes, 'n_semillas': len(X),
                          'banda_ensemble_M': round(float(g[P.BANDA[0] - 1:P.BANDA[1]].mean()), 4)})
    pd.DataFrame(filas).to_csv(DATOS / 'bandas_ensemble.csv', index=False)
    curvas_ganancia(P, fi, es_b2, carpetas)
    print(f'{"bandas_ensemble.csv":38s} <- exp/pipeline/*/pred (configuración de PAQ_P3, firma 786f0055d685f102)')


def curvas_ganancia(P, fi, es_b2, carpetas, hasta=15_000, paso=10):
    """Curva de ganancia del ensamble (ganancia acumulada según la cantidad de envíos), cada `paso` envíos."""
    filas = []
    for mes in (201909, 201910):
        y = es_b2[np.asarray(fi['mes_fila'] == mes)]
        for nombre, carpeta in carpetas.items():
            d = P.EXP / carpeta / 'pred' / str(mes)
            if not d.exists():
                continue
            X = np.stack([np.load(a) for a in sorted(d.glob('*.npy'))])
            orden = np.argsort(-X.mean(0), kind='stable')
            g = np.cumsum(np.where(y[orden], P.GANANCIA_ACIERTO, -P.COSTO_ESTIMULO)) / 1e6
            for n in range(paso, hasta + 1, paso):
                filas.append({'config': nombre, 'foto_mes': mes, 'envios': n, 'ganancia_M': round(float(g[n - 1]), 4)})
    pd.DataFrame(filas).to_csv(DATOS / 'curvas_ganancia.csv', index=False)
    print(f'{"curvas_ganancia.csv":38s} <- exp/pipeline/*/pred (ensamble de 5 semillas, cada {paso} envíos)')


if __name__ == '__main__':
    DATOS.mkdir(exist_ok=True)
    copiar_de_git()
    if len(sys.argv) > 1:
        copiar_v10(sys.argv[1])
    bandas_ensemble()
