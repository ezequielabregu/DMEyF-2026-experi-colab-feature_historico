# Diseño experimental (pre-registro) — `feature_historico`

> **Versión 1 · 2026-11-02 · borrador para el grupo.** Este documento fija el diseño **antes** de correr las variantes y antes de mirar 201909 y 201910. Cualquier cambio posterior va a la sección 11, con su fecha y su motivo, y nunca se borra lo anterior.
>
> Los puntos marcados *provisorio* dependen de preguntas hechas a la cátedra que todavía no tienen respuesta. Si la respuesta los cambia, se registra en la sección 11 **antes** de mirar los resultados.

## 1. Pregunta e hipótesis

**Pregunta:** ¿agregar más historia de cada cliente (3 y 4 meses hacia atrás) hace ganar más plata que el baseline, que solo ve 2 meses?

- **Hipótesis principal:** al menos una variante con más historia gana más que el control A en 201910, según la regla de la sección 6.
- **Hipótesis secundaria (dosis-respuesta):** la ganancia crece con la cantidad de historia, h = 2 → 3 → 4.
- **Análisis secundario:** si el resultado se sostiene cuando la historia de los montos se calcula sobre rankings dentro del mes en lugar de pesos nominales.

**Si ninguna variante cumple la regla**, la conclusión es que ~~*más de 2 meses de historia no suma en esta ventana*~~ *no se pudo demostrar que agregar más de 2 meses de historia sume en esta ventana*, y se reporta igual. Eso no prueba que no sume: un efecto real de 2 o 3 M puede no pasar Holm (sección 11).

## 2. Datos

- **Dataset:** `competencia_02_crudo.csv`, solo 2019.
- **Clase ternaria:** con el criterio de la cátedra (`z470`), calculada después de cortar en 201912. En 2019, la tasa de `BAJA+2` va de 0,41 a 0,62 % por mes.
- **Meses:**

| Rol | Meses |
|---|---|
| Entrenamiento *(provisorio)* | 201905–06 (255.133 filas, 1.247 `BAJA+2` y 1.241 `BAJA+1`) |
| Validación (Optuna y elección de N) | 201908 |
| Test principal | **201910** |
| Test secundario *(provisorio)* | 201909 |
| No se usan | 201911 y 201912 |
| Solo historia | de 201901 a 201904, y 201907 |

- **Por qué 201905–06 y no 201903–06** (la ventana de la consigna): el dataset empieza en 201901. Con 201903–06, el lag 3 y el lag 4 quedan vacíos en parte del entrenamiento y llenos en el test, y el modelo aprendería "falta el dato" en lugar de "historia". 201905–06 es la única ventana con historia completa hasta 4 meses (cobertura: 95,5 % y 95,3 % de clientes con lag 4).
- **Meses rotos:** 23 casos (variable, mes) con 95 % o más de ceros o nulos en un mes aislado (etapa 1). Pasan a NA **antes** de calcular la historia, igual en todas las variantes. 12 de esos casos caen en 201910.

## 3. Variantes

Todas usan las mismas filas, en el mismo orden, con los mismos hiperparámetros y las mismas semillas. **Lo único que cambia es la historia.**

| Variante | Qué ve el modelo | Variables |
|---|---|---:|
| **A (control)** | las 152 del mes + lag 1, lag 2, delta 1 y delta 2 de las 152 (la consigna) | 760 |
| L3 | A + lag y delta 3 | 1.044 |
| L4 | A + lag y delta 3 y 4 | 1.328 |
| T3 | A + tendencias de 3 meses | 1.284 |
| T4 | A + tendencias de 4 meses | 1.284 |
| LT3 | L3 + T3 | 1.568 |
| LT4 | L4 + T4 | 1.852 |

**Definiciones:**
- **lag k:** el valor del mismo cliente k meses calendario antes (NA si no estaba ese mes);
- **delta k:** el valor del mes menos el lag k;
- **tendencia de h meses:** con la ventana del mes m − h al mes m, la pendiente por mínimos cuadrados (por mes), el promedio, el mínimo y el máximo. Así L4 y T4 miran exactamente los mismos meses.

