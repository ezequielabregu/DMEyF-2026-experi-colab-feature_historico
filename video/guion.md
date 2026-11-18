# Guion del video — Experimentos Colaborativos (`feature_historico`)

**Versión 1 (2026-11-18).** Un solo guion, sin voces asignadas. Las slides están en `slides/video_experimentos.qmd`, una o más por tramo. Duración objetivo: unos 8 minutos.

**Cómo leerlo.** Cada tramo tiene:
- **Pantalla:** qué se ve. Es la base de los slides; los recursos visuales se diseñan en el `.qmd`.
- **Texto:** lo que se dice, tal cual.
- **Cifras:** todas salen de `datos/` a través de `slides/figuras.py`.

Todo lo que aparece en pantalla se dice en el texto.

---

## Tramo 1 — Pregunta, hipótesis y sesgos (~0:50)

**Pantalla:**
- Título: "¿Qué historia del cliente hace ganar más dinero?"
- Recuadro del baseline: **mes actual + lags 1 y 2 + deltas 1 y 2** · LightGBM · solo 2019.
- Hipótesis: "Agregar más historia de cada cliente gana más que el baseline".
- Dos tarjetas de sesgo:
  - "Ezequiel y Tomás: más meses → mucha más ganancia";
  - "Clara: las señales de abandono superan ampliamente a los lags crudos".

**Texto:**
> Nuestro tema es feature engineering histórico. La pregunta es simple: si a un LightGBM que ya conoce el mes actual y los dos meses anteriores, es decir, el baseline de la consigna, con lags y deltas de 1 y 2 meses, le agregamos más historia de cada cliente, ¿gana más dinero? Trabajamos solo con meses de 2019, como pide la consigna.
>
> Arrancamos con dos sesgos. El de Ezequiel y Tomás: que sumar más meses de historia iba a dar un margen de ganancia mucho mayor. El de Clara: que las señales de abandono, como las rachas de inactividad o la caída frente al propio historial del cliente, iban a superar ampliamente a los lags crudos. Al final vemos qué hizo la evidencia con cada uno.

*(~120 palabras)*

---

## Tramo 2 — Diseño: la vara común (~0:45)

**Pantalla:** flowchart horizontal de cuatro pasos:
1. **Banco temporal:** "entrenar hasta t − 2 → evaluar t";
2. **Ganancia:** "+1.072.500 por `BAJA+2` contactado · −27.500 por otro contacto";
3. **Banda:** "promedio entre 3.000 y 6.000 envíos";
4. **Semillas:** "5 semillas → ensemble".

Debajo, un mini calendario de 2019 que ilustra t − 2 para octubre.

**Texto:**
> Armamos dos pipelines que comparten la misma vara. Primero, el banco temporal: para evaluar un mes, el modelo entrena solo con meses que terminan dos meses antes, porque la clase de un mes se conoce dos meses después. Para octubre, por ejemplo, el último mes de entrenamiento es agosto. Así se trabajaría en producción.
>
> Segundo, la ganancia de la consigna: más 1.072.500 por cada `BAJA+2` contactado y menos 27.500 por cualquier otro contacto. No la medimos en un solo punto de corte, sino como el promedio entre 3.000 y 6.000 envíos. Así no elegimos después el corte que más nos favorece. Tercero, cada configuración se entrena con cinco semillas, y promediamos sus predicciones en un ensemble.

*(~130 palabras)*

---

## Tramo 3 — Diseño: pipeline de recetas (~1:00)

**Pantalla:**
- Diagrama: B0 en el centro, con 39 flechas, cada una "B0 + 1 receta", y cada flecha con su propio ícono de Optuna.
- Grilla de las recetas (filas) por profundidad W3 · W4 · W6 (columnas): promedio, mínimo, máximo, rango, tendencia, cambio relativo (al promedio, al mes anterior, al primer mes), lags 3–5, deltas 3–5, rankings, rachas y recencia, apagado y encendido, disponibilidad.
- Línea de tiempo:
  - "junio → julio: elegir hiperparámetros (AUC)";
  - "junio–julio → septiembre";
  - "junio–agosto → octubre".
- Contador: **39 recetas · 960 entrenamientos**.

**Texto:**
> El primer pipeline responde: ¿qué tipo de historia suma sola? Al baseline lo llamamos B0, y le agregamos una sola receta por vez: promedio, mínimo, máximo, rango, tendencia, cambios relativos, más lags, más deltas, rankings, rachas. Las recetas de ventana se prueban con 3, 4 y 6 observaciones, contando el mes actual: W4, por ejemplo, es el mes y los tres anteriores.
>
> Son 39 recetas. Cada una tuvo su propia búsqueda de hiperparámetros con Optuna: entrenando con junio y eligiendo por AUC en julio. Después se evaluó en septiembre y en octubre, reentrenando para cada mes. Las recetas no se acumulan: cada una se compara sola contra el mismo B0, con el mismo procedimiento. En total, 960 entrenamientos.

*(~125 palabras)*

