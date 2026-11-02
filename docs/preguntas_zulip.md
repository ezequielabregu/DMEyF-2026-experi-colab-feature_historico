# Preguntas Zulip

## 1. Ventana de meses

El problema: el dataset empieza en 201901, así que en los meses de entrenamiento del baseline (201903–06) la historia de más de 2 meses está vacía en parte o del todo. Por ejemplo, el lag 6 está vacío en todos los meses de entrenamiento y lleno en validación y test. Medimos la cobertura: donde el dataset tiene meses previos, entre el 90 y el 98 % de los clientes tiene historia, así que los vacíos vienen del borde del dataset, no de los clientes. En la competencia 1 nos pasó algo parecido: entrenando sin meses previos, un bloque de historia daba negativo solo por eso.

Opciones:
(a) Nuestra propuesta: los mismos meses de entrenamiento para todas las variantes, 201905–06, donde hay historia completa de hasta 4 meses. El control es el baseline (lag y delta 1–2), y las variantes agregan lags y tendencias de 3 y 4 meses. Validación 201908 y test 201910, como en la consigna. El costo es que el control entrena con 2 meses en vez de 4, así que además corremos el baseline original (201903–06) como referencia.
(b) La ventana original (201903–06), dejando que LightGBM maneje los vacíos.
(c) Otra ventana que prefieras.

¿Cuál te parece mejor? Y además: ¿aceptarías 201909 como segundo mes de prueba, junto con 201910?

---

## Pendientes

Para mandar después de la 1, para que la pregunta principal no se diluya.

### 2. Fórmula de ganancia

Para juzgar la hipótesis usamos la ganancia en 201910, cortando por cantidad de envíos (N) en la meseta de la curva. ¿La fórmula es la misma de la competencia 1 (1.072.500 por cada BAJA+2 estimulado, −27.500 por cada uno que no lo es), o cambia para este dataset?

### 3. Hiperparámetros

Proponemos una sola búsqueda con Optuna sobre el control (AUC en 201908), y reusar esos hiperparámetros en todas las variantes. Así lo único que cambia es la historia, y cuesta 7 veces menos que una búsqueda por variante. La contra es que las variantes con más columnas podrían necesitar otros valores (por ejemplo, de `feature_fraction`). ¿Te parece bien, o preferís una búsqueda por variante?

### 4. Diseño dosis-respuesta

En lugar de comparar un solo bloque de historia, proponemos medir la ganancia según cuánta historia ve el modelo (2, 3 y 4 meses) y de qué tipo: lags y deltas, tendencias (pendiente, promedio, mínimo y máximo), o las dos. Son 7 configuraciones: el control y 6 variantes. La idea es que el resultado responda cuánta historia conviene usar en la competencia 2. ¿Te parece un buen diseño, o es demasiado para el tiempo que hay?

### 5. Inflación

En 2019, un saldo de hace 4 meses no se compara directo con el de hoy en pesos. Proponemos calcular la historia de los montos sobre rankings dentro del mes, no sobre pesos nominales. ¿Te parece bien? ¿Conviene coordinar con los grupos de Inflación?

### 6. Semillas

Proponemos 10 semillas, las mismas para el control y cada variante, con un Wilcoxon pareado (p < 0,05) como regla para decidir. ¿Te alcanzan, o esperás más?

### 7. Código del baseline

¿La cátedra va a publicar código del baseline, o lo implementa cada grupo?