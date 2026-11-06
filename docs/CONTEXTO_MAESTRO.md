# Contexto maestro del experimento colaborativo

Actualizado al cierre del 6 de noviembre de 2026, hora de Buenos Aires. Este archivo permite retomar el trabajo después de reiniciar la computadora o abrir otra conversación. No reemplaza las tablas ni el código: registra el objetivo, acuerdos y estado operativo.

## Leer primero al retomar

1. Este archivo.
2. `docs/RETOMAR_20261107.md`, que contiene el checkpoint exacto y los pasos pendientes.
3. Los protocolos `docs/repeticion_cambios_relativos_20semillas.md` y `docs/repeticion_rankings_20semillas.md`.
4. Consultar la VM solo cuando el usuario quiera continuar: quedó confirmada como **TERMINATED**, sin procesos en ejecución y sin reanudación automática.

Frase sugerida para una nueva conversación: «Leé docs/CONTEXTO_MAESTRO.md y docs/RETOMAR_20261107.md y retomemos desde ahí».

## Objetivo y preferencias de Tomás

Trabajo práctico colaborativo DMEyF 2026, tema feature engineering histórico, con Clara y Ezequiel; tutor Alejandro Bolaños. Queremos encontrar representaciones de historia que mejoren el baseline de la cátedra, medir tanto AUC como ganancia y presentar el trabajo completo del grupo en tutorías con precisión y tono informal.

- Restringirse al dataset disponible y a la consigna; noviembre/diciembre de 2019 están reservados para dashboard.
- La reproducibilidad ya se verificó: no repetir réplicas como si fueran nuevos aportes.
- Experimentos en archivos independientes, dentro de una rama feature separada.
- Editar localmente; ejecutar entrenamientos en Google Cloud. Sincronizar versiones identificables y conservar resultados separados.
- Los informes deben cubrir lo hecho por compañeros y por Tomás, incluidos negativos, propuestas sin ejecución y corridas pendientes. No informar solo nuestras cuatro familias.
- Respetar costos: detener la VM cuando Tomás lo pida. Cerrar SSH o apagar la computadora local no apaga la VM.
- Tomás autorizó respaldar en su bucket también las predicciones individuales y claves de clientes. Esos datos no deben ir a GitHub; al repositorio solo métricas y metadatos agregados.
- La última instrucción fue guardar el contexto **localmente** antes de reiniciar la computadora. No requiere encender la VM ni subir esta actualización a la nube.

## Repositorio y ramas

Raíz local: `C:/Users/tomas/OneDrive/Documents/Maestria/DMEyF/dmeyf2026/Tp_experimentos`.

Remoto: `https://github.com/ezequielabregu/DMEyF-2026-experi-colab-feature_historico.git`.

Rama activa: `feat/historia-transformaciones`. No se mezcló con main ni se hizo push de esta rama durante esta sesión. Commits locales relevantes:

| Commit | Contenido |
|---|---|
| 4870c13 | Cuatro experimentos independientes |
| c9930bd | Cola original y notebook de tutoría; código congelado de los experimentos de diez semillas |
| 5aed7bf | Primer informe grupal completo con el snapshot antiguo |
| 276a1b9 | Reanudación del 6/11, reutilizando historia reciente completa |
| fde77e4 | Evaluación económica de agosto |
| b9af35b | Ganancia en el reporte principal |
| bcd853b | Repetición de cambios relativos con veinte semillas |
| 38357d7 | Rankings con veinte semillas |
| 9cb0b78 | Corte controlado y checkpoint para el 7/11 |

También hay cambios y archivos previos no versionados, incluidos PDFs originales. Preservarlos: no usar reset, clean ni restore indiscriminados para dejar el árbol limpio.

## Infraestructura y datos

- Proyecto: `proj-uba-261025192707274`.
- VM: `to-256ram-12vcpu-20261102-233922`.
- Zona: `northamerica-northeast2-a`.
- Usuario remoto: `tomas_henseler`.
- Recursos: 12 CPU, aproximadamente 256 GB RAM; disco ampliado de 70 a 150 GB.
- Bucket: `gs://tomas_henseler_buckito2026`.
- La CLI local está autenticada y se pudo usar `gcloud.cmd compute ssh/scp`. En PowerShell usar `gcloud.cmd`; `gcloud.ps1` encontró restricciones de ejecución. Pasar siempre proyecto y zona explícitos.
- La IP externa puede cambiar al reiniciar la VM; usar su nombre, no depender de la IP antigua. Nunca guardar claves o credenciales en el resumen.

