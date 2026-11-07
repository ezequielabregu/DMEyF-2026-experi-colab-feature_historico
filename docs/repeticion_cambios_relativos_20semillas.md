# Cambios relativos con veinte semillas

## Cierre del 7/11/2026

Ampliación completa y respaldada. Fuente definitiva:
`resultados/ampliaciones_20261107/cambios_relativos`, con control canónico
auditado. Δ AUC media -0,000375; Δ banda media +3,1109 M (15/20 favorables);
Δ N4000 media +3,7950 M. Las diez adicionales aportan +1,5214 M de banda.
Las métricas provisionales con el baseline de reanudación anterior quedaron
reemplazadas; detalle en `docs/auditoria_bins_20261107.md`. El notebook ejecutado
y las guías ya contienen el cierre. No quedan semillas ni corridas pendientes.
Lo que sigue conserva el protocolo fijado antes de ejecutar.

Ampliación exploratoria solicitada por Tomás el 6/11/2026 después de observar la primera evaluación con diez semillas. Cantidad fijada: veinte semillas totales por brazo, no veinte adicionales. Son cuarenta modelos: baseline ACO y baseline más cambios relativos.

Se mantienen marzo–junio, agosto, fórmulas, parámetros del 07, 339 árboles y ocho hilos. La secuencia de veinte primos se deriva con el mismo generador y semilla 979201; sus primeras diez entradas coinciden con las ya utilizadas. La ejecución es nueva y no sobrescribe la anterior. Al completar se comparan las AUC y predicciones de esas primeras diez para detectar cambios accidentales. Se reporta el conjunto de veinte y, como diagnóstico, las diez originales y las diez adicionales por separado.

Métricas: AUC por semilla y del ensamble; ganancia de agosto en banda inclusiva 3.000–6.000 y N común de 4.000. No se optimiza N. No abrir septiembre ni octubre. La decisión de ampliar siguió a resultados económicos favorables; no es una confirmación independiente ni se agregan semillas sucesivamente buscando un p favorable. No se ajusta el decaimiento de historia reciente.

Código aislado previsto: `~/historia_relative20_20261106`. Salidas: `~/experimento_historia/exp/relativos20_20261106`. Log general: `~/experimento_historia/relativos20_20261106.log`; log de modelos: `exp/relativos20_20261106/training.log`. Resumen económico y trazabilidad se guardan al terminar. El respaldo completo de predicciones y claves está autorizado por el usuario en su bucket; los datos individuales no se agregan a Git.
