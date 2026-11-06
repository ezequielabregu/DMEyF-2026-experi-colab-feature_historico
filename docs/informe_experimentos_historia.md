# Informe grupal de experimentos de historia

**Corte de resultados:** 2026-11-05T21:21:42.233417+00:00 (UTC). Informe regenerable desde las tablas del snapshot.

Registro conjunto del trabajo de Clara, Ezequiel y Tomás sobre feature engineering histórico. Reúne propuestas, corridas realizadas, resultados positivos y negativos, réplicas y tareas pendientes. Distingue la regla principal de ganancia, las exploraciones posteriores y nuestra serie actual orientada a AUC. Una corrida parcial no se clasifica como éxito ni como fracaso.

## Alcance del informe grupal

Este registro reúne el trabajo disponible de Clara, Ezequiel y Tomás: propuestas, preparación, experimento principal, exploraciones posteriores y nuevas corridas en Google Cloud. La atribución sigue los archivos disponibles: las ideas de clasificación y el protocolo están documentadas como aportes de Clara; los notebooks 01–09 y sus tablas están en la rama de Ezequiel; las réplicas y la nueva serie se ejecutaron en la VM de Tomás. No se atribuye autoría exclusiva de cada conclusión.

Los antecedentes se congelan en el commit 3b44f21 de ezequiel/etapa-1. No se afirma que incluya cambios posteriores. Las tablas agregadas se conservan en resultados/antecedentes_3b44f21. Para los experimentos nuevos, el corte temporal figura al inicio.

## Mapa de todo lo documentado

| Etapa | Trabajo | Evidencia disponible |
|---|---|---|
| Propuesta de Clara | Clasificación por tipo de variable e historia de 3–6 meses; luego protocolo de resúmenes, rachas, ratios, rankings y canaritos | Documentos y código propuesto; no equivale a una corrida completa de ese protocolo |
| 01 | Clase ternaria, calidad, cobertura y meses rotos | Tablas y controles |
| 02 | Prueba mínima A frente a LT4 con cinco semillas en agosto | Tabla de AUC y ganancia de validación |
| 03–04 | Diez configuraciones, 100 modelos, seis contrastes principales y evaluación | Métricas, regla y figuras |
| 05 | Ensambles y segundas diferencias | Tablas de semillas, ensambles y contrastes |
| 06 | Ratio3, zero_streak3 y combinación | Diez semillas y ensambles |
| 07 | Optimización propia para marzo–junio | Hiperparámetros y comparación con AC |
| 08 | Historia sin quitar meses, historia curada y mezclas | Diez semillas y ensambles |
| 09 | Eventos, ratios entre tarjetas, puntajes y hojas RF | Código; sin resultados publicados en el snapshot revisado |
| Réplica en Google Cloud | Preparación, A y A-consigna con dos semillas | Logs del usuario; coincidencia a precisión mostrada |
| Preparativos no ejecutados | Baseline local y experimento de disponibilidad de historia | Scripts preparados; no se presentan como resultados experimentales |
| Sin historia frente a con historia | 152 frente a 760 columnas, diez semillas | Corrida complementaria en agosto |
| Nuevas cuatro familias | Historia reciente, cambios relativos, persistencia, rankings con cero fijo | Estado y métricas al corte en la sección final |

## Controles y métricas que no debemos mezclar

| Nombre | Entrenamiento | Ajuste | Uso |
|---|---|---|---|
| A | Mayo–junio | 50 trials sobre A; 296 árboles | Control del experimento principal adaptado para historia hasta cuatro meses |
| A-consigna / AC | Marzo–junio | Hereda parámetros y 296 árboles de A | Referencia con todos los meses de la consigna; AC agrega saneamiento de dos roturas Master en octubre |
| ACO | Marzo–junio | 50 trials propios; 339 árboles | Baseline reajustado del 07 y control de nuestras cuatro familias |
| AC2 | Marzo–junio | Mezcla de dos semillas del control AC | Control de mezclas por semilla del 08 |

Todos estos modelos usan 760 variables de partida. Entrenan con ambas bajas; la AUC reportada por los notebooks usa BAJA+2 como positivo. Ganancia y AUC responden preguntas distintas. La ganancia usa +1.072.500 por BAJA+2 contactado y −27.500 por el resto; N se elige en agosto y se conserva para los meses posteriores. M significa millones de las unidades monetarias del ejercicio.

