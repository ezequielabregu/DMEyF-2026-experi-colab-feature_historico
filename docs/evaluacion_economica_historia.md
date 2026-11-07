# Evaluación económica de nuestras familias: cierre del 7/11/2026

Análisis secundario decidido el 6/11 después de mirar parte de las AUC. Es
exploratorio en agosto de 2019, que también se usó para ajuste; no es una regla
predefinida antes de observar todos los resultados ni validación independiente.

Se reutilizan probabilidades guardadas, sin abrir otros meses. Solo BAJA+2 es
positivo económico: +1.072.500 por acierto y -27.500 por el resto, incluidos
BAJA+1. Se informa banda inclusiva N=3.000-6.000 y corte común N=4.000. No se
elige N por variante ni se umbralizan en 2,5 % probabilidades sin calibrar.

Las claves se alinearon por cliente/mes y se recalcularon las AUC antes de medir
dinero. Empates usan orden estable. Los hashes y versiones están registrados.
Media de métricas y métrica del ensamble de probabilidades se informan aparte.
Al repositorio se descargaron únicamente agregados, sin claves ni NPY.

## Cuatro familias completas con diez semillas

Fuente: `resultados/familias_final_20261106`. Evaluación remota completa:
`exp/economia_20261106_final`; paquete histórico final:
`gs://tomas_henseler_buckito2026/exp/familias_20261106/tutoria_con_ganancia.zip`.

| Familia | Δ banda media M | Favorables banda | Δ banda ensamble M | Δ N4000 media M | Δ N4000 ensamble M |
|---|---:|---:|---:|---:|---:|
| Historia reciente | +0,7577 | 6/10 | +0,8863 | -0,9900 | -1,1000 |
| Cambios relativos | +4,7005 | 8/10 | +5,4736 | +4,1800 | +11,0000 |
| Persistencia | +0,6607 | 6/10 | +0,8398 | +0,5500 | -1,1000 |
| Rankings con cero fijo | +2,2491 | 7/10 | +2,3884 | +0,6600 | +0,0000 |

## Ampliaciones auditadas de veinte semillas totales

Fuente: `resultados/ampliaciones_20261107`. Misma banda, corte, etiquetas,
calendario, fórmulas y parámetros. Baseline canónico común a ambas familias,
construido con la inicialización de la primera semilla original. Detalle de la
corrección y los resultados provisionales reemplazados:
`docs/auditoria_bins_20261107.md`. No se seleccionó el control por su ganancia.

| Familia | Δ banda media M | Favorables banda | Δ banda ensamble M | Δ N4000 media M | Δ N4000 ensamble M |
|---|---:|---:|---:|---:|---:|
| Cambios relativos | +3,1109 | 15/20 | +3,2527 | +3,7950 | +7,7000 |
| Rankings con cero fijo | +0,7599 | 11/20 | +1,2012 | +0,8250 | +3,3000 |

En las diez adicionales, cambios relativos suma +1,5214 M de banda y rankings
pierde -0,7293 M. La AUC media total baja en ambas familias (-0,000375 y -0,000668).
La señal económica es más consistente para cambios relativos en este corte;
no confirma transporte temporal ni convierte una métrica favorable en ganadora.

Las ampliaciones terminaron, se respaldaron y la VM quedó apagada. No se añaden
semillas para fortalecer el resultado. No se comparan estos millones de agosto
directamente con septiembre/octubre o con el banco por clientes 13/14.

El notebook ejecutado presenta originales, adicionales y total, además del
ensamble. Guía de documentación: `docs/tutoria_historia.md`.
