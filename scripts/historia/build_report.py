"""Genera el informe versionable desde un snapshot agregado real."""
import argparse
import csv
import html
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from statistics import mean
try:
    from .group_history_report import sections as group_sections
except ImportError:
    from group_history_report import sections as group_sections

FAMILIES = {
    'historia_reciente': ('Historia reciente', 387, 'Dar mayor peso a las fotos recientes: media 4:2:1 y comparación con pasado ponderado 2:1.'),
    'cambios_relativos': ('Cambios relativos', 258, 'Medir cambios proporcionales simétricos de uno y dos meses, con valores finitos acotados entre −1 y 1.'),
    'persistencia': ('Persistencia y reversión', 516, 'Separar dos caídas, dos subidas, reversión y aceleración relativa en tres fotos.'),
    'rankings_cero_fijo': ('Rankings con cero fijo', 365, 'Comparar la posición del cliente dentro del mes y signo, y su cambio en uno y dos meses.'),
}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def render_html(markdown):
    """Renderiza el subconjunto de Markdown que genera este informe."""
    def inline(text):
        text = html.escape(text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', text)
        return re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    out, table, listing = [], False, False
    for line in markdown.splitlines():
        if table and not line.startswith('|'):
            out.append('</tbody></table></div>')
            table = False
        if listing and not line.startswith('- '):
            out.append('</ul>')
            listing = False
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                continue
            if not table:
                out.append('<div class="table"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells) + '</tr></thead><tbody>')
                table = True
            else:
                out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
        elif re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line):
            match = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            out.append(f'<figure><img src="{html.escape(match[2], quote=True)}" alt="{html.escape(match[1], quote=True)}"><figcaption>{html.escape(match[1])}</figcaption></figure>')
        elif line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            out.append(f'<h{level}>{inline(line[level:].strip())}</h{level}>')
        elif line.startswith('- '):
            if not listing:
                out.append('<ul>')
                listing = True
            out.append(f'<li>{inline(line[2:])}</li>')
        elif line.strip():
            out.append(f'<p>{inline(line)}</p>')
    if table:
        out.append('</tbody></table></div>')
    if listing:
        out.append('</ul>')
    return '''<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Informe grupal de experimentos de historia</title>
<style>body{font:16px/1.6 system-ui,sans-serif;color:#202833;margin:0;background:#f5f6f8}
main{max-width:1080px;margin:auto;background:white;padding:36px 42px}h1{font-size:30px;line-height:1.2}
h2{font-size:23px;margin-top:36px}h3{font-size:19px;margin-top:28px}p{max-width:95ch}
.table{overflow-x:auto;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border:1px solid #d9dfe5;padding:10px 12px;text-align:left;vertical-align:top}
th{background:#edf2f7}tbody tr:nth-child(even){background:#fafbfd}code{overflow-wrap:anywhere}
li{margin:8px 0}figure{margin:24px 0}img{max-width:100%;height:auto}figcaption{font-size:13px;color:#526070}@media print{body{background:white}main{max-width:none;padding:0}
.table{overflow:visible}thead{display:table-header-group}tr{break-inside:avoid}h2,h3{break-after:avoid}}
</style><main>''' + '\n'.join(out) + '</main></html>'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--prior', type=Path, default=Path('resultados/antecedentes_3b44f21'))
    p.add_argument('--own-comparison', type=Path, default=Path('resultados/sin_con_historia_10semillas'))
    args = p.parse_args()
    snapshot = read_json(args.results / 'snapshot.json')
    captured = snapshot.get('captured_utc', datetime.now(timezone.utc).isoformat())
    lines = [
        '# Informe grupal de experimentos de historia', '',
        f'**Corte de resultados:** {captured} (UTC). Informe regenerable desde las tablas del snapshot.', '',
        'Registro conjunto del trabajo de Clara, Ezequiel y Tomás sobre feature engineering histórico. Reúne propuestas, corridas realizadas, resultados positivos y negativos, réplicas y tareas pendientes. Distingue la regla principal de ganancia, las exploraciones posteriores y nuestra serie actual orientada a AUC. Una corrida parcial no se clasifica como éxito ni como fracaso.', '',
        '## Qué sabemos antes de estas pruebas', '',
        'El baseline ya contiene las 152 variables actuales más lag1, lag2, delta1 y delta2: 760 predictores. Reprodujimos los controles A (mayo–junio) y A-consigna (marzo–junio) con dos semillas, con coincidencia a la precisión mostrada. Esa verificación no fue un experimento de mejora.', '',
        'En el trabajo previo de Ezequiel se probaron lags/deltas de orden 3 y 4, tendencias, rankings simples, segundas diferencias, ratio3, rachas de ceros, historia curada y mezclas. Ninguna de las seis variantes principales superó su regla con corrección Holm frente a A; LT3 fue la más cercana (p ajustado 0,0703). Las señales posteriores de ganancia fueron exploratorias y no equivalen a mejoras confirmadas de AUC. El notebook 09 contiene otras propuestas implementadas, sin resultados publicados en el snapshot revisado.', '',
        'Fuentes de antecedentes: código y tablas de la rama ezequiel/etapa-1, commit 3b44f21; detalle en docs/revision_experimentos_20261104.md. Las métricas nuevas de este informe provienen de nuestras corridas, no de esas tablas.', '',
        '## Diseño que mantuvimos fijo', '',
        '| Elemento | Definición |', '|---|---|',
        '| Dataset | competencia_02_crudo.csv.gz; parquet 2019 preparado y verificado |',
        '| Entrenamiento | Marzo–junio, 506.871 filas, sin sampling |',
        '| Etiqueta de entrenamiento | BAJA+1 o BAJA+2 frente a CONTINUA |',
        '| Evaluación | Agosto de 2019, 131.775 filas; AUC positiva BAJA+2 |',
        '| Control | 760 predictores, sin ID ni foto_mes como features |',
        '| Ajuste | Parámetros del 07, 339 árboles, max_bin 31, bagging_freq 1 |',
        '| Semillas | Diez por brazo; iguales entre baseline y variante |',
        '| Recursos | Ocho hilos; cuatro familias ejecutadas secuencialmente |',
        '| Faltantes | NaN; mismas filas en ambos brazos; saneamiento antes de calcular historia |',
        '| Meses cargados | Enero–agosto; no se consultó octubre en estas pruebas |', '',
        '## Qué probamos', '', '| Familia | Nuevas columnas | Pregunta |', '|---|---:|---|',
    ]
    antecedent = lines.index('## Qué sabemos antes de estas pruebas')
    current_design = lines.index('## Diseño que mantuvimos fijo')
    lines = lines[:antecedent] + group_sections(args.prior, args.own_comparison) + lines[current_design:]
    for _, (label, count, hypothesis) in FAMILIES.items():
        lines.append(f'| {label} | {count} | {hypothesis} |')
    lines += ['', 'Las tres primeras familias transforman información ya contenida en las tres fotos; buscamos una representación que LightGBM aproveche mejor. Los rankings incorporan además la distribución contemporánea del conjunto de clientes. Las fórmulas exactas se fijaron antes de correr en docs/experimentos_historia.md.', '',
              '## Resultados al corte', '',
              'Las medias siguientes usan únicamente semillas emparejadas. Si hay tres variantes y diez baselines, se comparan esos tres pares, no medias de tamaños diferentes. La diferencia está en unidades de AUC; +0,001 equivale a pasar de 0,912 a 0,913.', '',
              '| Familia | Estado | Pares | AUC control | AUC variante | Diferencia media | A favor |',
              '|---|---|---:|---:|---:|---:|---:|']
    details = []
    for family, (label, _, _) in FAMILIES.items():
        folder = args.results / family
        path = folder / 'metrics.csv'
        rows = list(csv.DictReader(path.open(encoding='utf-8'))) if path.exists() else []
        keys = [(r['variant'], int(r['seed'])) for r in rows]
        if len(keys) != len(set(keys)):
            raise ValueError(f'Métricas duplicadas en {family}')
        baseline = {int(r['seed']): float(r['auc']) for r in rows if r['variant'] == 'baseline'}
        variant = {int(r['seed']): float(r['auc']) for r in rows if r['variant'] == family}
        paired = sorted(baseline.keys() & variant.keys())
        complete = read_json(folder / 'status.json').get('status') == 'complete'
        if complete and len(paired) != 10:
            raise ValueError(f'Estado completo sin diez pares en {family}')
        if not paired:
            lines.append(f'| {label} | {"En curso" if rows else "Pendiente"} | 0/10 | — | — | — | — |')
            continue
        deltas = [variant[s] - baseline[s] for s in paired]
        state = 'Completo' if complete else 'Parcial'
        lines.append(f'| {label} | {state} | {len(paired)}/10 | {mean(baseline[s] for s in paired):.6f} | {mean(variant[s] for s in paired):.6f} | {mean(deltas):+.6f} | {sum(d > 0 for d in deltas)}/{len(paired)} |')
        details += ['', f'### {label}', '', '| Semilla | AUC control | AUC variante | Diferencia |', '|---|---:|---:|---:|']
        for s in paired:
            details.append(f'| {s} | {baseline[s]:.9f} | {variant[s]:.9f} | {variant[s]-baseline[s]:+.9f} |')
        if not complete:
            details += ['', f'**Avance parcial:** {len(variant)}/10 variantes y {len(baseline)}/10 baselines. No cerrar una conclusión ni detener la prueba por estos resultados.']
        else:
            summary = read_json(folder / 'summary.json')
            ensemble = summary['ensemble_auc']
            details += ['', f'AUC del ensamble: control {ensemble["baseline"]:.6f}; variante {ensemble[family]:.6f}; diferencia {ensemble[family]-ensemble["baseline"]:+.6f}.', '',
                        'Lectura descriptiva: ' + ('la media entre semillas es favorable' if mean(deltas)>0 else 'la media entre semillas no mejora el control') + '. Esto no demuestra generalización a otros períodos.']
    lines += details
    lines += ['', '## Qué resultó y qué no podemos afirmar todavía', '',
              'Las familias pendientes no tienen un resultado negativo: todavía no fueron evaluadas. Las filas parciales muestran avance del entrenamiento, no una conclusión final. Cuando estén completos los diez pares, reportaremos conjuntamente la diferencia media, la dirección por semilla y el cambio en AUC del ensamble.', '',
              'No se elegirá una familia por una semilla favorable. Tampoco se confundirá una mejora de ganancia económica de antecedentes con una mejora de AUC en esta comparación.', '',
              '## Decisiones y siguientes pasos', '',
              '- Terminar las cuatro familias y conservar también resultados negativos.',
              '- Ajustar el decaimiento solo si historia reciente presenta una señal favorable al completar diez semillas, considerando media, consistencia y ensamble. No se fijó un umbral numérico formal: cualquier criterio nuevo debe registrarse antes de la búsqueda, no reconstruirse como si hubiera sido predefinido.',
              '- Si se habilita esa búsqueda, seleccionar alfa dentro de una partición temporal interna al bloque de entrenamiento, respetando las etiquetas a dos meses; reentrenar marzo–junio y evaluar la elección en agosto. No usar agosto para elegir alfa.',
              '- No modificar la cola ni los pesos actuales a partir de resultados parciales.', '',
              '## Límites de la evidencia', '',
              'Agosto ya se usó para optimizar el baseline y discutir otras variantes. Sigue siendo validación exploratoria, aunque una búsqueda posterior de alfa use otro bloque. Los parámetros del 07 favorecen potencialmente al baseline: aquí medimos el efecto de agregar features con ese ajuste fijo, no modelos optimizados individualmente. Las diez semillas comparten clientes y mes; su dispersión no mide incertidumbre entre períodos. Comparar cuatro familias introduce selección múltiple. El catálogo de roturas fue construido retrospectivamente y no representa una política estrictamente disponible en tiempo real.', '',
              '## Trazabilidad', '',
              'Cada experimento conserva config.json con hashes SHA-256, versiones y semillas; metrics.csv con AUC por modelo; summary.json con el ensamble; extra_coverage.csv con faltantes; y status.json al completar. El paquete para tutoría no contiene datos individuales. El notebook notebooks/tutoria_historia.ipynb permite revisar estas tablas y visualizar las diferencias.', '',
              'Corrida: familias_c9930bd. Código desplegado: c9930bd. Rama: feat/historia-transformaciones. El informe y el notebook pueden evolucionar sin modificar el código de la corrida en curso.', '']
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text('\n'.join(lines), encoding='utf-8')
    args.out.with_suffix('.html').write_text(render_html('\n'.join(lines)), encoding='utf-8')
    print(args.out)


if __name__ == '__main__':
    main()
