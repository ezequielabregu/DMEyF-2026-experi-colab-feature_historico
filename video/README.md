# Video del grupo feature_historico

Video de Experimentos Colaborativos (DMEyF 2026). Presenta las dos familias de experimentos del grupo:
- **familia 1, experimentos independientes:** 39 experimentos, cada uno agrega un tipo de variable histórica al mismo baseline;
- **familia 2, experimentos acumulativos:** el pipeline del `main`.

| Archivo | Qué es |
|---|---|
| `guion.md` | El guion: 9 tramos y 23 slides, con lo que se ve y lo que se dice |
| `slides/video_experimentos.qmd` | Las slides (Quarto revealjs, 1920×1080) |
| `slides/video_experimentos.html` | Las slides ya renderizadas: se abren en el navegador. Los gráficos interactivos cargan plotly desde internet |
| `slides/figuras.py` | Cifras y figuras: ningún número de las slides está tipeado a mano |
| `slides/tema.scss` | Estilo: azul = familia 1, naranja = familia 2, violeta = regla y branches |
| `datos/` | Las tablas chicas que leen las figuras |
| `preparar_datos.py` | Arma `datos/`, y dice de dónde sale cada tabla |

**Avanzar las slides:** barra espaciadora o flecha derecha. Son interactivos (pasar el mouse): la dispersión de los 39 experimentos, la profundidad de la historia, el valor de la historia por semilla, lo que no sumó y las dos curvas de ganancia.

## Renderizar

Desde `video/slides/`, con el entorno del proyecto (plotly, pandas):

```bash
QUARTO_PYTHON=<ruta al python del entorno> quarto render video_experimentos.qmd --execute-daemon-restart
```

## De dónde sale cada tabla de `datos/`

| Tabla | Origen |
|---|---|
| `v10_resultados.csv` | `ClariRZ/ExperimentoVH`, `v10/cierre/resultados.csv` (familia 1) |
| `paq_p3_comparacion.csv`, `paq_p3_ganancias.csv`, `ac_ganancias.csv` | `resultados/pipeline/` en `b09397e`: el `main` antes del merge de Optuna, y el baseline |
| `rango_comparacion.csv` | branch `rango` |
| `optuna_comparacion.csv` | branch `feat/optuna-paq-p3`, `resultados/optuna/evaluacion_final_comparacion.csv` |
| `exploratorio/*.csv` | branch `ezequiel/etapa-1`, notebooks `04` (prueba pre-registrada, dosis-respuesta) a `23` |
| `bandas_ensemble.csv`, `curvas_ganancia.csv` | calculadas de las predicciones guardadas del pipeline (`exp/pipeline/`, no versionado): banda y curva de ganancia del ensamble |
| `cifras_del_informe.csv` | los dos porcentajes del notebook `12` (69 % y 90 %), tomados del informe del grupo |
