# Optuna sobre PAQ_P3, resultado del experimento

Corrida autorizada el 13/11/2026. Rama feat/optuna-paq-p3 desde b09397e. Implementación 30ef0c3e2f1408c3c4067b88faa51c63348db980.

## Diseño ejecutado

Se optimizó la ganancia media de banda N=3000-6000 de junio-agosto con dos semillas. Se completaron 30 pruebas, incluida la configuración vigente. Las tres mejores se reevaluaron con otras cinco semillas en junio-agosto. Se eligió la mayor ganancia media de reevaluación y se congeló esa elección antes de la evaluación de septiembre-octubre.

PAQ_P3 aporta las 1.653 columnas y peso BAJA+2 igual a 3. Los meses de entrenamiento terminan dos meses antes del evaluado. Los rangos fueron elegidos por Codex alrededor del baseline antes de entrenar y comunicados a Tomás.

| Parámetro | Rango |
|---|---|
| num_leaves | 24-128, logarítmico |
| min_data_in_leaf | 200-3000, logarítmico |
| learning_rate | 0,005-0,05, logarítmico |
| feature_fraction | 0,20-0,90 |
| bagging_fraction | 0,50-1,00 |
| Árboles | 150-900, logarítmico |

Optuna 4.9.0, TPE secuencial con semilla 979201 y umbral inicial de ocho pruebas completas. La primera fue encolada con el baseline y las otras siete iniciales fueron aleatorias. LightGBM 4.7.0 y SQLAlchemy 2.1.8 estaban instalados al comenzar.

## Búsqueda y reevaluación

Baseline en las dos semillas de búsqueda, 252.808175 M/mes. Baseline en las cinco semillas de reevaluación, 252.917613 M/mes.

| Prueba | Ganancia de búsqueda M/mes | Ganancia de reevaluación M/mes | Delta reevaluación M/mes |
|---|---:|---:|---:|
| 28 | 254.501855 | 252.281976 | -0.635637 |
| 27 | 254.370388 | 253.302094 | +0.384481 |
| 21 | 253.899928 | 251.419179 | -1.498434 |

Se eligió la prueba 27. Su delta de reevaluación fue +0.384481 M/mes.

```json
{
  "num_leaves": 113,
  "min_data_in_leaf": 1852,
  "learning_rate": 0.01391671442151648,
  "feature_fraction": 0.29874911813255606,
  "bagging_fraction": 0.7560705071238571,
  "arboles": 451
}
```

## Evaluación de septiembre-octubre con diez semillas

| Indicador | Resultado |
|---|---:|
| Delta ganancia de banda M/mes | +0.566348 |
| IC 95 % de ganancia M | [-2.568933, +3.701629] |
| Semillas favorables en ganancia | 6/10 |
| Delta ganancia del ensamble M/mes | +0.333739 |
| Delta AUC media | +0.00102112 |
| Semillas favorables en AUC | 10/10 |

| Mes | Delta ganancia M | Delta AUC |
|---|---:|---:|
| 201909 | +1.380150 | +0.00179063 |
| 201910 | -0.247454 | +0.00025161 |

El intervalo de ganancia incluye cero. La mejora económica queda incierta.

## Interpretación y auditoría

Todos los meses de 2019 habían sido consultados por el grupo. La evaluación de septiembre-octubre se mantuvo separada de esta nueva búsqueda y selección. El resultado sigue siendo exploratorio. La cantidad de semillas describe variación del algoritmo sobre los mismos meses y clientes.

La primera prueba reprodujo seis predicciones del baseline bit a bit. La verificación local también reproduce sus ganancias y AUC a partir de las métricas exactas anteriores. El preflight comprobó ocho bloques y cincuenta predicciones importadas. Se verificaron los SHA256 de los cuatro archivos Python del TAR transferido a GCP y la equivalencia de contenido con el commit, contemplando los finales de línea CRLF/LF.

La corrida registró 245 modelos nuevos y duró 6.85 horas. El intento 1 corresponde al preflight y el intento 2 a la ejecución del estudio. Código de salida cero y respaldo final completo. Los rangos de parámetros y sus escalas constan en el protocolo 30ef0c3.

Se preservaron el estudio SQLite, el sampler, los parámetros, la elección congelada, las predicciones, hashes y métricas. Respaldo en gs://tomas_henseler_buckito2026/exp/optuna_paq_p3_20261113/. Los agregados locales están en resultados/optuna_paq_p3_20261113/.

Referencias técnicas utilizadas para implementar el estudio persistente y el sampler.

- https://optuna.readthedocs.io/en/stable/reference/generated/optuna.create_study.html
- https://optuna.readthedocs.io/en/stable/reference/generated/optuna.samplers.TPESampler.html
- https://lightgbm.readthedocs.io/en/stable/Parameters.html
