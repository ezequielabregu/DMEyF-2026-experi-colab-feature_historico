# Guion del video — Experimentos Colaborativos (`feature_historico`)

**Versión 2.1 (2026-11-18).** Un solo guion, sin voces asignadas. Unas 1.530 palabras: **cerca de 11 minutos, por encima del límite de 10.** El usuario decide qué recortar (ver el final).

**Cambios de la versión 2** (pedido del usuario):
- Vocabulario de la cátedra, tomado de las transcripciones de clase y de la plantilla de slides:
  - las dos líneas de trabajo son **familias de experimentos**;
  - cada prueba es un **experimento**;
  - se dice "baseline" (no "B0") y "ventana de 4 meses" (no "W4");
  - se dice "walk-forward" y "ensamble";
  - se dice "optimización bayesiana".
- Se suman las figuras técnicas del informe:
  - la curva de ganancia y la banda;
  - cómo se plancha la ganancia con más meses (la prueba pre-registrada y la profundidad de la primera familia);
  - la ganancia por semilla;
  - la curva de ganancia de la estrategia final contra el baseline.

**Cómo leerlo.** Cada tramo tiene:
- **Pantalla:** qué se ve.
- **Texto:** lo que se dice, tal cual.
- **Cifras:** todas salen de `datos/` a través de `slides/figuras.py`.

Todo lo que aparece en pantalla se dice. Las cifras las genera `slides/figuras.py` a partir de los CSV de `datos/`.

---

## Tramo 1 — Pregunta, hipótesis y sesgos (~0:50)

### 1a. La pregunta

**Pantalla:**
- "mes actual + lags 1 y 2 + deltas 1 y 2 + más historia";
- tarjetas: baseline de la consigna, hipótesis, datos de 2019.

**Texto:**
> Nuestro experimento es de feature engineering histórico. La pregunta: si a un LightGBM que ya tiene el baseline de la consigna, es decir, las variables del mes más lags y deltas de 1 y 2 meses, le agregamos más variables históricas de cada cliente, ¿gana más dinero? Usamos solo meses de 2019.

### 1b. Los sesgos

**Pantalla:** las dos tarjetas de sesgo.

**Texto:**
> Arrancamos con dos sesgos. Ezequiel y Tomás creían que sumar más meses de historia iba a dar mucha más ganancia. Clara creía que las señales de abandono, como las rachas de inactividad o la caída frente al propio historial del cliente, iban a superar ampliamente a los lags. Al final vemos qué hizo la evidencia con cada uno.

---

## Tramo 2 — Diseño: el marco común (~1:20)

### 2a. Cuatro reglas comunes

**Pantalla:**
- los cuatro pasos: walk-forward, ganancia, banda de envíos y semillas;
- el calendario de octubre.

**Texto:**
> Hicimos dos familias de experimentos, con el mismo marco de evaluación. Uno: walk-forward. Para evaluar un mes, el modelo entrena solo con meses que terminan dos meses antes, porque la clase se conoce dos meses después: para octubre, el último mes de entrenamiento es agosto. Dos: la ganancia de la consigna, más 1.072.500 por cada `BAJA+2` con estímulo y menos 27.500 por cualquier otro envío. Tres: la banda de envíos, que vemos en el gráfico siguiente. Cuatro: cinco semillas por configuración, y un ensamble que promedia sus probabilidades. El ensamble le gana a la media de las semillas en los 20 casos que medimos, por 1,8 millones.

### 2b. La curva de ganancia y la banda

**Pantalla:** curva de ganancia del baseline en octubre, interactiva, con la banda de 3.000 a 6.000 envíos sombreada y el máximo marcado.

**Texto:**
> Esta es la curva de ganancia del baseline en octubre. Ordenamos a los clientes por probabilidad y acumulamos la ganancia a medida que agregamos envíos. Sube rápido, se aplana cerca del máximo, de 293,4 millones, y después cae, porque cada envío extra cuesta más de lo que recupera. Como el máximo exacto depende del azar, comparamos el promedio de la curva entre 3.000 y 6.000 envíos. Así no elegimos el punto de corte que más nos favorece.


---

## Tramo 3 — Familia 1: experimentos independientes (~1:00)

