# Propuesta de estrategia (v1) — Ezequiel

> **Estado: propuesta para discutir en el grupo.** Los puntos marcados *provisorio* dependen de la respuesta de Bolaños. Todo queda como parámetro del código, así que cambiarlos no obliga a rehacer nada.

## 1. Pregunta e hipótesis

**Pregunta:** ¿agregar historia de los clientes (más de 2 meses) hace ganar más plata que el baseline (lag y delta de orden 1 y 2)? El objetivo es dejar una regla para la competencia 2: cuánta historia conviene usar, y de qué tipo.

**Hipótesis:** *un modelo que ve más meses de historia de cada cliente gana más plata en 201910 que el baseline, que solo ve 2 meses.* Si la ganancia no sube de forma consistente entre semillas, queda refutada, y ese resultado también se reporta.

## 2. El experimento, explicado sin jerga

**El problema del banco.** Cada mes, algunos clientes se van. El banco quiere detectarlos con tiempo para ofrecerles algo y que se queden. Acertar con uno que se iba a ir le hace ganar mucha plata; ofrecerle algo a uno que se iba a quedar igual le cuesta un poco. El modelo arma la lista de a quién llamar.

**Qué mira el modelo.** Para cada cliente, una "foto" del mes (saldos, consumos de tarjeta, transacciones, sueldo…) y fotos de meses anteriores:
- un **lag** es la foto de hace k meses (por ejemplo, el saldo de hace 3 meses);
- un **delta** es la diferencia entre hoy y esa foto (cuánto subió o bajó);
- una **tendencia** es la dirección de los últimos meses (si viene bajando de a poco, o de golpe).

**El baseline** es el modelo de referencia de la cátedra: ve la foto de hoy y las de hace 1 y 2 meses. Es el grupo de control.

**Qué cambiamos:** una sola cosa, cuántos meses hacia atrás ve el modelo y de qué forma. Todo lo demás queda igual: datos, modelo y semillas.

**Por qué podría funcionar.** Un cliente que se va no suele irse de golpe: antes deja de cobrar el sueldo en la cuenta, usa menos la tarjeta, cae el saldo. Con 2 meses, el modelo ve un pedazo de esa caída; con más, podría ver la curva entera.

**Por qué podría no funcionar.** Más variables también traen más ruido, y en 2019 hubo mucha inflación: un saldo de hace 4 meses no se compara directo con el de hoy en pesos.

## 3. De dónde sale la hipótesis

La hipótesis se fijó **antes** de mirar resultados en 2019.

**Evidencia propia de la competencia 1 (2021).** Bloques de variables probados sobre la misma base, con 10 semillas, en backtests. Diferencia de ganancia contra la base, en millones de $:

| Bloque | Prueba A (entrena 202103–04, predice 202106) | Prueba C (entrena 202103–05, predice 202106) |
|---|---|---|
| **Historia de 3 meses** (lags 1–2, delta, promedio, mínimo, máximo y pendiente de 3 meses, sobre 8 variables) | **+6,2** (10/10 semillas, Wilcoxon p = 0,002) | **+12,7** (10/10, p = 0,002) |
| **Señales de historia del negocio** (empieza a pagar comisión, perdió el sueldo, consumo contra el promedio de 3 meses, cae el saldo) | **+2,8** (8/10, p = 0,037) | **+8,1** (10/10, p = 0,002) |
| **Las dos + rankings** (la combinación adoptada) | **+15,3** (10/10, p = 0,002) | **+15,7** (10/10, p = 0,002) |

En el leaderboard público, esa combinación subió de 88,09 a **94,86**.

**El negocio.** En el análisis de segmentación de la competencia 1, la fila `BAJA+2` es el penúltimo mes del cliente. En esa fila ya se ve que empieza a pagar comisión (multiplica el riesgo por 8), que el sueldo se empieza a ir y que el saldo cae: es un proceso de varios meses.