URL del crudo: `https://storage.googleapis.com/open-courses/dmeyf2026-9c6f/competencia_02_crudo.csv.gz`. Documentada también en `docs/dataset.md`.

Crudo remoto: `~/datasets/competencia_02_crudo.csv.gz`, 679 MB comprimidos; gzip verificado. Original: 4.707.495 filas, 154 columnas, 185.094 clientes. Corte 2019: 1.563.565 filas y cero claves duplicadas; el pipeline de preparación pasó controles de clase y relectura.

Checkout de compañeros en VM: `~/experimento_historia`, fijado inicialmente a 3b44f21. Entorno: `~/experimento_historia/.venv`, Python 3.14.4, pandas 2.3.3, numpy 2.4.3, LightGBM 4.7.0, DuckDB 1.5.5, scikit-learn 1.8.0. Pandas 2.2.2 del requirements original falló al compilar en Python 3.14; se sustituyó en requirements-vm.txt. No reinstalar sin necesidad.

Parquet preparado: `~/experimento_historia/data/base_2019.parquet` (unos 186 MB decimales). Reportes de preparación: `resultados_replica/`. Los entornos grandes y datasets de `/home/ds` pertenecen al template; no se borraron.

## Definiciones científicas acordadas

El baseline de la cátedra ya tiene historia: 152 originales más lag1, lag2, delta1 y delta2 de todas las variables predictoras, total 760. ID, foto_mes y clase no son predictores en los notebooks de compañeros. Los lags buscan calendario exacto por cliente y conservan NaN.

Controles diferentes:

- A: entrenamiento mayo–junio; control adaptado del principal para historia hasta cuatro meses.
- A-consigna/AC: marzo–junio, pero hereda parámetros de A; AC incorpora corrección de dos roturas Master de octubre.
- ACO: marzo–junio con búsqueda propia del notebook 07; control de nuestras cuatro familias.
- ACH: AC más historia curada sobre 30 variables, 120 features adicionales. Es el control del banco posterior por clientes, no el baseline de la cátedra.

Nuestra serie: marzo–junio full (506.871 filas), validación agosto (131.775 filas). Entrenar positivo BAJA+1 o BAJA+2; AUC y ganancia positiva estricta BAJA+2. Parámetros ACO del 07 congelados, 339 árboles, max_bin=31, bagging_freq=1, ocho hilos. No optimizar nuevamente ni abrir octubre sin un protocolo nuevo explícito.

Ganancia del ejercicio: +1.072.500 por BAJA+2 contactado y −27.500 por resto. Reportar banda inclusiva N=3.000–6.000 y corte común N=4.000, sin elegir el N que más favorezca a cada variante. La evaluación económica fue añadida después de mirar algunas AUC: es secundaria y exploratoria en agosto, no una prueba independiente ni comparable directamente con septiembre/octubre o con el banco por clientes.

No confundir media de métricas de semillas con métrica de un ensamble de probabilidades. No interpretar diez semillas como diez meses independientes. No agregar semillas de a poco hasta conseguir p favorable. Más semillas reducen incertidumbre del algoritmo, no la temporal.

## Qué hicieron los compañeros y actualización importante de fuentes

Primero se revisó la rama `ezequiel/etapa-1` en 3b44f21 (hasta 09 y sin tablas del 09 en aquel snapshot). Un PDF nuevo mostró avances; se hizo fetch y se obtuvo **6cf189c**, con notebooks y resultados hasta 14. Usar la fuente nueva para hablar del estado actual. Tablas congeladas: `resultados/antecedentes_6cf189c` con hashes. El código nuevo completo está exportado en `tmp/ezequiel_6cf189c`, no mezclado con nuestra rama.