### 3a. Un experimento por tipo de variable

**Pantalla:**
- "baseline + un tipo de variable → comparar contra el baseline";
- grilla de tipos de variable por ventana de 3, 4 y 6 meses.

**Texto:**
> La primera familia responde: ¿qué tipo de variable histórica suma sola? A partir del baseline, cada experimento agrega un solo tipo de variable: promedio, mínimo, máximo, rango, tendencia, cambios relativos, más lags, más deltas, rankings o rachas. Los que usan una ventana se prueban con 3, 4 y 6 meses, contando el mes actual.

### 3b. Mismo procedimiento para todos

**Pantalla:**
- calendario: junio entrena y julio valida; septiembre y octubre evalúan;
- contadores: 39 experimentos, optimización bayesiana, 5 semillas, 960 entrenamientos;
- nota de diseño: hasta 1.500 árboles con early stopping de 100 rondas; baseline de 634 columnas después de depurar.

**Texto:**
> Son 39 experimentos. Cada uno tuvo su propia optimización bayesiana de hiperparámetros con Optuna: entrena con junio y elige por AUC en julio. Después se evalúa en septiembre y en octubre, reentrenando para cada mes. La cantidad de árboles sale de la validación, con early stopping. Los experimentos no se acumulan: cada uno se compara solo contra el mismo baseline. En total, 960 entrenamientos.


---

## Tramo 4 — Familia 2: experimentos acumulativos (~1:10)

### 4a. La escalera

**Pantalla:** la escalera, con un escalón por pieza que aparece de a uno.

**Texto:**
> La segunda familia responde otra pregunta: ¿cuánto dinero se gana combinando lo que suma? Partimos del mismo baseline y sumamos de a una pieza: cada una quedó solo si ganaba más. En este orden entraron:
> - la historia curada, que son cuatro variables que comparan a cada cliente con su propio pasado, en las 30 variables más importantes;
> - cuatro medidas más de historia;
> - `BAJA+2` con peso triple;
> - las tarjetas Visa y Master combinadas;
> - y los cambios relativos.

### 4b. Cinco meses evaluados

**Pantalla:** calendario de los cinco meses evaluados, con la ventana que crece.

**Texto:**
> La evaluamos en cinco meses, de junio a octubre: para cada mes, el modelo entrena con todos los meses desde marzo hasta dos antes.

### 4c. El pipeline único

**Pantalla:** diagrama del `main` con dos branches; la regla de merge.

**Texto:**
> En el camino cambiamos el método varias veces: ventanas, validación y criterios de decisión. Por eso congelamos la estrategia en un pipeline único, en el `main` del repositorio. Cada idea nueva se prueba en un branch, con un solo cambio, y entra al `main` solo si la diferencia de ganancia es positiva y al menos tres de cinco semillas están a favor.


---

## Tramo 5 — Limitaciones (~0:40)

**Pantalla:**
- cuatro limitaciones numeradas;
- barras de la maldición del ganador: +5,25 al elegirla · +2,14 con semillas nuevas · −0,92 en meses nuevos.

**Texto:**
> Cuatro limitaciones. Uno: los meses de 2019 ya los habíamos mirado, así que todo es exploratorio. Dos: hicimos muchas comparaciones, y la mejor de muchas sale favorecida por azar. Es la maldición del ganador, y la medimos: la mejor de sesenta combinaciones de hiperparámetros ganaba 5,25 millones al elegirla, 2,14 con semillas nuevas en los mismos meses, y perdía 0,92 en meses nuevos. Tres: en la primera familia, la búsqueda tuvo diez pruebas por experimento. Cuatro: pocos meses evaluados. El ruido de los clientes, con intervalos de unos ±10 millones, es el doble de la ventaja típica, y más semillas no lo achican. Además hay variables rotas en algunos meses de 2019, que tratamos como faltantes.


---

## Tramo 6 — Resultados de la familia 1 (~1:15)

### 6a. Septiembre contra octubre

**Pantalla:** dispersión interactiva de los 39 experimentos, con las destacadas al costado. Relativo al promedio de 6 meses e historia de rankings anotados como "un solo mes muy bueno".

