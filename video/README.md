# Video del grupo feature_historico

Video de Experimentos Colaborativos (DMEyF 2026). Presenta los dos pipelines del grupo:
- **el de recetas:** 39 recetas de historia, cada una sola contra el mismo baseline;
- **el acumulativo:** el pipeline del `main`.

| Archivo | Qué es |
|---|---|
| `guion.md` | El guion: 9 tramos, unos 8 minutos, con lo que se ve y lo que se dice |
| `slides/video_experimentos.qmd` | Las slides (Quarto revealjs, 1920×1080) |
| `slides/video_experimentos.html` | Las slides ya renderizadas: se abren en el navegador. El gráfico de las recetas carga plotly desde internet |
| `slides/figuras.py` | Cifras y figuras: ningún número de las slides está tipeado a mano |
| `slides/tema.scss` | Estilo: azul = recetas, naranja = acumulativo, violeta = regla y branches |
| `datos/` | Las tablas chicas que leen las figuras |
| `preparar_datos.py` | Arma `datos/`, y dice de dónde sale cada tabla |

**Avanzar las slides:** barra espaciadora o flecha derecha. En la dispersión de las 39 recetas, pasar el mouse por un punto muestra la receta y sus semillas a favor.

## Renderizar

Desde `video/slides/`, con el entorno del proyecto (plotly, pandas):

```bash
QUARTO_PYTHON=<ruta al python del entorno> quarto render video_experimentos.qmd --execute-daemon-restart
```

## De dónde sale cada tabla de `datos/`

| Tabla | Origen |
|---|---|
| `v10_resultados.csv` | `ClariRZ/ExperimentoVH`, `v10/cierre/resultados.csv` (pipeline de recetas) |
| `paq_p3_comparacion.csv` | `resultados/pipeline/main_comparacion.csv` en `b09397e`: el `main` antes del merge de Optuna |
| `rango_comparacion.csv` | branch `rango` |
| `optuna_comparacion.csv` | branch `feat/optuna-paq-p3`, `resultados/optuna/evaluacion_final_comparacion.csv` |
| `exploratorio/*.csv` | branch `ezequiel/etapa-1`, notebooks exploratorios `04` a `23` |
| `bandas_ensemble.csv` | calculada de las predicciones guardadas del pipeline (`exp/pipeline/`, no versionado) |
| `cifras_del_informe.csv` | los dos porcentajes del notebook `12` (69 % y 90 %), tomados del informe del grupo |
