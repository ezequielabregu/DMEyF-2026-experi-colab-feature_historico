"""Baseline + historia con ponderación fija hacia las fotos recientes."""
import pandas as pd
try:
    from .common import run
    from .transforms import numeric_variables, recency
except ImportError:
    from common import run
    from transforms import numeric_variables, recency


def build_extra(base, ids, control, variables):
    columns = {}
    for v in numeric_variables(variables):
        for name, value in recency(control[v], control[f'{v}_lag1'], control[f'{v}_lag2']).items():
            columns[f'{v}_{name}'] = value
    return pd.DataFrame(columns)


if __name__ == '__main__':
    run('historia_reciente', build_extra, __file__)
