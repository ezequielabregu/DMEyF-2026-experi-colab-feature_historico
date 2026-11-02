import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

from scripts.baseline_data import BaselineData, parquet_source


class BaselineTests(unittest.TestCase):
    def test_calendar_joins_and_future_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frame = pd.DataFrame([
                dict(numero_de_cliente=i, foto_mes=201900+m, valor=float(i+m),
                     clase_ternaria='BAJA+2' if i % 2 else 'CONTINUA')
                for m in range(1, 11) for i in range(12) if not (i == 0 and m == 2)])
            path = root / 'data.parquet'
            frame.to_parquet(path)
            data = BaselineData(path, 1)
            before, _, _ = data.split([201903])
            data.close()
            self.assertTrue(pd.isna(before.iloc[0].valor_lag1))
            self.assertEqual(before.iloc[0].valor_delta2, 2)
            self.assertNotIn('clase_ternaria', before)
            self.assertNotIn('numero_de_cliente', before)
            frame.loc[frame.foto_mes > 201903, 'valor'] = -9999
            frame.to_parquet(path)
            data = BaselineData(path, 1)
            after, _, _ = data.split([201903])
            data.close()
            pd.testing.assert_frame_equal(before, after)

    def test_run_registry_and_cache_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, cache = root / 'source.csv', root / 'cache.parquet'
            pd.DataFrame([
                dict(numero_de_cliente=i, foto_mes=201900+m, valor=i+m,
                     clase_ternaria='BAJA+1' if i % 2 else 'CONTINUA')
                for m in range(1, 11) for i in range(12)]).to_csv(source, index=False)
            cmd = [sys.executable, 'scripts/baseline.py', '--data', str(source),
                   '--cache', str(cache), '--out', str(root / 'run'),
                   '--registry', str(root / 'registry.sqlite'),
                   '--summary-dir', str(root / 'summary'), '--trials', '2',
                   '--max-rounds', '3', '--patience', '2', '--threads', '1']
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.assertEqual(json.loads((root / 'run/status.json').read_text())['status'], 'complete')
            with sqlite3.connect(root / 'registry.sqlite') as con:
                self.assertEqual(con.execute('SELECT status FROM runs').fetchone()[0], 'complete')
            self.assertEqual(len(pd.read_parquet(root / 'run/predictions_201910.parquet')), 12)
            self.assertEqual(len(pd.read_csv(root / 'run/trials.csv')), 2)
            self.assertEqual(parquet_source(source, cache, 1)[0], cache)
            with source.open('a') as out:
                out.write('99,201910,1,CONTINUA\n')
            with self.assertRaises(ValueError):
                parquet_source(source, cache, 1)
            # Una falla posterior a iniciar la corrida también queda registrada.
            cmd[cmd.index(str(root / 'run'))] = str(root / 'failed')
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads((root / 'failed/status.json').read_text())['status'], 'failed')
            with sqlite3.connect(root / 'registry.sqlite') as con:
                self.assertEqual(con.execute("SELECT count(*) FROM runs WHERE status='failed'").fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main()
