# Corrida baseline 2019

Implementación en Python de `Baseline_entregables.md`. No agrega historia de 3–6 meses del experimento.

- Entrenamiento completo: 201903–201906. Positivo: BAJA+1 o BAJA+2.
- Validación: 201908, AUC para Optuna y early stopping (100 rondas).
- Test: 201910, evaluado después de elegir parámetros y cantidad de rondas. No se reentrena con validación.
- El cache Parquet conserva 201901–201910; enero y febrero proveen historia. La conversión inicial recorre el CSV completo.
- Predictores originales salvo número de cliente y clase; se conserva foto_mes.
- Interpretación de «lag y delta 2»: para cada predictor salvo foto_mes, lags 1 y 2 y diferencias actual menos lag. Se buscan meses calendario exactos del mismo cliente. Los faltantes quedan como NaN.
- Semilla 2026, 30 trials secuenciales, máximo 3000 rondas, bagging_freq=1.
- Búsqueda: num_leaves 16–128, learning_rate 0.01–0.15 (log), min_data_in_leaf 100–4000 (log), feature_fraction y bagging_fraction 0.5–1.

## Ejecución

Desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python scripts/baseline.py \
  --data datasets/competencia_02_con_clase.csv.gz \
  --out exp/baseline_2019_control
```

El dataset debe contener `numero_de_cliente,foto_mes,clase_ternaria`, sin duplicados por cliente/mes, con etiquetas CONTINUA, BAJA+1 o BAJA+2. También se acepta `--data ARCHIVO.parquet`. Para construir las etiquetas desde el original, ver `etiquetado.md`.

Si se omite `--out`, se genera una carpeta única con fecha UTC e identificador aleatorio. Una carpeta explícita debe ser nueva. Cada corrida genera:

- `config.json`: meses, argumentos, semilla, versiones, hashes SHA-256 de datos y scripts.
- `run.log` y `status.json`: avance y estado `running`, `complete` o `failed`; errores con diagnóstico.
- `optuna.db` y `trials.csv`: parámetros, AUC y rondas por trial; se actualizan durante la optimización.
- `selection.json` y `model.txt`: selección por validación y mejor modelo guardado durante la búsqueda, antes de consultar test.
- `metrics.json`, `importance.csv` y `predictions_201910.parquet`: evaluación final e importancia por gain.

DuckDB realiza los cruces calendario sobre `datasets/baseline_2019.parquet`, un cache comprimido con Zstandard. Los metadatos `.source.json` verifican su correspondencia con el CSV mediante hashes. Si cambia la fuente o el cache, el script exige otra ruta `--cache` para evitar reutilizar datos incorrectos. Los faltantes de features permanecen como NaN; no hay sampling ni imputación con datos futuros.

El registro central está en `exp/experiments.sqlite`, tabla `runs`, con estado, configuración, métricas y ruta de cada ejecución. El estudio Optuna usa SQLite por separado. `exp/` está excluido de git por contener modelos y predicciones individuales. Se escribe un resumen sin datos individuales en `resultados/baseline/<run_id>.json`, apto para versionar.

```bash
# Consultar las corridas registradas
python - <<'PY'
import sqlite3
with sqlite3.connect('exp/experiments.sqlite') as con:
    for row in con.execute('SELECT run_id, status, output_dir FROM runs ORDER BY updated_utc'):
        print(row)
PY

# Verificar calendario, aislamiento de datos futuros y registro completo
python -m unittest scripts.test_baseline scripts.test_agregar_clase_ternaria
```

Se puede ajustar `--trials`, `--max-rounds`, `--patience`, `--threads` y `--seed`; esos valores quedan registrados. Reducir el presupuesto sirve para una prueba técnica, pero no equivale a la corrida de 30 trials. El registro persiste la búsqueda interrumpida para inspección; el comando no implementa reanudación automática. Un cierre forzado del proceso puede dejar estado `running`, que debe interpretarse junto al log.

El test de octubre se carga y evalúa después de guardar la selección definitiva. No se reentrena el ganador ni se ajustan umbrales con test. El modelo incluye `feature_pre_filter=False` para poder variar `min_data_in_leaf` reutilizando el mismo Dataset de LightGBM.

## Estado

El archivo original `competencia_02_crudo.csv.gz` contiene 154 columnas, sin `clase_ternaria`. El script `scripts/agregar_clase_ternaria.py` genera la copia con etiquetas por presencia en meses futuros; ver `docs/etiquetado.md` para sus supuestos y limitaciones. No hay resultados de AUC todavía.

La ganancia económica queda pendiente de definir pagos, costos y regla de selección con el grupo/tutor. La comparación oficial se hace con AUC; no elegir variantes ni umbrales usando octubre repetidamente. Para B–D, acordar primero la ventana de entrenamiento por la falta de historia de 6 meses que señala el borrador.
