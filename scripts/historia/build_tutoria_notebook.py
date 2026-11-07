"""Notebook de documentación: fuentes actuales y análisis de agregados sin entrenar."""
import argparse
import base64
import json
from pathlib import Path
import re
from textwrap import dedent


def build(out):
    cells = []

    def markdown(text, name):
        attachments = {}
        for alt, reference in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', text):
            path = Path('docs') / reference
            if path.exists():
                text = text.replace(f']({reference})', f'](attachment:{path.name})')
                attachments[path.name] = {'image/png': base64.b64encode(path.read_bytes()).decode()}
        cell = dict(cell_type='markdown', id=name, metadata={}, source=text.splitlines(True))
        if attachments:
            cell['attachments'] = attachments
        cells.append(cell)

    def code(text, name):
        cells.append(dict(cell_type='code', id=name, metadata={}, execution_count=None,
                          outputs=[], source=dedent(text).strip().splitlines(True)))

    markdown('''# Historia de clientes: cierre del experimento grupal

**Documentación actualizada al 7 de noviembre de 2026.** Integrantes: Tomás Henseler, Clara M. Rodríguez y Ezequiel Abregú. Tutor: Alejandro Bolaños.

Recorrido: antecedentes del grupo hasta **6cf189c (01-14)**, cuatro familias completas con diez semillas y ampliaciones auditadas de cambios relativos/rankings con veinte semillas totales por brazo.

Este notebook conserva salidas reales ejecutadas sobre **tablas agregadas**. No necesita dataset, predicciones individuales, credenciales ni VM. No entrena modelos ni abre meses adicionales. Las semillas comparten clientes y agosto: describen variación del algoritmo, no meses independientes.

En el repositorio, ejecutar desde la raíz o desde `notebooks/`. En Colab, abrir este archivo y subir `tutoria_historia_documentacion_20261107.zip` cuando lo pida. Las figuras de antecedentes están incorporadas al notebook. El ZIP solo contiene documentación y agregados.
''', 'intro-cierre')
    report = Path('docs/estado_grupal_para_tutoria.md').read_text(encoding='utf-8')
    strategy_start = report.index('## Dos estrategias de historia evaluadas con veinte semillas')
    prior = report[report.index('## El problema y el baseline'):strategy_start]
    for index, section in enumerate(re.split(r'(?=^## )', prior, flags=re.M)):
        if section.strip():
            markdown(section, f'antecedentes-{index}')
    strategy_end = report.index('### Cómo se compararon', strategy_start)
    markdown(report[strategy_start:strategy_end], 'estrategias-explicadas')

    markdown('''## Cargar y validar los agregados finales

Fuentes: `resultados/familias_final_20261106` (cuatro familias, diez pares), `resultados/ampliaciones_20261107` (dos familias, veinte pares) y `resultados/antecedentes_6cf189c` (antecedentes publicados hasta 14). Las copias parciales y los baselines provisionales no se utilizan.

Control ACO: marzo-junio, validación agosto, 339 árboles y ocho hilos en las corridas. Entrenamiento positivo BAJA+1/BAJA+2; AUC y ganancia positivas solo BAJA+2. Banda inclusiva N=3.000-6.000 y corte común N=4.000.
''', 'contrato-agregados')
    code('''
        from pathlib import Path
        import os, json, zipfile, hashlib
        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        from IPython.display import display, Markdown, Image

        candidates = [Path(os.environ.get('HISTORIA_DOC_ROOT', '.')), Path.cwd().parent]
        ROOT = next((p.resolve() for p in candidates if (p / 'resultados/ampliaciones_20261107/snapshot.json').exists()), None)
        if ROOT is None:
            try:
                from google.colab import files
            except ImportError:
                raise FileNotFoundError('Abrir desde el repositorio o descomprimir el ZIP agregado de documentación.')
            uploaded = files.upload()
            archives = [name for name in uploaded if name.endswith('.zip')]
            if len(archives) != 1:
                raise ValueError('Subir exactamente un ZIP de documentación final.')
            ROOT = Path('tutoria_documentacion').resolve()
            ROOT.mkdir(exist_ok=True)
            with zipfile.ZipFile(archives[0]) as archive:
                for member in archive.infolist():
                    if not (ROOT / member.filename).resolve().is_relative_to(ROOT):
                        raise ValueError('Ruta inválida en el ZIP')
                archive.extractall(ROOT)
        TEN = ROOT / 'resultados/familias_final_20261106'
        TWENTY = ROOT / 'resultados/ampliaciones_20261107'
        OUTPUT = ROOT / 'output/tutoria'
        OUTPUT.mkdir(parents=True, exist_ok=True)
        FAMILIES = ['historia_reciente', 'cambios_relativos', 'persistencia', 'rankings_cero_fijo']
        LABELS = dict(zip(FAMILIES, ['Historia reciente', 'Cambios relativos', 'Persistencia', 'Rankings con cero fijo']))
        EXPANDED = ['cambios_relativos', 'rankings_cero_fijo']
        sources = json.loads((TWENTY / 'snapshot.json').read_text())
        for name, expected in sources['sha256'].items():
            assert hashlib.sha256((TWENTY / name).read_bytes()).hexdigest() == expected, name

        configs, metrics, profits = {}, {}, {}
        for size, folder, families in [(10, TEN, FAMILIES), (20, TWENTY, EXPANDED)]:
            for family in families:
                key = (size, family)
                config = json.loads((folder / family / 'config.json').read_text())
                seeds = config['seeds_used']
                assert len(seeds) == len(set(seeds)) == size
                assert config['train'] == [201903, 201904, 201905, 201906] and config['validation'] == 201908
                table = pd.read_csv(folder / family / 'metrics.csv')
                assert not table.duplicated(['variant', 'seed']).any()
                pivot = table.pivot(index='seed', columns='variant', values='auc')
                assert set(pivot.index) == set(seeds) and set(pivot.columns) == {'baseline', family}
                assert not pivot.isna().any().any() and ((pivot >= 0) & (pivot <= 1)).all().all()
                money = pd.read_csv(folder / family / 'profit_metrics.csv')
                assert len(money[money.kind == 'seed']) == 2 * size and len(money[money.kind == 'ensemble']) == 2
                assert not money[money.kind == 'seed'].duplicated(['variant', 'seed']).any()
                mp = money[money.kind == 'seed'].pivot(index='seed', columns='variant', values='auc')
                np.testing.assert_allclose(mp.loc[pivot.index, pivot.columns], pivot, atol=1e-10, rtol=0)
                if size == 10:
                    assert json.loads((folder / family / 'status.json').read_text())['status'] == 'complete'
                configs[key], metrics[key], profits[key] = config, pivot, money
        for size, families in [(10, FAMILIES), (20, EXPANDED)]:
            reference = metrics[size, families[0]].baseline
            for family in families:
                np.testing.assert_allclose(metrics[size, family].baseline.sort_index(), reference.sort_index(), atol=1e-10, rtol=0)
        for family in EXPANDED:
            assert configs[20, family]['seeds_used'][:10] == configs[10, family]['seeds_used']
            old = metrics[10, family]
            np.testing.assert_allclose(metrics[20, family].loc[old.index, old.columns], old, atol=1e-10, rtol=0)
        for metric in ['auc', 'gain_band_3000_6000_M', 'gain_4000_M']:
            controls = [profits[20, family].query("variant == 'baseline' and kind == 'seed'").set_index('seed')[metric].sort_index() for family in EXPANDED]
            np.testing.assert_array_equal(controls[0], controls[1])
        print('Integridad OK: cuatro familias de diez pares; dos ampliaciones de veinte; baseline compartido y diez originales reproducidas.')
        print('Solo documentación: no se cargaron datos de clientes ni se entrenaron modelos.')
    ''', 'cargar-validar')
    markdown('## Cuatro familias completas: diez semillas\n\nAUC media por semilla y ensamble se informan por separado. Las diferencias se calculan frente al baseline ACO de los mismos pares.', 'diez-auc')
    code('''
        rows = []
        for family in FAMILIES:
            pivot = metrics[10, family]
            delta = pivot[family] - pivot.baseline
            summary = json.loads((TEN / family / 'summary.json').read_text())['ensemble_auc']
            rows.append({'familia': LABELS[family], 'pares': len(delta), 'AUC baseline': pivot.baseline.mean(),
                         'AUC variante': pivot[family].mean(), 'delta AUC media': delta.mean(),
                         'favorables AUC': int((delta > 0).sum()), 'delta AUC ensamble': summary[family] - summary['baseline']})
        auc10 = pd.DataFrame(rows)
        display(auc10.round(6))
        auc10.to_csv(OUTPUT / 'auc_10semillas.csv', index=False)
    ''', 'tabla-auc10')
    markdown('### Ganancia secundaria de agosto\n\n+1.072.500 por BAJA+2 contactado y -27.500 por el resto. La banda y N=4.000 son comunes a todas las familias; no se optimiza N. Esta evaluación económica se decidió después de mirar parte de las AUC.', 'dinero-diez')
    code('''
        rows = []
        for family in FAMILIES:
            summary = json.loads((TEN / family / 'profit_summary.json').read_text())
            band, fixed = summary['gain_band_3000_6000_M'], summary['gain_4000_M']
            rows.append({'familia': LABELS[family], 'delta banda media M': band['mean_delta'],
                         'favorables banda': f"{band['wins']}/10", 'delta banda ensamble M': band['ensemble_delta'],
                         'delta N4000 media M': fixed['mean_delta'], 'delta N4000 ensamble M': fixed['ensemble_delta']})
        profit10 = pd.DataFrame(rows)
        display(profit10.round(4))
        profit10.to_csv(OUTPUT / 'ganancia_10semillas.csv', index=False)
    ''', 'tabla-ganancia10')
    markdown('## Ampliaciones auditadas de veinte semillas\n\nVeinte totales por brazo, no veinte adicionales. Se fijó la cantidad después del resultado económico de diez semillas. La auditoría corrigió la semilla de construcción de bins al reanudar; ambas familias usan el mismo baseline canónico. La variante de rankings dañada durante el corte Spot se recalculó. Los resultados provisionales previos a la auditoría no entran a estas tablas.', 'veinte-contrato')
    code('''
        rows, ensemble_rows, seed_rows = [], [], []
        for family in EXPANDED:
            seeds = configs[20, family]['seeds_used']
            money = profits[20, family]
            pivots = {metric: money[money.kind == 'seed'].pivot(index='seed', columns='variant', values=metric)
                      for metric in ['auc', 'gain_band_3000_6000_M', 'gain_4000_M']}
            for name, subset in [('Originales', seeds[:10]), ('Adicionales', seeds[10:]), ('Total veinte', seeds)]:
                differences = {metric: (pivot[family] - pivot.baseline).loc[subset] for metric, pivot in pivots.items()}
                rows.append({'familia': LABELS[family], 'grupo': name, 'pares': len(subset),
                             'delta AUC media': differences['auc'].mean(),
                             'favorables AUC': int((differences['auc'] > 0).sum()),
                             'delta banda media M': differences['gain_band_3000_6000_M'].mean(),
                             'favorables banda': int((differences['gain_band_3000_6000_M'] > 0).sum()),
                             'delta N4000 media M': differences['gain_4000_M'].mean()})
            ensemble = money[money.kind == 'ensemble'].set_index('variant')
            ensemble_rows.append({'familia': LABELS[family], **{f'delta {metric}': float(ensemble.loc[family, metric] - ensemble.loc['baseline', metric])
                                  for metric in ['auc', 'gain_band_3000_6000_M', 'gain_4000_M']}})
            for position, seed in enumerate(seeds, 1):
                seed_rows.append({'familia': LABELS[family], 'posición': position, 'seed': seed,
                                  'grupo': 'Originales' if position <= 10 else 'Adicionales',
                                  'delta AUC': float(pivots['auc'].loc[seed, family] - pivots['auc'].loc[seed, 'baseline']),
                                  'delta banda M': float(pivots['gain_band_3000_6000_M'].loc[seed, family] - pivots['gain_band_3000_6000_M'].loc[seed, 'baseline'])})
        groups20, ensembles20, differences20 = pd.DataFrame(rows), pd.DataFrame(ensemble_rows), pd.DataFrame(seed_rows)
        display(groups20.round(6))
        display(Markdown('### Ensamble de probabilidades: no es la media de métricas individuales'))
        display(ensembles20.round(6))
        groups20.to_csv(OUTPUT / 'grupos_20semillas.csv', index=False)
        ensembles20.to_csv(OUTPUT / 'ensambles_20semillas.csv', index=False)
        differences20.to_csv(OUTPUT / 'diferencias_20semillas.csv', index=False)
    ''', 'tablas-veinte')
    markdown('### Diferencias por semilla en AUC\n\nCada punto representa una semilla del algoritmo sobre los mismos clientes y agosto. El color distingue originales y adicionales. No es una distribución de efectos entre meses.', 'grafico-auc-texto')
    code('''
        plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
        fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True, constrained_layout=True)
        for ax, family in zip(axes, EXPANDED):
            data = differences20[differences20.familia == LABELS[family]]
            for name, color in [('Originales', '#2563a6'), ('Adicionales', '#c76c1a')]:
                part = data[data.grupo == name]
                ax.scatter(part['posición'], part['delta AUC'], label=name, color=color, s=38)
            ax.axhline(0, color='#64748b', lw=1)
            ax.set(title=LABELS[family], xlabel='Posición en la secuencia fijada')
            ax.set_xticks([1, 5, 10, 15, 20])
            ax.grid(axis='y', alpha=.2)
        axes[0].set_ylabel('AUC variante - baseline')
        axes[1].legend(frameon=False)
        fig.savefig(OUTPUT / 'auc_20semillas.png', dpi=170)
        display(Image(filename=str(OUTPUT / 'auc_20semillas.png')))
        plt.close(fig)
    ''', 'grafico-auc20')
    markdown('### ¿La ganancia se sostiene en las diez adicionales?\n\nMedia de diferencias de banda, en millones del ejercicio. No se muestran intervalos temporales ni se elige el corte más favorable.', 'grafico-dinero-texto')
    code('''
        fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
        x = np.arange(len(EXPANDED))
        for offset, name, color in [(-.24, 'Originales', '#2563a6'), (0, 'Adicionales', '#c76c1a'), (.24, 'Total veinte', '#2a7f6e')]:
            values = [float(groups20[(groups20.familia == LABELS[f]) & (groups20.grupo == name)]['delta banda media M'].iloc[0]) for f in EXPANDED]
            bars = ax.bar(x + offset, values, width=.22, label=name, color=color)
            ax.bar_label(bars, fmt='%+.2f', padding=3, fontsize=9)
        ax.axhline(0, color='#64748b', lw=1)
        ax.set_xticks(x, [LABELS[f] for f in EXPANDED])
        ax.set_ylabel('Diferencia media de banda (M)')
        ax.set_ylim(-1.5, 6)
        ax.legend(frameon=False, ncol=3)
        ax.grid(axis='y', alpha=.15)
        fig.savefig(OUTPUT / 'ganancia_grupos_20semillas.png', dpi=170)
        display(Image(filename=str(OUTPUT / 'ganancia_grupos_20semillas.png')))
        plt.close(fig)
    ''', 'grafico-ganancia20')
    markdown('### Cobertura de las features\n\nFracción de faltantes en agosto calculada durante las corridas. Es un diagnóstico de disponibilidad; no demuestra mejoras en segmentos ni equivale a un experimento de disponibilidad ejecutado.', 'cobertura-texto')
    code('''
        coverage_rows = []
        for family in FAMILIES:
            coverage = pd.read_csv(TEN / family / 'extra_coverage.csv')
            coverage_rows.append({'familia': LABELS[family], 'features extra': len(coverage),
                                  'faltantes promedio': coverage.missing_fraction.mean(),
                                  'faltantes máximo': coverage.missing_fraction.max()})
        display(pd.DataFrame(coverage_rows).round(4))
    ''', 'cobertura')
    start = report.index('### Cierre de esta tanda y lectura para tutoría')
    stop = report.index('## Por qué está trabado', start)
    markdown(report[start:stop], 'conclusiones-cierre')
    markdown('''## Trazabilidad y estado de cierre

- Fuentes grupales actuales: `6cf189c`; `3b44f21` es solo un antecedente histórico, no la fuente vigente de 09-14.
- Auditoría: `docs/auditoria_bins_20261107.md`. Los NPY y claves de clientes permanecen en VM/bucket; este notebook solo utiliza agregados.
- No quedan entrenamientos pendientes ni reanudación automática. Los respaldos de las dos ampliaciones se verificaron y la VM quedó apagada.
- Historia reciente no habilitó búsqueda de pesos por su resultado de AUC. Autocorrelación y disponibilidad son propuestas no ejecutadas, sin cola activa.
- Siguen pendientes las respuestas del tutor y tablas fuente de diagnósticos macro/segmentos. La bibliografía metodológica se verificó con fuentes primarias. No se atribuyen al tutor respuestas inventadas.
- Septiembre/octubre ya fueron consultados por el grupo; noviembre/diciembre siguen reservados para dashboard. Un nuevo experimento requiere protocolo explícito.

Las versiones impresas debajo son las de **entrenamiento**, conservadas en config.json. El entorno actual del notebook solo calcula tablas y gráficos y no tiene que reproducir esas versiones para volver a entrenar.
''', 'trazabilidad-cierre')
    code('''
        version_rows = []
        for family in EXPANDED:
            version_rows.append({'familia': LABELS[family], **configs[20, family]['versions']})
        display(pd.DataFrame(version_rows))
        print('SHA256 de los agregados verificados:', len(sources['sha256']))
        print('Salidas de documentación:', OUTPUT)
    ''', 'trazabilidad-versiones')
    bibliography = Path('docs/bibliografia_historia.md')
    if bibliography.exists():
        markdown(bibliography.read_text(encoding='utf-8').replace('# Bibliografía', '## Bibliografía', 1), 'bibliografia-verificada')
    notebook = dict(cells=cells, nbformat=4, nbformat_minor=5,
                    metadata=dict(colab={'name': 'Tutoría - historia de clientes - cierre 20261107.ipynb'},
                                  kernelspec={'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                                  language_info={'name': 'python', 'version': '3.14'}))
    for cell in cells:
        if cell['cell_type'] == 'code':
            compile(''.join(cell['source']), cell['id'], 'exec')
    out.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{out}: {len(cells)} celdas')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('notebooks/tutoria_historia.ipynb'))
    build(parser.parse_args().out)