**La historia que agregan las variantes depende del tipo de variable.** La clasificación se hizo por el significado (diccionario de datos) y por los valores, sin mirar la clase:

| Tipo | Variables | Lags (L) | Tendencias (T) |
|---|---:|---|---|
| Montos y conteos | 129 | lag y delta | pendiente, promedio, mínimo, máximo |
| Banderas (0/1) | 8 | lag y delta (cambio: −1, 0, 1) | permanencia: meses activa en la ventana |
| Estados | 5 | lag y "cambió" (0/1) | — |
| Fechas (días relativos) | 8 | — | — |
| Edad y antigüedad | 2 | — | — |

**Configuraciones adicionales, fuera de la regla principal:**
- **A-ranking y LT4-ranking** (análisis secundario): la historia de los 73 montos en pesos se calcula sobre el percentil dentro del mes. Motivo: en 2019, el aguinaldo cae en 201906 (la mediana de `mpayroll` sube de 59 mil a 86 mil), y los montos en dólares casi se duplican en 201907–08;
- **A-consigna** (referencia): A entrenando con 201903–06, para comparar con los otros grupos.

## 4. Modelo

- **LightGBM** `gbdt`, `bagging_freq` 1, sin regularización (`lambda_l1`, `lambda_l2`, `min_gain_to_split` en 0), `max_bin` 31, `deterministic`, 8 hilos. Los nulos no se imputan.
- **Clase de entrenamiento** *(provisorio)*: `BAJA+1` y `BAJA+2` juntas contra `CONTINUA`. La ganancia cuenta solo `BAJA+2`.
- **Hiperparámetros:** **una búsqueda de Optuna de 50 pruebas sobre A**, reusada en todas las variantes.
  - Busca `num_leaves` (8–512), `min_data_in_leaf` (10–2.000), `learning_rate` (0,01–0,1), `feature_fraction` (0,2–1,0) y `bagging_fraction` (0,4–1,0), con TPE (semilla 979201).
  - Maximiza la AUC en 201908 contra `BAJA+2`. La cantidad de árboles sale del *early stopping* (paciencia de 100, tope de 3.000).
- **Semillas:** 10, las mismas para todas las variantes. Salen de la semilla primigenia 979201: 294103, 342929, 161093, 677561, 431077, 330679, 511579, 312773, 118147, 567529.
- **Sin reentrenar:** cada modelo (variante × semilla) se entrena una sola vez con 201905–06 y predice 201908, 201909 y 201910.

## 5. Métricas

- **Ganancia** *(provisorio)*: `1.072.500 × BAJA+2 contactados − 27.500 × resto de los contactados`, ordenando a los clientes por probabilidad.
- **Cantidad de envíos (N):** **una por variante, elegida en 201908**:
  - se promedia la curva de ganancia de las 10 semillas;
  - se suaviza con una media móvil centrada de 501 posiciones;
  - N es el máximo de esa curva.

  Ese mismo N se aplica sin cambios a 201909 y a 201910. **Ningún corte se elige mirando el test.**
- **Métrica principal:** la ganancia en 201910 con ese N, por semilla.
- **Control de robustez:** la ganancia promedio entre N = 3.000 y N = 6.000, por semilla.
- **También se reporta** la AUC en cada mes.

## 6. Regla de decisión (se aplica una sola vez)

**Ceguera:** el notebook que entrena todos los modelos (`03`) no carga la clase de 201909 ni de 201910. Solo guarda las predicciones de esos meses. La ganancia y la AUC de 201909 y 201910 se calculan **una sola vez**, en el notebook `04`, aplicando esta regla. Este documento y el `03` se commitean antes.

Para cada variante V (L3, L4, T3, T4, LT3 y LT4):
1. Por semilla, d = ganancia de V − ganancia de A, en 201910, cada una con su N.
2. Wilcoxon de rangos con signo, pareado, de dos colas, sobre las 10 diferencias.
3. **Corrección de Holm** sobre los 6 p-valores, con α = 0,05.

**V le gana a A si cumple las tres:**
- su p-valor corregido por Holm es menor que 0,05;
- la diferencia media en 201910 es positiva;
- la diferencia media en 201909 es ≥ 0.