---

## Tramo 4 — Diseño: pipeline acumulativo (~1:10)

**Pantalla:**
- Escalera de izquierda a derecha, un escalón por pieza:
  - baseline;
  - \+ historia curada (el cliente contra su propio pasado);
  - \+ cuatro medidas más de historia;
  - `BAJA+2` con peso triple;
  - \+ tarjetas Visa y Master combinadas;
  - \+ cambios relativos;
  - estrategia final.
- Calendario de 2019: una fila por mes evaluado (junio a octubre), con el entrenamiento desde marzo hasta t − 2.
- Diagrama de git: el `main` como línea principal; dos branches salen y vuelven solo si cumplen la regla: **d > 0 y al menos 3 de 5 semillas a favor**.

**Texto:**
> El segundo pipeline responde otra pregunta: ¿cuánto dinero se gana combinando lo que suma? Partimos del mismo baseline y sumamos de a una pieza: cada idea se probó sobre lo que ya teníamos, y quedó solo si ganaba más. En este orden entraron: la historia curada, que compara a cada cliente con su propio pasado; cuatro medidas más de historia; la clase `BAJA+2` con peso triple; las tarjetas Visa y Master combinadas; y los cambios relativos. Lo evaluamos en cinco meses, de junio a octubre: para cada mes, el modelo entrena con todos los meses desde marzo hasta dos antes.
>
> En el camino, el método cambió: probamos ventanas, formas de validar y reglas de decisión distintas. Por eso, al final, congelamos la estrategia en un pipeline único, en el `main` del repositorio. Desde ahí, cada idea nueva se prueba en un branch, con un solo cambio, y entra al `main` solo si cumple la regla de merge: diferencia positiva y al menos tres de cinco semillas a favor.

*(~165 palabras)*

---

## Tramo 5 — Limitaciones (~0:40)

**Pantalla:** cuatro íconos con una línea cada uno:
1. "2019 ya mirado → exploratorio";
2. "Muchas comparaciones → maldición del ganador", con barras: +5,25 al elegir · +2,14 con semillas nuevas · −0,92 en meses nuevos;
3. "Búsqueda de hiperparámetros acotada: 10 pruebas por receta";
4. "Pocos meses evaluados · variables rotas como faltantes".

**Texto:**
> Cuatro limitaciones. Uno: los meses de 2019 ya los habíamos mirado, así que todo es exploratorio. Dos: probamos muchas configuraciones, y la mejor de muchas sale favorecida por azar. Es la maldición del ganador, y la medimos: la mejor de sesenta combinaciones de hiperparámetros ganaba 5,25 millones por mes al elegirla, 2,14 con semillas nuevas en los mismos meses, y perdía 0,92 en meses nuevos. Tres: la búsqueda de hiperparámetros del pipeline de recetas fue acotada, con diez pruebas por receta. Cuatro: pocos meses evaluados, y en 2019 hay variables rotas en algunos meses, que tratamos como faltantes.

*(~95 palabras)*

---

## Tramo 6 — Resultados: recetas (~1:15)

**Pantalla:**
- **Gráfico interactivo:** cada punto es una receta; eje x = ganancia sobre B0 en septiembre; eje y = en octubre (millones por mes). Los cuatro cuadrantes muestran sus conteos: **19** arriba a la derecha, **5** abajo a la izquierda, **15** mixtas. Al pasar el mouse se ven la receta y sus semillas a favor.
- Resaltadas:
  - tendencia W4: +2,2 / +4,6, 5/5 y 5/5;
  - máximo W6: +2,4 / +4,4;
  - rango W6: +3,0 / +4,2.
- Los lags y deltas 3–5, marcados en gris: ninguno en el cuadrante superior derecho.
- Nota al pie: "Intervalos sin corregir por comparaciones múltiples".

**Texto:**
> Resultados del pipeline de recetas. En el gráfico, cada punto es una receta: en el eje horizontal, cuánto gana sobre B0 en septiembre; en el vertical, cuánto gana en octubre. 19 recetas quedan arriba a la derecha: ganan en los dos meses. 5 quedan abajo a la izquierda: pierden en los dos. Las otras 15 ganan en un mes y pierden en el otro. Si ninguna receta sirviera, esperaríamos unas diez de cada lado.
>
> La más consistente es la tendencia de cuatro observaciones: +2,2 millones en septiembre y +4,6 en octubre, con las cinco semillas a favor en los dos meses. Le siguen el máximo y el rango de seis observaciones, de +2,4 a +4,4. Y un dato clave: los lags y deltas de 3, 4 o 5 meses atrás, en gris, no ganan en los dos meses en ningún caso. Una aclaración: estos resultados todavía no están corregidos por comparaciones múltiples.

*(~155 palabras)*

---

## Tramo 7 — Resultados: pipeline acumulativo (~1:15)

