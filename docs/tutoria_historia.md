# Tutoría: cuatro experimentos históricos

Notebook: `notebooks/tutoria_historia.ipynb`. Puede abrirse con Jupyter o subirse a Google Colab mediante Archivo → Subir notebook. No requiere dataset, entrenamiento ni credenciales de Google Cloud para presentar las tablas.

## Para mostrar en clase

1. Descargar `tutoria_resultados.zip` del prefijo de la corrida en el bucket.
2. Abrir el notebook en Colab, ejecutar las celdas y subir ese ZIP cuando lo pida.
3. Recorrer contrato experimental → tabla de AUC → diferencias por semilla → cobertura → discusión.

El paquete contiene exclusivamente métricas, configuración, cobertura y logs; no IDs ni predicciones individuales. Los resultados parciales se identifican como pendientes. El notebook exige diez pares completos por experimento y verifica que los baselines coincidan entre familias antes de comparar. Genera `resumen_tutoria.csv` y `diferencias_auc.png` para compartir.

El notebook no incluye resultados inventados ni conclusiones anticipadas. Su ejecución con resultados reales y la revisión visual de los gráficos quedan para cuando termine al menos una familia.

Actualización: el notebook ya fue ejecutado con un snapshot real parcial y conserva sus tablas visibles. Muestra progreso y medias calculadas solo sobre pares disponibles; los gráficos finales siguen reservados para familias completas. El informe narrativo está en `docs/informe_experimentos_historia.md` y su versión para navegador en `docs/informe_experimentos_historia.html`.

Alcance grupal: el informe cubre las propuestas y etapas 01–09 de los compañeros, las réplicas, la comparación sin/con historia y las cuatro familias nuevas. El notebook incorpora un recorrido de antecedentes con las tablas principales y exploratorias; el informe contiene el detalle completo de métricas y controles. Los antecedentes y sus hashes están congelados en `resultados/antecedentes_3b44f21`; la comparación complementaria terminada está en `resultados/sin_con_historia_10semillas`. El generador requiere esas carpetas además del snapshot de la serie nueva.

Para regenerar el informe desde un paquete actualizado, descomprimirlo en `resultados/familias_c9930bd` y ejecutar:

```bash
python scripts/historia/complete_tutoria_template.py --results resultados/familias_20261106 --out docs/informe_experimentos_historia.md
```

El exportador `scripts/historia/export_results.py` permite capturar un snapshot antes de que termine toda la cola, sin incluir predicciones ni identificadores. La condición de ajustar alfa solo si aparece señal en historia reciente figura tanto en el notebook como en el informe y el protocolo.

El archivo principal `informe_experimentos_historia.html` ahora usa también la estructura del PDF nuevo, incluye antecedentes hasta 14 y la sección de ganancia económica de agosto con tabla y gráfico. `estado_grupal_para_tutoria.html` conserva la misma versión de trabajo. La evaluación económica entra al paquete con `--profit`; rankings se agregará cuando termine la evaluación final automática.

## Cola en la VM

`scripts/historia/run_batch.py` ejecuta las familias secuencialmente, diez semillas por brazo (80 modelos en total). Historia reciente primero. Espera la corrida previa sin/con historia para no competir por CPU. Si una familia falla, conserva el log y continúa con las demás; el estado final lo indica.

Cada familia conserva su propio baseline, así puede ejecutarse también de forma independiente. No cambia el protocolo según los resultados de las primeras familias. El respaldo del ZIP agregado se actualiza en el bucket después de cada experimento; los archivos individuales grandes permanecen en el disco de la VM.

La cola está desacoplada de SSH con nohup; cerrar la conexión no la interrumpe. Detener la VM sí interrumpe el entrenamiento. No tiene reanudación automática: antes de relanzar revisar estado y usar una nueva carpeta para cualquier experimento incompleto.

## Corrida iniciada el 5/11/2026

- Versión desplegada: commit `c9930bd`, con manifiesto SHA-256.
- Código aislado en VM: `/home/tomas_henseler/historia_c9930bd`.
- Salidas: `/home/tomas_henseler/experimento_historia/exp/familias_c9930bd`.
- Log de cola: `/home/tomas_henseler/experimento_historia/familias_c9930bd.log`.
- Estado: `exp/familias_c9930bd/batch_status.json`.
- Respaldo agregado: `gs://tomas_henseler_buckito2026/exp/familias_c9930bd/tutoria_resultados.zip`, disponible después de completar la primera familia.
- Comprobación inicial: cinco tests pasaron; Jupyter leyó y convirtió el notebook sin errores; cola activa con `historia_reciente` como primera familia. Resultados todavía pendientes al registrar este estado.

Para descargar el paquete a la computadora al terminar:

```bash
gcloud storage cp gs://tomas_henseler_buckito2026/exp/familias_c9930bd/tutoria_resultados.zip .
```