**Además, siempre:**
- **Dosis-respuesta:** se reporta la ganancia media de 201910 (con su intervalo entre semillas) para h = 2 (A), 3 y 4, en las familias L, T y LT, sea o no significativa.
- **Robustez:** si la métrica de banda (N de 3.000 a 6.000) da la diferencia con el signo contrario al de la métrica principal, el resultado se reporta como **frágil**.
- **Rankings:** LT4-ranking contra A-ranking, con el mismo test, sin corrección y fuera de la regla principal.
- **A-consigna:** solo descriptiva.

**Exigencia de la regla:** la comparación más exigente de Holm pide p < 0,0083. Con 10 semillas, eso significa ganar en las 10, o en 9 si la semilla que pierde lo hace por muy poco.

## 7. Sesgos y limitaciones (declarados de antemano)

- **Expectativa de los autores:** en la competencia 1 (2021), la historia de 3 meses sumó. Esperamos que 3–4 meses sumen. La regla se fija antes para no forzarlo.
- **Hiperparámetros elegidos para A:** la comparación es conservadora y favorece al control.
- **Pocos positivos:** 1.247 `BAJA+2` en el entrenamiento y unas 600 por mes de test. La ganancia varía bastante entre semillas.
- **Una sola ventana y una sola época:** entrenamiento de 2 meses, en 2019. No prueba que pase lo mismo en otra época.
- **h máximo = 4:** con el dataset empezando en 201901, no se puede probar más historia sin cambiar de época.
- **201910 tiene 12 variables rotas**, que pasan a NA. Un modelo con más historia puede compensarlas mejor con sus lags: es un efecto real de la historia, pero no es el mismo efecto que en un mes sano.
- **Inflación:** la regla principal usa pesos nominales. Los rankings se miran como análisis secundario.
- **Experimento mínimo previo:** en la etapa 2 se comparó A contra LT4 en 201908, la validación, con 5 semillas. LT4 dio +3,5 M de media. Ese resultado no se usó para elegir variantes: las 6 entran en la regla.
- **La ventana pesa más que la historia, al menos en validación:** en 201908, A-consigna (A con 201903–06) le saca +6,4 M a A, más que cualquier variante. Entrenar solo con 201905–06 permite comparar la historia de forma justa, pero puede costar más plata que la que la historia agrega.
- **A-ranking es un control débil:** en 201908 pierde 7,9 M contra A. Una ventaja de LT4-ranking sobre A-ranking puede venir de esa debilidad, y no solo de la historia.

## 8. Qué es provisorio

Hay preguntas hechas a la cátedra sin respuesta. Si la respuesta cambia algo, se cambia el parámetro, se registra en la sección 11 y se vuelve a correr todo (de 2 a 3 horas):
- la ventana de entrenamiento (201905–06);
- la fórmula de ganancia;
- la clase de entrenamiento (las dos bajas juntas);
- 201909 como segundo mes de prueba;
- el alcance de "lag y delta 2" en el baseline (se interpretó como lag y delta 1 y 2 de todas las variables).

## 9. Figuras del video

1. **Ganancia por semilla en 201910:** A contra cada variante (puntos unidos por semilla), con el resultado de la regla.
2. **Dosis-respuesta:** ganancia media según h (2, 3, 4), una línea por familia (L, T, LT), con el intervalo entre semillas.
3. **Curvas de ganancia promedio** en 201910 según N, para A y para la mejor variante, con el N elegido en 201908 marcado.
4. **Tabla de la regla aplicada:** diferencia media, p-valor, p-valor de Holm, 201909 y robustez, una fila por variante.

## 10. Reproducibilidad

- **Código:** los notebooks `01` (clase y calidad), `02` (experimento mínimo), `03` (entrenamiento de todas las configuraciones, sin la clase de los meses de test) y `04` (evaluación con la regla). Cada uno tiene un bloque de parámetros y controles automáticos (`assert`).
- **Determinismo:** con la misma semilla, la AUC sale idéntica de una corrida a otra (verificado en la etapa 2).
- **Reproducción cruzada:** otro integrante corre A con 2 semillas en su VM. Tiene que dar la misma AUC, o una diferencia mínima explicada por la plataforma.
- **Costo estimado:** ~2,6 horas en una Mac M4.

