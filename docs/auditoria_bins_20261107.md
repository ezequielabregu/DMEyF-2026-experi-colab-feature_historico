# Auditoría de bins y recuperación tras el corte Spot

**Cierre verificado:** rankings veinte pares y cambios relativos auditado
terminaron con código 0, respaldos completos y VM en TERMINATED. Los agregados
finales están en `resultados/ampliaciones_20261107`, con manifiesto de hashes.
La banda media corregida de cambios relativos es +3,1109 M (15/20 favorables),
y la de rankings +0,7599 M (11/20). Se actualizaron los informes HTML/Markdown.

## Diferencia entre baselines

Al reanudar cambios relativos se saltaban los diez baselines ya guardados antes
de llamar por primera vez a `lgb.train` sobre un Dataset nuevo. LightGBM recibía
entonces como primera semilla 859783 en lugar de 294103. La construcción del
Dataset depende de esa inicialización: los nuevos baselines no coincidían con
los de rankings, cuya ejecución había comenzado por la primera semilla original.
La configuración y las fórmulas de features no habían cambiado.

Se corrigió el código para construir explícitamente el Dataset con los parámetros
fijos y la semilla 294103 antes de entrenar cualquier semilla faltante. La prueba
real reconstruyó el baseline 859783 y sus predicciones coincidieron exactamente
con el baseline canónico de rankings. El resultado está registrado en
`baseline_bin_audit.json`. Para continuar una variante parcial se reconstruye
además su primera semilla y se exige identidad exacta con el checkpoint.

La corrección no se decide por AUC o ganancia: se conserva la inicialización de
la corrida original. Las veinte variantes de cambios relativos comenzaron por
294103 y no requieren cambiarse por esta causa. Se reevalúan contra los veinte
baselines canónicos de rankings. Antes de hacerlo se verifican datos, parámetros,
versiones, secuencia de semillas, columnas y claves. Los diez baselines originales
deben coincidir exactamente entre fuentes. Las métricas y predicciones previas
se conservan; la salida auditada es una carpeta nueva con manifiesto de origen
y hashes de cada predicción.

Las cifras provisionales de cambios relativos (+3,5392 M de banda media en veinte
pares) pertenecen al baseline anterior a esta corrección. No deben presentarse
como resultado final ni mezclarse con la comparación auditada.

## Checkpoint de rankings

La VM es Spot/preemptible y se detuvo a las 12:13:54 de Buenos Aires. El disco
conservó un CSV con veinte baselines y catorce variantes, pero la predicción de
la variante 646669 estaba vacía. La primera reanudación la rechazó, respaldó
el intento fallido y apagó la VM. El estado final de aquella cola tiene código
de salida 1 y no representa un experimento completo.

La recuperación posterior recalculó AUC y validó forma/rango de todos los NPY;
conservó 33 predicciones y excluyó explícitamente la vacía. Las siete variantes
restantes incluyen recalcular esa semilla. El checkpoint dañado se conserva;
`recovery_manifest.json` registra la exclusión. Los nuevos guardados hacen
`fsync` del NPY antes de registrar la fila de métricas, además de reemplazos
atómicos. Las pruebas sintéticas cubren archivo vacío, AUC incorrecta y
preservación de las fuentes.

## Salidas de cierre

- Rankings recuperado: `exp/rankings20_resume_v4_20261107`.
- Cambios relativos con control canónico: `exp/relativos20_auditado_20261107`.
- Bucket: `gs://tomas_henseler_buckito2026/exp/<carpeta>/checkpoint_completo`.
- Cola: `~/historia_resume_20261107/continuation_v4.log`.

El estado completo debe verificarse en los respaldos; la existencia de estas
rutas previstas no acredita por sí misma que el experimento haya terminado.
Las ampliaciones son exploratorias en agosto y no añaden validación temporal.
