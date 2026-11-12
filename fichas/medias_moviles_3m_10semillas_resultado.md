# Medias móviles: cierre con diez semillas

Fecha de la corrida: 12/11/2026. Rama feat/medias-moviles-3m; protocolo cb87b1d. Resultado: señal pequeña en AUC, sin mejora de ganancia. Mantener MAIN y cerrar en diez semillas. La ampliación a veinte sigue cancelada.

## Diseño

MM3D sin cambios: media simple de los valores disponibles del mismo cliente en t, t-1 y t-2, mínimo dos valores finitos. 129 columnas nuevas sobre PAQ_P3: 1.782 frente a 1.653. Mismos meses junio-octubre, ventanas, pesos, hiperparámetros y 296 árboles. Se conservaron las cinco semillas originales por brazo y se agregaron 330679, 511579, 312773, 118147 y 567529. Son diez totales, no diez adicionales.

## Resultados pareados, media de cinco meses

| Grupo | Delta banda M/mes | IC 95 % banda M | Favorables banda | Delta AUC | Favorables AUC |
|---|---:|---|---:|---:|---:|
| Originales (5) | -0,3400 | [-2,4933; +1,8133] | 2/5 | +0,000246 | 4/5 |
| Adicionales (5) | +0,2986 | [-1,5211; +2,1183] | 2/5 | +0,000610 | 5/5 |
| Total (10) | -0,0207 | [-1,3527; +1,3112] | 4/10 | +0,000428 | 9/10 |

Banda media: MAIN 263.332669 M; variante 263.311945 M. AUC media: MAIN 0.91688677; variante 0.91731462.

Ensamble: delta banda +0,0224 M/mes y delta AUC +0,000424. El ensamble se evalúa por separado del promedio de métricas de semillas.

IC t del delta AUC entre las diez semillas: [+0,000106; +0,000750]. Describe únicamente variación algorítmica sobre los mismos clientes y meses; no incorpora incertidumbre de clientes ni de meses futuros. La banda usa el IC original del pipeline, con componentes de clientes y semillas. Los dos intervalos no son equivalentes.

## Diferencias por mes, total diez

| Mes | Delta banda M | Delta AUC |
|---|---:|---:|
| 201906 | -1,0983 | -0,000017 |
| 201907 | +0,7699 | +0,000659 |
| 201908 | -0,5373 | +0,000693 |
| 201909 | +1,2192 | +0,000760 |
| 201910 | -0,4570 | +0,000045 |

## Interpretación y cierre

No hay señal favorable en ganancia: promedio prácticamente cero, intervalo que incluye cero y solo 4/10 semillas a favor. No pasa la regla del pipeline (diagnóstico fijado en delta positivo y 6/10 favorables). En AUC hay una señal pequeña y consistente entre semillas, pero no se traduce en dinero. No se modifica MAIN ni se hace merge automático. Concluir este experimento en diez semillas; no ampliar a veinte ni modificar la ventana buscando un resultado favorable.

La ampliación se decidió después de mirar cinco semillas y todos los meses de 2019 ya fueron consultados. Es exploratoria. Más semillas reducen variación del algoritmo; no aportan una nueva validación temporal. Reoptimizar, probar otras ventanas o cambiar la media sería otro experimento y requiere una definición nueva.

## Auditoría y operación

50 predicciones originales validadas por clave, forma, finitud y huella antes de entrenar. 100 predicciones finales (50 por brazo), nueve bloques sin cambios y mismas firmas de estrategia. Se verificó que el subconjunto original reproduce su ganancia y AUC anteriores. Funciones ejecutadas y parámetros (salvo ruta CRUDO) coinciden por SHA256 con el código local. La ampliación terminó en un intento, en 66.72 minutos; código de salida cero.

Evidencia: resultados/medias_moviles_3m_10semillas_20261112, con métricas exactas, originales/adicionales/total, logs y manifiesto de hashes. Respaldo confirmado en gs://tomas_henseler_buckito2026/exp/medias_moviles_3m_10semillas_20261112/. VM confirmada en TERMINATED después del respaldo y apagado automáticos.

Nota de referencia: PAQ_P3 reproducido da +9,00 M/mes contra AC con ventana reciente común y +12,60 M contra A_CONSIGNA. Estos números son los del baseline, no el aporte de MM3D.
