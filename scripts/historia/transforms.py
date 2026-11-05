"""Operadores puros; faltantes y ceros conservan significados distintos."""
import numpy as np
import pandas as pd


def numeric_variables(variables):
    flags = {'active_quarter', 'cliente_vip', 'internet', 'cdescubierto_preacordado',
             'tcallcenter', 'thomebanking', 'tmobile_app', 'ccajas_transacciones'}
    states = {'tcuentas', 'Visa_status', 'Master_status', 'Visa_delinquency', 'Master_delinquency'}
    dates = {f'{t}_{c}' for t in ('Visa', 'Master') for c in
             ('Fvencimiento', 'Finiciomora', 'fultimo_cierre', 'fechaalta')}
    return [v for v in variables if v not in flags | states | dates | {'cliente_edad', 'cliente_antiguedad'}]


def relative(a, b):
    """Cambio simétrico acotado [-1,1]; dos ceros observados dan cero."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    denominator = np.abs(a) + np.abs(b)
    result = np.full(a.shape, np.nan)
    valid = np.isfinite(a) & np.isfinite(b)
    result[valid & (denominator == 0)] = 0.
    np.divide(a - b, denominator, out=result, where=valid & (denominator > 0))
    return result


def trajectory(a, b, c):
    """Orden: actual, mes anterior, dos meses antes."""
    a, b, c = (np.asarray(v, dtype=float) for v in (a, b, c))
    complete = np.isfinite(a) & np.isfinite(b) & np.isfinite(c)
    recent, previous = a - b, b - c
    return {
        'caidas2': np.where(complete, ((recent < 0) & (previous < 0)).astype(float), np.nan),
        'subidas2': np.where(complete, ((recent > 0) & (previous > 0)).astype(float), np.nan),
        'reversion': np.where(complete, (((recent < 0) & (previous > 0)) | ((recent > 0) & (previous < 0))).astype(float), np.nan),
        'aceleracion_relativa': np.where(complete, relative(a, b) - relative(b, c), np.nan),
    }


def recency(a, b, c):
    a, b, c = (np.asarray(v, dtype=float) for v in (a, b, c))
    complete = np.isfinite(a) & np.isfinite(b) & np.isfinite(c)
    previous = (2 * b + c) / 3
    return {
        'media_ponderada3': np.where(complete, (4 * a + 2 * b + c) / 7, np.nan),
        'desvio_pasado_ponderado': np.where(complete, a - previous, np.nan),
        'cambio_rel_pasado_ponderado': np.where(complete, relative(a, previous), np.nan),
    }


def zero_fixed_rank(values, months):
    """Percentil por mes y signo. Ceros en 0; nulos permanecen nulos."""
    x = pd.Series(np.asarray(values, dtype=float))
    month = pd.Series(np.asarray(months))
    result = pd.Series(np.nan, index=x.index, dtype=float)
    result[x == 0] = 0.
    for sign in [1, -1]:
        use = np.isfinite(x) & (x * sign > 0)
        ranked = (x[use] * sign).groupby(month[use]).rank(method='average', pct=True)
        result.loc[use] = sign * ranked
    return result.to_numpy()
