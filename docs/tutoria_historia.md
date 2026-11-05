# Tutoría: cuatro experimentos históricos

Notebook: `notebooks/tutoria_historia.ipynb`. Puede abrirse con Jupyter o subirse a Google Colab mediante Archivo → Subir notebook. No requiere dataset, entrenamiento ni credenciales de Google Cloud para presentar las tablas.

## Para mostrar en clase

1. Descargar `tutoria_resultados.zip` del prefijo de la corrida en el bucket.
2. Abrir el notebook en Colab, ejecutar las celdas y subir ese ZIP cuando lo pida.
3. Recorrer contrato experimental → tabla de AUC → diferencias por semilla → cobertura → discusión.

El paquete contiene exclusivamente métricas, configuración, cobertura y logs; no IDs ni predicciones individuales. Los resultados parciales se identifican como pendientes. El notebook exige diez pares completos por experimento y verifica que los baselines coincidan entre familias antes de comparar. Genera `resumen_tutoria.csv` y `diferencias_auc.png` para compartir.

El notebook no incluye resultados inventados ni conclusiones anticipadas. Su ejecución con resultados reales y la revisión visual de los gráficos quedan para cuando termine al menos una familia.

## Cola en la VM

`scripts/historia/run_batch.py` ejecuta las familias secuencialmente, diez semillas por brazo (80 modelos en total). Historia reciente primero. Espera la corrida previa sin/con historia para no competir por CPU. Si una familia falla, conserva el log y continúa con las demás; el estado final lo indica.

Cada familia conserva su propio baseline, así puede ejecutarse también de forma independiente. No cambia el protocolo según los resultados de las primeras familias. El respaldo del ZIP agregado se actualiza en el bucket después de cada experimento; los archivos individuales grandes permanecen en el disco de la VM.

La cola está desacoplada de SSH con nohup; cerrar la conexión no la interrumpe. Detener la VM sí interrumpe el entrenamiento. No tiene reanudación automática: antes de relanzar revisar estado y usar una nueva carpeta para cualquier experimento incompleto.
