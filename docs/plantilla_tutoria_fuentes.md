# Plantilla de tutoría y fuentes del cierre

El reporte conserva la estructura del PDF original de Ezequiel: problema y
baseline, recorrido de pruebas, obstáculos, preguntas para Alejandro y glosario.
El original se preserva. Las versiones editables son
`estado_grupal_para_tutoria.md/.html` e `informe_experimentos_historia.md/.html`.
El PDF nuevo está en `output/pdf/informe_ezequiel_actualizado_20261107.pdf`.

## Fuentes vigentes

- Antecedentes: commit **6cf189c**, con resultados hasta 14, congelados en
  `resultados/antecedentes_6cf189c`. El antiguo 3b44f21 es histórico; su ausencia
  de tablas 09 no describe el estado actual.
- Cuatro familias de diez semillas: `resultados/familias_final_20261106`.
- Ampliaciones auditadas de veinte: `resultados/ampliaciones_20261107`.
  `snapshot.json` registra hashes y prefijos de respaldo completos.
- Auditoría: `docs/auditoria_bins_20261107.md`.

El notebook `notebooks/tutoria_historia.ipynb` ya utiliza estas fuentes y se
ejecutó con ocho celdas de código y dos gráficos, sin errores, sobre agregados
finales. No se mezclaron ramas ni se descargaron claves/predicciones al repositorio.

## Regeneración de los informes

```bash
python scripts/historia/complete_tutoria_template.py --twenty resultados/ampliaciones_20261107 --out docs/estado_grupal_para_tutoria.md
python scripts/historia/complete_tutoria_template.py --twenty resultados/ampliaciones_20261107 --out docs/informe_experimentos_historia.md
```

`--twenty` incorpora las ampliaciones auditadas. El valor predeterminado de
`--results` apunta al paquete final de diez semillas. El PDF se genera desde el
Markdown de Ezequiel; las figuras de 13 y 14 se conservan en `docs/figuras`.
Instrucciones de notebook y paquete: `docs/tutoria_historia.md`.

Todas las corridas de esta tanda terminaron y la VM está apagada. Siguen pendientes
las respuestas del tutor, verificaciones de diagnósticos sin sus tablas fuente,
decisiones de entrega; no se inventan respuestas o resultados.

La bibliografía metodológica se verificó con seis fuentes primarias y se incluye
en `docs/bibliografia_historia.md`, los informes, el PDF y el notebook.
