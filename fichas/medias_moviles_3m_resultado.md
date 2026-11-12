# Medias móviles de tres meses: resultado final

12/11/2026. Rama feat/medias-moviles-3m; implementación d259778e05d3564c1269a66145c200229d66f9b9. Baseline PAQ_P3 b09397e, reproducido previamente en GCP.

## Qué se probó

Se agregó una media simple sobre 129 variables de montos y conteos: valores disponibles del cliente en t, t-1 y t-2, con mínimo dos valores finitos. Si hay dos se promedian esos dos, sin buscar meses anteriores. Con uno o ninguno queda NaN. Ceros y negativos cuentan como observados. Total: 1.782 columnas frente a 1.653 del main.

Se conservan ventanas de entrenamiento, datos, pesos, hiperparámetros, 296 árboles y cinco semillas del pipeline. Comparación en junio-octubre de 2019. Se modificó una única representación, sin buscar ventanas ni reoptimizar. La media ya usa información presente en los lags: prueba una representación para árboles, no información nueva.

La primera propuesta exigía tres valores; se detuvo durante el cálculo de bloques, antes de entrenar modelos nuevos, por sugerencia de Tomás de aprovechar la historia disponible. La definición vigente se fijó antes de obtener resultados.

## Resultado contra main

| Métrica | Resultado |
|---|---:|
| Delta de ganancia banda, media por mes | -0,3400 M |
| IC 95 % del pipeline | -2,4933 a +1,8133 M |
| Semillas favorables | 2/5 |
| Delta banda del ensamble | -0,3847 M |
| Delta AUC media (desde CSV redondeado) | +0,000246 |
| Ganancia banda media MAIN | 263,5347 M |
| Ganancia banda media variante | 263,1947 M |
| Regla del pipeline | NO PASA |

| Mes | Delta banda M |
|---|---:|
| 201906 | -1,1306 |
| 201907 | +0,4850 |
| 201908 | -0,1968 |
| 201909 | -0,9099 |
| 201910 | +0,0520 |

La diferencia no muestra una mejora: el promedio es ligeramente negativo y el intervalo incluye cero. La pequeña mejora de AUC no se traduce en dinero. Mantener MAIN. No afirmar un daño demostrado ni que ninguna media móvil pueda funcionar; el resultado corresponde a esta definición, variables y ajuste fijo.

## Cobertura y verificaciones

Aceptar dos valores recupera entre 2,16 % y 12,17 % de los casos cliente-variable en los meses evaluados respecto de exigir tres. Son celdas de variables, no porcentajes de clientes. Mayor cobertura no implicó mayor ganancia.

Pasaron los controles de meses calendario con huecos, separación de clientes, nulos, ceros y no uso de futuro. El pipeline comprobó las ocho huellas originales sin cambios y las 25 predicciones de MAIN idénticas a las originales. No se modificaron funciones del baseline.

Hubo un corte Spot antes de guardar octubre. Se recuperaron veinte predicciones completas y se reanudó solo lo faltante con las mismas firmas y semilla fija de bins. Se conservaron el log/estado anteriores, checkpoint, código y manifiesto. El intento estricto quedó separado. Resultado final complete, 25 predicciones nuevas.

## Evidencia y cierre

Tablas, figuras, cobertura, deltas por semilla, logs y estado: resultados/medias_moviles_3m_min2_20261112. Respaldo de predicciones, claves, firmas y código: gs://tomas_henseler_buckito2026/exp/medias_moviles_3m_min2_20261112/. Marcador respaldo_completo.txt comprobado. VM confirmada en TERMINATED tras respaldo automático.

Todos los meses de 2019 ya fueron consultados: es exploratorio, sin validación temporal independiente. El promedio de cinco semillas no equivale a cinco meses independientes. Se conserva el resultado negativo en esta ficha; no se incorpora al PDF como una mejora y no se hace merge ni push.