La regla principal evalúa ganancia, no mejora de AUC. Las comparaciones posteriores ya conocen septiembre y octubre: son exploratorias. No corresponde ordenar todas las variantes en una única tabla de ganancia sin respetar sus distintos controles, ventanas y reglas de selección.

## Preparación y prueba mínima de los notebooks 01 y 02

El crudo contiene 4.707.495 filas, 154 columnas y 185.094 clientes. El corte 2019 tiene 1.563.565 filas, 146.623 clientes y cero claves duplicadas. El 01 construye la clase después de cortar a diciembre de 2019 y detecta 23 casos de variable/mes roto: 17 por regla y 6 manuales. Después se identificaron dos roturas Master adicionales en octubre. El catálogo usa información retrospectiva de calidad; no es un detector estrictamente disponible a cada fecha.

La cobertura explica la adaptación de ventana: marzo dispone como máximo de dos meses anteriores; lag6 queda vacío en todo marzo–junio. El principal se limita a mayo–junio para comparar historia hasta cuatro meses; el 08 explora explícitamente conservar marzo–abril aun con historia parcial.

| Prueba mínima | Semillas | AUC agosto media | Ganancia meseta agosto media M |
|---|---:|---:|---:|
| A | 5 | 0.907642 | 195.0108 |
| LT4 | 5 | 0.909006 | 198.5370 |

Fue una prueba técnica y exploratoria sobre validación, con 370 árboles. No reemplaza las corridas posteriores de 296 árboles ni ofrece una evaluación independiente.

## Experimento principal de los notebooks 03 y 04

Se optimizó A una vez y se congelaron sus parámetros para diez configuraciones. L3/L4 añaden lags y deltas; T3/T4 añaden tendencias; LT combina ambas. La ventana de T3 va de t−3 a t (cuatro fotos), y T4 de t−4 a t (cinco). La historia adicional se adapta a montos, conteos, banderas y estados, excluyendo fechas y edad/antigüedad de esas extensiones. Los controles mantienen lag/delta1/2 de todas las variables.

Regla: Wilcoxon pareado exacto entre diez semillas y Holm para seis contrastes; diferencia media positiva en octubre y no negativa en septiembre. La banda de N entre 3.000 y 6.000 verifica la dirección. Ninguna variante pasó la regla.

| Variante frente a A | Δ ganancia septiembre M | Δ ganancia octubre M | p Holm | Semillas favorables octubre | Pasa regla |
|---|---:|---:|---:|---:|---|
| L3 | +4.6750 | +3.4650 | 0.2422 | 6/10 | No |
| L4 | +6.0225 | +5.0325 | 0.1465 | 9/10 | No |
| T3 | +5.0600 | +3.6300 | 0.1484 | 9/10 | No |
| T4 | +4.1525 | +3.6025 | 0.2422 | 8/10 | No |
| LT3 | +6.1875 | +5.4175 | 0.0703 | 8/10 | No |
| LT4 | +5.1150 | +5.2250 | 0.1484 | 9/10 | No |

AUC media de cada configuración (la regla anterior se aplica a ganancia):

| Configuración | AUC agosto media | AUC septiembre media | AUC octubre media |
|---|---:|---:|---:|
| A | 0.907533 | 0.909347 | 0.922030 |
| L3 | 0.907012 | 0.910674 | 0.922116 |
| L4 | 0.908105 | 0.910558 | 0.921909 |
| T3 | 0.907416 | 0.910340 | 0.922211 |
| T4 | 0.908935 | 0.910494 | 0.922166 |
| LT3 | 0.907458 | 0.911026 | 0.922776 |
| LT4 | 0.908244 | 0.910841 | 0.921871 |
| A-ranking | 0.906664 | 0.907995 | 0.920734 |
| LT4-ranking | 0.908092 | 0.907763 | 0.920643 |
| A-consigna | 0.910871 | 0.911917 | 0.923561 |

A-consigna frente a A dio +9.1850 M en septiembre y +3.9050 M en octubre. Esto muestra la importancia práctica de conservar meses, pero mezcla ventana y ajuste: no aísla solo historia.

Los rankings simples también se ejecutaron: LT4-ranking mejora frente a A-ranking, pero ese control era débil. Su superioridad sobre un control rankeado no demuestra que supere al nominal. La ausencia de significancia no prueba efecto nulo.

