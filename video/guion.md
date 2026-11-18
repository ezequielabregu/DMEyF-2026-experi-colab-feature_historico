# Guion del video — Experimentos Colaborativos (`feature_historico`)

**Versión 2.1 (2026-11-18).** Un solo guion, sin voces asignadas. Unas 2.250 palabras habladas: **cerca de 16 minutos, por encima del límite de 10.** El usuario decide qué recortar (ver el final).

**Cambios de la versión 2** (pedido del usuario):
- Vocabulario de la cátedra, tomado de las transcripciones de clase y de la plantilla de slides:
  - las dos líneas de trabajo son **familias de experimentos**;
  - cada prueba es un **experimento**;
  - se dice "baseline" (no "B0") y "ventana de 4 meses" (no "W4");
  - se dice "walk-forward" y "ensamble";
  - se dice "optimización bayesiana".
- Se suman las figuras técnicas del informe:
  - la curva de ganancia y la banda;
  - cómo se plancha la ganancia con más meses (lags y tendencias de 3 y 4 meses, y la profundidad de la primera familia);
  - la ganancia por semilla;
  - la curva de ganancia de la estrategia final contra el baseline.

**Cómo leerlo.** Cada sección lleva el **número de slide** que aparece abajo a la derecha en pantalla (24 en total). Cada una tiene:
- **Pantalla:** qué se ve.
- **Texto:** lo que se dice, tal cual.
- **Cifras:** todas salen de `datos/` a través de `slides/figuras.py`.

Todo lo que aparece en pantalla se dice. Las cifras las genera `slides/figuras.py` a partir de los CSV de `datos/`.

---

## Portada

### Slide 1 · Portada

**Pantalla:** "Historia del cliente", las dos familias de experimentos y los integrantes del grupo.

**Texto:** ninguno; se ve mientras arranca el video.

---

## Tramo 1 — Pregunta, hipótesis y sesgos (~0:50)

### Slide 2 · 1a. La pregunta

**Pantalla:**
- "mes actual + lags 1 y 2 + deltas 1 y 2 + más historia";
- tarjetas: baseline de la consigna, hipótesis general, datos de 2019.

**Texto:**
> Nuestro experimento es de feature engineering histórico. La pregunta: si a un LightGBM que ya tiene el baseline de la consigna, es decir, las variables del mes más lags y deltas de 1 y 2 meses, le agregamos más variables históricas de cada cliente, ¿gana más dinero? Usamos solo meses de 2019.

### Slide 3 · 1b. Las dos hipótesis y sus sesgos

**Pantalla:** dos tarjetas: hipótesis 1 · familia 1 (azul) e hipótesis 2 · familia 2 (naranja).

**Texto:**
> Arrancamos con dos hipótesis, cada una con su sesgo. La hipótesis 1, la de la primera familia: las señales de abandono, como las rachas de inactividad o la caída frente al propio historial del cliente, iban a superar ampliamente a los lags. La hipótesis 2, la de la segunda familia: sumar más meses de historia iba a dar mucha más ganancia. Al final vemos qué hizo la evidencia con cada una.

---

## Tramo 2 — Diseño: el marco común (~1:20)

### Slide 4 · 2a. Cuatro reglas comunes

**Pantalla:**
- los cuatro pasos: walk-forward, ganancia, banda de envíos y semillas;
- el calendario de octubre.

**Texto:**
> Hicimos dos familias de experimentos, con el mismo marco de evaluación. Uno: walk-forward. Para evaluar un mes, el modelo entrena solo con meses que terminan dos meses antes, porque la clase se conoce dos meses después: para octubre, el último mes de entrenamiento es agosto. Dos: la ganancia de la consigna, más 1.072.500 por cada `BAJA+2` con estímulo y menos 27.500 por cualquier otro envío. Tres: la banda de envíos, que vemos en el gráfico siguiente. Cuatro: cada configuración se entrena con cinco semillas, y el ensamble promedia sus probabilidades antes de ordenar a los clientes. ¿Conviene? En una de nuestras primeras pruebas, con 10 configuraciones de 10 semillas evaluadas en septiembre y en octubre, el ensamble ganó más que el promedio de las semillas por separado en los 20 casos, 1,8 millones en promedio.