**Lo que hicieron otros.**
- El ganador de la competencia 1 usó tendencias y ventanas de 3 meses, y la mayoría de sus variables que le ganaron al ruido (canaritos) eran históricas.
- El flujo de la cátedra 2024 incluye la pendiente de 6 meses.
- Clase 04: lags, deltas y tendencias son imprescindibles, porque un árbol no los puede inventar.

**Lo que no sabemos (el hueco que cubre el experimento).**
- En 2021 se probó historia de hasta 3 meses; más nunca se probó.
- No toda la historia suma: lag 1 y delta 1 de todas las variables dio casi neutro.
- 2021 no es 2019.

**Sesgo declarado.** Venimos de un resultado donde la historia sumó. Esperamos que 3–4 meses sumen y que más allá rinda menos. Para no forzarlo, la regla de decisión (punto 7) se fija antes de mirar 201910.

## 4. El problema: la historia no entra en la ventana del baseline

El dataset empieza en **201901**. Porcentaje de clientes de cada mes que ya estaban en el banco h meses antes (verificado sobre `competencia_02_crudo.csv`):

| Mes | Rol | h=2 | h=3 | h=4 | h=5 | h=6 |
|---|---|---:|---:|---:|---:|---:|
| 201903 | entrenamiento | 97,6 | 0 | 0 | 0 | 0 |
| 201904 | entrenamiento | 98,0 | 96,6 | 0 | 0 | 0 |
| 201905 | entrenamiento | 97,9 | 96,9 | 95,5 | 0 | 0 |
| 201906 | entrenamiento | 97,2 | 96,3 | 95,3 | 93,9 | 0 |
| 201908 | validación | 96,5 | 94,8 | 93,7 | 92,9 | 91,9 |
| 201910 | test | 96,3 | 94,4 | 92,9 | 91,3 | 90,2 |

- Donde hay meses previos, entre el 90 y el 98 % de los clientes tiene historia: los ceros vienen del borde del dataset, no de los clientes.
- Con la ventana del baseline (201903–06), el lag 6 está vacío en todo el entrenamiento y lleno en test. El modelo aprendería "falta el dato" en lugar de "historia".
- **Ya nos pasó en la competencia 1:** en un backtest que entrenaba con el primer mes del dataset, el bloque de historia dio −5,0. Sin historia en el entrenamiento, la historia no se puede juzgar.

Meses de entrenamiento con historia completa, manteniendo validación 201908 y test 201910:

| h | Meses de entrenamiento |
|---|---|
| 2 | 201903–06 (el baseline) |
| 3 | 201904–06 |
| 4 | 201905–06 |
| 5 | 201906 |
| 6 | ninguno |

## 5. Diseño propuesto

**Ventana** *(provisorio)*: los **mismos meses de entrenamiento para todas las variantes**, 201905–06, donde existe historia de hasta 4 meses. Validación 201908 y test 201910, como en la consigna. Así lo único que cambia entre variantes es la historia.

**Variantes** (configuraciones del mismo código, no ramas de git):

| Variante | Qué ve el modelo |
|---|---|
| **A (control)** | Foto del mes + lag y delta de 1 y 2 meses (el baseline de la consigna) |
| L3 | A + lag y delta de 3 meses |
| L4 | A + lag y delta de 3 y 4 meses |
| T3 | A + tendencias de 3 meses |
| T4 | A + tendencias de 4 meses |
| LT3 | L3 + T3 |
| LT4 | L4 + T4 |

- **Tendencias de h meses:** pendiente por mínimos cuadrados, promedio, mínimo y máximo de los últimos h meses.
- Es un diseño **dosis-respuesta**: mide la ganancia según cuánta historia ve el modelo (h = 2, 3, 4) y de qué tipo. Se puede graficar como una curva, y responde "cuánta historia conviene".
- **Referencia extra:** el baseline exacto de la consigna (entrena con 201903–06), para comparar con los demás grupos.

**Variables que reciben historia** *(a decidir)*: propongo **todas las numéricas**, sin seleccionar. Elegir "las más importantes" agrega una decisión que puede mezclarse con el efecto de la historia, y si se elige con datos que no corresponden, filtra información. Una selección puede ser una variante posterior.

