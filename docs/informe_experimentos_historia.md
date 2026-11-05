# Experimentos de historia corta para mejorar la AUC

**Corte de resultados:** 2026-11-05T20:50:13.811990+00:00 (UTC). Informe regenerable desde las tablas del snapshot.

Buscamos mejorar el baseline histórico de la cátedra. Este documento registra qué probamos, los resultados disponibles y las decisiones. Una corrida parcial no se clasifica como éxito ni como fracaso.

## Qué sabemos antes de estas pruebas

El baseline ya contiene las 152 variables actuales más lag1, lag2, delta1 y delta2: 760 predictores. Reprodujimos los controles A (mayo–junio) y A-consigna (marzo–junio) con dos semillas, con coincidencia a la precisión mostrada. Esa verificación no fue un experimento de mejora.

En el trabajo previo de Ezequiel se probaron lags/deltas de orden 3 y 4, tendencias, rankings simples, segundas diferencias, ratio3, rachas de ceros, historia curada y mezclas. Ninguna de las seis variantes principales superó su regla con corrección Holm frente a A; LT3 fue la más cercana (p ajustado 0,0703). Las señales posteriores de ganancia fueron exploratorias y no equivalen a mejoras confirmadas de AUC. El notebook 09 contiene otras propuestas implementadas, sin resultados publicados en el snapshot revisado.

Fuentes de antecedentes: código y tablas de la rama ezequiel/etapa-1, commit 3b44f21; detalle en docs/revision_experimentos_20261104.md. Las métricas nuevas de este informe provienen de nuestras corridas, no de esas tablas.

## Diseño que mantuvimos fijo

| Elemento | Definición |
|---|---|
| Dataset | competencia_02_crudo.csv.gz; parquet 2019 preparado y verificado |
| Entrenamiento | Marzo–junio, 506.871 filas, sin sampling |
| Etiqueta de entrenamiento | BAJA+1 o BAJA+2 frente a CONTINUA |
| Evaluación | Agosto de 2019, 131.775 filas; AUC positiva BAJA+2 |
| Control | 760 predictores, sin ID ni foto_mes como features |
| Ajuste | Parámetros del 07, 339 árboles, max_bin 31, bagging_freq 1 |
| Semillas | Diez por brazo; iguales entre baseline y variante |
| Recursos | Ocho hilos; cuatro familias ejecutadas secuencialmente |
| Faltantes | NaN; mismas filas en ambos brazos; saneamiento antes de calcular historia |
| Meses cargados | Enero–agosto; no se consultó octubre en estas pruebas |

## Qué probamos

| Familia | Nuevas columnas | Pregunta |
|---|---:|---|
| Historia reciente | 387 | Dar mayor peso a las fotos recientes: media 4:2:1 y comparación con pasado ponderado 2:1. |
| Cambios relativos | 258 | Medir cambios proporcionales simétricos de uno y dos meses, con valores finitos acotados entre −1 y 1. |
| Persistencia y reversión | 516 | Separar dos caídas, dos subidas, reversión y aceleración relativa en tres fotos. |
| Rankings con cero fijo | 365 | Comparar la posición del cliente dentro del mes y signo, y su cambio en uno y dos meses. |

Las tres primeras familias transforman información ya contenida en las tres fotos; buscamos una representación que LightGBM aproveche mejor. Los rankings incorporan además la distribución contemporánea del conjunto de clientes. Las fórmulas exactas se fijaron antes de correr en docs/experimentos_historia.md.

## Resultados al corte

Las medias siguientes usan únicamente semillas emparejadas. Si hay tres variantes y diez baselines, se comparan esos tres pares, no medias de tamaños diferentes. La diferencia está en unidades de AUC; +0,001 equivale a pasar de 0,912 a 0,913.

| Familia | Estado | Pares | AUC control | AUC variante | Diferencia media | A favor |
|---|---|---:|---:|---:|---:|---:|
| Historia reciente | Parcial | 4/10 | 0.912117 | 0.910812 | -0.001305 | 1/4 |
| Cambios relativos | Pendiente | 0/10 | — | — | — | — |
| Persistencia y reversión | Pendiente | 0/10 | — | — | — | — |
| Rankings con cero fijo | Pendiente | 0/10 | — | — | — | — |

### Historia reciente

| Semilla | AUC control | AUC variante | Diferencia |
|---|---:|---:|---:|
| 161093 | 0.909832201 | 0.908692345 | -0.001139856 |
| 294103 | 0.914852804 | 0.910844762 | -0.004008042 |
| 342929 | 0.911741449 | 0.911399274 | -0.000342174 |
| 677561 | 0.912040962 | 0.912311328 | +0.000270366 |

**Avance parcial:** 4/10 variantes y 10/10 baselines. No cerrar una conclusión ni detener la prueba por estos resultados.

## Qué resultó y qué no podemos afirmar todavía

Las familias pendientes no tienen un resultado negativo: todavía no fueron evaluadas. Las filas parciales muestran avance del entrenamiento, no una conclusión final. Cuando estén completos los diez pares, reportaremos conjuntamente la diferencia media, la dirección por semilla y el cambio en AUC del ensamble.

No se elegirá una familia por una semilla favorable. Tampoco se confundirá una mejora de ganancia económica de antecedentes con una mejora de AUC en esta comparación.

## Decisiones y siguientes pasos

- Terminar las cuatro familias y conservar también resultados negativos.
- Ajustar el decaimiento solo si historia reciente presenta una señal favorable al completar diez semillas, considerando media, consistencia y ensamble. No se fijó un umbral numérico formal: cualquier criterio nuevo debe registrarse antes de la búsqueda, no reconstruirse como si hubiera sido predefinido.
- Si se habilita esa búsqueda, seleccionar alfa dentro de una partición temporal interna al bloque de entrenamiento, respetando las etiquetas a dos meses; reentrenar marzo–junio y evaluar la elección en agosto. No usar agosto para elegir alfa.
- No modificar la cola ni los pesos actuales a partir de resultados parciales.

## Límites de la evidencia

Agosto ya se usó para optimizar el baseline y discutir otras variantes. Sigue siendo validación exploratoria, aunque una búsqueda posterior de alfa use otro bloque. Los parámetros del 07 favorecen potencialmente al baseline: aquí medimos el efecto de agregar features con ese ajuste fijo, no modelos optimizados individualmente. Las diez semillas comparten clientes y mes; su dispersión no mide incertidumbre entre períodos. Comparar cuatro familias introduce selección múltiple. El catálogo de roturas fue construido retrospectivamente y no representa una política estrictamente disponible en tiempo real.

## Trazabilidad

Cada experimento conserva config.json con hashes SHA-256, versiones y semillas; metrics.csv con AUC por modelo; summary.json con el ensamble; extra_coverage.csv con faltantes; y status.json al completar. El paquete para tutoría no contiene datos individuales. El notebook notebooks/tutoria_historia.ipynb permite revisar estas tablas y visualizar las diferencias.

Corrida: familias_c9930bd. Código desplegado: c9930bd. Rama: feat/historia-transformaciones. El informe y el notebook pueden evolucionar sin modificar el código de la corrida en curso.
