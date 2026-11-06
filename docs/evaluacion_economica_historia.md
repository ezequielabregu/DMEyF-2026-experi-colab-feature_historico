# Evaluación económica de nuestras cuatro familias

Decisión del 6/11/2026, después de mirar parte de las AUC y antes de calcular estas ganancias. Es un análisis secundario exploratorio, no una regla económica predefinida antes de todos los datos.

Se reutilizan las probabilidades de agosto ya guardadas; no se reentrena ni se abren meses adicionales. Positivo económico: solo BAJA+2. Resultado por contacto: +1.072.500 si es BAJA+2 y −27.500 en otro caso, incluidos BAJA+1.

Métricas fijadas para todos los modelos: ganancia promedio de la curva acumulada entre N=3.000 y N=6.000 inclusive; ganancia y BAJA+2 capturados en N=4.000, presupuesto común. No se elige el mejor N por variante ni se aplica un umbral de 2,5 % a probabilidades entrenadas sobre ambas bajas sin calibración.

Se reportan diez semillas pareadas y ensamble, con diferencia contra el mismo baseline ACO. Las claves se unen por cliente/mes, y la AUC se recalcula y debe coincidir con la corrida para detectar desalineamientos. Empates de probabilidad usan orden estable de las claves guardadas. Se registran hashes de fuente y predicciones; solo las tablas agregadas se descargan al repositorio.

La ganancia de agosto comparte datos con el ajuste del baseline y no valida generalización. La banda coincide en definición con análisis previos, pero nuestros valores de agosto no se equiparan a resultados de septiembre/octubre ni al banco por clientes 13/14. Evaluar esos otros esquemas sería otro experimento con protocolo explícito; los modelos entrenados no se guardaron y nuestras predicciones actuales cubren solo agosto.

Se evalúan solo familias completas. Si rankings aún no terminó, queda pendiente y luego se regenera en una carpeta nueva sin sobrescribir resultados anteriores.

Primera evaluación: `exp/economia_20261106_v1` en la VM. Evaluación final preparada en segundo plano: `profit_after_batch.py` espera el cierre de `familias_20261106`, calcula las cuatro familias en `exp/economia_20261106_final` y respalda el paquete agregado en `gs://tomas_henseler_buckito2026/exp/familias_20261106/tutoria_con_ganancia.zip`. Log: `~/experimento_historia/economia_final.log`. No hay entrenamiento adicional.

Resultados disponibles de la primera evaluación (agosto, millones del ejercicio):

| Familia | Δ banda media | Semillas favorables | Δ banda ensamble | Δ N4000 media |
|---|---:|---:|---:|---:|
| Historia reciente | +0,7577 | 6/10 | +0,8863 | −0,9900 |
| Cambios relativos | +4,7005 | 8/10 | +5,4736 | +4,1800 |
| Persistencia | +0,6607 | 6/10 | +0,8398 | +0,5500 |
| Rankings con cero fijo | Pendiente | — | — | — |

Cambios relativos es desfavorable en AUC media pero favorable en estas medidas económicas de agosto. Es una señal descriptiva para discutir, no una confirmación fuera de muestra ni una mejora demostrada en otro mes. No sustituir la conclusión de AUC ni elegir a posteriori solo la métrica favorable.
