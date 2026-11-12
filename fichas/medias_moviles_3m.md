# Media móvil simple de tres meses

Protocolo fijado el 12/11/2026, antes de entrenar la variante.
Rama: feat/medias-moviles-3m. Baseline: b09397e518aa3051dab41ea8fc64d3518b8bf52d,
PAQ_P3 reproducido en GCP con ocho bloques y 65 predicciones idénticas.

## Hipótesis y único cambio

Agregar el nivel suavizado permite al árbol detectar comportamientos que los niveles,
lags, deltas y cocientes actuales representan con más particiones.
MM3D agrega la media de los valores finitos de t, t-1 y t-2 sobre los 129 montos/conteos de d.montos.
Pesos iguales, suma en float64 y salida float32; 129 columnas, total 1.782.
Las fotos son meses calendario exactos del mismo cliente. Si falta un valor o foto, se promedian los disponibles, exigiendo MINIMO_MM3=2.
Con menos de dos valores finitos la media es NaN; ceros y negativos conservan su valor. Se aplican previamente las
roturas del baseline. En marzo se dispone de enero-febrero; no se requiere historia
anterior a enero. No se eliminan filas por historia incompleta.

CURADA ya contiene actual/media3 para 30 variables y ACH_T actual/media histórica;
MM3D añade medias explícitas, no nuevos cocientes ni otros estadísticos. La ventana
de tres meses usa información ya disponible en AC. No afirmar información nueva.
No se repite el bloque anterior de media 4:2:1, desvío y cambio relativo: aquel
experimento no aisló la contribución de la media ponderada.

## Comparación fijada

CORRIDA = medias_moviles_3m_min2; bloques de MAIN en el mismo orden más MM3D al final.
Mismos meses junio-octubre, ventanas recientes, pesos, 296 árboles, hiperparámetros
y cinco semillas que MAIN. Se reutilizan las predicciones de MAIN ya verificadas,
comprobando sus firmas y huellas. No reoptimizar ni seleccionar entre ventanas.
Una única variante fijada: eligio_entre_varias no aplica.

Evaluación original del pipeline: ganancia media de banda N=3000-6000 inclusive,
+1.072.500 por BAJA+2 y -27.500 por resto. Reportar delta por mes/semilla, AUC,
ensamble e IC. Regla de merge: delta medio >0 y al menos 3/5 semillas a favor.
No equivale a exigir significancia estadística: informar si el IC incluye cero.
Todos los resultados nuevos de 2019 son exploratorios; cinco semillas no son
cinco muestras temporales independientes. Publicar también el resultado negativo.
No modificar MAIN, hacer merge ni sumar ventanas según el resultado de esta prueba.

## Ejecución y controles

python pipeline/test_mm3.py; luego notebooks 02, 03 y 04 desde pipeline/ en GCP.
Validar calendario con huecos, cliente, NaN, cero y no uso del futuro. El 02 verifica
además el bloque con datos truncados a tres cortes. Comparar las ocho huellas del
baseline con las originales antes de entrenar; conservar evidencia y resultados.

## Ajuste por indicación de Tomás antes de entrenar

Se suspendió el intento estricto medias_moviles_3m durante el cálculo de bloques,
sin modelos ni resultados de la variante. Tomás propuso aprovechar la historia
disponible. Se fija mínimo de dos observaciones dentro de los tres meses calendario,
sin extender hacia meses anteriores. El intento original queda separado y no se
usa para elegir esta definición. El nuevo nombre de bloque es MM3D.
