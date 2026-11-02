# Construcción de clase_ternaria

Ejecutar desde la raíz del repositorio:

```bash
.venv/bin/python scripts/agregar_clase_ternaria.py \
  --input /home/tomas_henseler/datasets/competencia_02_crudo.csv.gz \
  --output datasets/competencia_02_con_clase.csv.gz \
  --report-dir resultados/etiquetado
```

El script verifica unicidad de `numero_de_cliente,foto_mes` antes de etiquetar. Solo usa presencia de estas claves y meses calendario. Si existe la foto de t+1 y el cliente falta, asigna BAJA+1; si aparece allí y falta en una foto disponible de t+2, BAJA+2; si aparece en ambas, CONTINUA. Sin t+1, o sin t+2 cuando el cliente sigue en t+1, deja el campo vacío (nulo al leer con pandas).

Se conserva el orden y los valores textuales de todas las columnas originales, incluso números escritos con notación científica. El formato de comillas y terminadores de línea del CSV puede normalizarse. El archivo original no se modifica y se rechazan salidas preexistentes. Una segunda lectura de la salida verifica la cantidad de filas, cada etiqueta y un SHA-256 de todas las celdas originales en orden, incluidas las claves.

## Alcance de las etiquetas

Las fotos disponibles abarcan 201901–202108 sin meses enteros faltantes. **Esto no demuestra que cada extracción mensual esté completa ni que toda ausencia corresponda a una baja real.** El repositorio no aporta una validación independiente de esos supuestos. Las etiquetas son operativas bajo la hipótesis de fotos completas; no se usan otras variables para inferirlas.

Se usan todos los meses disponibles para construir las etiquetas del dataset completo. Por eso 201911 y 201912 tienen etiquetas; esto difiere del escenario restringido a 2019 de la consigna. El baseline conserva los meses fijados: entrenamiento marzo–junio de 2019, validación agosto y test octubre. No utiliza las filas de noviembre/diciembre como ejemplos ni como predictores futuros.

Los conteos completos por mes están en `resultados/etiquetado/conteos_por_mes.csv`. La auditoría de rutas, filas, meses faltantes y conservación se guarda en `resultados/etiquetado/verificacion.json`. El dataset está excluido de git por `.gitignore`.

La corrida local finalizó y verificó 4.707.495 filas, sin duplicados ni meses enteros faltantes. La relectura confirmó la conservación de todas las celdas originales en orden. Julio de 2021 tiene 1.103 BAJA+1 y 163.245 nulos; agosto de 2021 tiene 164.647 nulos. Los meses anteriores tienen etiquetas completas bajo el supuesto de cobertura mensual íntegra.

Pruebas de calendario, cambio de año, meses ausentes, censura y duplicados:

```bash
.venv/bin/python -m unittest scripts.test_agregar_clase_ternaria
```
