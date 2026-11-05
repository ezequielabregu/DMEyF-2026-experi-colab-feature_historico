"""Secciones del informe grupal construidas desde las tablas históricas."""
import csv
from collections import defaultdict
from statistics import mean


def rows(root, name):
    with (root / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def averages(data, metric):
    groups = defaultdict(list)
    for r in data:
        groups[(r['config'], r['foto_mes'])].append(float(r[metric]))
    return {k: mean(v) for k, v in groups.items()}


def comparison_table(root, file, kind='semillas'):
    data = [r for r in rows(root, file) if r['medida'] == kind]
    groups = defaultdict(dict)
    for r in data:
        groups[(r['config'], r['contra'])][r['foto_mes']] = r
    out = ['| Variante | Control | Δ ganancia septiembre M | Δ ganancia octubre M | Δ banda octubre M |', '|---|---|---:|---:|---:|']
    for (config, control), months in groups.items():
        sep, octo = months['201909'], months['201910']
        out.append(f'| {config} | {control} | {float(sep["d_M"]):+.4f} | {float(octo["d_M"]):+.4f} | {float(octo["d_banda_M"]):+.4f} |')
    return out


def auc_table(root, file, configs):
    values = averages(rows(root, file), 'auc')
    out = ['| Configuración | AUC agosto media | AUC septiembre media | AUC octubre media |', '|---|---:|---:|---:|']
    for config in configs:
        out.append('| ' + config + ' | ' + ' | '.join(f'{values[(config,m)]:.6f}' for m in ['201908','201909','201910']) + ' |')
    return out


def sections(root, own):
    lines = [
        '## Alcance del informe grupal', '',
        'Este registro reúne el trabajo disponible de Clara, Ezequiel y Tomás: propuestas, preparación, experimento principal, exploraciones posteriores y nuevas corridas en Google Cloud. La atribución sigue los archivos disponibles: las ideas de clasificación y el protocolo están documentadas como aportes de Clara; los notebooks 01–09 y sus tablas están en la rama de Ezequiel; las réplicas y la nueva serie se ejecutaron en la VM de Tomás. No se atribuye autoría exclusiva de cada conclusión.', '',
        'Los antecedentes se congelan en el commit 3b44f21 de ezequiel/etapa-1. No se afirma que incluya cambios posteriores. Las tablas agregadas se conservan en resultados/antecedentes_3b44f21. Para los experimentos nuevos, el corte temporal figura al inicio.', '',
        '## Mapa de todo lo documentado', '',
        '| Etapa | Trabajo | Evidencia disponible |', '|---|---|---|',
        '| Propuesta de Clara | Clasificación por tipo de variable e historia de 3–6 meses; luego protocolo de resúmenes, rachas, ratios, rankings y canaritos | Documentos y código propuesto; no equivale a una corrida completa de ese protocolo |',
        '| 01 | Clase ternaria, calidad, cobertura y meses rotos | Tablas y controles |',
        '| 02 | Prueba mínima A frente a LT4 con cinco semillas en agosto | Tabla de AUC y ganancia de validación |',
        '| 03–04 | Diez configuraciones, 100 modelos, seis contrastes principales y evaluación | Métricas, regla y figuras |',
        '| 05 | Ensambles y segundas diferencias | Tablas de semillas, ensambles y contrastes |',
        '| 06 | Ratio3, zero_streak3 y combinación | Diez semillas y ensambles |',
        '| 07 | Optimización propia para marzo–junio | Hiperparámetros y comparación con AC |',
        '| 08 | Historia sin quitar meses, historia curada y mezclas | Diez semillas y ensambles |',
        '| 09 | Eventos, ratios entre tarjetas, puntajes y hojas RF | Código; sin resultados publicados en el snapshot revisado |',
        '| Réplica en Google Cloud | Preparación, A y A-consigna con dos semillas | Logs del usuario; coincidencia a precisión mostrada |',
        '| Preparativos no ejecutados | Baseline local y experimento de disponibilidad de historia | Scripts preparados; no se presentan como resultados experimentales |',
        '| Sin historia frente a con historia | 152 frente a 760 columnas, diez semillas | Corrida complementaria en agosto |',
        '| Nuevas cuatro familias | Historia reciente, cambios relativos, persistencia, rankings con cero fijo | Estado y métricas al corte en la sección final |', '',
        '## Controles y métricas que no debemos mezclar', '',
        '| Nombre | Entrenamiento | Ajuste | Uso |', '|---|---|---|---|',
        '| A | Mayo–junio | 50 trials sobre A; 296 árboles | Control del experimento principal adaptado para historia hasta cuatro meses |',
        '| A-consigna / AC | Marzo–junio | Hereda parámetros y 296 árboles de A | Referencia con todos los meses de la consigna; AC agrega saneamiento de dos roturas Master en octubre |',
        '| ACO | Marzo–junio | 50 trials propios; 339 árboles | Baseline reajustado del 07 y control de nuestras cuatro familias |',
        '| AC2 | Marzo–junio | Mezcla de dos semillas del control AC | Control de mezclas por semilla del 08 |', '',
        'Todos estos modelos usan 760 variables de partida. Entrenan con ambas bajas; la AUC reportada por los notebooks usa BAJA+2 como positivo. Ganancia y AUC responden preguntas distintas. La ganancia usa +1.072.500 por BAJA+2 contactado y −27.500 por el resto; N se elige en agosto y se conserva para los meses posteriores. M significa millones de las unidades monetarias del ejercicio.', '',
        'La regla principal evalúa ganancia, no mejora de AUC. Las comparaciones posteriores ya conocen septiembre y octubre: son exploratorias. No corresponde ordenar todas las variantes en una única tabla de ganancia sin respetar sus distintos controles, ventanas y reglas de selección.', '',
        '## Preparación y prueba mínima de los notebooks 01 y 02', '',
        'El crudo contiene 4.707.495 filas, 154 columnas y 185.094 clientes. El corte 2019 tiene 1.563.565 filas, 146.623 clientes y cero claves duplicadas. El 01 construye la clase después de cortar a diciembre de 2019 y detecta 23 casos de variable/mes roto: 17 por regla y 6 manuales. Después se identificaron dos roturas Master adicionales en octubre. El catálogo usa información retrospectiva de calidad; no es un detector estrictamente disponible a cada fecha.', '',
        'La cobertura explica la adaptación de ventana: marzo dispone como máximo de dos meses anteriores; lag6 queda vacío en todo marzo–junio. El principal se limita a mayo–junio para comparar historia hasta cuatro meses; el 08 explora explícitamente conservar marzo–abril aun con historia parcial.', '',
        '| Prueba mínima | Semillas | AUC agosto media | Ganancia meseta agosto media M |', '|---|---:|---:|---:|',
    ]
    minimum = rows(root, '02_minimo_semillas.csv')
    for variant in ['A','LT4']:
        selected = [r for r in minimum if r['variante']==variant]
        lines.append(f'| {variant} | {len(selected)} | {mean(float(r["auc_201908"]) for r in selected):.6f} | {mean(float(r["ganancia_meseta_M"]) for r in selected):.4f} |')
    lines += ['', 'Fue una prueba técnica y exploratoria sobre validación, con 370 árboles. No reemplaza las corridas posteriores de 296 árboles ni ofrece una evaluación independiente.', '',
              '## Experimento principal de los notebooks 03 y 04', '',
              'Se optimizó A una vez y se congelaron sus parámetros para diez configuraciones. L3/L4 añaden lags y deltas; T3/T4 añaden tendencias; LT combina ambas. La ventana de T3 va de t−3 a t (cuatro fotos), y T4 de t−4 a t (cinco). La historia adicional se adapta a montos, conteos, banderas y estados, excluyendo fechas y edad/antigüedad de esas extensiones. Los controles mantienen lag/delta1/2 de todas las variables.', '',
              'Regla: Wilcoxon pareado exacto entre diez semillas y Holm para seis contrastes; diferencia media positiva en octubre y no negativa en septiembre. La banda de N entre 3.000 y 6.000 verifica la dirección. Ninguna variante pasó la regla.', '',
              '| Variante frente a A | Δ ganancia septiembre M | Δ ganancia octubre M | p Holm | Semillas favorables octubre | Pasa regla |', '|---|---:|---:|---:|---:|---|']
    for r in rows(root, '04_regla.csv'):
        lines.append(f'| {r["variante"]} | {float(r["d_media_201909_M"]):+.4f} | {float(r["d_media_201910_M"]):+.4f} | {float(r["p_holm"]):.4f} | {r["semillas_a_favor"]}/10 | {"Sí" if r["gana"]=="True" else "No"} |')
    configs=['A','L3','L4','T3','T4','LT3','LT4','A-ranking','LT4-ranking','A-consigna']
    lines += ['', 'AUC media de cada configuración (la regla anterior se aplica a ganancia):', ''] + auc_table(root,'04_ganancias.csv', configs)
    gains=averages(rows(root,'04_ganancias.csv'),'ganancia_M')
    lines += ['', f'A-consigna frente a A dio {gains[("A-consigna","201909")]-gains[("A","201909")]:+.4f} M en septiembre y {gains[("A-consigna","201910")]-gains[("A","201910")]:+.4f} M en octubre. Esto muestra la importancia práctica de conservar meses, pero mezcla ventana y ajuste: no aísla solo historia.', '',
              'Los rankings simples también se ejecutaron: LT4-ranking mejora frente a A-ranking, pero ese control era débil. Su superioridad sobre un control rankeado no demuestra que supere al nominal. La ausencia de significancia no prueba efecto nulo.', '',
              '## Exploraciones del notebook 05', '',
              'Se promediaron probabilidades de diez semillas y se recalculó N en agosto. Las diferencias frente al ensamble de A son:', '',
              '| Ensamble | Δ ganancia septiembre M | Δ ganancia octubre M |', '|---|---:|---:|']
    ensemble=rows(root,'05_ensamble_vs_A.csv')
    for config in ['L3','L4','T3','T4','LT3','LT4','A-consigna']:
        pair={r['foto_mes']:r for r in ensemble if r['config']==config}
        lines.append(f'| {config} | {float(pair["201909"]["d_M"]):+.4f} | {float(pair["201910"]["d_M"]):+.4f} |')
    lines += ['', 'Son resultados posteriores al principal. Los intervalos de bootstrap de clientes pueden ser amplios; no se interpreta una diferencia puntual en N como confirmación. El ensamble de LT3, por ejemplo, da una ventaja grande en el corte de octubre, pero menor en la banda de cortes.', '',
              'Segundas diferencias: D2 añade la segunda diferencia sobre A; LT3D2 la añade sobre LT3.', '',
              '| Variante | Control | Mes | Δ ganancia M | Δ banda M |', '|---|---|---|---:|---:|']
    for r in rows(root,'05_d2_comparacion.csv'):
        lines.append(f'| {r["config"]} | {r["contra"]} | {r["foto_mes"]} | {float(r["d_media_M"]):+.4f} | {float(r["d_banda_M"]):+.4f} |')
    lines += ['', 'No aparece una mejora clara de segundas diferencias: D2 cambia de signo entre meses y LT3D2 pierde en ambos. No se retiran resultados negativos del registro.', '',
              '## Ratios y rachas del notebook 06', '',
              'AC_R agrega ratio3 = actual/promedio(actual, lag1, lag2); AC_Z agrega racha de ceros en tres fotos; AC_RZ combina ambas. Se aplican a 129 variables de montos/conteos y requieren observaciones completas, conservando NaN cuando no se puede calcular. Se usa marzo–junio, con el ajuste heredado de A.', '',
              'Diferencias de la media entre semillas:', ''] + comparison_table(root,'06_comparacion.csv')
    lines += ['', 'Diferencias de ensambles:', ''] + comparison_table(root,'06_comparacion.csv','ensamble')
    lines += ['', 'AUC media:', ''] + auc_table(root,'06_semillas.csv',['AC','AC_R','AC_Z','AC_RZ'])
    lines += ['', 'Ratio3 mostró señal de ganancia; las rachas solas fueron desfavorables en la media y la banda. La combinación no domina de manera uniforme. Estas observaciones no se convierten automáticamente en una mejora de AUC ni en una validación independiente.', '',
              '## Optimización del control en el notebook 07', '',
              'Se optimizaron parámetros específicamente para marzo–junio (ACO): trial 38, 339 árboles. La mejor AUC de agosto de la búsqueda fue 0,914852804, frente a 0,909510031 del ajuste anterior sobre A. No son medias ni estimaciones independientes: son valores de selección sobre ventanas y búsquedas distintas.', '']
    lines += comparison_table(root,'07_comparacion.csv')
    lines += ['', 'AUC media de ACO:', ''] + auc_table(root,'07_semillas.csv',['ACO'])
    lines += ['', 'La optimización mejora AUC de validación pero la ganancia posterior no mejora frente a AC: aproximadamente −5,9 M de media en octubre. No se elige retrospectivamente el ajuste anterior por ese resultado. Las cuatro familias nuevas usan el ajuste ACO como control congelado y apuntan específicamente a AUC.', '',
              '## Historia sin quitar meses en el notebook 08', '',
              'ACL3/ACL4 agregan lags y tendencias sobre marzo–junio; ACH agrega historia curada sobre 30 variables seleccionadas por importancia de entrenamiento: ratio3, z frente al pasado, relación al máximo previo y ranking mensual del ratio. M_LT3 y M_LT4 mezclan AC con LT3/LT4; M_H mezcla ACH con LT3. Por semilla, las mezclas se comparan contra AC2 (mezcla de dos semillas de AC); los ensambles se comparan contra AC. Por eso no deben confundirse los controles.', '',
              'Diferencias de la media entre semillas:', ''] + comparison_table(root,'08_comparacion.csv')
    lines += ['', 'Diferencias de ensambles:', ''] + comparison_table(root,'08_comparacion.csv','ensamble')
    lines += ['', 'AUC media:', ''] + auc_table(root,'08_semillas.csv',['AC','AC2','ACL3','ACL4','ACH','M_LT3','M_LT4','M_H'])
    lines += ['', 'Hay señales favorables en octubre, especialmente ACH y ciertas mezclas, pero las diferencias y la banda de septiembre son menos favorables. Es evidencia exploratoria dependiente del mes, sin nueva confirmación ciega.', '',
              '## Código del notebook 09 y propuestas sin resultado publicado', '',
              'El 09 implementa cuatro bloques sobre ACH: eventos de pérdida de productos (ACE), ratios Visa/Master (ACR), historia de un puntaje base calculado con pliegues por cliente (ACP) y hojas de Random Forest (ACF). Incluye una combinación (ACX) y un control de ruido (ACK). No hay tablas 09 publicadas en el snapshot; no se afirma ni éxito ni fracaso de esas variantes.', '',
              'El segundo PDF contiene además un protocolo de 20 semillas, resúmenes trimestrales, inactividad, ratios personales, rankings con cero fijo, selección por canaritos y reoptimización final. Es una propuesta con código, no evidencia de que se haya ejecutado íntegramente. Algunas familias se solapan con 06/08/09, pero no deben contabilizarse como corridas adicionales sin sus salidas.', '',
              'También se preparó un script de disponibilidad de historia (foto ausente, nulo y cero observado), pero se priorizaron otras hipótesis antes de ejecutarlo. El baseline local de 30 trials es otra implementación, con decisiones distintas de etiqueta de AUC y predictores; no hay una corrida suya que se incorpore como resultado en este registro.', '',
              '## Réplicas y comparación complementaria en Google Cloud', '',
              'La preparación en la VM pasó controles de filas, clases, duplicados y relectura de parquet. A y A-consigna coincidieron con los valores publicados a la precisión mostrada para las primeras dos semillas. La diferencia de entorno registrada es pandas 2.3.3 frente a 2.2.2; el resto de versiones científicas principales coincide. Esta etapa verifica ejecución, no constituye una mejora.', '',
              'También se completó una ablación sin historia (152 columnas) frente a con historia (760), en marzo–junio, con parámetros del 07 y diez semillas. Es contexto sobre el aporte del baseline, no una mejora sobre la referencia de la cátedra.', '',
              '| Modelo | AUC agosto media | Semillas |', '|---|---:|---:|']
    data=rows(own,'metrics.csv')
    for model in ['sin_historia','con_historia']:
        selected=[r for r in data if r['variant']==model]
        lines.append(f'| {model} | {mean(float(r["auc"]) for r in selected):.6f} | {len(selected)} |')
    base={r['seed']:float(r['auc']) for r in data if r['variant']=='sin_historia'}
    current={r['seed']:float(r['auc']) for r in data if r['variant']=='con_historia'}
    difference=[current[s]-base[s] for s in current]
    lines += ['', f'Diferencia media con − sin: {mean(difference):+.6f} AUC; {sum(d>0 for d in difference)}/{len(difference)} semillas favorables. El ajuste se eligió para con_historia: la ablación con parámetros fijos no compara óptimos independientes.', '',
              '## Síntesis del trabajo previo y preguntas abiertas', '',
              '- El experimento principal no demostró mejora bajo su regla de ganancia; sí hubo diferencias medias favorables frente al control adaptado A.',
              '- Recuperar meses de entrenamiento fue tan importante como extender la historia; no evaluar las features sin identificar el control.',
              '- Ratio3, historia curada y mezclas dejaron señales exploratorias, no una combinación ganadora confirmada en todos los meses y métricas.',
              '- Segundas diferencias y rachas solas no mostraron una ventaja consistente en los contrastes reportados.',
              '- Optimizar AUC no garantiza aumentar ganancia en otro mes.',
              '- Falta resultado publicado del 09 y del protocolo completo del segundo PDF. No confundir ausencia de tabla con resultado negativo.',
              '- Nuestro aporte nuevo evalúa representaciones específicas sobre el control ACO, con objetivo AUC y sin abrir octubre. Sus resultados al corte siguen a continuación.', '',
              '## Serie nueva de cuatro familias', '']
    return lines