## 11. Registro de cambios

| Fecha | Cambio | Motivo | ¿Antes de ver resultados? |
|---|---|---|---|
| 2026-11-02 | Versión 1 | — | Sí |
| 2026-11-03 | **Precisiones de la evaluación (`04`)**, sin cambiar la regla:<br>(a) **intervalo de la dosis-respuesta:** IC 95 % de la media entre las 10 semillas, con t de Student (9 grados de libertad);<br>(b) **Wilcoxon exacto:** se enumeran las 2ⁿ asignaciones de signo (1.024 con 10 pares). Si hay empates en \|d\|, se usan rangos promedio; las diferencias iguales a 0 se descartan;<br>(c) **banda de robustez:** por semilla, el promedio de la curva de ganancia sin suavizar entre N = 3.000 y N = 6.000, ambos incluidos. "Frágil" si la diferencia media en la banda tiene el signo contrario al de la diferencia media principal, en 201910;<br>(d) **AUC de 201909 y 201910:** contra `BAJA+2`, como en la validación. Solo se reporta;<br>(e) **"la mejor variante" de la figura 3:** la de mayor diferencia media en 201910. Es solo para la figura y no entra en la regla | Lo que la sección 6 dejó sin detallar. En (b), con N fijo la ganancia se mueve de a saltos de 1,1 M, así que las diferencias pueden empatar, y el exacto clásico supone que no hay empates | Sí (precisión, antes de ver resultados) |
| 2026-11-03 | **Corrección de código en el `04`:** las diferencias se redondean a 6 decimales antes del Wilcoxon, sin cambiar la regla | El ruido de `float` ocultaba empates y no se aplicaban los rangos promedio de la precisión (b). Detectado por el verificador, solo con 201908 (T4 pasa de 0,1250 a 0,1191, y LT4 de 0,8320 a 0,8164) | Sí |
| 2026-11-03 | **Conclusión si ninguna variante gana (sección 1).** Antes: "más de 2 meses de historia no suma en esta ventana". Después: "no se pudo demostrar que agregar más de 2 meses de historia sume en esta ventana" | La regla es exigente: en 201908, LT3 tiene 9 de 10 semillas a favor y p = 0,0176, que con Holm queda en 0,106. No pasar la regla no prueba que el efecto sea nulo | Sí |
| 2026-11-03 | **Dos limitaciones nuevas (sección 7):** A-consigna le saca +6,4 M a A en 201908, y A-ranking es un control débil (−7,9 M contra A en 201908) | Señaladas por el verificador, con los datos de validación del `03` | Sí |
| 2026-11-03 | **El `04` se corre sin publicar este documento en Zulip** y sin que el resto del grupo lo haya revisado. El respaldo de que todo se fijó antes es la fecha de los commits en GitHub | Decisión de Ezequiel: comunicar al grupo cuando se complete la estrategia. **Consecuencia:** si después la cátedra o el grupo cambian un punto provisorio (sección 8), la nueva corrida ya no es a ciegas, y se reporta así | Sí |
| 2026-11-03 | **Limitación nueva, sin cambios en el diseño:** `ctarjeta_master_descuentos` y `mtarjeta_master_descuentos` están en 100 % de ceros en 201910 y no se pasaron a NA. Son 2 casos más de los 12 declarados en la sección 2. Quedan como están, con el mismo tratamiento en las 10 configuraciones | Detectado al comparar con la presentación de la cátedra (diapositiva 51: 14 variables rotas en 201910). Es la misma rotura que sus pares de Visa. Corregirlo ahora ya no sería a ciegas; su efecto no está medido | **No** (después de ver resultados) |
| 2026-11-03 | **Consigna actualizada, sin cambios en el diseño.** Confirma tres puntos provisorios de la sección 8: lag y delta 1 y 2, las dos bajas juntas en el entrenamiento, y ganancia en test. Siguen provisorios la ventana, la fórmula de ganancia y 201909 | Texto publicado por el profesor. Lo corrido ya coincide con esos tres puntos | No (después de ver resultados), pero no cambia nada |