**Pantalla:**
- Barras por mes, de junio a octubre: estrategia final contra baseline, con la diferencia arriba de cada par (12,3 · 4,0 · 7,8 · 9,7 · 11,2).
- Número grande: **+9,0 M por mes** · IC 5,2 a 12,8 · 5 de 5 semillas. Al lado: **+12,6** contra la ventana de la consigna.
- Recuadro "Lo más firme":
  - historia curada +4,1;
  - entrenar con meses recientes: la ventana de la consigna pierde −5,8.
- Mini diagrama de la interacción: "tarjetas 0,6 + relativos 0,6 → juntos 2,2".
- Tabla de branches:
  - `rango` de 3 meses: −0,23 · NO PASA;
  - Optuna sobre el `main`: +0,57 · IC −2,6 a +3,7 · 6 de 10.

**Texto:**
> Resultados del pipeline acumulativo. Contra el baseline con el mismo calendario, la estrategia final gana 9 millones por mes más, con las cinco semillas a favor y un intervalo de 5,2 a 12,8. Gana en los cinco meses, de 4 a 12 millones. Contra el baseline con la ventana de la consigna, la diferencia es de 12,6.
>
> ¿De dónde sale? Lo más firme: la historia curada, que sumó 4,1 millones, y entrenar con los meses recientes, porque la ventana vieja de la consigna perdía 5,8. Y una interacción que solo se ve acumulando: las tarjetas combinadas sumaban 0,6 solas, los cambios relativos 0,6 solos, y juntos, 2,2.
>
> Sobre el `main` ya corrimos dos branches. El rango de tres meses dio −0,23 y no pasa la regla. Reoptimizar los hiperparámetros con Optuna dio +0,57, con seis de diez semillas a favor: pasa la regla y ya entró al `main`, aunque con un intervalo que va de −2,6 a +3,7.

*(~165 palabras)*

---

## Tramo 8 — Coincidencias y diferencias (~0:45)

**Pantalla:** tabla de dos columnas (recetas | acumulativo), con ✓ donde coinciden y ≠ donde difieren:
- ✓ la historia suma sobre lags y deltas 1–2;
- ✓ más meses crudos casi no suman;
- ✓ la tendencia de unos 4 meses suma (W4: +2,2 / +4,6 · 5 observaciones: +4,2 / +3,6);
- ✓ rinde comparar al cliente con su propio pasado;
- ≠ el rango: suma sobre B0, NO PASA sobre el `main`.

Debajo, dos frases: "Recetas: qué suma **sola**" · "Acumulativo: cuánto suma **junto**".

**Texto:**
> Los dos pipelines coinciden en lo importante. La historia suma sobre los lags y deltas de 1 y 2 meses. Mirar más meses crudos casi no suma. La tendencia de unos cuatro meses aparece en los dos: en nuestra prueba pre-registrada, con cinco observaciones, sumaba 4,2 y 3,6 millones. Y lo que rinde es comparar al cliente con su propio pasado.
>
> Difieren en el rango: sobre B0 suma, y sobre el `main` no pasa, porque el `main` ya tiene otras comparaciones contra el propio pasado. Por eso los diseños se complementan: el de recetas dice qué suma sola, con un procedimiento parejo; el acumulativo, cuánto suma junto.

*(~110 palabras)*

---

## Tramo 9 — Conclusiones y qué seguiríamos probando (~0:50)

**Pantalla:**
- Las dos tarjetas de sesgo del tramo 1, con su sello:
  - "Más meses → mucha más ganancia": **perforado** (los meses 1 y 2 dan del 69 % al 90 % del valor de la historia);
  - "Señales de abandono > lags crudos": **a medias** (las rachas, sin ganancia consistente; la caída frente al propio historial, sí).
- Recuadro "Para la competencia 2": pocas fotos hacia atrás · el cliente contra sí mismo · meses recientes.
- Lista "Seguiríamos probando":
  - las recetas con señal como branches del `main`, juzgadas en junio–agosto;
  - lags sin deltas;
  - sacar un bloque por vez del `main`.

**Texto:**
> ¿Qué hizo la evidencia con nuestros sesgos? Más meses no dieron mucho más: los dos primeros meses ya dan entre el 69 y el 90 % de lo que aporta la historia. El sesgo de Clara quedó a medias: las rachas de inactividad no mostraron una ganancia consistente, pero la caída frente al propio historial sí.
>
> Para la segunda competencia nos llevamos esto: pocas fotos hacia atrás, el cliente comparado consigo mismo, y entrenar con los meses más recientes. Y seguiríamos probando: las recetas que dieron señal en el pipeline de recetas, como branches del `main`, juzgadas en junio a agosto, que son los meses que no se usaron para elegirlas; los lags sin deltas; y sacar un bloque por vez del `main`, para medir cuánto aporta cada uno. El código de los dos pipelines está en los repositorios que aparecen en pantalla.

*(~145 palabras)*

---

**Total aproximado:** 1.195 palabras, entre 8 y 9 minutos a un ritmo pausado. Si hace falta recortar, conviene empezar por el segundo párrafo del tramo 4 o por la interacción del tramo 7.
