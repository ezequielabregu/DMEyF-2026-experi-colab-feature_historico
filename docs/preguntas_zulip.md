# Preguntas Zulip

## 1. Ventana de meses

El problema: el dataset empieza en 201901, así que en los meses de entrenamiento del baseline (201903–06) la historia de más de 2 meses está vacía en parte o del todo. Por ejemplo, el lag 6 está vacío en todos los meses de entrenamiento y lleno en validación y test. Medimos la cobertura: donde el dataset tiene meses previos, entre el 90 y el 98 % de los clientes tiene historia, así que los vacíos vienen del borde del dataset, no de los clientes. En la competencia 1 nos pasó algo parecido: entrenando sin meses previos, un bloque de historia daba negativo solo por eso.

Opciones:
(a) Nuestra propuesta: los mismos meses de entrenamiento para todas las variantes, 201905–06, donde hay historia completa de hasta 4 meses. El control es el baseline (lag y delta 1–2), y las variantes agregan lags y tendencias de 3 y 4 meses. Validación 201908 y test 201910, como en la consigna. El costo es que el control entrena con 2 meses en vez de 4, así que además corremos el baseline original (201903–06) como referencia.
(b) La ventana original (201903–06), dejando que LightGBM maneje los vacíos.
(c) Otra ventana que prefieras.

¿Cuál te parece mejor? Y además: ¿aceptarías 201909 como segundo mes de prueba, junto con 201910?