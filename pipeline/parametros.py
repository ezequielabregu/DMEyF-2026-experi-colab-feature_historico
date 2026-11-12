"""Parámetros del pipeline. Es el ÚNICO lugar donde se definen.

Ficha: fichas/etapa_31_pipeline_main.md (en el laboratorio).

Cómo se usa:
- en el main, CORRIDA = MAIN;
- en un branch, CORRIDA es una copia de MAIN con un solo cambio y otro nombre (ejemplos al final);
- al hacer merge, el cambio pasa a MAIN y CORRIDA vuelve a MAIN (pasos en el README).
"""
from pathlib import Path

# --- 1. Rutas (relativas a feature_historico/pipeline/) ------------------------
# CRUDO es lo único que cambia entre la Mac y la VM (en la VM: ~/buckets/b1/datasets/competencia_02_crudo.csv)
CRUDO = Path('../../../dataset/competencia_02_crudo.csv')
BASE_PARQUET = Path('../data/base_2019.parquet')       # lo escribe el 01 si no existe
RESULTADOS_ANTERIORES = Path('../resultados')           # solo se lee: 01_meses_rotos.csv, 03_hiperparametros.json, 08_variables.csv
EXP = Path('../exp/pipeline')                           # salidas pesadas (no van al repo)
RESULTADOS = Path('../resultados/pipeline')             # tablas chicas y figuras (van al repo)
EXP_22 = Path('../exp/22')                              # solo para verificar PAQ_P3 contra el 22; si no existe, se saltea
EXP_15 = Path('../exp/15')                              # ídem, para AC

# --- 2. Meses ------------------------------------------------------------------
MES_DESDE, MES_HASTA = 201901, 201912                   # el 01 lee 2019 entero: la clase de 201910 necesita 201911 y 201912
MES_TOPE = 201910                                       # la clase solo se guarda hasta acá; nada posterior entra en el 02 al 05
MESES_TABLA = [201903, 201904, 201905, 201906, 201907, 201908, 201909, 201910]   # filas de la tabla de variables
MESES_EVALUADOS = [201906, 201907, 201908, 201909, 201910]                       # banco temporal
MESES_CONSIGNA = [201903, 201904, 201905, 201906]       # ventana de la consigna
DISTANCIA = 2                                           # la clase de un mes se conoce dos meses después

# --- 3. Meses rotos (01) ---------------------------------------------------------
UMBRAL_ROTO, UMBRAL_VECINOS = 95, 50                    # % de ceros o nulos en el mes, y máximo en los meses vecinos
ROTOS_A_MANO = [                                        # los que la regla no detecta (01_clase_calidad)
    ('Visa_fultimo_cierre', 'ceros', 201907), ('Master_fultimo_cierre', 'ceros', 201907),
    ('mcajeros_propios_descuentos', 'ceros', 201910), ('ccajeros_propios_descuentos', 'ceros', 201910),
    ('ctarjeta_visa_descuentos', 'ceros', 201910), ('mtarjeta_visa_descuentos', 'ceros', 201910),
]
ROTOS_EXTRA = [('ctarjeta_master_descuentos', 201910), ('mtarjeta_master_descuentos', 201910)]   # como el 06 y el 12

# --- 4. Bloques de variables -----------------------------------------------------
# Cada bloque es una función de funciones.py (ver PRODUCTORES). El orden de la lista es el orden de las columnas,
# y el orden de las columnas cambia el modelo: no reordenar.
# Cambiar un valor de esta sección cambia bloques que ya existen: el 02 los rehace y corta si no dan lo mismo
# que resultados/pipeline/huellas_bloques.csv. Un cambio a propósito va como bloque nuevo, con otro nombre.
BLOQUES_AC = ['AC']                                     # lag y delta de 1 y 2 meses (760 columnas)
BLOQUES_PAQ_P3 = ['AC', 'CURADA', 'ACH_V', 'ACH_Q', 'ACH_T', 'ACH_Z', 'MVH', 'R']   # 1.653 columnas
N_CURADAS = 30                                          # las de RESULTADOS_ANTERIORES / 08_variables.csv
MINIMO_PREVIOS = 2                                      # z4, relmax4 y los bloques del 13 piden al menos 2 fotos previas
FOTOS = 9                                               # 201910 mira hasta 201901
LAGS_MV = [1, 2]                                        # Visa y Master con su historia (como el 17)
ROTO_NUEVO = ('Visa_mfinanciacion_limite', 201904)      # roto solo en las combinaciones de Visa y Master (como el 17)
LAGS_R = [1, 2]                                         # cambios relativos de Tomás (como el 20)
EPSILON = 1e-12
BLOQUE_FILAS = 20_000                                   # filas por bloque al calcular (solo memoria y tiempo)

# --- 5. Modelo -----------------------------------------------------------------
POSITIVOS = ['BAJA+1', 'BAJA+2']                        # clase de entrenamiento
N_HILOS = 8                                             # no cambia los resultados (deterministic); no entra en la firma
FIJOS = {'objective': 'binary', 'metric': 'auc', 'boosting': 'gbdt', 'max_bin': 31, 'bagging_freq': 1,
         'lambda_l1': 0.0, 'lambda_l2': 0.0, 'min_gain_to_split': 0.0, 'feature_pre_filter': False,
         'num_threads': N_HILOS, 'deterministic': True, 'force_col_wise': True, 'verbose': -1}