### Slide 5 · 2b. La curva de ganancia y la banda

**Pantalla:** curva de ganancia del baseline en octubre, interactiva, con la banda de 3.000 a 6.000 envíos sombreada y el máximo marcado.

**Texto:**
> Esta es la curva de ganancia del baseline en octubre. Ordenamos a los clientes por probabilidad y acumulamos la ganancia a medida que agregamos envíos. Sube rápido, se aplana cerca del máximo, de 293,4 millones, y después cae, porque cada envío extra cuesta más de lo que recupera. Como el máximo exacto depende del azar, comparamos el promedio de la curva entre 3.000 y 6.000 envíos. Así no elegimos el punto de corte que más nos favorece.


---

## Tramo 3 — Familia 1: experimentos independientes (~1:00)

### Slide 6 · 3a. Un experimento por tipo de variable

**Pantalla:**
- "baseline + un tipo de variable → comparar contra el baseline";
- grilla de tipos de variable por ventana de 3, 4 y 6 meses, con una definición debajo de cada uno;
- nota: todo sobre los 129 montos y conteos; 8 tipos × 3 ventanas + 15 = 39 experimentos.

**Texto:**
> La primera familia responde: ¿qué tipo de variable histórica suma sola? A partir del baseline, cada experimento agrega un solo tipo de variable, calculada sobre los mismos 129 montos y conteos. Son tres grupos.
>
> El primero resume una ventana de meses, contando el mes actual: el promedio; el mínimo y el máximo; el rango, que es el máximo menos el mínimo; y la tendencia, que es la pendiente de una recta ajustada a los valores de la ventana, o sea, cuánto sube o baja la variable por mes. También los cambios relativos: el mes contra el promedio de la ventana, contra el mes anterior o contra el primer mes de la ventana, divididos por ese valor de referencia. Cada uno se prueba con ventanas de 3, 4 y 6 meses.
>
> El segundo grupo es más memoria cruda: lags y deltas de 3, 4 y 5 meses atrás.
>
> El tercero son señales de actividad: la posición del cliente dentro del mes y su historia; rachas de meses en cero o con movimiento, y meses desde el último movimiento; si la variable se apagó, se prendió o viene cayendo varios meses seguidos; y si el cliente existía uno y dos meses atrás.

### Slide 7 · 3b. Un ejemplo

**Pantalla:** el saldo de un cliente en los últimos 6 meses (130, 150, 120, 110, 95, 70; ejemplo ilustrativo), interactivo. Botones de ventana: 3, 4 o 6 meses. La ventana elegida se sombrea y se dibujan el promedio (línea punteada), la recta de tendencia, el mínimo y el máximo; a la derecha, todos los valores calculados. Nota: lag 3 y delta 3.

**Texto:**
> Un ejemplo con el saldo de un cliente que viene cayendo. Con la ventana de 4 meses, el promedio es 98,8, el mínimo 70 y el máximo 120, así que el rango es 50. La tendencia, la pendiente de la recta, da −16,5 por mes. El mes actual está 29 % por debajo de su promedio, 26 % por debajo del mes anterior y 42 % por debajo del primer mes de la ventana. Con 3 meses de memoria cruda, el lag 3 es 120 y el delta 3 es −50. Con los botones se ve cómo cambia cada valor con una ventana de 3 o de 6 meses.

### Slide 8 · 3c. Mismo procedimiento para todos

**Pantalla:**
- calendario: junio entrena y julio valida; septiembre y octubre evalúan;
- contadores: 39 experimentos, optimización bayesiana, 5 semillas, 960 entrenamientos;
- nota de diseño: hasta 1.500 árboles con early stopping de 100 rondas; baseline de 634 columnas después de depurar.

