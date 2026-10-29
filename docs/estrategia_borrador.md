# Estrategia — borrador

> **Estado: borrador.** Propuesta de Clara, copiada textual. 

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