## Exploraciones del notebook 05

Se promediaron probabilidades de diez semillas y se recalculó N en agosto. Las diferencias frente al ensamble de A son:

| Ensamble | Δ ganancia septiembre M | Δ ganancia octubre M |
|---|---:|---:|
| L3 | +8.9375 | +2.3375 |
| L4 | +13.6950 | +5.9950 |
| T3 | +12.1550 | +5.5550 |
| T4 | +5.6925 | +3.4925 |
| LT3 | +7.1225 | +13.7225 |
| LT4 | +12.7875 | +7.2875 |
| A-consigna | +12.7875 | +2.8875 |

Son resultados posteriores al principal. Los intervalos de bootstrap de clientes pueden ser amplios; no se interpreta una diferencia puntual en N como confirmación. El ensamble de LT3, por ejemplo, da una ventaja grande en el corte de octubre, pero menor en la banda de cortes.

Segundas diferencias: D2 añade la segunda diferencia sobre A; LT3D2 la añade sobre LT3.

| Variante | Control | Mes | Δ ganancia M | Δ banda M |
|---|---|---|---:|---:|
| D2 | A | 201909 | -0.8525 | +0.2505 |
| D2 | A | 201910 | +0.7975 | -0.6251 |
| LT3D2 | LT3 | 201909 | -2.1725 | -1.0348 |
| LT3D2 | LT3 | 201910 | -1.6225 | -0.1014 |

No aparece una mejora clara de segundas diferencias: D2 cambia de signo entre meses y LT3D2 pierde en ambos. No se retiran resultados negativos del registro.

## Ratios y rachas del notebook 06

AC_R agrega ratio3 = actual/promedio(actual, lag1, lag2); AC_Z agrega racha de ceros en tres fotos; AC_RZ combina ambas. Se aplican a 129 variables de montos/conteos y requieren observaciones completas, conservando NaN cuando no se puede calcular. Se usa marzo–junio, con el ajuste heredado de A.

Diferencias de la media entre semillas:

| Variante | Control | Δ ganancia septiembre M | Δ ganancia octubre M | Δ banda octubre M |
|---|---|---:|---:|---:|
| AC_R | AC | +3.1625 | +3.4925 | +2.4163 |
| AC_Z | AC | -3.1350 | -3.0250 | -0.6157 |
| AC_RZ | AC | +4.5925 | +1.2925 | +1.4731 |

Diferencias de ensambles:

| Variante | Control | Δ ganancia septiembre M | Δ ganancia octubre M | Δ banda octubre M |
|---|---|---:|---:|---:|
| AC_R | AC | +0.8525 | +9.6525 | +2.2004 |
| AC_Z | AC | -5.5825 | +1.0175 | -0.9391 |
| AC_RZ | AC | +4.2075 | +5.3075 | +1.0454 |

AUC media:

| Configuración | AUC agosto media | AUC septiembre media | AUC octubre media |
|---|---:|---:|---:|
| AC | 0.910871 | 0.911917 | 0.923559 |
| AC_R | 0.909484 | 0.912501 | 0.924026 |
| AC_Z | 0.910171 | 0.912089 | 0.923400 |
| AC_RZ | 0.910304 | 0.912552 | 0.923682 |

Ratio3 mostró señal de ganancia; las rachas solas fueron desfavorables en la media y la banda. La combinación no domina de manera uniforme. Estas observaciones no se convierten automáticamente en una mejora de AUC ni en una validación independiente.

## Optimización del control en el notebook 07

Se optimizaron parámetros específicamente para marzo–junio (ACO): trial 38, 339 árboles. La mejor AUC de agosto de la búsqueda fue 0,914852804, frente a 0,909510031 del ajuste anterior sobre A. No son medias ni estimaciones independientes: son valores de selección sobre ventanas y búsquedas distintas.

| Variante | Control | Δ ganancia septiembre M | Δ ganancia octubre M | Δ banda octubre M |
|---|---|---:|---:|---:|
| ACO | AC | -0.7150 | -5.8850 | -4.7824 |

AUC media de ACO:

| Configuración | AUC agosto media | AUC septiembre media | AUC octubre media |
|---|---:|---:|---:|
| ACO | 0.911657 | 0.909938 | 0.920699 |