**Texto:**
> Resultados de la primera familia. Cada punto es un experimento: en el eje horizontal, cuánto gana sobre el baseline en septiembre; en el vertical, en octubre. 19 ganan en los dos meses y 5 pierden en los dos; las otras 15 ganan en un solo mes. Si ningún experimento sirviera, esperaríamos unos diez de cada lado. Los más consistentes:
> - la tendencia de 4 meses, con +2,2 y +4,6 millones y las cinco semillas a favor en los dos meses;
> - el máximo y el rango de 6 meses, de +2,4 a +4,4.
>
> Ojo con los que ganan un solo mes: el relativo al promedio de 6 meses y la historia de rankings tienen un mes muy bueno y otro flojo. Un buen mes no demuestra persistencia. Y todavía no están corregidos por comparaciones múltiples.

### 6b. ¿Mirar más atrás suma más?

**Pantalla:**
- ganancia sobre el baseline según los meses de historia, interactiva. Hay una línea por tipo de variable, con tendencia, máximo y rango resaltados; los lags y deltas de 3 a 5 meses van en punteado;
- tarjetas: "Resumida, la historia larga suma algo" (máximo +2,1 → +3,4; rango +2,3 → +3,6; tendencia en 4 meses) y "Lags y deltas 3–5: alrededor de cero".

**Texto:**
> ¿Mirar más atrás suma más? Depende de cómo. Cada línea es un tipo de variable, y el eje horizontal es cuántos meses mira. Resumida, la historia larga suma algo: de 3 a 6 meses, el máximo pasa de +2,1 a +3,4 millones y el rango, de +2,3 a +3,6. La tendencia rinde más en 4 meses. Pero los lags y deltas de 3, 4 o 5 meses atrás, en punteado, quedan alrededor de cero: ninguno gana en los dos meses.


---

## Tramo 7 — Resultados de la familia 2 (~3:00)

### 7a0. ¿Cuánto vale la historia?

**Pantalla:** ganancia por semilla en septiembre y octubre, sin lags ni deltas, con lags y deltas 1–2 y con historia curada, interactiva. Debajo: +20,1 / +19,9 M (cerca de 8 %), −0,4 / +5,4 M, y 69–90 %.

**Texto:**
> Primero: ¿cuánto vale tener historia? Sin lags ni deltas, el modelo gana unos 20 millones por mes menos, cerca de 8 %. Es el efecto más grande de todo el experimento. Cada punto es una semilla. Sumar la historia curada agrega mucho menos: −0,4 en septiembre y +5,4 en octubre. Los meses 1 y 2 ya dan entre el 69 y el 90 % de lo que aporta la historia.

### 7a. La prueba pre-registrada

**Pantalla:** ganancia media según los meses de historia (2, 3 y 4) para lags, tendencias y lags más tendencias, con IC 95 %, en septiembre y octubre.

**Texto:**
> La segunda familia empezó con una prueba pre-registrada: lags y tendencias de 3 y 4 meses contra el baseline, con 10 semillas, test de Wilcoxon y corrección de Holm. Pasar de 2 a 3 meses sumó de 3,5 a 5,4 millones en octubre; pasar de 3 a 4, de −0,2 a +1,6. La curva se plancha. Ninguna variante pasó la regla con la corrección de Holm.

### 7b. La estrategia final, por semilla

**Pantalla:**
- número grande: +9,0 M por mes, IC 5,2 a 12,8, 5 de 5 semillas, y +12,6 contra la ventana de la consigna;
- puntos por semilla y mes, con la media de cada mes.

**Texto:**
> Acumulando, la estrategia final gana 9 millones por mes más que el baseline con el mismo calendario, con un intervalo de 5,2 a 12,8. En el gráfico, cada punto es una semilla: 24 de los 25 pares de mes y semilla quedan a favor, y gana en los cinco meses, de 4 a 12 millones. Contra el baseline con la ventana de la consigna, la diferencia es de 12,6.

### 7c. Dónde está la mejora en la curva

**Pantalla:** curva de ganancia de octubre, interactiva: baseline contra estrategia final, con la banda sombreada.

**Texto:**
> En la curva de ganancia de octubre se ve dónde está la mejora: la estrategia final levanta toda la zona entre 3.000 y 6.000 envíos, y su máximo pasa de 293,4 a 305,2 millones.

