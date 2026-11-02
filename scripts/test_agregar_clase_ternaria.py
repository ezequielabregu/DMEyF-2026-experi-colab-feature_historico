import unittest

import pandas as pd

from scripts.agregar_clase_ternaria import label_keys


class LabelTests(unittest.TestCase):
    def keys(self, rows):
        return pd.DataFrame(rows, columns=['numero_de_cliente', 'foto_mes'])

    def test_calendar_and_censoring(self):
        keys = self.keys([(1, 202112), (1, 202201), (1, 202202),
                          (2, 202112), (3, 202112), (3, 202201), (4, 202204)])
        self.assertEqual(label_keys(keys).tolist(),
                         ['CONTINUA', '', '', 'BAJA+1', 'BAJA+2', 'BAJA+1', ''])

    def test_missing_whole_month_is_not_dropout(self):
        self.assertEqual(label_keys(self.keys([(1, 202101), (2, 202103)])).tolist(), ['', ''])

    def test_duplicates_rejected(self):
        with self.assertRaises(ValueError):
            label_keys(self.keys([(1, 202101), (1, 202101)]))

    def test_invalid_month_rejected(self):
        with self.assertRaises(ValueError):
            label_keys(self.keys([(1, 202113)]))


if __name__ == '__main__':
    unittest.main()
