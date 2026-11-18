"""Cifras y figuras del video del grupo feature_historico.

Todo sale de video/datos/*.csv (ver video/preparar_datos.py, que dice de dónde viene cada tabla).
Ningún número del deck se tipea a mano: si un CSV cambia, se vuelve a renderizar.

Uso desde el .qmd:
    from figuras import C, fig_recetas, mostrar
    mostrar(fig_recetas())
    `{python} C['paq_d']`

Diseño (skill dataviz):
- Un color por pipeline en todo el video: recetas = azul, acumulativo = naranja, regla y branches = violeta
  (paleta validada para fondo oscuro: validate_palette.js, 3 slots, todo PASS).
- El resto en gris; texto en tintas neutras, nunca del color de la serie.
- Sin grilla, etiquetas directas y selectivas; un solo eje.
- La dispersión de las 39 recetas es interactiva (hover); las demás figuras son estáticas.
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

DATOS = Path(__file__).resolve().parent.parent / 'datos'

# ---- Paleta (modo oscuro)
FONDO = '#111110'
SUPERFICIE = '#1a1a19'
TINTA = '#f0efec'
TINTA_2 = '#c3c2b7'
TINTA_MUTED = '#898781'
GRIS = '#3a3a37'
GRIS_CLARO = '#6b6a65'
RECETAS = '#3987e5'      # pipeline de recetas (v10)
ACUMULATIVO = '#d95926'  # pipeline acumulativo (main)
REGLA = '#9085e9'        # regla de merge, branches
BIEN = '#0ca30c'         # estado: pasa (siempre con ícono y texto)
MAL = '#e66767'          # estado: no pasa / pierde (siempre con ícono y texto)
FUENTE = 'system-ui, -apple-system, "Segoe UI", sans-serif'

ANCHO, ALTO = 1100, 720
ESTATICA = {'staticPlot': True, 'displayModeBar': False, 'responsive': False}
INTERACTIVA = {'displayModeBar': False, 'responsive': False, 'scrollZoom': False}


# ---------------------------------------------------------------- formato

def f(x, d=1, signo=False):
    """Número con coma decimal y punto de miles; signo opcional (con el menos tipográfico)."""
    s = f'{abs(x):,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    if x < 0:
        return '−' + s
    return ('+' + s) if signo else s


# ---------------------------------------------------------------- datos

def _csv(nombre):
    return pd.read_csv(DATOS / nombre)


NOMBRES = {
    'slope': 'Tendencia', 'max': 'Máximo', 'min': 'Mínimo', 'mean': 'Promedio', 'range': 'Rango',
    'rel_mean': 'Relativo al promedio', 'rel_prev': 'Relativo al mes anterior', 'rel_first': 'Relativo al primer mes',
}
SUELTOS = {
    'rank_actual': 'Ranking del mes', 'rank_historia': 'Historia de rankings', 'rr4_zero_run': 'Racha de ceros',
    'rr4_nonzero_run': 'Racha de no ceros', 'rr4_recency': 'Recencia', 'apago1': 'Apagado', 'prendio1': 'Encendido',
    'caidas3': 'Caídas', 'disponibilidad': 'Disponibilidad',
}


def nombre_receta(r):
    if r in SUELTOS:
        return SUELTOS[r]
    if r.startswith(('lag', 'delta')):
        return r.replace('lag', 'Lag ').replace('delta', 'Delta ')
    base, w = r.rsplit('_W', 1)
    return f'{NOMBRES[base]}, {w} meses'


def _v10():
    v = _csv('v10_resultados.csv')
    v = v[v['recipe'] != 'v5__B0']
    t = v.pivot(index='recipe', columns='month', values=['delta', 'positive_seeds'])
    t.columns = [f'{a}_{b}' for a, b in t.columns]
    t = t.rename(columns={'delta_201909': 'sep', 'delta_201910': 'oct',
                          'positive_seeds_201909': 'sem_sep', 'positive_seeds_201910': 'sem_oct'})
    t[['sep', 'oct']] = t[['sep', 'oct']] / 1e6
    t['nombre'] = [nombre_receta(r) for r in t.index]
    t['crudo'] = [r.startswith(('lag', 'delta')) for r in t.index]
    return t.reset_index()


V10 = _v10()
_B0 = _csv('v10_resultados.csv').query("recipe == 'v5__B0'").set_index('month')['gain'] / 1e6

_paq = _csv('paq_p3_comparacion.csv').set_index('contra')
_rango = _csv('rango_comparacion.csv').iloc[0]
_opt = _csv('optuna_comparacion.csv').iloc[0]
_bandas = _csv('bandas_ensemble.csv').set_index(['config', 'foto_mes'])['banda_ensemble_M']
_ex = {n: _csv(f'exploratorio/{n}.csv') for n in
       ['04_regla', '12_comparacion', '15_comparacion', '17_comparacion', '20_comparacion',
        '22_comparacion', '23_comparacion', '23_reevaluacion']}
_inf = _csv('cifras_del_informe.csv').set_index('cifra')['valor']


def _fila(tabla, **cond):
    t = _ex[tabla]
    for k, val in cond.items():
        t = t[t[k] == val]
    assert len(t) == 1, (tabla, cond, len(t))
    return t.iloc[0]


_ach = _fila('15_comparacion', config='ACH', contra='AC')
_ventana = _fila('15_comparacion', config='ACH_4_F', contra='ACH_4')
_mv = _fila('17_comparacion', config='ACH_4_MVH_P3', contra='ACH_4_P3')
_rel = _fila('20_comparacion', config='ACH_4_R_P3', contra='ACH_4_P3')
_juntos = _fila('22_comparacion', config='PAQ_P3', contra='ACH_4_P3')
_conf23 = _fila('23_comparacion', config='ELEGIDA', meses='201909-10')
_reev23 = _ex['23_reevaluacion'].sort_values('busqueda_contra_vigente_M', ascending=False).iloc[0]
_t4 = _fila('04_regla', variante='T4')
_sin_hist = _ex['12_comparacion'].query("medida == 'semillas' and config == 'AC' and contra == 'ACS'")

_ambos_mas = V10[(V10.sep > 0) & (V10.oct > 0)]
_ambos_menos = V10[(V10.sep < 0) & (V10.oct < 0)]
_arriba_izq = V10[(V10.sep < 0) & (V10.oct > 0)]
_abajo_der = V10[(V10.sep > 0) & (V10.oct < 0)]
_crudos_ambos = V10[V10.crudo & (V10.sep > 0) & (V10.oct > 0)]


def _rec(r):
    return V10.set_index('recipe').loc[r]


DESTACADAS = ['slope_W4', 'max_W6', 'range_W6']
MESES = {201906: 'junio', 201907: 'julio', 201908: 'agosto', 201909: 'septiembre', 201910: 'octubre'}

C = {
    # v10
    'n_recetas': len(V10),
    'n_ambos_mas': len(_ambos_mas), 'n_ambos_menos': len(_ambos_menos),
    'n_mixtas': len(_arriba_izq) + len(_abajo_der),
    'n_arriba_izq': len(_arriba_izq), 'n_abajo_der': len(_abajo_der),
    'n_azar': f(len(V10) / 4, 0),
    'n_crudos_ambos': len(_crudos_ambos),
    'b0_sep': f(_B0[201909]), 'b0_oct': f(_B0[201910]),
    **{f'{r}_{m}': f(_rec(r)[m], 1, True) for r in DESTACADAS for m in ('sep', 'oct')},
    **{f'{r}_sem_{m}': f'{int(_rec(r)[f"sem_{m}"])}/5' for r in DESTACADAS for m in ('sep', 'oct')},
    # pipeline acumulativo: PAQ_P3 contra AC y A-consigna
    'paq_d': f(_paq.loc['AC', 'd_M'], 1, True),
    'paq_ic': f"{f(_paq.loc['AC', 'ic95_inf_M'])} a {f(_paq.loc['AC', 'ic95_sup_M'])}",
    'paq_sem': f"{int(_paq.loc['AC', 'semillas_a_favor'])} de 5",
    'paq_consigna': f(_paq.loc['A_CONSIGNA', 'd_M'], 1, True),
    'paq_min_mes': f(min(_paq.loc['AC', f'd_{m}'] for m in MESES), 0),
    'paq_max_mes': f(max(_paq.loc['AC', f'd_{m}'] for m in MESES), 0),
    'ach': f(_ach['d_M'], 1, True), 'ventana': f(_ventana['d_M'], 1, True),
    'mv': f(_mv['d_M'], 1, True), 'rel': f(_rel['d_M'], 1, True), 'juntos': f(_juntos['d_M'], 1, True),
    'busq23': f(_reev23['busqueda_contra_vigente_M'], 2, True),
    'reev23': f(_reev23['reevaluacion_4_contra_vigente_M'], 2, True),
    'conf23': f(_conf23['d_M'], 2, True),
    't4_sep': f(_t4['d_media_201909_M'], 1, True), 't4_oct': f(_t4['d_media_201910_M'], 1, True),
    'sin_historia': f(_sin_hist['d_banda_M'].mean(), 0),
    'lags12_min': int(_inf['lags12_pct_min']), 'lags12_max': int(_inf['lags12_pct_max']),
    # branches
    'rango_d': f(_rango['d_M'], 2, True),
    'rango_ic': f"{f(_rango['ic95_inf_M'])} a {f(_rango['ic95_sup_M'])}",
    'rango_sem': f"{int(_rango['semillas_a_favor'])} de 5", 'rango_veredicto': _rango['veredicto'],
    'opt_d': f(_opt['d_M'], 2, True),
    'opt_ic': f"{f(_opt['ic95_inf_M'])} a {f(_opt['ic95_sup_M'], 1, True)}",
    'opt_sem': f"{int(_opt['semillas_a_favor'])} de {int(_opt['n_semillas'])}",
    # bandas del ensemble (misma métrica que el v10)
    'ac_sep': f(_bandas[('AC', 201909)]), 'ac_oct': f(_bandas[('AC', 201910)]),
}


# ---------------------------------------------------------------- utilidades de plotly

def mostrar(fig, interactiva=False):
    fig.show(config=INTERACTIVA if interactiva else ESTATICA)


def _base(fig, ancho=ANCHO, alto=ALTO, **kw):
    kw.setdefault('margin', dict(l=20, r=20, t=20, b=20))
    fig.update_layout(width=ancho, height=alto, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(family=FUENTE, size=24, color=TINTA_2), showlegend=False, **kw)
    return fig


def _texto(fig, x, y, texto, size=24, color=TINTA_2, **kw):
    fig.add_annotation(x=x, y=y, text=texto, showarrow=False, font=dict(family=FUENTE, size=size, color=color), **kw)


# ---------------------------------------------------------------- figuras

def fig_recetas():
    """Los 39 experimentos: ganancia sobre el baseline en septiembre (x) y en octubre (y). Interactiva."""
    v = V10.copy()
    lim = max(v[['sep', 'oct']].abs().max()) * 1.18
    fig = go.Figure()
    # cuadrante "gana en los dos meses", apenas sombreado
    fig.add_shape(type='rect', x0=0, y0=0, x1=lim, y1=lim, fillcolor=RECETAS, opacity=0.07, line_width=0, layer='below')
    for eje in ('x', 'y'):
        fig.add_shape(type='line', xref='x', yref='y',
                      x0=0 if eje == 'x' else -lim, x1=0 if eje == 'x' else lim,
                      y0=-lim if eje == 'x' else 0, y1=lim if eje == 'x' else 0,
                      line=dict(color=GRIS_CLARO, width=2))
    plantilla = '<b>%{customdata[0]}</b><br>Septiembre: %{x:+.2f} M · semillas %{customdata[1]}/5' \
                '<br>Octubre: %{y:+.2f} M · semillas %{customdata[2]}/5<extra></extra>'
    grupos = [
        (v[~v.crudo & ~v.recipe.isin(DESTACADAS)], dict(color=GRIS_CLARO, size=16, line=dict(color=FONDO, width=2))),
        (v[v.crudo], dict(color=FONDO, size=16, line=dict(color=TINTA_MUTED, width=2.5))),
        (v[v.recipe.isin(DESTACADAS)], dict(color=RECETAS, size=22, line=dict(color=FONDO, width=2))),
    ]
    for datos, marca in grupos:
        fig.add_trace(go.Scatter(x=datos.sep, y=datos.oct, mode='markers', marker=marca,
                                 customdata=datos[['nombre', 'sem_sep', 'sem_oct']].values, hovertemplate=plantilla))
    for r, ax, ay in [('slope_W4', -40, -60), ('max_W6', 70, -40), ('range_W6', 80, 30)]:
        x = _rec(r)
        fig.add_annotation(x=x.sep, y=x.oct, text=x.nombre, showarrow=True, arrowhead=0, arrowwidth=2,
                           arrowcolor=TINTA_MUTED, ax=ax, ay=ay, font=dict(size=24, color=TINTA))
    for r, ax, ay in [('rank_historia', -24, 70), ('rel_mean_W6', -10, 70)]:
        x = _rec(r)
        fig.add_annotation(x=x.sep, y=x.oct, text=f'{x.nombre}<br><span style="font-size:18px">un solo mes muy bueno</span>',
                           showarrow=True, arrowhead=0, arrowwidth=2, arrowcolor=GRIS_CLARO, ax=ax, ay=ay,
                           font=dict(size=20, color=TINTA_2), align='right', xanchor='right', yanchor='top')
    m = lim * 0.94
    _texto(fig, m, m, f"<b>{C['n_ambos_mas']}</b> ganan en los dos meses", 26, TINTA, xanchor='right', yanchor='top')
    _texto(fig, -m, -m, f"<b>{C['n_ambos_menos']}</b> pierden en los dos", 26, TINTA, xanchor='left', yanchor='bottom')
    _texto(fig, -m, m, f"{C['n_arriba_izq']} solo en octubre", 22, TINTA_MUTED, xanchor='left', yanchor='top')
    _texto(fig, m, -m, f"{C['n_abajo_der']} solo en septiembre", 22, TINTA_MUTED, xanchor='right', yanchor='bottom')
    eje = dict(range=[-lim, lim], showgrid=False, zeroline=False, ticksuffix=' M', tickfont=dict(size=20),
               color=TINTA_MUTED, dtick=2)
    fig.update_xaxes(**eje, title=dict(text='Ganancia sobre el baseline en septiembre', font=dict(size=22, color=TINTA_2)))
    fig.update_yaxes(**eje, title=dict(text='Ganancia sobre el baseline en octubre', font=dict(size=22, color=TINTA_2)))
    _base(fig, 1000, 780, hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=GRIS_CLARO,
                                          font=dict(family=FUENTE, size=22, color=TINTA)))
    return fig


def fig_meses():
    """PAQ_P3 − AC por mes (d promedio por semilla), de junio a octubre."""
    meses = list(MESES)
    d = [_paq.loc['AC', f'd_{m}'] for m in meses]
    fig = go.Figure(go.Bar(x=[MESES[m].capitalize() for m in meses], y=d, marker_color=ACUMULATIVO,
                           marker_line_width=0, width=0.56, text=[f(x, 1, True) for x in d], textposition='outside',
                           textfont=dict(size=30, color=TINTA), cliponaxis=False))
    media = _paq.loc['AC', 'd_M']
    fig.add_shape(type='line', x0=-0.5, x1=len(meses) - 0.5, y0=media, y1=media,
                  line=dict(color=TINTA_MUTED, width=2, dash='dot'))
    _texto(fig, len(meses) - 0.5, media, f'promedio {f(media, 1, True)}', 22, TINTA_MUTED,
           xanchor='left', xshift=12)
    fig.update_yaxes(visible=False, range=[0, max(d) * 1.22])
    fig.update_xaxes(showgrid=False, tickfont=dict(size=24, color=TINTA_2), linecolor=GRIS_CLARO)
    return _base(fig, 980, 520, bargap=0.3, margin=dict(l=20, r=170, t=30, b=40))


def fig_maldicion():
    """La mejor de 60 combinaciones de hiperparámetros (23), en cada fase."""
    fases = ['Al elegirla', 'Semillas nuevas,<br>mismos meses', 'Meses nuevos']
    d = [_reev23['busqueda_contra_vigente_M'], _reev23['reevaluacion_4_contra_vigente_M'], _conf23['d_M']]
    colores = [TINTA_MUTED, TINTA_MUTED, MAL]
    fig = go.Figure(go.Bar(x=fases, y=d, marker_color=colores, marker_line_width=0, width=0.55,
                           text=[f(x, 2, True) for x in d], textposition='outside', cliponaxis=False,
                           textfont=dict(size=30, color=TINTA)))
    fig.add_shape(type='line', x0=-0.5, x1=2.5, y0=0, y1=0, line=dict(color=GRIS_CLARO, width=2))
    fig.update_yaxes(visible=False, range=[min(d) * 2.2, max(d) * 1.3])
    fig.update_xaxes(showgrid=False, tickfont=dict(size=22, color=TINTA_2), showline=False)
    return _base(fig, 760, 520, margin=dict(l=10, r=10, t=30, b=20))


# ---------------------------------------------------------------- componentes HTML / SVG

MESES_CORTOS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct']
ESTADOS = {'h': ('hist', ''), 'e': ('train', 'entrena'), 'v': ('valid', 'valida'), 'g': ('gap', ''),
           't': ('eval', 'evalúa'), '.': ('nada', ''), 'f': ('fija', 'entrena')}


def calendario(filas, color, etiquetas=True):
    """Calendario de 2019 (enero a octubre): una fila por paso.
    filas: lista de (rótulo, cadena de 10 letras) con h = solo historia, e = entrena, v = valida,
    g = la clase todavía no se conoce (t − 1), t = evalúa, . = nada."""
    cab = ''.join(f'<div class="cal-mes">{m}</div>' for m in MESES_CORTOS)
    html = [f'<div class="calendario" style="--c:{color}"><div class="cal-rot"></div>{cab}']
    for rotulo, estados in filas:
        assert len(estados) == 10, rotulo
        html.append(f'<div class="cal-rot">{rotulo}</div>')
        for letra in estados:
            clase, texto = ESTADOS[letra]
            html.append(f'<div class="cal-celda {clase}">{texto if etiquetas else ""}</div>')
    html.append('</div>')
    return ''.join(html)


def _rama(x0, x1, y_main, y, color, puntos):
    """Camino SVG de un branch que sale del main en x0, corre a la altura y y termina en x1."""
    r = 60
    sube = -1 if y < y_main else 1
    d = (f'M{x0},{y_main} C{x0 + r},{y_main} {x0 + r},{y} {x0 + 2 * r},{y} L{x1 - 2 * r},{y}')
    circ = ''.join(f'<circle cx="{x}" cy="{y}" r="11" fill="{FONDO}" stroke="{color}" stroke-width="5"/>' for x in puntos)
    return d, circ, sube


def svg_git(resultados=False):
    """El main y dos branches: uno no cumple la regla y no vuelve; el otro la cumple y hace merge."""
    W, H, ym = 1700, 430, 230
    a, b = 120, 1640
    # branch 1 (arriba): no pasa
    d1, c1, _ = _rama(300, 860, ym, 90, REGLA, [480, 620, 740])
    # branch 2 (abajo): pasa y vuelve
    x2a, x2b, y2 = 900, 1300, 370
    d2 = (f'M{x2a},{ym} C{x2a + 60},{ym} {x2a + 60},{y2} {x2a + 120},{y2} L{x2b - 120},{y2} '
          f'C{x2b - 60},{y2} {x2b - 60},{ym} {x2b},{ym}')
    c2 = ''.join(f'<circle cx="{x}" cy="{y2}" r="11" fill="{FONDO}" stroke="{REGLA}" stroke-width="5"/>'
                 for x in (1060, 1160))
    if resultados:
        t1 = (f'<tspan font-weight="700" fill="{TINTA}">rango</tspan> de 3 meses · {C["rango_d"]} M · '
              f'{C["rango_sem"]}')
        e1 = C['rango_veredicto']
        t2 = (f'<tspan font-weight="700" fill="{TINTA}">Optuna</tspan> sobre el main · {C["opt_d"]} M · '
              f'{C["opt_sem"]}')
        e2 = 'pasa: entró al main'
    else:
        t1, e1 = 'una idea, un solo cambio', 'no cumple la regla'
        t2, e2 = 'otra idea, un solo cambio', 'cumple la regla: merge'
    main_commits = ''.join(f'<circle cx="{x}" cy="{ym}" r="13" fill="{TINTA_2}"/>' for x in (180, 300, 600, 900))
    merge = f'<circle cx="{x2b}" cy="{ym}" r="17" fill="{BIEN}" stroke="{FONDO}" stroke-width="4"/>'
    return f'''<svg class="git" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"
  aria-label="Diagrama del main con dos branches: uno no cumple la regla y no vuelve; el otro la cumple y hace merge">
  <line x1="{a}" y1="{ym}" x2="{b}" y2="{ym}" stroke="{TINTA_2}" stroke-width="7" stroke-linecap="round"/>
  {main_commits}
  <text x="{a - 10}" y="{ym - 34}" font-size="30" font-weight="700" fill="{TINTA}">main</text>
  <path d="{d1}" fill="none" stroke="{REGLA}" stroke-width="6" stroke-linecap="round"/>
  {c1}
  <circle cx="860" cy="90" r="22" fill="{FONDO}" stroke="{MAL}" stroke-width="5"/>
  <path d="M849,79 L871,101 M871,79 L849,101" stroke="{MAL}" stroke-width="5" stroke-linecap="round"/>
  <text x="440" y="46" font-size="27" fill="{TINTA_2}">{t1}</text>
  <text x="900" y="100" font-size="27" font-weight="700" fill="{MAL}">{e1}</text>
  <path d="{d2}" fill="none" stroke="{REGLA}" stroke-width="6" stroke-linecap="round"/>
  {c2}
  {merge}
  <path d="M{x2b - 8},{ym} l6,7 l11,-13" fill="none" stroke="{FONDO}" stroke-width="4" stroke-linecap="round"/>
  <text x="1000" y="420" font-size="27" fill="{TINTA_2}">{t2}</text>
  <text x="{x2b + 34}" y="{ym + 82}" font-size="27" font-weight="700" fill="{BIEN}">{e2}</text>
</svg>'''


PARTES = ['Hipótesis', 'Diseño', 'Limitaciones', 'Resultados', 'Conclusiones']


def partes(activa):
    """Barra inferior con las partes de la consigna; resalta la activa."""
    spans = ''.join(f'<span class="{"activa" if p == activa else ""}">{p}</span>' for p in PARTES)
    return f'<div class="partes">{spans}</div>'


_pf = _ex['04_regla']['d_media_201910_M']
C['pf_min'], C['pf_max'] = f(_pf.min(), 1, True), f(_pf.max(), 1, True)


def tabla_coincidencias():
    filas = [
        ('✓', 'c-bien', 'Las variables históricas suman sobre lags y deltas 1–2',
         f"{C['n_ambos_mas']} de {C['n_recetas']} experimentos ganan en los dos meses", f"{C['paq_d']} M por mes"),
        ('✓', 'c-bien', 'Lags más lejanos casi no suman',
         f"lags y deltas 3–5: {C['n_crudos_ambos']} de 6 ganan en los dos meses",
         f"de 3 a 4 meses de historia: {C['dosis_34']} M en octubre"),
        ('✓', 'c-bien', 'La tendencia de unos 4 meses suma',
         f"4 meses: {C['slope_W4_sep']} / {C['slope_W4_oct']}", f"5 meses: {C['t4_sep']} / {C['t4_oct']}"),
        ('✓', 'c-bien', 'Rinde comparar al cliente con su propio pasado',
         'máximo, rango, relativo al promedio', f"historia curada {C['ach']}"),
        ('≠', 'c-mal', 'El rango', '6 meses: suma sobre el baseline', f"3 meses: {C['rango_veredicto']} sobre el main"),
    ]
    cuerpo = ''.join(f'<tr><td class="marca {c}">{m}</td><td class="tema">{t}</td><td>{r}</td><td>{a}</td></tr>'
                     for m, c, t, r, a in filas)
    return ('<table class="coinc"><thead><tr><th></th><th>Tema</th>'
            '<th><span class="c-recetas">Familia 1 · independientes</span></th>'
            f'<th><span class="c-acum">Familia 2 · acumulativos</span></th></tr></thead><tbody>{cuerpo}</tbody></table>')


# ---------------------------------------------------------------- figuras técnicas del informe

TRES = ['#199e70', '#c98500', '#d55181']   # tres series sin significado de familia (validadas, modo oscuro)
_curvas = _csv('curvas_ganancia.csv')
_dosis = _ex.get('04_dosis') if '04_dosis' in _ex else _csv('exploratorio/04_dosis.csv')
_gan = pd.concat([_csv('paq_p3_ganancias.csv').assign(corrida='PAQ_P3'), _csv('ac_ganancias.csv')])

ETIQUETA = {'AC': 'Baseline', 'A_CONSIGNA': 'Baseline, ventana de la consigna', 'PAQ_P3': 'Estrategia final'}
COLOR_CFG = {'AC': GRIS_CLARO, 'A_CONSIGNA': TINTA_MUTED, 'PAQ_P3': ACUMULATIVO}


def fig_curva(mes=201910, configs=('AC',), ancho=1500, alto=640):
    """Curva de ganancia del ensamble según la cantidad de envíos, con la banda de 3.000 a 6.000 sombreada.
    Interactiva: el cursor muestra la ganancia de cada configuración en ese punto de corte."""
    fig = go.Figure()
    fig.add_vrect(x0=3000, x1=6000, fillcolor=TINTA, opacity=0.06, line_width=0, layer='below')
    for cfg in configs:
        c = _curvas[(_curvas.config == cfg) & (_curvas.foto_mes == mes)]
        fig.add_trace(go.Scatter(x=c.envios, y=c.ganancia_M, mode='lines', name=ETIQUETA[cfg],
                                 line=dict(color=COLOR_CFG[cfg], width=4 if cfg == 'PAQ_P3' else 3),
                                 hovertemplate=f'{ETIQUETA[cfg]}: %{{y:.1f}} M<extra></extra>'))
        i = c.ganancia_M.idxmax()
        ax, ay = (60, -46) if cfg == 'PAQ_P3' else (90, 70)
        fig.add_annotation(x=c.envios[i], y=c.ganancia_M[i], text=f'{ETIQUETA[cfg]}: máx. {f(c.ganancia_M[i])} M',
                           showarrow=True, arrowhead=0, ax=ax, ay=ay, arrowcolor=TINTA_MUTED,
                           font=dict(size=22, color=TINTA), xanchor='left')
    ymax = _curvas[_curvas.foto_mes == mes].ganancia_M.max()
    _texto(fig, 4500, ymax * 0.08, 'banda: promedio entre<br>3.000 y 6.000 envíos', 21, TINTA_2)
    fig.update_xaxes(title=dict(text='Cantidad de envíos (ordenados por probabilidad)', font=dict(size=22)),
                     showgrid=False, tickfont=dict(size=20), color=TINTA_MUTED, range=[0, 15000],
                     tickformat=',d', separatethousands=True, zeroline=False, showspikes=True, spikecolor=GRIS_CLARO,
                     spikethickness=1, spikedash='dot', spikemode='across')
    fig.update_yaxes(title=dict(text=f'Ganancia en {MESES[mes]} (M)', font=dict(size=22)), showgrid=True,
                     gridcolor=GRIS, zeroline=False, tickfont=dict(size=20), color=TINTA_MUTED, range=[0, ymax * 1.12])
    _base(fig, ancho, alto, hovermode='x unified', separators=',.',
          hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=GRIS_CLARO, font=dict(family=FUENTE, size=20, color=TINTA)),
          margin=dict(l=20, r=30, t=30, b=20))
    return fig


def fig_dosis():
    """Prueba pre-registrada (04): ganancia media por semilla según los meses de historia (h), con IC 95 %."""
    from plotly.subplots import make_subplots
    fam = {'L': 'Lags', 'T': 'Tendencias', 'LT': 'Lags + tendencias'}
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Septiembre', 'Octubre'], horizontal_spacing=0.09)
    fig.update_annotations(font=dict(size=24, color=TINTA))   # títulos de los paneles (antes de las etiquetas)
    for j, mes in enumerate((201909, 201910), start=1):
        for k, (cod, nombre) in enumerate(fam.items()):
            d = _dosis[(_dosis.familia == cod) & (_dosis.foto_mes == mes)].sort_values('h')
            x = d.h + (k - 1) * 0.07
            fig.add_trace(go.Scatter(
                x=x, y=d.ganancia_media_M, mode='lines+markers', line=dict(color=TRES[k], width=3),
                marker=dict(size=13, color=TRES[k], line=dict(color=FONDO, width=2)),
                error_y=dict(type='data', symmetric=False, array=d.ic95_sup_M - d.ganancia_media_M,
                             arrayminus=d.ganancia_media_M - d.ic95_inf_M, color=TRES[k], thickness=2, width=6),
                hovertemplate=f'{nombre}, h = %{{customdata}}: %{{y:.1f}} M<extra></extra>', customdata=d.h),
                row=1, col=j)
            if j == 2:
                ult = d.iloc[-1]
                fig.add_annotation(x=4.2, y=ult.ganancia_media_M, text=nombre, showarrow=False,
                                   yshift={'L': -16, 'T': 0, 'LT': 16}[cod],
                                   xanchor='left', font=dict(size=21, color=TRES[k]), row=1, col=j)
    fig.update_xaxes(tickvals=[2, 3, 4], ticktext=['2 (baseline)', '3', '4'], range=[1.75, 4.25 + 0.0],
                     showgrid=False, tickfont=dict(size=20), color=TINTA_MUTED,
                     title=dict(text='Meses de historia (h)', font=dict(size=20)))
    fig.update_xaxes(range=[1.75, 5.1], row=1, col=2)
    fig.update_yaxes(showgrid=True, gridcolor=GRIS, zeroline=False, tickfont=dict(size=20), color=TINTA_MUTED,
                     ticksuffix=' M')
    return _base(fig, 1500, 500, separators=',.', margin=dict(l=20, r=20, t=50, b=20))


def fig_profundidad():
    """Experimentos independientes: ganancia sobre el baseline (promedio de septiembre y octubre)
    según la profundidad de la ventana, por tipo de variable. Más lags y deltas, en línea punteada."""
    v = V10.assign(prom=(V10.sep + V10.oct) / 2)
    fig = go.Figure()
    fig.add_hline(y=0, line=dict(color=GRIS_CLARO, width=2))
    destacados = {'slope': 'Tendencia', 'max': 'Máximo', 'range': 'Rango'}
    for base, nombre in NOMBRES.items():
        d = v[v.recipe.str.match(rf'^{base}_W\d$')]
        d = d.assign(w=d.recipe.str[-1].astype(int)).sort_values('w')
        color = RECETAS if base in destacados else GRIS_CLARO
        fig.add_trace(go.Scatter(x=d.w, y=d.prom, mode='lines+markers', line=dict(color=color, width=3 if base in destacados else 2),
                                 marker=dict(size=11, color=color), hovertemplate=f'{nombre}, %{{x}} meses: %{{y:+.2f}} M<extra></extra>'))
        if base in destacados:
            ult = d.iloc[-1]
            fig.add_annotation(x=6.1, y=ult.prom, text=nombre, showarrow=False, xanchor='left',
                               font=dict(size=21, color=TINTA))
    for pref, nombre in (('lag', 'Más lags'), ('delta', 'Más deltas')):
        d = v[v.recipe.str.match(rf'^{pref}\d$')]
        d = d.assign(k=d.recipe.str[-1].astype(int)).sort_values('k')
        fig.add_trace(go.Scatter(x=d.k, y=d.prom, mode='lines+markers', line=dict(color=TINTA_2, width=3, dash='dot'),
                                 marker=dict(size=11, color=FONDO, line=dict(color=TINTA_2, width=2.5)),
                                 hovertemplate=f'{nombre} (%{{x}} meses atrás): %{{y:+.2f}} M<extra></extra>'))
        fig.add_annotation(x=d.k.iloc[-1] + 0.1, y=d.prom.iloc[-1], text=nombre, showarrow=False, xanchor='left',
                           font=dict(size=19, color=TINTA_2))
    fig.update_xaxes(tickvals=[3, 4, 5, 6], ticktext=['3', '4', '5', '6'], range=[2.7, 7.0], showgrid=False,
                     tickfont=dict(size=20), color=TINTA_MUTED,
                     title=dict(text='Meses de historia (ventana, o lag/delta más lejano)', font=dict(size=20)))
    fig.update_yaxes(showgrid=False, zeroline=False, tickfont=dict(size=20), color=TINTA_MUTED, ticksuffix=' M',
                     title=dict(text='Ganancia sobre el baseline (promedio sep–oct)', font=dict(size=20)))
    return _base(fig, 1100, 640, separators=',.',
                 hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=GRIS_CLARO, font=dict(family=FUENTE, size=20, color=TINTA)))


def fig_semillas():
    """Estrategia final − baseline, por semilla y por mes (ganancia promedio entre 3.000 y 6.000 envíos)."""
    p = _gan.pivot_table(index=['foto_mes', 'semilla'], columns='corrida', values='ganancia_banda_M').reset_index()
    p = p.assign(d=p['PAQ_P3'] - p['AC'])
    fig = go.Figure()
    fig.add_hline(y=0, line=dict(color=GRIS_CLARO, width=2))
    meses = list(MESES)
    for i, mes in enumerate(meses):
        d = p[p.foto_mes == mes]
        fig.add_trace(go.Scatter(x=[i + (j - 2) * 0.07 for j in range(len(d))], y=d.d, mode='markers',
                                 marker=dict(size=16, color=ACUMULATIVO, line=dict(color=FONDO, width=2)),
                                 hovertemplate=f'{MESES[mes]}: %{{y:+.2f}} M<extra></extra>'))
        fig.add_shape(type='line', x0=i - 0.25, x1=i + 0.25, y0=d.d.mean(), y1=d.d.mean(), line=dict(color=TINTA, width=3))
        _texto(fig, i, d.d.max(), f(d.d.mean(), 1, True), 26, TINTA, yshift=30)
    fig.update_xaxes(tickvals=list(range(len(meses))), ticktext=[MESES[m].capitalize() for m in meses],
                     showgrid=False, zeroline=False, tickfont=dict(size=22, color=TINTA_2), range=[-0.6, len(meses) - 0.4])
    fig.update_yaxes(showgrid=True, gridcolor=GRIS, zeroline=False, tickfont=dict(size=20), color=TINTA_MUTED,
                     ticksuffix=' M', rangemode='tozero')
    return _base(fig, 980, 520, separators=',.', margin=dict(l=20, r=20, t=20, b=20))


_ps = _gan.pivot_table(index=['foto_mes', 'semilla'], columns='corrida', values='ganancia_banda_M')
C['semillas_positivas'] = int(((_ps['PAQ_P3'] - _ps['AC']) > 0).sum())
C['semillas_total'] = len(_ps)
_d2 = _dosis.set_index(['familia', 'h', 'foto_mes'])['ganancia_media_M']
C['dosis_23'] = f"{f(min(_d2[(c, 3, 201910)] - _d2[(c, 2, 201910)] for c in ('L', 'T', 'LT')), 1, True)} a " \
                f"{f(max(_d2[(c, 3, 201910)] - _d2[(c, 2, 201910)] for c in ('L', 'T', 'LT')), 1, True)}"
C['dosis_34'] = f"{f(min(_d2[(c, 4, 201910)] - _d2[(c, 3, 201910)] for c in ('L', 'T', 'LT')), 1, True)} a " \
                f"{f(max(_d2[(c, 4, 201910)] - _d2[(c, 3, 201910)] for c in ('L', 'T', 'LT')), 1, True)}"
_cv = _curvas.set_index(['config', 'foto_mes', 'envios'])['ganancia_M']
C['curva_ac_max'] = f(_curvas[(_curvas.config == 'AC') & (_curvas.foto_mes == 201910)].ganancia_M.max())
C['curva_paq_max'] = f(_curvas[(_curvas.config == 'PAQ_P3') & (_curvas.foto_mes == 201910)].ganancia_M.max())


_pv = V10.assign(prom=(V10.sep + V10.oct) / 2).set_index('recipe')['prom']
for _b in ('max', 'range', 'slope', 'mean'):
    for _w in (3, 4, 6):
        C[f'prof_{_b}_{_w}'] = f(_pv[f'{_b}_W{_w}'], 1, True)



# ---------------------------------------------------------------- cuánto vale la historia y lo que no sumó

_s12 = _ex.get('12_semillas') if '12_semillas' in _ex else _csv('exploratorio/12_semillas.csv')
_d2c = _csv('exploratorio/05_d2_comparacion.csv')
_c06 = _csv('exploratorio/06_comparacion.csv')
_c24 = _csv('exploratorio/24_comparacion.csv')
_c22 = _ex['22_comparacion']

VALOR = [('ACS', 'Sin lags ni deltas', TINTA_MUTED), ('AC', 'Lags y deltas 1–2 (baseline)', GRIS_CLARO),
         ('ACH', '+ historia curada', ACUMULATIVO)]


def fig_valor_historia():
    """Notebook 12: ganancia (promedio entre 3.000 y 6.000 envíos) por semilla, sin historia, con lags y deltas 1–2
    y con historia curada, en septiembre y octubre. Ventana de la consigna (201903–06). Interactiva."""
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Septiembre', 'Octubre'], horizontal_spacing=0.08,
                        shared_yaxes=True)
    fig.update_annotations(font=dict(size=24, color=TINTA))
    for j, mes in enumerate((201909, 201910), start=1):
        medias = {}
        for i, (cfg, nombre, color) in enumerate(VALOR):
            d = _s12[(_s12.config == cfg) & (_s12.foto_mes == mes)]
            medias[cfg] = d.ganancia_banda_M.mean()
            fig.add_trace(go.Scatter(
                x=d.ganancia_banda_M, y=[nombre] * len(d), mode='markers',
                marker=dict(size=15, color=color, opacity=0.85, line=dict(color=FONDO, width=1.5)),
                hovertemplate=f'{nombre}<br>semilla %{{customdata}}: %{{x:.1f}} M<extra></extra>',
                customdata=d.semilla), row=1, col=j)
            fig.add_trace(go.Scatter(x=[medias[cfg]], y=[nombre], mode='markers',
                                     marker=dict(symbol='line-ns', size=34, line=dict(color=TINTA, width=4)),
                                     hovertemplate=f'{nombre}: media %{{x:.1f}} M<extra></extra>'), row=1, col=j)
        sube = medias['AC'] - medias['ACS']
        fig.add_annotation(x=(medias['AC'] + medias['ACS']) / 2, y=VALOR[0][1], text=f'<b>{f(sube, 1, True)} M</b>',
                           showarrow=False, yshift=40, font=dict(size=26, color=TINTA), row=1, col=j)
        pass
    fig.update_xaxes(showgrid=True, gridcolor=GRIS, zeroline=False, tickfont=dict(size=20), color=TINTA_MUTED,
                     ticksuffix=' M')
    fig.update_yaxes(showgrid=False, tickfont=dict(size=22, color=TINTA_2), categoryorder='array',
                     categoryarray=[v[1] for v in VALOR][::-1])
    return _base(fig, 1600, 420, separators=',.', margin=dict(l=20, r=30, t=50, b=20),
                 hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=GRIS_CLARO, font=dict(family=FUENTE, size=20, color=TINTA)))


_acs = _s12.groupby(['config', 'foto_mes']).ganancia_banda_M.mean()
C['valor_sep'] = f(_acs[('AC', 201909)] - _acs[('ACS', 201909)], 1, True)
C['valor_oct'] = f(_acs[('AC', 201910)] - _acs[('ACS', 201910)], 1, True)
C['valor_pct'] = f(100 * (_acs[('AC', 201910)] - _acs[('ACS', 201910)]) / _acs[('ACS', 201910)], 0)
C['curada_sep'] = f(_acs[('ACH', 201909)] - _acs[('AC', 201909)], 1, True)
C['curada_oct'] = f(_acs[('ACH', 201910)] - _acs[('AC', 201910)], 1, True)


def _fila_df(df, **cond):
    t = df
    for k, val in cond.items():
        t = t[t[k] == val]
    assert len(t) == 1, cond
    return t.iloc[0]


def _no_sumo():
    d2s = _fila_df(_d2c, config='D2', contra='A', foto_mes=201909)
    d2o = _fila_df(_d2c, config='D2', contra='A', foto_mes=201910)
    zs = _fila_df(_c06, medida='semillas', config='AC_Z', foto_mes=201909)
    zo = _fila_df(_c06, medida='semillas', config='AC_Z', foto_mes=201910)
    can = _fila_df(_c22, config='PAQ_C_P3', contra='PAQ_P3')
    paq2 = _fila_df(_c24, config='PAQ2_P3', meses='201906-10')
    return [  # (nombre, detalle, d, inf, sup, veredicto, contra)
        ('Segundas diferencias', 'septiembre', d2s.d_media_M, d2s.ic95_inf_M, d2s.ic95_sup_M, 'Sin señal', 'baseline, prueba fijada'),
        ('Segundas diferencias', 'octubre', d2o.d_media_M, d2o.ic95_inf_M, d2o.ic95_sup_M, 'Sin señal', 'baseline, prueba fijada'),
        ('Racha de meses en cero', 'septiembre', zs.d_M, zs.ic95_inf_M, zs.ic95_sup_M, 'Falla en las tres condiciones', 'baseline, ventana de la consigna'),
        ('Racha de meses en cero', 'octubre', zo.d_M, zo.ic95_inf_M, zo.ic95_sup_M, 'Falla en las tres condiciones', 'baseline, ventana de la consigna'),
        ('Selección con canaritos', 'junio–octubre', can.d_M, can.ic95_inf_M, can.ic95_sup_M, 'Empate', 'estrategia final'),
        ('Segundo paquete (960 columnas)', 'junio–octubre', paq2.d_M, paq2.ic95_inf_M, paq2.ic95_sup_M, 'Resta', 'estrategia final'),
        ('Rango de 3 meses (branch)', 'junio–octubre', _rango['d_M'], _rango['ic95_inf_M'], _rango['ic95_sup_M'],
         _rango['veredicto'], 'main'),
    ]


def fig_no_sumo():
    """Forest plot de lo que no sumó: diferencia de ganancia por semilla e IC 95 % contra su control. Interactiva."""
    filas = _no_sumo()
    etiquetas = [f'{n} · {det}' for n, det, *_ in filas]
    fig = go.Figure()
    fig.add_vline(x=0, line=dict(color=TINTA_2, width=2))
    for (n, det, d, lo, hi, ver, contra), et in zip(filas, etiquetas):
        fig.add_trace(go.Scatter(
            x=[d], y=[et], mode='markers', marker=dict(size=18, color=MAL if hi < 0 or d < 0 else TINTA_MUTED,
                                                       line=dict(color=FONDO, width=2)),
            error_x=dict(type='data', symmetric=False, array=[hi - d], arrayminus=[d - lo], color=GRIS_CLARO,
                         thickness=3, width=8),
            hovertemplate=f'<b>{n}</b> ({det})<br>contra: {contra}<br>diferencia: %{{x:+.2f}} M'
                          f'<br>IC 95 %: {f(lo, 2)} a {f(hi, 2)} M<extra></extra>'))
        fig.add_annotation(x=1, xref='paper', y=et, text=f'<b>{ver}</b>', showarrow=False, xanchor='left',
                           xshift=14, font=dict(size=22, color=TINTA_2))
    fig.update_xaxes(showgrid=True, gridcolor=GRIS, zeroline=False, tickfont=dict(size=20), color=TINTA_MUTED,
                     ticksuffix=' M', title=dict(text='Diferencia de ganancia contra su control, IC 95 %', font=dict(size=20)))
    fig.update_yaxes(showgrid=False, tickfont=dict(size=22, color=TINTA_2), autorange='reversed')
    return _base(fig, 1560, 540, separators=',.', margin=dict(l=20, r=360, t=10, b=20),
                 hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=GRIS_CLARO, font=dict(family=FUENTE, size=20, color=TINTA)))


C['ic_clientes'] = f(float(_inf['ic_clientes_M']), 0)
C['ens_casos'] = int(_inf['ensamble_casos'])
C['ens_mejora'] = f(float(_inf['ensamble_mejora_M']), 1, True)
_rm, _rh = _rec('rel_mean_W6'), _rec('rank_historia')
C['relmed6_sep'], C['relmed6_oct'] = f(_rm.sep, 1, True), f(_rm.oct, 1, True)
C['rankh_sep'], C['rankh_oct'] = f(_rh.sep, 1, True), f(_rh.oct, 1, True)


# ---------------------------------------------------------------- ejemplo ilustrativo de los experimentos de ventana
# Serie inventada (no es un resultado): el saldo de un cliente en los últimos 6 meses, para mostrar cómo se calcula
# cada tipo de variable de la familia 1. Se rotula como "ejemplo ilustrativo".
EJ_MESES = ['t − 5', 't − 4', 't − 3', 't − 2', 't − 1', 't (mes actual)']
EJ_SALDO = [130, 150, 120, 110, 95, 70]


def _ej_calculos(w):
    import numpy as np
    v = np.array(EJ_SALDO[-w:], dtype=float)
    x = np.arange(w)
    pend, ord_ = np.polyfit(x, v, 1)
    prom = v.mean()
    return dict(v=v, x=x, prom=prom, mn=v.min(), mx=v.max(), rango=v.max() - v.min(), pend=pend, ord=ord_,
                rel_prom=(v[-1] - prom) / abs(prom), rel_ant=(v[-1] - v[-2]) / abs(v[-2]), rel_pri=(v[-1] - v[0]) / abs(v[0]))


def fig_ejemplo():
    """Ejemplo interactivo: botones para cambiar la ventana (3, 4 o 6 meses) y ver cada cálculo."""
    n = len(EJ_SALDO)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=EJ_MESES, y=EJ_SALDO, mode='lines+markers+text', line=dict(color=GRIS_CLARO, width=3),
                             marker=dict(size=14, color=TINTA_2), text=[str(s) for s in EJ_SALDO],
                             textposition='top center', textfont=dict(size=20, color=TINTA_2),
                             hovertemplate='%{x}: %{y}<extra></extra>', name='saldo'))
    estados = {}
    for w in (3, 4, 6):
        c = _ej_calculos(w)
        xs = EJ_MESES[n - w:]
        k0 = len(fig.data)
        fig.add_trace(go.Scatter(x=xs, y=[c['prom']] * w, mode='lines', line=dict(color=TRES[1], width=3, dash='dash'),
                                 hovertemplate=f'promedio: {f(c["prom"], 1)}<extra></extra>', visible=(w == 4)))
        fig.add_trace(go.Scatter(x=xs, y=c['ord'] + c['pend'] * c['x'], mode='lines', line=dict(color=RECETAS, width=4),
                                 hovertemplate=f'tendencia: {f(c["pend"], 1, True)} por mes<extra></extra>', visible=(w == 4)))
        imn, imx = int(c['v'].argmin()), int(c['v'].argmax())
        fig.add_trace(go.Scatter(x=[xs[imn], xs[imx]], y=[c['mn'], c['mx']], mode='markers',
                                 marker=dict(size=24, color='rgba(0,0,0,0)', line=dict(color=TINTA, width=3)),
                                 hovertemplate='%{x}: %{y}<extra></extra>', visible=(w == 4)))
        estados[w] = (k0, c, xs)
    ntr = len(fig.data)

    def capa(w):
        k0, c, xs = estados[w]
        vis = [True] + [False] * (ntr - 1)
        for k in range(k0, k0 + 3):
            vis[k] = True
        shapes = [dict(type='rect', xref='x', yref='paper', x0=n - w - 0.5, x1=n - 0.5, y0=0, y1=1,
                       fillcolor=RECETAS, opacity=0.08, line_width=0, layer='below')]
        texto = (f'<b>Ventana de {w} meses</b><br><br>'
                 f'<span style="color:{TRES[1]}">- - promedio</span>: <b>{f(c["prom"], 1)}</b><br>'
                 f'<span style="color:{TINTA}">○ mínimo</span>: <b>{f(c["mn"], 0)}</b> · <span style="color:{TINTA}">○ máximo</span>: <b>{f(c["mx"], 0)}</b><br>'
                 f'rango (máx − mín): <b>{f(c["rango"], 0)}</b><br>'
                 f'<span style="color:{RECETAS}">— tendencia</span> (pendiente): <b>{f(c["pend"], 1, True)} por mes</b><br><br>'
                 f'relativo al promedio: <b>{f(100 * c["rel_prom"], 0, True)} %</b><br>'
                 f'relativo al mes anterior: <b>{f(100 * c["rel_ant"], 0, True)} %</b><br>'
                 f'relativo al primer mes: <b>{f(100 * c["rel_pri"], 0, True)} %</b>')
        ann = [dict(xref='paper', yref='paper', x=1.02, y=0.98, xanchor='left', yanchor='top', align='left',
                    showarrow=False, text=texto, font=dict(family=FUENTE, size=22, color=TINTA_2))]
        return vis, shapes, ann

    botones = []
    for w in (3, 4, 6):
        vis, shapes, ann = capa(w)
        botones.append(dict(label=f'{w} meses', method='update', args=[{'visible': vis}, {'shapes': shapes, 'annotations': ann}]))
    vis, shapes, ann = capa(4)
    fig.update_layout(shapes=shapes, annotations=ann,
                      updatemenus=[dict(type='buttons', direction='right', active=1, x=0, y=1.16, xanchor='left',
                                        buttons=botones, bgcolor=TINTA_MUTED, bordercolor=GRIS_CLARO,
                                        font=dict(family=FUENTE, size=22, color=FONDO), pad=dict(r=14, t=6, b=6, l=14))])
    fig.update_xaxes(showgrid=False, tickfont=dict(size=20, color=TINTA_2))
    fig.update_yaxes(showgrid=True, gridcolor=GRIS, zeroline=False, tickfont=dict(size=18), color=TINTA_MUTED,
                     range=[40, 175], title=dict(text='saldo (ejemplo, en miles)', font=dict(size=20)))
    return _base(fig, 1700, 560, separators=',.', margin=dict(l=20, r=520, t=80, b=20),
                 hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=GRIS_CLARO, font=dict(family=FUENTE, size=20, color=TINTA)))


_e4 = _ej_calculos(4)
C.update({'ej_prom4': f(_e4['prom'], 1), 'ej_mn4': f(_e4['mn'], 0), 'ej_mx4': f(_e4['mx'], 0), 'ej_rango4': f(_e4['rango'], 0),
          'ej_pend4': f(_e4['pend'], 1, True), 'ej_relprom4': f(100 * _e4['rel_prom'], 0, True),
          'ej_relant4': f(100 * _e4['rel_ant'], 0, True), 'ej_relpri4': f(100 * _e4['rel_pri'], 0, True),
          'ej_lag3': f(EJ_SALDO[-4], 0), 'ej_delta3': f(EJ_SALDO[-1] - EJ_SALDO[-4], 0, True)})


# ---------------------------------------------------------------- qué variables usa la estrategia final
_imp = _csv('importancia_paq_p3.csv')
BLOQUE_NOMBRE = {'AC': 'Baseline: el mes, lags y deltas 1–2', 'MVH': 'Visa y Master combinadas', 'CURADA': 'Historia curada',
                 'ACH_T': 'Contra toda su historia', 'R': 'Cambios relativos', 'ACH_V': 'Inestabilidad (desvío)',
                 'ACH_Q': 'Quiebre (caídas)', 'ACH_Z': 'Contra el resto del mes'}
# Descripción de las variables más importantes (diccionario de datos de la cátedra y funciones.py del pipeline)
DESCRIPCION = {
    'mcaja_ahorro': 'Saldo de la caja de ahorro',
    'ctrx_quarter': 'Movimientos en cuentas, últimos 90 días',
    'mcaja_ahorro_lag1': 'Saldo de la caja de ahorro, mes anterior',
    'mv_mpagospesos': 'Pagos en pesos, Visa + Master',
    'mtarjeta_visa_consumo': 'Consumo con Visa',
    'cdescubierto_preacordado': 'Tiene descubierto acordado',
    'ctrx_quarter_relmediaT': 'Movimientos contra su media de toda la historia',
    'Visa_Finiciomora': 'Días al inicio de la mora de Visa',
    'mv_Finiciomora': 'Días al inicio de la mora, la más cercana de las dos',
    'cdescubierto_preacordado_delta2': 'Descubierto acordado, cambio en 2 meses',
    'mv_status05_delta2': 'Estado de las tarjetas (abierta → cerrada), cambio en 2 meses',
    'ctarjeta_visa_transacciones': 'Transacciones con Visa',
}


def fig_importancia():
    """Parte del gain de LightGBM por bloque (izquierda) y las 12 columnas que más pesan (derecha). Interactiva."""
    from plotly.subplots import make_subplots
    pb = _imp.groupby('bloque').parte_gain.sum().sort_values()
    top = _imp.head(len(DESCRIPCION)).iloc[::-1]
    color = lambda b: GRIS_CLARO if b == 'AC' else ACUMULATIVO
    fig = make_subplots(rows=1, cols=2, column_widths=[0.42, 0.58], horizontal_spacing=0.26,
                        subplot_titles=['Por bloque de variables', 'Las 12 columnas que más pesan'])
    fig.update_annotations(font=dict(size=24, color=TINTA))
    fig.add_trace(go.Bar(x=pb.values * 100, y=[BLOQUE_NOMBRE[b] for b in pb.index], orientation='h',
                         marker_color=[color(b) for b in pb.index], marker_line_width=0,
                         text=[f(v * 100, 1) + ' %' for v in pb.values], textposition='outside', cliponaxis=False,
                         textfont=dict(size=20, color=TINTA), hovertemplate='%{y}: %{x:.1f} % del gain<extra></extra>'),
                  row=1, col=1)
    fig.add_trace(go.Bar(x=top.parte_gain * 100, y=[DESCRIPCION[v] for v in top.variable], orientation='h',
                         marker_color=[color(b) for b in top.bloque], marker_line_width=0,
                         text=[f(v * 100, 1) + ' %' for v in top.parte_gain], textposition='outside', cliponaxis=False,
                         textfont=dict(size=18, color=TINTA_2), customdata=list(zip(top.variable, [BLOQUE_NOMBRE[b] for b in top.bloque])),
                         hovertemplate='%{y}<br><b>%{customdata[0]}</b> · %{customdata[1]}<br>%{x:.2f} % del gain<extra></extra>'),
                  row=1, col=2)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(tickfont=dict(size=19, color=TINTA_2), showgrid=False, ticksuffix='   ')
    return _base(fig, 1700, 600, bargap=0.28, margin=dict(l=20, r=60, t=50, b=10), separators=',.',
                 hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=GRIS_CLARO, font=dict(family=FUENTE, size=20, color=TINTA)))


_pb = _imp.groupby('bloque').parte_gain.sum()
C.update({f'imp_{b.lower()}': f(100 * _pb[b], 1) for b in _pb.index})
C['imp_ac'] = f(100 * _pb['AC'], 0)
C['imp_nuevas'] = f(100 * (1 - _pb['AC']), 0)


# ---------------------------------------------------------------- la interacción de Visa y Master con los cambios relativos
_ia_mv, _ia_rel, _ia_jun = float(_mv['d_M']), float(_rel['d_M']), float(_juntos['d_M'])
_ia_suma = _ia_mv + _ia_rel
C.update({'ia_suma': f(_ia_suma, 1, True), 'ia_extra': f(_ia_jun - _ia_suma, 1, True)})


def fig_interaccion():
    """Cada pieza sola, lo que darían si sus efectos se sumaran, y lo que dieron juntas (todas contra la misma
    estrategia previa). La diferencia es la interacción. Interactiva."""
    x = ['Visa y Master<br>combinadas, solas', 'Cambios relativos,<br>solos', 'Si sus efectos<br>se sumaran', 'Las dos juntas']
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x[:2], y=[_ia_mv, _ia_rel], marker_color=GRIS_CLARO, marker_line_width=0, width=0.55,
                         text=[f(_ia_mv, 1, True), f(_ia_rel, 1, True)], textposition='outside', cliponaxis=False,
                         textfont=dict(size=26, color=TINTA), hovertemplate='%{x}: %{y:+.2f} M<extra></extra>'))
    fig.add_trace(go.Bar(x=[x[2]], y=[_ia_suma], marker=dict(color='rgba(0,0,0,0)', line=dict(color=TINTA_2, width=3)),
                         width=0.55, text=[f(_ia_suma, 1, True)], textposition='outside', cliponaxis=False,
                         textfont=dict(size=26, color=TINTA_2), hovertemplate='0,6 + 0,6 = %{y:+.2f} M<extra></extra>'))
    fig.add_trace(go.Bar(x=[x[3]], y=[_ia_suma], marker_color=GRIS_CLARO, marker_line_width=0, width=0.55,
                         hovertemplate='lo esperado: %{y:+.2f} M<extra></extra>'))
    fig.add_trace(go.Bar(x=[x[3]], y=[_ia_jun - _ia_suma], marker_color=ACUMULATIVO, marker_line_width=0, width=0.55,
                         text=[f'{f(_ia_jun, 1, True)}'], textposition='outside', cliponaxis=False,
                         textfont=dict(size=30, color=TINTA), hovertemplate='interacción: %{y:+.2f} M<extra></extra>'))
    fig.add_annotation(x=x[3], y=_ia_suma + (_ia_jun - _ia_suma) / 2, text=f'<b>{C["ia_extra"]}</b><br>solo juntas',
                       showarrow=False, xshift=150, font=dict(size=22, color=ACUMULATIVO), align='left')
    fig.update_yaxes(visible=False, range=[0, _ia_jun * 1.25])
    fig.update_xaxes(showgrid=False, tickfont=dict(size=21, color=TINTA_2), showline=True, linecolor=GRIS_CLARO)
    return _base(fig, 1060, 440, barmode='stack', separators=',.', margin=dict(l=10, r=150, t=20, b=10),
                 hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=GRIS_CLARO, font=dict(family=FUENTE, size=20, color=TINTA)))

C['ventana_abs'] = f(abs(float(_ventana['d_M'])), 1)
