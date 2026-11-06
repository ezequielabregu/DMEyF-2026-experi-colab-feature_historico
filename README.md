# DMEyF 2026 — Experimento colaborativo: feature_historico

Experimento colaborativo de Data Mining en Economía y Finanzas (UBA, comisión de los lunes).

- **Integrantes:** Tomás H., Clara M. R., Ezequiel A.
- **Tutor:** Alejandro Bolaños.

Para retomar el trabajo después de reiniciar, leer [contexto maestro](docs/CONTEXTO_MAESTRO.md) y [último checkpoint](docs/RETOMAR_20261107.md).

## Cómo trabajamos con git

- `main` tiene siempre código que corre.
- Cada pieza nueva va en una rama (`feat/<tema>`).
- Una rama se mergea **cuando el código funciona**, gane o pierda el experimento: los resultados negativos también se reportan.
- Antes de empezar una rama: `git switch main && git pull`.

## Baseline

La URL del dataset original y los comandos para descargarlo en la VM están en [docs/dataset.md](docs/dataset.md).

Con el dataset etiquetado disponible en `datasets/competencia_02_con_clase.csv.gz`:

```bash
python -m pip install -r requirements.txt
python scripts/baseline.py
```

La corrida prepara un cache Parquet, calcula lags/deltas con DuckDB, optimiza LightGBM por AUC de agosto de 2019 y evalúa el ganador en octubre. Registra configuración, trials, modelo y métricas en `exp/`, y un resumen versionable en `resultados/baseline/`.

Ver [diseño y registro del baseline](docs/baseline_corrida.md) y [construcción de etiquetas](docs/etiquetado.md).
