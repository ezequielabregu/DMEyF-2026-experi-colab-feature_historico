# Guion corto del video — Experimentos Colaborativos (`feature_historico`)

**Versión corta (2026-11-18)** de `guion.md`. Mismas 24 slides, mismo orden y mismas cifras. **1.381 palabras habladas, unos 9,6 minutos** al ritmo de 2,4 palabras por segundo; el guion completo tiene unas 2.250. Un solo guion, sin voces asignadas.

**Cómo se recortó:**
1. **Estilo ASD-STE100, adaptado al castellano:**
   - oraciones cortas, de 20 palabras como máximo;
   - una idea por oración, en voz activa;
   - siempre el mismo término para la misma cosa;
   - nada de "o sea", "es decir" ni cadenas de subordinadas.
   Las preguntas que abren cada slide y los remates cortos se mantienen.
2. **Sin repeticiones entre slides:**
   - "los lags lejanos no suman" se dice en la slide 15 y se retoma en la 17;
   - la historia curada se define en la slide 9;
   - el 69–90 % se dice en la slide 16.
3. **Voz contra pantalla:** la voz dice la idea y el número clave; la pantalla guarda el detalle (fórmulas, intervalos, definiciones). Cuando un detalle queda solo en pantalla, la voz lo nombra ("en pantalla", "la grilla", "las barras"), así que nada aparece sin que se lo mencione.

**Cómo leerlo:**
- cada sección lleva el número de slide que aparece abajo a la derecha;
- **Pantalla** es igual que en `guion.md`; acá solo se dice qué se nombra;
- el número entre paréntesis es la cantidad de palabras.

---

## Slide 1 · Portada

Sin texto. Se ve mientras arranca el video.

---

## Tramo 1 — Pregunta e hipótesis

### Slide 2 · 1a. La pregunta (45)

> Nuestro experimento es de feature engineering histórico. El baseline de la consigna es un LightGBM. Usa las variables del mes y sus lags y deltas de 1 y 2 meses. La pregunta: ¿más historia de cada cliente gana más dinero? Usamos solo meses de 2019.

### Slide 3 · 1b. Las dos hipótesis y sus sesgos (43)

> Arrancamos con dos hipótesis, cada una con su sesgo. Hipótesis 1, de la primera familia: las señales de abandono, como las rachas de inactividad, superan ampliamente a los lags. Hipótesis 2, de la segunda familia: más meses de historia dan mucha más ganancia.

---

## Tramo 2 — El marco común

### Slide 4 · 2a. Cuatro reglas comunes (75)

> Las dos familias comparten el mismo marco de evaluación. Uno: walk-forward. Para evaluar un mes, el modelo entrena hasta dos meses antes, porque la clase se conoce dos meses después. Dos: la ganancia de la consigna, con los montos en pantalla. Tres: la banda de envíos, que muestra el próximo gráfico. Cuatro: cinco semillas por configuración. El ensamble promedia sus probabilidades. En una prueba con 20 casos, le ganó siempre a las semillas por separado.

### Slide 5 · 2b. La curva de ganancia y la banda (53)

> Esta es la curva de ganancia del baseline en octubre. Ordenamos a los clientes por probabilidad y sumamos la ganancia de cada envío. La curva sube, se aplana cerca del máximo y después cae. El máximo exacto depende del azar. Por eso comparamos el promedio de la curva entre 3.000 y 6.000 envíos.

---

## Tramo 3 — Familia 1: experimentos independientes

### Slide 6 · 3a. Un experimento por tipo de variable (114)

> La primera familia pregunta qué tipo de variable histórica suma sola. Cada experimento agrega un solo tipo al baseline, sobre los mismos 129 montos y conteos. Hay tres grupos. El primero resume una ventana de 3, 4 o 6 meses: promedio, mínimo, máximo, rango y tendencia. La tendencia es la pendiente de la recta: cuánto sube o baja la variable por mes. Este grupo también compara el mes con el promedio, con el mes anterior y con el primer mes de la ventana. El segundo grupo agrega lags y deltas de 3 a 5 meses. El tercero mide actividad: ranking dentro del mes, rachas en cero y apagados. Cada definición está en la grilla.