**Texto:**
> Son 39 experimentos. Cada uno tuvo su propia optimización bayesiana de hiperparámetros con Optuna: entrena con junio y elige por AUC en julio. Después se evalúa en septiembre y en octubre, reentrenando para cada mes. La cantidad de árboles sale de la validación, con early stopping. Los experimentos no se acumulan: cada uno se compara solo contra el mismo baseline. En total, 960 entrenamientos.


---

## Tramo 4 — Familia 2: experimentos acumulativos (~1:10)

### Slide 9 · 4a. La escalera

**Pantalla:** la escalera, con un escalón por pieza que aparece de a uno; cada escalón lleva una línea que dice qué es.

**Texto:**
> La segunda familia responde otra pregunta: ¿cuánto dinero se gana combinando lo que suma? Partimos del mismo baseline y sumamos de a una pieza: cada una quedó solo si ganaba más. En este orden entraron:
> - la historia curada: cuatro variables que comparan a cada cliente con su propio pasado, calculadas en las 30 variables más importantes. Por ejemplo, el mes dividido por el promedio de los 3 meses anteriores, o dividido por su máximo de los últimos 4;
> - cuatro medidas más de historia, sobre esas mismas 30 variables: cuánto varía el cliente, si viene cayendo, cómo está contra toda su historia, y cómo cambió comparado con el resto de los clientes ese mes;
> - `BAJA+2` con peso triple, para que el modelo priorice a los que se van dentro de dos meses;
> - las tarjetas Visa y Master combinadas en una sola: saldos, consumos y límites sumados, y cocientes como saldo sobre límite;
> - y los cambios relativos: la diferencia con 1 y 2 meses antes, dividida por la suma de los dos valores en valor absoluto, así que queda entre −1 y 1.

### Slide 10 · 4b. Qué variables usa la estrategia final

**Pantalla:** dos gráficos de barras interactivos. A la izquierda, la parte del gain de LightGBM de cada bloque de variables: baseline 48 %, Visa y Master combinadas 15,8 %, historia curada 13,5 %, contra toda su historia 7,9 %, cambios relativos 5,5 %, inestabilidad 3,8 %, quiebre 2,9 %, contra el resto del mes 2,6 %. A la derecha, las 12 columnas que más pesan, con su descripción; gris si son del baseline y naranja si son nuevas.

**Texto:**
> ¿Qué usa el modelo final? Medimos la importancia de cada columna con el gain de LightGBM, es decir, cuánto baja la pérdida cada vez que un árbol corta por esa columna, promediado en los 25 modelos: cinco meses por cinco semillas. Las columnas del baseline explican el 48 %, y las nuevas, el 52 %. Entre las nuevas, pesan más las tarjetas combinadas, con 16 %, y la historia curada, con 13,5 %; después vienen la comparación contra toda la historia del cliente, con 8 %, y los cambios relativos, con 5,5 %. Las columnas que más pesan son el saldo de la caja de ahorro, la cantidad de movimientos de los últimos 90 días y el saldo del mes anterior. Entre las históricas, se destacan los movimientos contra su media de toda la historia, los pagos con tarjeta, los días hasta el inicio de la mora y si la tarjeta pasó de abierta a cerrada en los últimos dos meses.

### Slide 11 · 4c. Cinco meses evaluados

**Pantalla:**
- calendario de los cinco meses evaluados, con la ventana que crece;
- una sexta fila, en gris: octubre con la ventana fija de la consigna (marzo a junio);
- en la nota, resaltado: la ventana fija gana 5,8 M por mes menos que la que crece.

**Texto:**
> La evaluamos en cinco meses, de junio a octubre: para cada mes, el modelo entrena con todos los meses desde marzo hasta dos antes. ¿Por qué no usar la ventana fija de la consigna, de marzo a junio? Porque entrenar siempre con esos cuatro meses perdía 5,8 millones por mes contra la ventana que crece: lo que más importa es que los meses de entrenamiento sean recientes.

### Slide 12 · 4d. El pipeline único