**Inflación:** la historia de los montos se calcula sobre rankings dentro del mes, no sobre pesos nominales. En la competencia 1, los rankings sumados a la historia aportaron +10.

## 6. Modelo y evaluación

- **Hay que generar la clase ternaria (Propuesta de Tomás):** el dataset no dice quién se fue; hay que generar la **clase ternaria** para cada cliente y mes m:
  - `CONTINUA`: aparece en m+1 y en m+2;
  - `BAJA+1`: no aparece en m+1 (se va el mes que viene);
  - `BAJA+2`: aparece en m+1 pero no en m+2 (se va dentro de dos meses). **Es la que paga:** da tiempo a llamar al cliente.

  Se genera sobre el dataset cortado en 201912, como en la consigna: 201911 queda solo con `BAJA+1` y 201912 sin clase. Los clientes que se van y vuelven siguen la regla de la cátedra (cuentan como `BAJA+1` antes del hueco), como en la competencia 1.
- **Clase de entrenamiento** (Propuesta de Tomás)*(provisorio)*: `BAJA+1` y `BAJA+2` juntas contra `CONTINUA`, y la ganancia se calcula solo sobre `BAJA+2`. En la competencia 1, entrenar con las dos bajas juntas dio unos $269 M contra $248 M de `BAJA+2` sola (`z601`). Es la misma para el control y todas las variantes, así que no afecta la comparación.
- **Modelo:** LightGBM, como en la consigna.
- **Hiperparámetros** *(provisorio)*: una sola búsqueda con Optuna sobre el control A (AUC en 201908), reusada en todas las variantes. Aísla el efecto de la historia y cuesta 7 veces menos. En el experimento mínimo se revisa si una variante cambia mucho con su propia búsqueda.
- **Semillas:** 10, las mismas para todas las variantes (comparación pareada).
- **Ganancia en 201910:** cortando por cantidad de envíos (N), en la meseta de la curva de ganancia. También se reporta la AUC.
- **Segundo mes de prueba** *(provisorio)*: 201909, para ver si el resultado se sostiene en más de un mes.

## 7. Regla de decisión (se fija antes de mirar 201910)

Una variante le gana al control si:
1. su ganancia en 201910 es mayor, con Wilcoxon pareado p < 0,05 sobre las 10 semillas;
2. y no pierde en 201909.

Si ninguna cumple, la conclusión es que **más de 2 meses de historia no suma** en esta ventana, y se reporta igual.

## 8. Plan de trabajo (en orden)

1. **Pipeline y calidad de datos:** generar la clase ternaria y verificar la tabla de clases por mes de 2019; detectar meses rotos que contaminan la historia; armar la tabla de cobertura. Parte del código de la competencia 1 (Python), que ya genera la clase en SQL.
2. **Experimento mínimo:** A contra una variante, con pocas semillas, en Google Cloud. Valida el código y mide tiempos.
3. **Ajuste del diseño**, con lo aprendido y con la respuesta del profe.
4. **Diseño final** (`docs/diseno_experimental.md`), publicado en Zulip antes de correr.
5. **Baseline completo y variantes.**
6. **Corridas repartidas** entre las tres VM, con las mismas semillas. Uno reproduce el baseline de otro, para verificar.
7. **Evaluación final y video.**

## 9. Pendiente de Respuesta del Profe

1. Ventana de meses (punto 5).
2. 201909 como segundo mes de prueba.
3. ¿La fórmula de ganancia es la de la competencia 1 (1.072.500 × BAJA+2 − 27.500 × resto)?
4. Una búsqueda de hiperparámetros compartida o una por variante.

## 10. Para decidir entre los tres

1. ¿Están de acuerdo con el diseño dosis-respuesta (punto 5)?
2. Variables que reciben historia: ¿todas, o un subconjunto?
3. Clase de entrenamiento: ¿las dos bajas juntas (punto 6) o `BAJA+2` sola?
4. ¿Python (con el código de la competencia 1 como base) o R?
5. ¿Quién toma cada etapa del punto 8?