La optimización mejora AUC de validación pero la ganancia posterior no mejora frente a AC: aproximadamente −5,9 M de media en octubre. No se elige retrospectivamente el ajuste anterior por ese resultado. Las cuatro familias nuevas usan el ajuste ACO como control congelado y apuntan específicamente a AUC.

## Historia sin quitar meses en el notebook 08

ACL3/ACL4 agregan lags y tendencias sobre marzo–junio; ACH agrega historia curada sobre 30 variables seleccionadas por importancia de entrenamiento: ratio3, z frente al pasado, relación al máximo previo y ranking mensual del ratio. M_LT3 y M_LT4 mezclan AC con LT3/LT4; M_H mezcla ACH con LT3. Por semilla, las mezclas se comparan contra AC2 (mezcla de dos semillas de AC); los ensambles se comparan contra AC. Por eso no deben confundirse los controles.

Diferencias de la media entre semillas:

| Variante | Control | Δ ganancia septiembre M | Δ ganancia octubre M | Δ banda octubre M |
|---|---|---:|---:|---:|
| M_LT3 | AC2 | -1.5400 | +1.6500 | +0.9574 |
| M_LT4 | AC2 | -1.8150 | +3.9050 | +2.5678 |
| ACL3 | AC | +0.8525 | +3.2725 | +3.3287 |
| ACL4 | AC | -0.6875 | +0.7425 | +2.3455 |
| ACH | AC | +1.5675 | +5.1975 | +5.4438 |
| M_H | AC2 | +1.7050 | +6.7650 | +5.2494 |

Diferencias de ensambles:

| Variante | Control | Δ ganancia septiembre M | Δ ganancia octubre M | Δ banda octubre M |
|---|---|---:|---:|---:|
| M_LT3 | AC | -4.5100 | +2.0900 | +0.8999 |
| M_LT4 | AC | -3.9050 | +7.0950 | +2.7945 |
| ACL3 | AC | +0.7150 | +7.3150 | +4.5441 |
| ACL4 | AC | -4.7850 | +2.9150 | +2.8371 |
| ACH | AC | -3.9325 | +10.3675 | +6.1250 |
| M_H | AC | +1.4025 | +6.9025 | +5.7082 |

AUC media:

| Configuración | AUC agosto media | AUC septiembre media | AUC octubre media |
|---|---:|---:|---:|
| AC | 0.910871 | 0.911917 | 0.923559 |
| AC2 | 0.911351 | 0.912348 | 0.923932 |
| ACL3 | 0.910028 | 0.913537 | 0.923442 |
| ACL4 | 0.910908 | 0.913573 | 0.923894 |
| ACH | 0.909973 | 0.913955 | 0.924312 |
| M_LT3 | 0.910602 | 0.912868 | 0.924332 |
| M_LT4 | 0.911116 | 0.912850 | 0.923980 |
| M_H | 0.910334 | 0.914065 | 0.924875 |

Hay señales favorables en octubre, especialmente ACH y ciertas mezclas, pero las diferencias y la banda de septiembre son menos favorables. Es evidencia exploratoria dependiente del mes, sin nueva confirmación ciega.

## Código del notebook 09 y propuestas sin resultado publicado

El 09 implementa cuatro bloques sobre ACH: eventos de pérdida de productos (ACE), ratios Visa/Master (ACR), historia de un puntaje base calculado con pliegues por cliente (ACP) y hojas de Random Forest (ACF). Incluye una combinación (ACX) y un control de ruido (ACK). No hay tablas 09 publicadas en el snapshot; no se afirma ni éxito ni fracaso de esas variantes.

El segundo PDF contiene además un protocolo de 20 semillas, resúmenes trimestrales, inactividad, ratios personales, rankings con cero fijo, selección por canaritos y reoptimización final. Es una propuesta con código, no evidencia de que se haya ejecutado íntegramente. Algunas familias se solapan con 06/08/09, pero no deben contabilizarse como corridas adicionales sin sus salidas.

También se preparó un script de disponibilidad de historia (foto ausente, nulo y cero observado), pero se priorizaron otras hipótesis antes de ejecutarlo. El baseline local de 30 trials es otra implementación, con decisiones distintas de etiqueta de AUC y predictores; no hay una corrida suya que se incorpore como resultado en este registro.