### Slide 7 · 3b. Un ejemplo (54)

> Un ejemplo: el saldo de un cliente que viene cayendo. Con una ventana de 4 meses, el rango es 50 y la tendencia es −16,5 por mes. El mes actual está 29 % debajo de su promedio. Los demás valores están en pantalla. Los botones cambian la ventana a 3 o a 6 meses.

### Slide 8 · 3c. Mismo procedimiento para todos (42)

> Son 39 experimentos. Cada uno tuvo su propia optimización bayesiana con Optuna: entrena con junio y elige por AUC de julio. Después se evalúa en septiembre y en octubre. Cada experimento se compara solo contra el mismo baseline. En total, 960 entrenamientos.

---

## Tramo 4 — Familia 2: experimentos acumulativos

### Slide 9 · 4a. La escalera (101)

> La segunda familia pregunta cuánto dinero se gana combinando lo que suma. Partimos del mismo baseline y sumamos una pieza por vez. Cada pieza quedó solo si ganaba más. Entraron cinco, en este orden. Primero, la historia curada: cuatro variables que comparan al cliente con su propio pasado, en las 30 variables más importantes. Segundo, cuatro medidas más sobre esas variables: variación, caídas, toda su historia y el resto del mes. Tercero, más peso a `BAJA+2`. Cuarto, Visa y Master combinadas en una sola tarjeta. Quinto, los cambios relativos contra 1 y 2 meses. Cada escalón tiene su definición en pantalla.

### Slide 10 · 4b. Qué variables usa la estrategia final (89)

> ¿Qué usa el modelo final? Medimos la importancia con el gain de LightGBM: cuánto baja la pérdida en cada corte por esa columna. Las columnas del baseline explican el 48 %. Las nuevas explican el 52 %. Entre los bloques nuevos, pesan más las tarjetas combinadas y la historia curada. Entre las columnas, lideran el saldo de la caja de ahorro y los movimientos de los últimos 90 días. Entre las históricas, los movimientos contra su media de toda la historia y los días al inicio de la mora.

### Slide 11 · 4c. Cinco meses evaluados (51)

> Evaluamos de junio a octubre. Para cada mes, el modelo entrena con todos los meses desde marzo hasta dos antes. En gris, la ventana fija de la consigna, de marzo a junio. Esa ventana gana 5,8 millones por mes menos. Lo que importa es que los meses de entrenamiento sean recientes.

### Slide 12 · 4d. El pipeline único (41)

> El método cambió varias veces en el camino. Por eso congelamos la estrategia en un pipeline único, en el `main`. Cada idea nueva va a un branch con un solo cambio. Entra al `main` solo si cumple la regla en pantalla.

---

## Tramo 5 — Limitaciones

### Slide 13 · 5. Cuatro limitaciones (86)

> Cuatro limitaciones. Uno: ya habíamos mirado los meses de 2019, así que todo es exploratorio. Dos: con muchas comparaciones, la mejor sale favorecida por azar. Es la maldición del ganador. La mejor de 60 combinaciones de hiperparámetros ganaba 5,25 millones al elegirla y perdía 0,92 en meses nuevos. Las barras muestran cada paso. Tres: la primera familia tuvo diez pruebas de Optuna por experimento. Cuatro: pocos meses evaluados. El ruido de los clientes es el doble de la ventaja típica, y más semillas no lo achican.

---

## Tramo 6 — Resultados de la familia 1

### Slide 14 · 6a. Septiembre contra octubre (82)

> Resultados de la primera familia. Cada punto es un experimento: septiembre en el eje horizontal y octubre en el vertical. 19 ganan en los dos meses y 5 pierden en los dos. Por azar esperaríamos unos 10 de cada lado. La más consistente es la tendencia de 4 meses: +2,2 y +4,6 millones, con todas las semillas a favor. Le siguen el máximo y el rango de 6 meses. Ojo: un solo mes bueno no alcanza, como muestran los dos experimentos anotados.