**Pantalla:** diagrama del `main` con dos branches; la regla de merge.

**Texto:**
> En el camino cambiamos el método varias veces: ventanas, validación y criterios de decisión. Por eso congelamos la estrategia en un pipeline único, en el `main` del repositorio. Cada idea nueva se prueba en un branch, con un solo cambio, y entra al `main` solo si la diferencia de ganancia es positiva y al menos tres de cinco semillas están a favor.


---

## Tramo 5 — Limitaciones (~0:40)

### Slide 13 · 5. Cuatro limitaciones

**Pantalla:**
- cuatro limitaciones numeradas;
- barras de la maldición del ganador: +5,25 al elegirla · +2,14 con semillas nuevas · −0,92 en meses nuevos.

**Texto:**
> Cuatro limitaciones. Uno: los meses de 2019 ya los habíamos mirado, así que todo es exploratorio. Dos: hicimos muchas comparaciones, y la mejor de muchas sale favorecida por azar. Es la maldición del ganador, y la medimos: la mejor de sesenta combinaciones de hiperparámetros ganaba 5,25 millones al elegirla, 2,14 con semillas nuevas en los mismos meses, y perdía 0,92 en meses nuevos. Tres: en la primera familia, la búsqueda tuvo diez pruebas por experimento. Cuatro: pocos meses evaluados. El ruido de los clientes, con intervalos de unos ±10 millones, es el doble de la ventaja típica, y más semillas no lo achican. Además hay variables rotas en algunos meses de 2019, que tratamos como faltantes.


---

## Tramo 6 — Resultados de la familia 1 (~1:15)

### Slide 14 · 6a. Septiembre contra octubre

**Pantalla:** dispersión interactiva de los 39 experimentos, con las destacadas al costado. Relativo al promedio de 6 meses e historia de rankings anotados como "un solo mes muy bueno".

**Texto:**
> Resultados de la primera familia. Cada punto es un experimento: en el eje horizontal, cuánto gana sobre el baseline en septiembre; en el vertical, en octubre. 19 ganan en los dos meses y 5 pierden en los dos; las otras 15 ganan en un solo mes. Si ningún experimento sirviera, esperaríamos unos diez de cada lado. Los más consistentes:
> - la tendencia de 4 meses, con +2,2 y +4,6 millones y las cinco semillas a favor en los dos meses;
> - el máximo y el rango de 6 meses, de +2,4 a +4,4.
>
> Ojo con los que ganan un solo mes: el relativo al promedio de 6 meses y la historia de rankings tienen un mes muy bueno y otro flojo. Un buen mes no demuestra persistencia. Y todavía no están corregidos por comparaciones múltiples.

### Slide 15 · 6b. ¿Mirar más atrás suma más?

**Pantalla:**
- ganancia sobre el baseline según los meses de historia, interactiva. Hay una línea por tipo de variable, con tendencia, máximo y rango resaltados; los lags y deltas de 3 a 5 meses van en punteado;
- tarjetas: "Resumida, la historia larga suma algo" (máximo +2,1 → +3,4; rango +2,3 → +3,6; tendencia en 4 meses) y "Lags y deltas 3–5: alrededor de cero".

**Texto:**
> ¿Mirar más atrás suma más? Depende de cómo. Cada línea es un tipo de variable, y el eje horizontal es cuántos meses mira. Resumida, la historia larga suma algo: de 3 a 6 meses, el máximo pasa de +2,1 a +3,4 millones y el rango, de +2,3 a +3,6. La tendencia rinde más en 4 meses. Pero los lags y deltas de 3, 4 o 5 meses atrás, en punteado, quedan alrededor de cero: ninguno gana en los dos meses.


---

## Tramo 7 — Resultados de la familia 2 (~3:00)

### Slide 16 · 7a. ¿Cuánto vale la historia?

**Pantalla:** ganancia por semilla en septiembre y octubre, sin lags ni deltas, con lags y deltas 1–2 y con historia curada, interactiva. Debajo: +20,1 / +19,9 M (cerca de 8 %), −0,4 / +5,4 M, y 69–90 %.

