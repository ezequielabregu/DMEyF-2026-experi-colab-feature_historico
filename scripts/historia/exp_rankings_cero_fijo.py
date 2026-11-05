"""Baseline + historia de rankings mensuales separados por signo, con cero fijo."""
import numpy as np
import pandas as pd
try:
    from .common import run
    from .transforms import numeric_variables, zero_fixed_rank
except ImportError:
    from common import run
    from transforms import numeric_variables, zero_fixed_rank


def build_extra(base, ids, control, variables):
    base = base.sort_values(['foto_mes', 'numero_de_cliente']).reset_index(drop=True)
    period = (base.foto_mes // 100) * 12 + base.foto_mes % 100
    index = pd.MultiIndex.from_arrays([base.numero_de_cliente, period])
    selected_period = (ids.foto_mes // 100) * 12 + ids.foto_mes % 100
    positions = {k: index.get_indexer(pd.MultiIndex.from_arrays([
        ids.numero_de_cliente, selected_period - k])) for k in [0, 1, 2]}
    columns = {}
    monetary = [v for v in numeric_variables(variables) if v.startswith(('m', 'Visa_m', 'Master_m'))]
    for v in monetary:
        ranked = zero_fixed_rank(base[v], base.foto_mes)
        history = {}
        for k, pos in positions.items():
            history[k] = ranked[np.maximum(pos, 0)].copy()
            history[k][pos < 0] = np.nan
        columns[f'{v}_rank0'] = history[0]
        for k in [1, 2]:
            columns[f'{v}_rank_lag{k}'] = history[k]
            columns[f'{v}_rank_delta{k}'] = history[0] - history[k]
    return pd.DataFrame(columns)


if __name__ == '__main__':
    run('rankings_cero_fijo', build_extra, __file__)