### Slide 15 · 6b. ¿Mirar más atrás suma más? (46)

> ¿Mirar más atrás suma más? Depende de cómo. Resumida, la historia larga suma algo: el máximo y el rango mejoran de 3 a 6 meses. La tendencia rinde más en 4. En cambio, los lags y deltas de 3 a 5 meses quedan cerca de cero.

---

## Tramo 7 — Resultados de la familia 2

### Slide 16 · 7a. ¿Cuánto vale la historia? (55)

> ¿Cuánto vale la historia? Sin lags ni deltas, el modelo gana 20 millones por mes menos, cerca de 8 %. Es el efecto más grande del experimento. Cada punto es una semilla. La historia curada agrega mucho menos. Los meses 1 y 2 ya dan entre el 69 y el 90 % de ese valor.

### Slide 17 · 7b. Más meses de lags y tendencias: se plancha (35)

> Con lags y tendencias pasa lo mismo. Pasar de 2 a 3 meses suma entre 3,5 y 5,4 millones en octubre. Pasar de 3 a 4 suma entre −0,2 y +1,6. La curva se plancha.

### Slide 18 · 7c. La estrategia final, por semilla (39)

> La estrategia final gana 9 millones por mes más que el baseline, con el mismo calendario. El intervalo va de 5,2 a 12,8. Cada punto es una semilla: 24 de 25 quedan a favor. Gana en los cinco meses.

### Slide 19 · 7d. Dónde está la mejora en la curva (18)

> En la curva de octubre se ve la mejora: la estrategia final levanta toda la banda de envíos.

### Slide 20 · 7e. ¿De dónde sale? La historia curada y una interacción (98)

> ¿De dónde sale? Lo más firme es la historia curada: 4,1 millones. Además hay una interacción. Probamos cada pieza sola sobre la misma estrategia. Visa y Master combinadas sumaban 0,6 millones. Los cambios relativos sumaban otros 0,6. Si sus efectos se sumaran, juntas darían 1,2. Juntas dieron 2,2: un millón más, que aparece solo con las dos. Nuestra lectura: las tarjetas dicen cómo está el cliente, y los cambios relativos dicen cuánto cambió. Con las dos, el modelo cruza el estado con el cambio. Por último, reoptimizar los hiperparámetros con Optuna sumó 0,57 millones y entró al `main`.

### Slide 21 · 7f. Lo que no sumó (43)

> Los resultados negativos también se reportan. Las segundas diferencias no mostraron señal. La racha de meses en cero falló. La selección con canaritos empató. El segundo paquete, de 960 columnas, restó. Cada definición está en pantalla. En todos, el intervalo incluye el cero.

---

## Tramo 8 — Coincidencias y diferencias

### Slide 22 · 8. Dos familias, las mismas conclusiones (59)

> Las dos familias coinciden. La historia suma sobre los lags y deltas de 1 y 2 meses. La tendencia de unos 4 meses aparece en las dos. Comparar al cliente con su propio pasado rinde. Difieren en el rango: suma sobre el baseline, pero no sobre el `main`. Una familia mide qué suma solo; la otra, cuánto suma junto.

---

## Tramo 9 — Conclusiones

### Slide 23 · 9a. Las hipótesis contra la evidencia (45)

> ¿Qué hizo la evidencia con las hipótesis? La hipótesis 1 quedó a medias: las rachas no suman de forma consistente, pero la caída frente al propio historial sí. La hipótesis 2 quedó perforada: más meses no dieron mucha más ganancia. La tarjeta muestra por qué.

### Slide 24 · 9b. Qué nos llevamos (67)

> Para la segunda competencia nos llevamos tres ideas. Usar pocos lags crudos y resumir la historia larga. Comparar al cliente consigo mismo. Entrenar con los meses más recientes. Seguiríamos probando tres cosas. Primero, los experimentos con señal de la primera familia, como branches del `main`. Segundo, los lags sin deltas. Tercero, sacar un bloque por vez del `main`. El código está en los dos repositorios en pantalla.
