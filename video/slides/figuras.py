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
    return f'{NOMBRES[base]} W{w}'


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
    """Las 39 recetas: ganancia sobre B0 en septiembre (x) y en octubre (y). Interactiva."""
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
    m = lim * 0.94
    _texto(fig, m, m, f"<b>{C['n_ambos_mas']}</b> ganan en los dos meses", 26, TINTA, xanchor='right', yanchor='top')
    _texto(fig, -m, -m, f"<b>{C['n_ambos_menos']}</b> pierden en los dos", 26, TINTA, xanchor='left', yanchor='bottom')
    _texto(fig, -m, m, f"{C['n_arriba_izq']} solo en octubre", 22, TINTA_MUTED, xanchor='left', yanchor='top')
    _texto(fig, m, -m, f"{C['n_abajo_der']} solo en septiembre", 22, TINTA_MUTED, xanchor='right', yanchor='bottom')
    eje = dict(range=[-lim, lim], showgrid=False, zeroline=False, ticksuffix=' M', tickfont=dict(size=20),
               color=TINTA_MUTED, dtick=2)
    fig.update_xaxes(**eje, title=dict(text='Ganancia sobre B0 en septiembre', font=dict(size=22, color=TINTA_2)))
    fig.update_yaxes(**eje, title=dict(text='Ganancia sobre B0 en octubre', font=dict(size=22, color=TINTA_2)))
    _base(fig, 1000, 820, hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=GRIS_CLARO,
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
           't': ('eval', 'evalúa'), '.': ('nada', '')}


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
        ('✓', 'c-bien', 'La historia suma sobre lags y deltas 1–2',
         f"{C['n_ambos_mas']} de {C['n_recetas']} recetas en los dos meses", f"{C['paq_d']} M por mes"),
        ('✓', 'c-bien', 'Más meses crudos casi no suman',
         f"lags y deltas 3–5: {C['n_crudos_ambos']} de 6 en los dos meses",
         f"3 o 4 meses: de {C['pf_min']} a {C['pf_max']} M en octubre, sin pasar la regla"),
        ('✓', 'c-bien', 'La tendencia de unos 4 meses suma',
         f"W4: {C['slope_W4_sep']} / {C['slope_W4_oct']}", f"5 observaciones: {C['t4_sep']} / {C['t4_oct']}"),
        ('✓', 'c-bien', 'Rinde comparar al cliente con su propio pasado',
         'máximo, rango, relativo al promedio', f"historia curada {C['ach']}"),
        ('≠', 'c-mal', 'El rango', 'W6 suma sobre B0', f"3 meses: {C['rango_veredicto']} sobre el main"),
    ]
    cuerpo = ''.join(f'<tr><td class="marca {c}">{m}</td><td class="tema">{t}</td><td>{r}</td><td>{a}</td></tr>'
                     for m, c, t, r, a in filas)
    return ('<table class="coinc"><thead><tr><th></th><th>Tema</th><th><span class="c-recetas">Recetas</span></th>'
            f'<th><span class="c-acum">Acumulativo</span></th></tr></thead><tbody>{cuerpo}</tbody></table>')