HIPER_03 = {'num_leaves': 50, 'min_data_in_leaf': 764, 'learning_rate': 0.016711332559601208,
            'feature_fraction': 0.4170576239818614, 'bagging_fraction': 0.641424496819069}   # 03_hiperparametros.json
ARBOLES_03 = 296

# --- 6. Configuraciones --------------------------------------------------------
# Una estrategia es lo que define las predicciones: bloques, peso de BAJA+2, ventana, hiperparámetros y árboles.
# ventana: 'reciente' = todos los meses de MESES_TABLA hasta DISTANCIA antes del mes evaluado;
#          'consigna' = MESES_CONSIGNA;
#          una lista de meses = esos meses, siempre que terminen DISTANCIA antes del mes evaluado.
# PAQ_P3 queda congelada: es la estrategia del 22. Los controles contra el 22 se aplican solo a ella.
PAQ_P3 = {'bloques': BLOQUES_PAQ_P3, 'peso_b2': 3, 'ventana': 'reciente', 'hiper': HIPER_03, 'arboles': ARBOLES_03}

MAIN = {'nombre': 'main', 'meses': MESES_EVALUADOS, **PAQ_P3}   # al hacer merge, el cambio del branch va acá
REFERENCIAS = {                                         # el main se compara también contra el baseline
    'AC': {'nombre': 'AC', 'meses': MESES_EVALUADOS, 'bloques': BLOQUES_AC, 'peso_b2': 1, 'ventana': 'reciente',
           'hiper': HIPER_03, 'arboles': ARBOLES_03},
    'A_CONSIGNA': {'nombre': 'A_CONSIGNA', 'meses': [201908, 201909, 201910], 'bloques': BLOQUES_AC, 'peso_b2': 1,
                   'ventana': 'consigna', 'hiper': HIPER_03, 'arboles': ARBOLES_03},
}

CORRIDA = MAIN                                          # en un branch: la configuración del branch (ejemplos al final)

# --- 7. Evaluación ---------------------------------------------------------------
SEMILLA_PRIMIGENIA = 979201
N_SEMILLAS = 5                                          # decisión 4 de la ficha
BANDA = (3_000, 6_000)                                  # ambos incluidos
LARGO_CURVA = 25_000
GANANCIA_ACIERTO = 1_072_500
COSTO_ESTIMULO = 27_500
N_BOOTSTRAP = 2_000
SEMILLA_BOOTSTRAP = SEMILLA_PRIMIGENIA                  # la comparación j del 04 usa SEMILLA_BOOTSTRAP + j

# Regla de merge (decisiones 1 y 2 de la ficha): se hace merge si d > 0 y gana en al menos MINIMO_SEMILLAS
# de N_SEMILLAS. Se juzga en MESES_EVALUADOS; si el branch eligió entre varias configuraciones mirando los
# meses (por ejemplo, con Optuna), elige con MESES_ELECCION y se juzga solo en MESES_REGLA_SI_ELIGIO.
# Eso se declara en la configuración del branch con 'eligio_entre_varias': True.
MINIMO_SEMILLAS = 3
MESES_ELECCION = [201906, 201907, 201908]
MESES_REGLA_SI_ELIGIO = [201909, 201910]

# Lo que tiene que dar PAQ_P3 con estos parámetros (d, meses e IC: ±0,005). Cambia solo si cambia PAQ_P3.
ESPERADO_PAQ_P3 = {'AC': {'d_M': 9.00, 'ic95_inf_M': 5.18, 'ic95_sup_M': 12.82, 'semillas_a_favor': 5,
                          'por_mes': {201906: 12.26, 201907: 4.04, 201908: 7.82, 201909: 9.69, 201910: 11.19}},
                   'A_CONSIGNA': {'d_M': 12.60, 'ic95_inf_M': 7.73, 'ic95_sup_M': 17.46, 'semillas_a_favor': 5,
                                  'por_mes': {201908: 7.82, 201909: 12.10, 201910: 17.87}}}

# --- 8. Producción (05) ------------------------------------------------------------
MES_PRODUCCION = 201910                                 # predice este mes sin mirar su clase
N_SEMILLAS_PRODUCCION = 20                              # semillerío (decisiones.md:466)
ENVIOS_PRODUCCION = 4_500                               # el medio de la banda (decisiones.md:467)

# --- Ejemplos de branch ---------------------------------------------------------------
# Reemplazan la línea `CORRIDA = MAIN` de la sección 6.
# Propuesta #3, el rango (hace falta la función del bloque 'RANGO' en funciones.py):
#   CORRIDA = {**MAIN, 'nombre': 'rango', 'bloques': BLOQUES_PAQ_P3 + ['RANGO']}
# Propuesta #1, un solo mes de entrenamiento:
#   CORRIDA = {**MAIN, 'nombre': 'ventana_1mes', 'ventana': 'ultimo'}   (hace falta definir 'ultimo' en funciones.ventana)
# Propuesta #6, hiperparámetros elegidos con Optuna en MESES_ELECCION:
#   CORRIDA = {**MAIN, 'nombre': 'optuna_auc', 'hiper': {...}, 'arboles': ..., 'eligio_entre_varias': True}
