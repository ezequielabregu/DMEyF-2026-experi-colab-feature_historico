# Rankings con cero fijo con veinte semillas

## Cierre del 7/11/2026

Ampliación completa y respaldada. Fuente definitiva:
`resultados/ampliaciones_20261107/rankings_cero_fijo`, procedente de la
recuperación `rankings20_resume_v4_20261107`. Δ AUC media -0,000668;
Δ banda media +0,7599 M (11/20 favorables); Δ N4000 media +0,8250 M.
Las diez adicionales pierden -0,7293 M de banda. El NPY vacío tras el corte
Spot se excluyó y recalculó; detalle en `docs/auditoria_bins_20261107.md`.
El notebook ejecutado y las guías ya contienen el cierre. No quedan semillas
ni corridas pendientes. Lo que sigue conserva el protocolo original.

Ampliación exploratoria solicitada el 6/11/2026. Veinte semillas totales por brazo: las diez originales y diez adicionales de la misma secuencia reproducible. Cuarenta entrenamientos en una carpeta nueva, sin sobrescribir ni sumar como treinta semillas el experimento anterior.

Se mantienen datos, calendario marzo–junio/agosto, saneamiento, 73 variables monetarias, ranking por mes y signo con cero fijo, fórmulas de lag/delta, parámetros ACO del 07, 339 árboles y ocho hilos. Se conservan NaN y las mismas filas. No se abren septiembre/octubre ni se cambian pesos o hiperparámetros.

Se evalúan AUC media por semilla y del ensamble, y ganancia de agosto con banda inclusiva 3.000–6.000 y corte N=4.000. La primera evaluación con diez semillas mostró menor AUC media (−0,000611171), pero mayor ganancia media de banda (+2,249080 M, 7/10 semillas favorables). La ampliación no es confirmación independiente ni una búsqueda secuencial de significancia.

La cola espera la terminación de cambios relativos con veinte semillas. Si esa corrida termina con error, rankings puede ejecutarse porque no depende de sus predicciones. Al finalizar se comprueba la reproducción de las diez semillas originales por brazo; se muestran originales, adicionales y total en AUC. Las métricas económicas corresponden al total de veinte y al ensamble.

Código aislado: `~/historia_rank20_20261106`. Runner: `scripts/historia/run_rankings20.py`. Salidas: `~/experimento_historia/exp/rankings20_20261106`. Log general: `~/experimento_historia/rankings20_20261106.log`. Log de entrenamientos: `exp/rankings20_20261106/training.log`. Bucket: `gs://tomas_henseler_buckito2026/exp/rankings20_20261106/`. Los archivos completos, incluidas predicciones y claves, se respaldan según autorización del usuario; solo métricas agregadas van al repositorio.