## Réplicas y comparación complementaria en Google Cloud

La preparación en la VM pasó controles de filas, clases, duplicados y relectura de parquet. A y A-consigna coincidieron con los valores publicados a la precisión mostrada para las primeras dos semillas. La diferencia de entorno registrada es pandas 2.3.3 frente a 2.2.2; el resto de versiones científicas principales coincide. Esta etapa verifica ejecución, no constituye una mejora.

También se completó una ablación sin historia (152 columnas) frente a con historia (760), en marzo–junio, con parámetros del 07 y diez semillas. Es contexto sobre el aporte del baseline, no una mejora sobre la referencia de la cátedra.

| Modelo | AUC agosto media | Semillas |
|---|---:|---:|
| sin_historia | 0.905180 | 10 |
| con_historia | 0.911657 | 10 |

Diferencia media con − sin: +0.006477 AUC; 10/10 semillas favorables. El ajuste se eligió para con_historia: la ablación con parámetros fijos no compara óptimos independientes.

## Síntesis del trabajo previo y preguntas abiertas

- El experimento principal no demostró mejora bajo su regla de ganancia; sí hubo diferencias medias favorables frente al control adaptado A.
- Recuperar meses de entrenamiento fue tan importante como extender la historia; no evaluar las features sin identificar el control.
- Ratio3, historia curada y mezclas dejaron señales exploratorias, no una combinación ganadora confirmada en todos los meses y métricas.
- Segundas diferencias y rachas solas no mostraron una ventaja consistente en los contrastes reportados.
- Optimizar AUC no garantiza aumentar ganancia en otro mes.
- Falta resultado publicado del 09 y del protocolo completo del segundo PDF. No confundir ausencia de tabla con resultado negativo.
- Nuestro aporte nuevo evalúa representaciones específicas sobre el control ACO, con objetivo AUC y sin abrir octubre. Sus resultados al corte siguen a continuación.

## Serie nueva de cuatro familias

## Diseño que mantuvimos fijo

| Elemento | Definición |
|---|---|
| Dataset | competencia_02_crudo.csv.gz; parquet 2019 preparado y verificado |
| Entrenamiento | Marzo–junio, 506.871 filas, sin sampling |
| Etiqueta de entrenamiento | BAJA+1 o BAJA+2 frente a CONTINUA |
| Evaluación | Agosto de 2019, 131.775 filas; AUC positiva BAJA+2 |
| Control | 760 predictores, sin ID ni foto_mes como features |
| Ajuste | Parámetros del 07, 339 árboles, max_bin 31, bagging_freq 1 |
| Semillas | Diez por brazo; iguales entre baseline y variante |
| Recursos | Ocho hilos; cuatro familias ejecutadas secuencialmente |
| Faltantes | NaN; mismas filas en ambos brazos; saneamiento antes de calcular historia |
| Meses cargados | Enero–agosto; no se consultó octubre en estas pruebas |

## Qué probamos

| Familia | Nuevas columnas | Pregunta |
|---|---:|---|
| Historia reciente | 387 | Dar mayor peso a las fotos recientes: media 4:2:1 y comparación con pasado ponderado 2:1. |
| Cambios relativos | 258 | Medir cambios proporcionales simétricos de uno y dos meses, con valores finitos acotados entre −1 y 1. |
| Persistencia y reversión | 516 | Separar dos caídas, dos subidas, reversión y aceleración relativa en tres fotos. |
| Rankings con cero fijo | 365 | Comparar la posición del cliente dentro del mes y signo, y su cambio en uno y dos meses. |

Las tres primeras familias transforman información ya contenida en las tres fotos; buscamos una representación que LightGBM aproveche mejor. Los rankings incorporan además la distribución contemporánea del conjunto de clientes. Las fórmulas exactas se fijaron antes de correr en docs/experimentos_historia.md.

## Resultados al corte

Las medias siguientes usan únicamente semillas emparejadas. Si hay tres variantes y diez baselines, se comparan esos tres pares, no medias de tamaños diferentes. La diferencia está en unidades de AUC; +0,001 equivale a pasar de 0,912 a 0,913.