- 01–02: clase/calidad/cobertura y ensayo técnico A–LT4.
- 03–04: lags/deltas3/4, tendencias3/4, combinaciones, rankings y A-consigna. Ninguna de las seis variantes principales pasó la regla de ganancia frente a A.
- Regla propia del grupo, no exigida por la consigna: diferencia positiva en octubre, no negativa en septiembre, y Wilcoxon exacto con Holm <0,05 en seis contrastes. Todas cumplieron dirección y fallaron Holm. p ajustados: L3 0,2422; L4 0,1465; T3 0,1484; T4 0,2422; LT3 0,0703; LT4 0,1484. Diez pares por contraste.
- 05: ensambles y segundas diferencias; no mejora consistente de estas últimas.
- 06: ratio3, rachas de cero y combinación; ratio3 prometedor en ganancia, rachas solas generalmente desfavorables.
- 07: ajuste propio de marzo–junio; mejor AUC de selección sin mejor ganancia posterior.
- 08: historia curada, conservar meses aun con historia parcial y mezclas.
- 09–11: eventos, ratios de tarjetas, puntajes actuales/pasados, hojas RF y particiones alternativas de clientes. Ahora sí tienen tablas publicadas.
- 12: sin historia y ventanas más recientes; historia básica aporta unos 20 M en banda por mes de septiembre/octubre.
- 13: banco exploratorio por cinco grupos de clientes, marzo–agosto, dos semillas; inestabilidad, quiebre reciente, toda la historia y ranking de cambios. Misma época de calendario entre entrenamiento y evaluación; no valida meses futuros.
- 14: combinación de cuatro bloques sobre ACH, cinco semillas. +1,9263 M/mes, intervalo reportado total 0,0876–3,7651 M; señal intermedia según su criterio. Inestabilidad sola +2,0047 M con dos semillas. No afirmar que la combinación supera a la mejor individual ni que es confirmación temporal.

Hay solapamientos entre nuestras familias y las recientes del 13 (persistencia/quiebre y rankings), aunque cambian fórmulas, control, métrica y evaluación. No afirmar novedad sin aclararlo. Las preguntas para Alejandro todavía no tienen respuestas: no completarlas inventando su opinión. Los diagnósticos macro y segmentos del PDF requieren sus tablas fuente para auditarlos.

## Nuestras cuatro familias y resultados finales con diez semillas

Archivos independientes en `scripts/historia/`:

- `exp_historia_reciente.py`: 387 features, media 4:2:1, desviación y cambio relativo frente al pasado 2:1; 129 variables.
- `exp_cambios_relativos.py`: 258 features, `(actual-previo)/(abs(actual)+abs(previo))`, lag1/2, dos ceros dan cero y faltantes siguen NaN; 129 variables.
- `exp_persistencia.py`: 516 features, dos caídas, dos subidas, reversión y aceleración relativa; 129 variables.
- `exp_rankings_cero_fijo.py`: 365 features sobre 73 montos, percentil por mes y signo con cero fijo, más sus lags/deltas.

Los operadores comunes y controles pasaron cinco tests sintéticos; la evaluación económica pasó dos tests más. Las claves se alinean por cliente/mes y se recalculan AUC para verificar consistencia antes de computar dinero.

| Modelo | AUC media | Δ AUC | Ganancia banda media M | Δ ganancia banda M |
|---|---:|---:|---:|---:|
| Baseline ACO | 0,911657 | — | 205,7974 | — |
| Historia reciente | 0,910525 | −0,001132 | 206,5551 | +0,7577 |
| Cambios relativos | 0,910749 | −0,000908 | 210,4979 | +4,7005 |
| Persistencia | 0,911887 | +0,000231 | 206,4581 | +0,6607 |
| Rankings con cero fijo | 0,911046 | −0,000611 | 208,0465 | +2,2491 |

Cambios relativos: 8/10 semillas favorables en banda; Δ banda ensamble +5,4736 M, Δ N4000 medio +4,18 M y ensamble +11 M. Rankings: 7/10 favorables en banda y Δ banda ensamble +2,3884 M. Persistencia es la única mejora media de AUC, pequeña, con 5/10 semillas favorables. Resultados exploratorios de agosto; no declarar una ganadora confirmada.

Las cuatro familias de diez semillas y la evaluación económica final están completas en la VM: `exp/familias_20261106` y `exp/economia_20261106_final`. Paquete final: `gs://tomas_henseler_buckito2026/exp/familias_20261106/tutoria_con_ganancia.zip`. También se descargó a `tmp/tutoria_final_10semillas.zip`; puede faltar extraerlo/regenerar reportes para reflejar el último resultado de rankings.

## Estado exacto de las ampliaciones de veinte semillas

Se solicitaron veinte semillas **totales** por brazo para cambios relativos y rankings, no veinte adicionales. La secuencia extiende los mismos primos con RNG 979201 y conserva las diez originales. Mantener datos, parámetros, fórmulas y métricas. Las nuevas diez son repeticiones del algoritmo, no nuevas observaciones temporales.

