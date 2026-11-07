# Tutoría: documentación final del experimento de historia

Cierre del 7 de noviembre de 2026. Las cuatro familias de diez semillas y las
dos ampliaciones de veinte están completas y respaldadas. La VM quedó apagada.
Este recorrido solo lee agregados y no requiere entrenamientos, credenciales,
dataset ni predicciones individuales.

## Material para presentar

- Notebook ejecutado: `notebooks/tutoria_historia.ipynb`, con tablas y dos gráficos visibles.
- Informe de Ezequiel: `docs/estado_grupal_para_tutoria.md` y `.html`.
- Informe principal equivalente: `docs/informe_experimentos_historia.md` y `.html`.
- PDF revisado: `output/pdf/informe_ezequiel_actualizado_20261107.pdf`.
- Paquete para Colab: `output/tutoria/tutoria_historia_documentacion_20261107.zip`.
- Tablas y gráficos derivados por el notebook: `output/tutoria/`.
- Bibliografía metodológica verificada: `docs/bibliografia_historia.md`.

En Colab: subir el notebook mediante Archivo → Subir notebook. Las salidas ya
están visibles; para recalcularlas, ejecutar y subir el ZIP de documentación
cuando lo pida. No hay un enlace de Colab publicado. En Jupyter, descomprimir
el ZIP y abrir `notebooks/tutoria_historia.ipynb`, o usar el repositorio completo.

Recorrido sugerido: controles y antecedentes 01-14 → cuatro familias de diez
semillas → ampliaciones separando originales/adicionales/total → gráficos →
limitaciones y preguntas de tutoría. Las imágenes de antecedentes se incluyen
como adjuntos del notebook y no dependen de enlaces externos.

## Fuentes definitivas

| Fuente | Alcance |
|---|---|
| `resultados/antecedentes_6cf189c` | Evidencia grupal publicada hasta 14; reemplaza el alcance antiguo de 3b44f21 |
| `resultados/familias_final_20261106` | Cuatro familias completas con diez pares, AUC y ganancia |
| `resultados/ampliaciones_20261107` | Cambios relativos y rankings con veinte pares y baseline canónico común |
| `docs/auditoria_bins_20261107.md` | Corrección de bins y recuperación de un NPY vacío tras el corte Spot |

El notebook verifica los hashes de `snapshot.json`, semillas, calendario, pares
completos, coincidencia entre AUC económica y de entrenamiento, baseline común
y reproducción de las diez semillas originales. Las versiones de entrenamiento
y de documentación son conceptos distintos: el notebook no entrena LightGBM.

## Resultados y lectura de cierre

| Familia | Δ AUC media (20) | Δ banda media M | Favorables banda | Δ N4000 media M |
|---|---:|---:|---:|---:|
| Cambios relativos | -0,000375 | +3,1109 | 15/20 | +3,7950 |
| Rankings con cero fijo | -0,000668 | +0,7599 | 11/20 | +0,8250 |

Cambios relativos conserva ganancia favorable en las diez adicionales
(+1,5214 M); rankings cambia de signo en ese bloque (-0,7293 M). Las dos familias
tienen menor AUC media de veinte. Todo sigue siendo exploratorio en agosto;
más semillas no validan otros meses. Se cierra la tanda sin sumar semillas para
fortalecer un resultado. El ajuste de pesos de historia reciente no se habilitó.

## Regeneración

Desde la raíz del repositorio, con las dependencias de documentación instaladas:

```bash
python -m pip install -r scripts/historia/requirements-documentacion.txt
python scripts/historia/complete_tutoria_template.py --twenty resultados/ampliaciones_20261107 --out docs/estado_grupal_para_tutoria.md
python scripts/historia/complete_tutoria_template.py --twenty resultados/ampliaciones_20261107 --out docs/informe_experimentos_historia.md
python scripts/historia/build_tutoria_notebook.py
python scripts/historia/execute_tutoria_notebook.py
python scripts/historia/build_tutoria_pdf.py
python scripts/historia/package_documentation.py
```

El generador del notebook toma los antecedentes y el cierre del informe de
Ezequiel, además de los agregados: se regenera después del informe. El ejecutor
crea un kernel temporal, guarda salidas reales y lo cierra al terminar. El PDF
usa Arial en Windows; se revisan las páginas renderizadas antes de entregar.
Estos comandos no llaman a los runners ni usan Google Cloud.

## Pendientes reales

- Respuestas de Alejandro y decisión sobre el mensaje del video/baseline de entrega.
- Tablas fuente de los diagnósticos macroeconómicos y segmentos del PDF original.
- Decisiones de integración de ramas y formato final de la entrega.

Autocorrelación y disponibilidad de historia siguen como propuestas sin ejecución,
sin cola activa. Un nuevo experimento temporal requiere protocolo explícito.
El historial permanece en los documentos de contexto; no hay entrenamientos
pendientes de esta tanda.
