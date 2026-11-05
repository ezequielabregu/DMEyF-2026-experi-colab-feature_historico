"""Controles de operadores y de meses calendario con historia incompleta."""
import unittest
import numpy as np
import pandas as pd
from .common import features
from .transforms import relative, trajectory, recency, zero_fixed_rank, numeric_variables
from .exp_rankings_cero_fijo import build_extra as rank_features


class TransformTests(unittest.TestCase):
    def test_relative_sign_zero_and_missing(self):
        result = relative([0, 2, -2, 0, np.nan], [0, 0, 2, 2, 3])
        np.testing.assert_allclose(result[:4], [0, 1, -1, -1])
        self.assertTrue(np.isnan(result[4]))
        self.assertTrue((np.abs(result[:4]) <= 1).all())

    def test_persistence_and_reversal(self):
        r = trajectory([1, 3, 1, np.nan], [2, 2, 3, 2], [3, 1, 1, 1])
        np.testing.assert_array_equal(r['caidas2'][:3], [1, 0, 0])
        np.testing.assert_array_equal(r['subidas2'][:3], [0, 1, 0])
        np.testing.assert_array_equal(r['reversion'][:3], [0, 0, 1])
        self.assertTrue(np.isnan(r['reversion'][3]))

    def test_recency_weights_and_complete_history(self):
        r = recency([7, 0, np.nan], [3, np.nan, 1], [1, 0, 2])
        self.assertAlmostEqual(r['media_ponderada3'][0], 5.)
        self.assertAlmostEqual(r['desvio_pasado_ponderado'][0], 14 / 3)
        self.assertTrue(np.isnan(r['media_ponderada3'][1:]).all())

    def test_monthly_rank_signs_ties_and_zeros(self):
        r = zero_fixed_rank([0, 2, 2, 8, -2, -8, np.nan, 200], [1]*7 + [2])
        np.testing.assert_allclose(r[[0, 1, 2, 3, 4, 5, 7]], [0, .5, .5, 1, -.5, -1, 1])
        self.assertTrue(np.isnan(r[6]))

    def test_calendar_gap_and_rank_history(self):
        variables = ['mvalue'] + [f'x{i}' for i in range(151)]
        rows = []
        for client, months in [(1, [201901, 201903]), (2, [201901, 201902, 201903])]:
            for month in months:
                row = dict(numero_de_cliente=client, foto_mes=month, clase_ternaria='CONTINUA')
                row.update({v: float(month % 100) for v in variables})
                rows.append(row)
        base = pd.DataFrame(rows)
        ids, frame, _, _ = features(base)
        self.assertEqual(frame.shape, (2, 760))
        self.assertTrue(np.isnan(frame.loc[0, 'mvalue_lag1']))
        self.assertEqual(frame.loc[0, 'mvalue_lag2'], 1.)
        extra = rank_features(base, ids, frame, variables)
        self.assertTrue(np.isnan(extra.loc[0, 'mvalue_rank_lag1']))
        self.assertTrue(np.isfinite(extra.loc[0, 'mvalue_rank_lag2']))
        self.assertEqual(len(extra), len(ids))


if __name__ == '__main__':
    unittest.main()
