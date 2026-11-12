# Pipeline del `main`

Es la mejor estrategia del grupo hasta ahora (`PAQ_P3`). Gana +9,00 M por mes sobre el baseline de la consigna con la misma ventana (IC 95 %: 5,18 a 12,82), y +12,60 M sobre el baseline con la ventana de la consigna (7,73 a 17,46). Es exploratoria: los meses de 2019 ya se usaron para decidir.

## Archivos

| Archivo | Qué hace |
|---|---|
| `parametros.py` | **El único lugar con parámetros.** La configuración que se corre es `CORRIDA` |
| `funciones.py` | Todo el código. Cada bloque de variables es una función |
| `01_datos.ipynb` | Del crudo al parquet base de 2019, con la clase ternaria (guardada solo hasta 201910) y los meses rotos. Corre una sola vez |
| `02_variables.ipynb` | Arma y guarda los bloques de variables |
| `03_modelos.ipynb` | Entrena el banco temporal (201906 a 201910, 5 semillas) y guarda las predicciones. Si la VM se apaga, sigue donde quedó |
| `04_comparacion.ipynb` | Ganancia por mes y por semilla, comparación, veredicto y figuras |
| `05_produccion.ipynb` | Semillerío de 20 y los 4.500 envíos del mes a predecir |

Se corren en orden: `01` → `02` → `03` → `04` (→ `05`).

## Primera vez (en el `main`)

1. En `parametros.py`, ajustar `CRUDO` si el dataset está en otro lugar.
2. Correr `01` a `04` en orden. Unos 25 a 30 minutos de modelos en una Mac M4 (75 modelos: `main`, `AC` y A-consigna); memoria, unos 7 GB.
3. El `04` tiene que terminar con **"MAIN VERIFICADO"**. Además, el `02` y el `03` comparan los bloques y las predicciones con las huellas versionadas en `resultados/pipeline/` (`huellas_bloques.csv` y `<corrida>_huellas_pred.csv`): si esta máquina da otros números, cortan. Eso es la reproducción cruzada.

## Cómo se prueba una propuesta en un branch

1. Crear un branch desde el `main`.
2. Cambiar **una sola cosa**:
   - **variables nuevas** (propuestas #2 a #5 y #8): una función nueva en `funciones.py`, agregada a `PRODUCTORES` y `BLOQUE_DE`;
   - **ventana** (#1): el campo `ventana` de la configuración;
   - **hiperparámetros** (#6): el campo `hiper`, buscado con Optuna en 201906–08.
3. En `parametros.py`, reemplazar la línea `CORRIDA = MAIN` por la configuración del branch, con otro nombre. Por ejemplo:
   ```python
   CORRIDA = {**MAIN, 'nombre': 'rango', 'bloques': BLOQUES_PAQ_P3 + ['RANGO']}
   ```
   **Si el branch eligió entre varias configuraciones mirando los meses** (Optuna, varias ventanas), agregar `'eligio_entre_varias': True`: la regla se juzga solo en 201909–10. Escribir antes de correr, en la ficha del branch, qué configuración se elige y cómo.
4. Correr `02` a `04`. Si el `main` no está entrenado en esta máquina, el `03` lo entrena primero (25 modelos) y comprueba que da las huellas versionadas. El `04` compara contra las predicciones guardadas del `main` y aplica la **regla de merge**: `d` > 0 y al menos 3 de 5 semillas a favor.
5. Versionar `resultados/pipeline/<branch>_*.csv` y las figuras del branch.

## Cómo se hace el merge (si el branch pasa)

1. En `parametros.py` del `main`, el cambio del branch pasa a `MAIN` (solo el cambio: nunca `'eligio_entre_varias'`). Por ejemplo, `MAIN = {'nombre': 'main', 'meses': MESES_EVALUADOS, **PAQ_P3, 'bloques': BLOQUES_PAQ_P3 + ['RANGO']}`. `CORRIDA` vuelve a `MAIN`.
2. Renombrar `exp/pipeline/main` a `exp/pipeline/main_anterior` (o el nombre de la estrategia vieja). Si no se renombra, el `03` corta: las predicciones guardadas son de otra configuración.
3. Correr `02` a `04`. El `04` dice **"MAIN NUEVO"**: ya no es `PAQ_P3`, así que no se compara con el `22`, y sigue comparándose contra `AC` y A-consigna.
4. Versionar `resultados/pipeline/main_*.csv` y las figuras nuevas, y hacer el merge.
5. **Cada branch abierto trae el `main` nuevo** (`git merge main` en el branch) y se vuelve a correr: su configuración cambió, así que el `03` pide borrar su carpeta y volver a entrenarlo.

## Qué controla solo el pipeline

- **Firma de cada resultado:** un bloque o una predicción guardados se reusan solo si se hicieron con el mismo código, los mismos parámetros y los mismos datos. Cambiar algo nunca devuelve resultados viejos sin avisar: el `02` rehace el bloque y el `03` corta.
- **Huellas versionadas:** los bloques y las predicciones tienen que ser iguales bit a bit a los versionados con la misma configuración.
- **`PAQ_P3` contra el `22`:** si la estrategia es `PAQ_P3` y están `exp/22/` y `exp/15/`, las predicciones tienen que ser iguales bit a bit a las del `22`, y el `04`, dar sus números.
- **Escritura atómica:** si la VM se apaga a mitad de una escritura, no queda un archivo cortado con el nombre definitivo.

## Reglas

- Si se cambia la lógica o un parámetro de un bloque que ya existe, va como bloque nuevo, con otro nombre: si no, el `02` corta porque el bloque no da la huella versionada.
- Un bloque nuevo que mire más de 2 meses atrás tiene que decir cómo trata el borde de 201901. Desde 201903, los lags de 1 y 2 meses nunca llegan antes de 201901; los bloques que miran más atrás (`CURADA`, `ACH_*`) piden al menos 2 fotos previas.
- No reordenar `BLOQUES_PAQ_P3`: el orden de las columnas cambia el modelo.
- Antes de cada commit, borrar las salidas de los notebooks.
- 201911 y 201912 no se usan nunca: el parquet base los tiene solo como filas sin clase (hacen falta para la clase de 201910 y para la regla de meses rotos).
