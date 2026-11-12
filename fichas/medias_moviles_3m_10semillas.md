# Ampliación final a diez semillas

Pedido de Tomás, 12/11/2026, después de observar el resultado de cinco semillas:
ganancia -0,34 M/mes y delta AUC aproximado +0,000246. La ampliación a veinte
permanece cancelada. Cerrar esta comparación en diez semillas totales por brazo,
independientemente del resultado; no ampliar para perseguir una señal.

Baseline: MAIN PAQ_P3 b09397e. Variante MM3D definida en d259778, sin cambios:
media de valores disponibles de t/t-1/t-2, mínimo dos valores finitos, 129 columnas.
Mismos datos, roturas, orden de columnas, ventanas, pesos, parámetros, 296 árboles
y meses junio-octubre. No elegir nuevas ventanas ni reoptimizar.

Se conservan las cinco semillas originales y se añaden las cinco siguientes de
F.semillas con semilla primigenia 979201: 330679, 511579, 312773, 118147, 567529.
Se importan 25 predicciones de cada brazo y se generan otras 25 por brazo.
Todas las importadas se validan por clave mes/semilla, longitud, finitud y huella.
La semilla de construcción de bins sigue fija en 979201, incluso al reanudar.

Guardar originales cinco, adicionales cinco y total diez separadamente. Ganancia
principal: banda N=3000-6000 inclusiva, mismos pagos de la consigna; delta pareado,
por mes/semilla, IC del pipeline y ensamble. AUC BAJA+2: por mes/semilla, delta
pareado medio y AUC de ensambles. IC t del delta AUC entre semillas describe
variación algorítmica condicionada a estos meses/clientes: no es un IC que
incorpore incertidumbre de clientes o futuros meses.

MINIMO_SEMILLAS pasa a 6/10 para conservar el diagnóstico de proporción 3/5. No
equivale a una prueba de significancia ni autoriza merge automático. No afirmar
confirmación por mejorar solo AUC o solo dinero. Interpretar ambas por separado.
La ampliación es posterior al resultado inicial, sobre meses ya usados; sigue
siendo exploratoria. Diez semillas reducen incertidumbre del algoritmo, no la
incertidumbre temporal. Si no hay señal suficiente, cerrar y pasar a otra idea.

Carpeta aislada en GCP: ~/medias_moviles_3m_10semillas_20261112. Reutilizar datos y
bloques ya calculados, sin alterar los originales. Checkpoints atómicos, respaldo
y apagado al finalizar. No ejecutar 05 de producción. Conservar resultados cinco.
