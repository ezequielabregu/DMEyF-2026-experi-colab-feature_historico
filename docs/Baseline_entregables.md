Notas
El baseline a continuación es una referencia, pero no único. Cada experimento deberá adaptarlo a las necesidades de sus experimentos.

Esta lineado a la segunda entrega, es bastante simple, para que los experimentos muestren una clara mejora o descarten la mejora de plano. La intensidad baja del baseline busca que se puedan enfocar:

En la calidad del experimento
En la calidad del entregable
Poner foco rapidamente en la siguiente entrega
Baseline
Al igual que el entrenamiento para la segundo entrega, se usarán solo los meses de 2019.

Esto significa que el mes 201911 solo tiene BAJA+1 y 201912 no puede tener clases.
Estos dos meses serán parte del dashboard, por los que no se los puede usar. Solo tendrán datos con clase hasta 201910.
Modelo:
features: lag y delta 2
Optimización del LGBM (la ventana de búsqueda la deben setear ustedes): num_leaves,learning_rate,min_data_in_leaf,feature_fraction, bagging_fraction. Fijen bagging_freq en un entero mayor igual a 1
Meses de entrenamiento: 201903, 201904, 201905, 201906 full sin sampling
En entrenamiento B+1, B+2 combinadas.
Mes de validación: 201908
Mes de test: 201910
métrica auc
Cuando hagan la optimización, entrenan con los meses de entrenamiento, se calcula sobre validación su auc y eso es lo que ordena la salida de la optimización. La comparación con sus experimentos es usando 201910 (que no debe ser usado para más que eso)

Recuerde Es una referencia. Los distintos experimentos van a tener que ver si necesita una adaptación del baseline para que tengan un poco más de sentido. Lo ven con sus tutores

Entrega
Los experimentos se entregan junto a un video grupal. Directo, clarificador y no aburrido. No se cargarán los slides, pero la estructura de los mismos debe guiar:

Hipotesis: Que se va experimentar y que se espera
Diseño experimental: como fue el método de experimentación
Limitaciones de lo que se probo
Resultados
Conclusiones + que seguirían experimentando
La biblio, por zulip cuando comparten video