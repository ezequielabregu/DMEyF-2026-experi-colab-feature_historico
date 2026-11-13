# Optuna sobre PAQ_P3

Ejecución autorizada por Tomás el 13/11/2026. Rama feat/optuna-paq-p3 desde
b09397e, con 1.653 columnas del baseline reproducido y peso BAJA+2 igual a 3.

Objetivo principal de Optuna: ganancia media de banda N=3000-6000 inclusiva,
promediada entre junio, julio y agosto y dos semillas fijas. AUC secundaria.
Cada modelo entrena desde marzo hasta dos meses antes de su mes evaluado.

Treinta pruebas completas, incluida la configuración actual como primera prueba.
TPE secuencial, semilla 979201, ocho pruebas iniciales aleatorias. Rangos fijados
antes de entrenar: num_leaves 24-128 log, min_data_in_leaf 200-3000 log,
learning_rate 0.005-0.05 log, feature_fraction 0.20-0.90, bagging_fraction
0.50-1.00 y árboles 150-900 log. Límites elegidos por Codex alrededor del baseline.

Semillas de búsqueda: 294103 y 342929. Las tres mejores pruebas se reevalúan
en junio-agosto con 161093, 677561, 431077, 330679 y 511579. La configuración
vigente siempre participa como referencia. Se elige la mayor ganancia media en
reevaluación y se desempata por número de prueba. Si supera a MAIN, se congela
la elección y se evalúa en septiembre-octubre con las diez semillas originales
del pipeline. Si ninguna supera MAIN en reevaluación, termina el experimento.

Funciones de entrenamiento, columnas, orden, roturas, max_bin=31, pesos y ventanas
son los del pipeline. Se optimizan seis hiperparámetros. El notebook 23 de Ezequiel
ya optimizó cinco parámetros y peso_b2 con 296 árboles fijos. Esta prueba incorpora
árboles junto al learning rate, usa dos semillas en búsqueda y cinco nuevas en
reevaluación, con peso_b2 fijo.

Preflight con ocho bloques y cincuenta predicciones originales verificadas. La
primera prueba vuelve a entrenar seis modelos del baseline y exige predicciones
idénticas. Bins fijos con data_random_seed=979201. Cache por firma de configuración,
mes y semilla, predicciones atómicas y verificadas por forma, finitud y hash.
Estudio persistente SQLite, sampler persistido, snapshot consistente por SQLite
backup. Las pruebas interrumpidas se reencolan con sus parámetros y cache.

La comparación de septiembre-octubre incluye delta de banda, IC del pipeline,
semillas favorables, ensamble y AUC. Todos los meses de 2019 ya se consultaron,
por lo que el resultado es exploratorio. La elección se fija antes de la nueva
evaluación en septiembre-octubre. El resultado se publica también si es negativo.

Entrada de ejecución: python pipeline/optuna_paq.py desde el checkout. Un chequeo
previo se ejecuta con --check-only. La corrida vive en una carpeta GCP aislada,
con respaldos y apagado al concluir. MAIN se conserva como referencia versionada.