- Cambios relativos: `~/historia_relative20_20261106`, salida `~/experimento_historia/exp/relativos20_20261106`. Se cortó al guardar **10/20 baselines y 0/20 variantes**. Estado `interrupted_at_checkpoint`. No hay aún resultados de veinte pares.
- Rankings: `~/historia_rank20_20261106`, salida `~/experimento_historia/exp/rankings20_20261106`. Se detuvo la cola en espera antes de iniciar. Estado `not_started_user_shutdown`.
- Checkpoint respaldado completo (predicciones/claves incluidas): `gs://tomas_henseler_buckito2026/backup/corte_20261106/`.
- Runners: `run_relative20.py` y `run_rankings20.py`. Actualmente exigen carpeta nueva y **no reanudan por semilla**. No lanzarlos a ciegas tras encender la VM.
- Próximo trabajo: implementar reanudación validada por hashes, claves, columnas, semillas y AUC para aprovechar los diez baselines guardados; luego calcular los faltantes y las variantes, sin mezclar artefactos incompatibles. Conservar el checkpoint original.

La VM quedó apagada; todos los procesos se detuvieron. No sigue corriendo nada ni habrá arranque automático al encenderla.

## Otras decisiones

- Ajustar los pesos de historia reciente solo si la prueba fija mostraba señal favorable en AUC. No la mostró; no iniciar la búsqueda de alfa por ahora. Si se retomara, elegir alfa con partición temporal interna y evaluar en agosto, declarando que LightGBM ya se ajustó sobre agosto.
- Se conversó un gráfico de **autocorrelación**, no de correlación entre modelos. No se implementó. Propuesta: unas diez variables de negocio, cruces calendario dentro de cliente, solo entrenamiento y conteos de pares por lag; distinguir persistencia de niveles y de cambios. No concatenar clientes como una única serie.
- La comparación sin/con historia de diez semillas ya terminó: Δ AUC +0,006476751, 10/10 favorables. Es contexto sobre el baseline, no una mejora sobre él; no volver a priorizar esa ablación.
- El script de disponibilidad de historia se preparó pero no se ejecutó; no presentarlo como experimento realizado.

## Documentos y archivos para continuar

| Archivo | Función |
|---|---|
| docs/RETOMAR_20261107.md | Estado operativo más reciente y lista de siguientes pasos |
| docs/informe_experimentos_historia.html y .md | Reporte principal abierto por el usuario; ya sigue la estructura del PDF nuevo y contiene ganancia |
| docs/estado_grupal_para_tutoria.html y .md | Versión de la plantilla de Ezequiel completada con el trabajo grupal |
| notebooks/tutoria_historia.ipynb | Compatible con Colab, con outputs reales; tiene tabla y gráfico de ganancia |
| scripts/historia/complete_tutoria_template.py | Generador actual del reporte usando fuentes hasta 14 |
| scripts/historia/build_report.py y group_history_report.py | Generador anterior de detalle; no usar sin revisar fuentes porque parte de 3b44f21 |
| scripts/historia/evaluate_profit.py | Evaluación económica secundaria de probabilidades existentes |
| scripts/historia/export_results.py | Exporta únicamente tablas/metadatos agregados, opcionalmente ganancia |
| docs/plantilla_tutoria_fuentes.md | Cambio de fuente 3b44f21 a 6cf189c |
| docs/evaluacion_economica_historia.md | Criterios económicos fijados y primer corte |
| docs/experimentos_historia.md | Protocolo de las cuatro familias |

PDFs originales en raíz: informe_experimento.pdf; protocolo largo con nombre que empieza «bueno ordenamos»; nuevo «Experimento feature_historico dónde estamos (1).pdf». El último tiene trece páginas y estructura problema/baseline → pruebas → obstáculos → preguntas al tutor → glosario. No se modificaron los originales. No se creó un PDF de salida nuevo: las versiones completadas son HTML imprimible y Markdown editable.

El notebook conserva advertencias de fuente antigua en parte de los antecedentes. Pendiente unificarlo por completo con 6cf189c y regenerar tablas/gráficos de las cuatro familias con el paquete final, sin outputs parciales obsoletos. No llamar a una copia local de .ipynb un Colab ya publicado: el archivo está listo para subir/abrir, sin link nativo publicado en esta sesión.

## Respaldo y pendientes locales

Se hicieron backups en bucket: `backup/reanudacion_20261105/` y `backup/reanudacion_20261106/`, con ZIP del trabajo y bundle de Git. La última copia local de trabajo anterior a este resumen está en `tmp/reanudacion_20261106.zip` y el bundle homónimo. Los datasets y predicciones viven en VM/bucket, no en el repositorio local.

Esta actualización de contexto se guarda solo local por pedido del usuario. El reinicio de la computadora no requiere ninguna acción en la VM detenida. Al retomar no asumir que el chat conserva todo: usar estos archivos y verificar el estado real antes de ejecutar.