### 7d. ¿De dónde sale?

**Pantalla:** historia curada +4,1 · ventana de la consigna −5,8 · interacción 0,6 + 0,6 → 2,2.

**Texto:**
> ¿De dónde sale? Lo más firme: la historia curada, que sumó 4,1 millones, y entrenar con los meses recientes, porque la ventana vieja de la consigna perdía 5,8. Y una interacción que solo se ve acumulando: las tarjetas combinadas sumaban 0,6 solas, los cambios relativos 0,6 solos, y juntos, 2,2.

### 7e. Los branches

**Pantalla:** diagrama de git con el rango (NO PASA) y Optuna (entró al `main`).

**Texto:**
> Sobre el `main` ya corrimos dos branches. El rango de 3 meses dio −0,23 y no pasa. Reoptimizar los hiperparámetros con Optuna dio +0,57, con seis de diez semillas a favor: pasa y ya entró al `main`, aunque con un intervalo de −2,6 a +3,7.


---

### 7f. Lo que no sumó

**Pantalla:** forest plot interactivo: diferencia contra su control, con IC 95 %, y el veredicto registrado de cada prueba (segundas diferencias, racha de meses en cero, selección con canaritos, segundo paquete, rango).

**Texto:**
> Y los resultados negativos también se reportan. Las segundas diferencias no mostraron señal. La racha de meses en cero falló en las tres condiciones. La selección de variables con canaritos dio empate, y el segundo paquete, de 960 columnas más, restó. En todos, la diferencia es chica o negativa, y el intervalo incluye el cero.

---

## Tramo 8 — Coincidencias y diferencias (~0:40)

**Pantalla:** tabla con ✓ y ≠ (Familia 1 · independientes | Familia 2 · acumulativos), y dos píldoras: "qué suma **solo**" · "cuánto suma **junto**".

**Texto:**
> Las dos familias coinciden en lo importante. Las variables históricas suman sobre los lags y deltas de 1 y 2 meses. Agregar lags más lejanos casi no suma. La tendencia de unos 4 meses aparece en las dos. Y rinde comparar al cliente con su propio pasado. Difieren en el rango: sobre el baseline suma, y sobre el `main` no pasa, porque el `main` ya tiene otras comparaciones contra el propio pasado. Se complementan: una dice qué suma solo; la otra, cuánto suma junto.

---

## Tramo 9 — Conclusiones y qué seguiríamos probando (~0:55)

### 9a. Los sesgos contra la evidencia

**Pantalla:** las tarjetas de sesgo con sello ("Perforado", "A medias").

**Texto:**
> ¿Qué hizo la evidencia con nuestros sesgos? Más meses no dieron mucho más: los dos primeros meses ya dan entre el 69 y el 90 % de lo que aporta la historia. El de Clara quedó a medias: las rachas no mostraron una ganancia consistente, pero la caída frente al propio historial sí.

### 9b. Qué nos llevamos

**Pantalla:**
- "Para la competencia 2";
- "Seguiríamos probando";
- los dos repositorios.

**Texto:**
> Para la segunda competencia nos llevamos esto: pocos lags crudos y la historia larga resumida, con máximo, rango o tendencia; el cliente comparado consigo mismo; y entrenar con los meses más recientes. Y seguiríamos probando: los experimentos con señal de la primera familia, como branches del `main`, juzgados en junio a agosto, que no se usaron para elegirlos; los lags sin deltas; y sacar un bloque por vez del `main`. El código de las dos familias está en los repositorios que aparecen en pantalla.

---

**Total aproximado:** 1.530 palabras, cerca de 11 minutos a un ritmo pausado. **Hay que recortar alrededor de un minuto.** Candidatos, de menor a mayor costo:
1. 7c, la curva de la estrategia final (~15 s); queda para decidir más adelante;
2. la interacción de 7d (~15 s);
3. la frase del ensamble en 2a y la nota de early stopping en 3b (~10 s);
4. 4b, el calendario de la familia 2 (~10 s), porque el calendario del marco común ya explica el walk-forward;
5. acortar 6b y 8, que repiten la idea de los lags lejanos (~20 s).