**Texto:**
> Primero: ¿cuánto vale tener historia? Sin lags ni deltas, el modelo gana unos 20 millones por mes menos, cerca de 8 %. Es el efecto más grande de todo el experimento. Cada punto es una semilla. Sumar la historia curada agrega mucho menos: −0,4 en septiembre y +5,4 en octubre. Los meses 1 y 2 ya dan entre el 69 y el 90 % de lo que aporta la historia, si tomamos como total la diferencia entre no tener historia y el modelo con más historia que probamos en esa etapa.

### Slide 17 · 7b. Más meses de lags y tendencias: se plancha

**Pantalla:** ganancia media según los meses de historia (2, 3 y 4) para lags, tendencias y lags más tendencias, con IC 95 %, en septiembre y octubre. Debajo, dos cifras: +3,5 a +5,4 M (de 2 a 3 meses) y −0,2 a +1,6 M (de 3 a 4 meses), en octubre.

**Texto:**
> Comparamos lags y tendencias de 3 y 4 meses contra el baseline, que mira 2. Pasar de 2 a 3 meses sumó de 3,5 a 5,4 millones en octubre; pasar de 3 a 4, de −0,2 a +1,6. La curva se plancha.

### Slide 18 · 7c. La estrategia final, por semilla

**Pantalla:**
- número grande: +9,0 M por mes, IC 5,2 a 12,8, 5 de 5 semillas;
- puntos por semilla y mes, con la media de cada mes.

**Texto:**
> Acumulando, la estrategia final gana 9 millones por mes más que el baseline con el mismo calendario, con un intervalo de 5,2 a 12,8. En el gráfico, cada punto es una semilla: 24 de los 25 pares de mes y semilla quedan a favor, y gana en los cinco meses, de 4 a 12 millones.

### Slide 19 · 7d. Dónde está la mejora en la curva

**Pantalla:** curva de ganancia de octubre, interactiva: baseline contra estrategia final, con la banda sombreada.

**Texto:**
> En la curva de ganancia de octubre se ve dónde está la mejora: la estrategia final levanta toda la zona entre 3.000 y 6.000 envíos, y su máximo pasa de 293,4 a 305,2 millones.

### Slide 20 · 7e. ¿De dónde sale? La historia curada y una interacción

**Pantalla:**
- a la izquierda, dos tarjetas: historia curada +4,1 M; Optuna sobre la estrategia final +0,57 M (6 de 10 semillas, IC −2,6 a +3,7, entró al `main`);
- a la derecha, "Una interacción que solo se ve acumulando": barras interactivas con Visa y Master combinadas solas +0,6 · cambios relativos solos +0,6 · si sus efectos se sumaran +1,2 (barra vacía) · las dos juntas +2,2, con +1,0 en naranja que aparece solo juntas; debajo, la lectura: el modelo cruza cómo está el cliente con sus tarjetas con cuánto cambió cada monto.

**Texto:**
> ¿De dónde sale? Lo más firme es la historia curada, que sumó 4,1 millones. Y hay una interacción que solo se ve acumulando. Probamos cada pieza sola sobre la misma estrategia: las tarjetas Visa y Master combinadas sumaban 0,6 millones; los cambios relativos, otros 0,6. Si sus efectos se sumaran, juntas darían 1,2. Pero juntas dieron 2,2: un millón más, que aparece solo cuando están las dos. Nuestra lectura: las tarjetas combinadas dicen cómo está el cliente con sus tarjetas este mes, y los cambios relativos dicen cuánto cambió cada monto; con las dos, el modelo puede cruzar el estado con el cambio. Por eso, probar las piezas de a una no alcanza para ver todo lo que suman. Por último, reoptimizamos los hiperparámetros de la estrategia final con Optuna, eligiendo con junio a agosto y evaluando en septiembre y octubre: sumó 0,57 millones, con seis de diez semillas a favor. Pasó la regla y ya está en el `main`, aunque el intervalo va de −2,6 a +3,7.

