import unittest
import numpy as np
try:
    from .evaluate_profit import profit, HIT, MISS
except ImportError:
    from evaluate_profit import profit, HIT, MISS


class ProfitTests(unittest.TestCase):
    def test_payouts_band_boundaries_and_stable_ties(self):
        prob = np.ones(6000) * .5
        y = np.zeros(6000, dtype=bool)
        y[[0, 2999, 3999, 4000, 5999]] = True
        result = profit(prob, y)
        self.assertEqual(result['hits_4000'], 3)
        self.assertEqual(result['gain_4000_M'], (3 * HIT + 3997 * MISS) / 1e6)
        independent = []
        for n in range(3000, 6001):
            hits = int(y[:n].sum())
            independent.append(hits * HIT + (n - hits) * MISS)
        self.assertAlmostEqual(result['gain_band_3000_6000_M'], sum(independent) / len(independent) / 1e6)

    def test_invalid_probabilities_rejected(self):
        with self.assertRaises(ValueError):
            profit(np.full(6000, np.nan), np.zeros(6000, dtype=bool))


if __name__ == '__main__':
    unittest.main()
