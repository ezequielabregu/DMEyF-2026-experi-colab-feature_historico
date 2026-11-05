"""Baseline + cambios relativos simétricos de uno y dos meses."""
import pandas as pd
try:
    from .common import run
    from .transforms import numeric_variables, relative
except ImportError:
    from common import run
    from transforms import numeric_variables, relative


def build_extra(base, ids, control, variables):
    return pd.DataFrame({f'{v}_rel_sim{k}': relative(control[v], control[f'{v}_lag{k}'])
                         for v in numeric_variables(variables) for k in [1, 2]})


if __name__ == '__main__':
    run('cambios_relativos', build_extra, __file__)