| Familia | Estado | Pares | AUC control | AUC variante | Diferencia media | A favor |
|---|---|---:|---:|---:|---:|---:|
| Historia reciente | Completo | 10/10 | 0.911657 | 0.910525 | -0.001132 | 3/10 |
| Cambios relativos | Parcial | 3/10 | 0.912142 | 0.910844 | -0.001299 | 1/3 |
| Persistencia y reversión | Pendiente | 0/10 | — | — | — | — |
| Rankings con cero fijo | Pendiente | 0/10 | — | — | — | — |

### Historia reciente

| Semilla | AUC control | AUC variante | Diferencia |
|---|---:|---:|---:|
| 118147 | 0.910461455 | 0.908168607 | -0.002292848 |
| 161093 | 0.909832201 | 0.908692345 | -0.001139856 |
| 294103 | 0.914852804 | 0.910844762 | -0.004008042 |
| 312773 | 0.911760323 | 0.910921383 | -0.000838940 |
| 330679 | 0.910671646 | 0.911928821 | +0.001257175 |
| 342929 | 0.911741449 | 0.911399274 | -0.000342174 |
| 431077 | 0.911529503 | 0.910106314 | -0.001423189 |
| 511579 | 0.911200366 | 0.911532324 | +0.000331958 |
| 567529 | 0.912476865 | 0.909343884 | -0.003132981 |
| 677561 | 0.912040962 | 0.912311328 | +0.000270366 |

AUC del ensamble: control 0.913309; variante 0.912135; diferencia -0.001174.

Lectura descriptiva: la media entre semillas no mejora el control. Esto no demuestra generalización a otros períodos.

### Cambios relativos

| Semilla | AUC control | AUC variante | Diferencia |
|---|---:|---:|---:|
| 161093 | 0.909832201 | 0.910612566 | +0.000780365 |
| 294103 | 0.914852804 | 0.910919377 | -0.003933427 |
| 342929 | 0.911741449 | 0.910998918 | -0.000742531 |

**Avance parcial:** 3/10 variantes y 10/10 baselines. No cerrar una conclusión ni detener la prueba por estos resultados.

## Qué resultó y qué no podemos afirmar todavía

Las familias pendientes no tienen un resultado negativo: todavía no fueron evaluadas. Las filas parciales muestran avance del entrenamiento, no una conclusión final. Cuando estén completos los diez pares, reportaremos conjuntamente la diferencia media, la dirección por semilla y el cambio en AUC del ensamble.

No se elegirá una familia por una semilla favorable. Tampoco se confundirá una mejora de ganancia económica de antecedentes con una mejora de AUC en esta comparación.

## Decisiones y siguientes pasos

- Terminar las cuatro familias y conservar también resultados negativos.
- Ajustar el decaimiento solo si historia reciente presenta una señal favorable al completar diez semillas, considerando media, consistencia y ensamble. No se fijó un umbral numérico formal: cualquier criterio nuevo debe registrarse antes de la búsqueda, no reconstruirse como si hubiera sido predefinido.
- Si se habilita esa búsqueda, seleccionar alfa dentro de una partición temporal interna al bloque de entrenamiento, respetando las etiquetas a dos meses; reentrenar marzo–junio y evaluar la elección en agosto. No usar agosto para elegir alfa.
- No modificar la cola ni los pesos actuales a partir de resultados parciales.

## Límites de la evidencia

Agosto ya se usó para optimizar el baseline y discutir otras variantes. Sigue siendo validación exploratoria, aunque una búsqueda posterior de alfa use otro bloque. Los parámetros del 07 favorecen potencialmente al baseline: aquí medimos el efecto de agregar features con ese ajuste fijo, no modelos optimizados individualmente. Las diez semillas comparten clientes y mes; su dispersión no mide incertidumbre entre períodos. Comparar cuatro familias introduce selección múltiple. El catálogo de roturas fue construido retrospectivamente y no representa una política estrictamente disponible en tiempo real.

## Trazabilidad

Cada experimento conserva config.json con hashes SHA-256, versiones y semillas; metrics.csv con AUC por modelo; summary.json con el ensamble; extra_coverage.csv con faltantes; y status.json al completar. El paquete para tutoría no contiene datos individuales. El notebook notebooks/tutoria_historia.ipynb permite revisar estas tablas y visualizar las diferencias.

Corrida: familias_c9930bd. Código desplegado: c9930bd. Rama: feat/historia-transformaciones. El informe y el notebook pueden evolucionar sin modificar el código de la corrida en curso.