### Slide 21 · 7f. Lo que no sumó

**Pantalla:** forest plot interactivo: diferencia contra su control, con IC 95 %, y el veredicto registrado de cada prueba (segundas diferencias, racha de meses en cero, selección con canaritos, segundo paquete, rango). Debajo, una línea que define cada una.

**Texto:**
> Y los resultados negativos también se reportan. Las segundas diferencias, que miden la aceleración (el mes, menos dos veces el anterior, más el de dos meses antes), no mostraron señal. La racha de meses en cero tenía que ganar en septiembre y en octubre en tres medidas: la ganancia media por semilla, la ganancia en la banda por semilla y la del ensamble; falló en las tres. La selección de variables con canaritos dio empate. Y el segundo paquete, 960 columnas más, con el puntaje de los meses anteriores, hojas de Random Forest, rankings, cruces de las tarjetas y el sueldo sin aguinaldo, restó. En todos, la diferencia es chica o negativa, y el intervalo incluye el cero.

---

## Tramo 8 — Coincidencias y diferencias (~0:40)

### Slide 22 · 8. Dos familias, las mismas conclusiones

**Pantalla:** tabla con ✓ y ≠ (Familia 1 · independientes | Familia 2 · acumulativos), y dos píldoras: "qué suma **solo**" · "cuánto suma **junto**".

**Texto:**
> Las dos familias coinciden en lo importante. Las variables históricas suman sobre los lags y deltas de 1 y 2 meses. Agregar lags más lejanos casi no suma. La tendencia de unos 4 meses aparece en las dos. Y rinde comparar al cliente con su propio pasado. Difieren en el rango: sobre el baseline suma, y sobre el `main` no pasa, porque el `main` ya tiene otras comparaciones contra el propio pasado. Se complementan: una dice qué suma solo; la otra, cuánto suma junto.

---

## Tramo 9 — Conclusiones y qué seguiríamos probando (~0:55)

### Slide 23 · 9a. Las hipótesis contra la evidencia

**Pantalla:** las dos tarjetas con sello: hipótesis 1, "A medias"; hipótesis 2, "Perforado".

**Texto:**
> ¿Qué hizo la evidencia con nuestras hipótesis? La hipótesis 1 quedó a medias: las rachas no mostraron una ganancia consistente, pero la caída frente al propio historial sí. La hipótesis 2 quedó perforada: más meses no dieron mucho más, porque los dos primeros meses ya dan entre el 69 y el 90 % de lo que aporta la historia.

### Slide 24 · 9b. Qué nos llevamos

**Pantalla:**
- "Para la competencia 2";
- "Seguiríamos probando";
- los dos repositorios.

**Texto:**
> Para la segunda competencia nos llevamos esto: pocos lags crudos y la historia larga resumida, con máximo, rango o tendencia; el cliente comparado consigo mismo; y entrenar con los meses más recientes. Y seguiríamos probando: los experimentos con señal de la primera familia, como branches del `main`, juzgados en junio a agosto, que no se usaron para elegirlos; los lags sin deltas; y sacar un bloque por vez del `main`. El código de las dos familias está en los repositorios que aparecen en pantalla.

---

**Total aproximado:** 2.250 palabras habladas, cerca de 16 minutos a un ritmo pausado. **Hay que recortar alrededor de 6 minutos.** Candidatos, de menor a mayor costo:
1. slide 19 (7d), la curva de la estrategia final (~15 s); queda para decidir más adelante;
2. la interacción de la slide 20 (7e) (~15 s);
3. la frase del ensamble en la slide 4 (2a) y la nota de early stopping en la slide 8 (3c) (~10 s);
4. slide 11 (4c), el calendario de la familia 2 (~10 s), porque el calendario del marco común ya explica el walk-forward;
5. acortar las slides 15 (6b) y 22 (8), que repiten la idea de los lags lejanos (~20 s).
