# Nuevas representaciones de historia corta

Rama de trabajo: `feat/historia-transformaciones`. Diseño fijado el 5/11/2026 antes de ejecutar estas cuatro familias. Los resultados anteriores quedan como antecedentes; no se presentan como nuevas validaciones independientes.

## Archivos independientes

Cada script ejecuta su propio baseline y una sola familia. No consume salidas de los otros experimentos, ni exige correrlos en orden. El motor y los operadores comunes evitan diferencias accidentales en filas, etiquetas o entrenamiento.

| Script en scripts/historia/ | Hipótesis | Variables nuevas |
|---|---|---:|
| exp_cambios_relativos.py | La variación proporcional simétrica facilita detectar deterioro a distintas escalas | 258 |
| exp_persistencia.py | Dos cambios del mismo signo o una reversión distinguen trayectorias distintas | 516 |
| exp_historia_reciente.py | Ponderar más las fotos recientes mejora la representación del nivel y del cambio | 387 |
| exp_rankings_cero_fijo.py | La trayectoria de posición dentro del mes y signo reduce dependencia de niveles nominales | 365 |

Se reutiliza la clasificación de compañeros: 129 montos/conteos; dentro de ellos, 73 montos monetarios. Fechas, estados, banderas, edad y antigüedad no reciben nuevas transformaciones en estas familias, pero conservan los lags/deltas del baseline.

### Definiciones congeladas

Todos los operadores usan t, t−1 y t−2, meses calendario exactos. Valores desconocidos permanecen NaN y los dos modelos conservan las mismas filas.

1. Cambio relativo: `(a-b)/(|a|+|b|)`, para lag1 y lag2. Si a=b=0, devuelve 0; si falta algún valor, NaN. El resultado finito está en [−1,1]. No se buscan epsilons o variantes del denominador según AUC.
2. Persistencia: indicadores de dos caídas, dos subidas y reversión entre los dos cambios consecutivos; diferencia entre cambios relativos consecutivos. Si falta alguna de las tres fotos/valores, todos quedan NaN. «Deterioro» depende del significado de cada variable: una caída no siempre es mala.
3. Historia reciente: media `(4*x_t+2*x_t−1+x_t−2)/7`; desvío actual respecto al pasado ponderado `(2*x_t−1+x_t−2)/3`; cambio relativo simétrico actual frente a ese pasado. Pesos fijos, sin búsqueda. Requiere tres observaciones finitas. Se distingue de modificar la ponderación de filas de entrenamiento, que no se hace aquí.
4. Ranking: por variable, mes y signo, percentil con rangos promedio sobre magnitud absoluta; positivos en (0,1], negativos en [−1,0), cero exacto en 0, faltante en NaN. Agregar ranking actual, lag1/2 y delta1/2. El mes completo está disponible para construir el percentil; no se usa clase ni otro mes para rankear.

Las primeras tres familias son funciones de información ya presente en el baseline. La hipótesis es mejorar la representación para árboles de capacidad finita, no incorporar información nueva. Los rankings también incorporan la distribución contemporánea del conjunto de clientes.

## Comparación común

- Baseline: originales + lag1/2 + delta1/2 (760), sin ID ni foto_mes como predictores.
- Train marzo–junio full; positivo BAJA+1 o BAJA+2. Agosto: AUC positiva BAJA+2.
- Se leen únicamente enero–agosto; no hay evaluación ni selección con septiembre/octubre.
- Catálogo de roturas de la réplica, aplicado antes de historia. Fue construido retrospectivamente: declarar esa limitación.
- Parámetros del 07 conservados en baseline07.json, 339 árboles, max_bin=31, bagging_freq=1, ocho hilos. Sin Optuna, early stopping nuevo ni selección de columnas por agosto.
- Diez semillas idénticas y ordenadas; dos semillas solo como control técnico, seguido de diez independientemente del signo inicial. No ejecutar los cuatro experimentos en paralelo con ocho hilos cada uno en la VM de 12 CPU.
- Métricas: AUC por semilla, diferencia media de AUC, número de semillas favorables y AUC del ensamble. Reportar las cuatro familias, incluyendo resultados negativos; no combinar automáticamente las ganadoras.
- Parámetros elegidos previamente sobre el baseline; comparar con ajuste fijo es una ablación, no una comparación de óptimos de cada familia.
- Agosto ya fue consultado y usado para ajuste. Las mejoras son exploratorias y condicionadas al mes; diez semillas no representan diez meses independientes. No se etiqueta una candidata como confirmada por ganar una de cuatro comparaciones. Toda combinación o ajuste posterior será otra exploración explícita.

## Ejecución

Desde la raíz del checkout, con el entorno científico activo:

```bash
python -m unittest scripts.historia.test_features
python scripts/historia/exp_historia_reciente.py \
  --data data/base_2019.parquet \
  --broken resultados_replica/01_meses_rotos.csv \
  --hyper scripts/historia/baseline07.json \
  --out exp/historia_reciente_smoke --seeds 2
```

Para las otras familias, cambiar solo el script y la carpeta de salida. Corrida completa: otra carpeta nueva y `--seeds 10`. Cada carpeta contiene hashes de datos/código/parámetros, versiones, columnas, cobertura de features nuevas, claves y predicciones de agosto, métricas y resumen del ensamble. `status.json` con complete señala finalización; no hay reanudación automática.

No se lanzaron corridas nuevas al crear esta rama. El experimento previo sin/con historia queda separado de estas familias.

Verificación: sintaxis y whitespace comprobados localmente; cinco pruebas sintéticas pasaron en el entorno de la VM (calendario con huecos, signos/ceros/nulos, persistencia, pesos y rankings con empates). No se entrenaron modelos nuevos durante esa verificación.

## Próximo experimento acordado: decaimiento ajustable

Solo si historia reciente muestra una señal favorable al completar las diez semillas (considerando diferencia media, consistencia entre semillas y ensamble), preparar un archivo independiente que seleccione alfa en una partición temporal interna al bloque marzo–junio y evalúe esa elección en agosto. No hay umbral numérico de habilitación predefinido; no presentarlo retrospectivamente como una regla formal. Si no aparece señal, conservar el negativo y priorizar las otras familias. No modificar la cola en ejecución ni elegir alfa mirando sus AUC de agosto. Definir antes de correr la grilla, las semillas de selección y la partición con separación suficiente para las etiquetas a dos meses; las ventanas internas son cortas, lo que limita esta estrategia. Reentrenar luego con marzo–junio y el alfa seleccionado. Los parámetros del 07 ya fueron elegidos usando agosto: esta separación evita usarlo para la nueva búsqueda de alfa, pero no convierte agosto en un test independiente de todo el pipeline.
