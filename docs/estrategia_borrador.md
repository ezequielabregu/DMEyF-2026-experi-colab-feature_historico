# Estrategia — borrador

> **Estado: borrador.** Propuesta de Clara, copiada textual. 

## Clara

### Algoritmo de decisión — Experimento HISTORIA

Pregunta: ¿Agregar historia de 3 a 6 meses mejora la ganancia económica del modelo?

1\. Seleccionar variables: elegir las más importantes según el Gain de C3, que cambien con el tiempo y tengan datos confiables.

2\. Fijar el control: mantener constantes los datos, hiperparámetros, semillas y evaluación. Solo modificamos la historia.

3\. Comparar cuatro ramas:

- A: Modelo actual.
- B: A + lags de 3 a 6 meses.
- C: A + tendencias a 6 meses.
- D: A + lags + tendencias.

4\. Evaluar: comparar la ganancia económica y su estabilidad entre semillas y meses.

5\. Decidir: elegir la rama que mejore consistentemente al control. Si ninguna mejora, conservar A.

6\. Confirmar: probar la ganadora en un mes no utilizado previamente. Si mantiene la mejora, incorporarla; si no, volver a A.

En síntesis: Elegir variables → Agregar historia → Comparar ganancias → Confirmar → Decidir.

---
## Ezequiel

#### Observaciones sobre la propuesta de estrategia


### 1. Variantes como configuraciones, no como ramas de git

Propuesta: las cuatro ramas de la propuesta (A, B, C, D) como **configuraciones del mismo código** (por ejemplo `VARIANTE = "B"`), no como ramas de git.

- Así las cuatro corren con exactamente los mismos datos, semillas y evaluación (el paso 2 de la propuesta).
- Las que pierden quedan registradas en `main`, y la consigna pide reportar también los resultados negativos.

### 2. Baseline de la cátedra (referencia)

- Datos: solo 2019, con clase hasta 201910 (201911 y 201912 quedan para el dashboard).
- Entrenamiento: 201903–201906, completos y sin sampling.
- Validación: 201908. Su AUC ordena la optimización.
- Test: 201910, usado **solo** para comparar.
- LightGBM, optimizando `num_leaves`, `learning_rate`, `min_data_in_leaf`, `feature_fraction` y `bagging_fraction`; `bagging_freq` fijo en un entero ≥ 1.

La consigna aclara que es una referencia y que cada grupo lo adapta con su tutor.

### 3. Problema: la historia no entra en la ventana del baseline

El dataset (`competencia_02_crudo.csv`) empieza en **201901**. Un lag k en el mes m existe solo si m − k ≥ 201901:

| Mes | Rol | Lag máximo con datos |
|---|---|---|
| 201903 | entrenamiento | 2 |
| 201904 | entrenamiento | 3 |
| 201905 | entrenamiento | 4 |
| 201906 | entrenamiento | 5 |
| 201908 | validación | 7 |
| 201910 | test | 9 |

- El lag 6 queda **vacío en todo el entrenamiento** y lleno en validación y test.
- Los lags 3 a 5 quedan vacíos en parte.
- El modelo aprendería "falta el dato" en lugar de "historia", y la comparación contra A no mediría la hipótesis.

Opciones para llevar al tutor:
- usar menos historia (lag máximo 3 o 4) y aceptar los vacíos;
- mover la ventana de entrenamiento;
- repetir el diseño en otra época del dataset (2020–2021), donde hay 6 meses previos.

### 4. Decisiones pendientes

1. **Ventana de meses**, según el problema de arriba.
2. **Métrica.** La consigna usa AUC; la propuesta y la materia usan ganancia. Propuesta: optimizar con AUC en validación, como pide la consigna, y juzgar la hipótesis con la **ganancia en test**, reportando también la AUC.
3. **Hiperparámetros.** El paso 2 los deja fijos; la consigna pide optimizar el LGBM. Opciones: optimizar una vez sobre A y reusarlos en B–D (aísla el efecto de las variables), u optimizar cada variante (más justo, cuesta 4 veces más).
4. **"Gain de C3"** (paso 1): ¿a qué se refiere? Sea cual sea el criterio, la selección de variables sale de un modelo entrenado solo con los meses de entrenamiento, nunca con el mes de test.
5. **Estabilidad "entre semillas y meses"** (paso 4). El mes de test se usa una sola vez, así que la estabilidad entre meses necesita un backtest, si el tutor lo acepta. ¿Cuántas semillas?
6. **"Un mes no utilizado previamente"** (paso 6): con la consigna, es 201910.
7. **Lenguaje:** Python o R.
