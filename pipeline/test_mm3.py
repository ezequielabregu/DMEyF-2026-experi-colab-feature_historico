"""Controles del operador: calendario, clientes, faltantes, ceros y ausencia de futuro."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
import numpy as np
import pandas as pd

# Permite verificar el operador en Windows, donde resource no está disponible.
source = ast.parse(Path(__file__).with_name('funciones.py').read_text(encoding='utf8'))
operators = ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef)
                            and n.name in {'_posiciones', '_historia', 'bloque_mm3'}], type_ignores=[])
namespace = {'np': np}
exec(compile(operators, 'funciones.py', 'exec'), namespace)


class MediaMovilTest(unittest.TestCase):
    def test_calendar_clients_missing_and_zero(self):
        clientes = np.repeat([1, 2, 3], [6, 3, 3])
        meses = np.array([201901, 201902, 201903, 201905, 201906, 201907,
                          201901, 201902, 201903, 201901, 201902, 201903])
        valores = np.array([3, 6, 9, 15, 18, 21, 0, 0, 0, 1, np.nan, 3], dtype=np.float32)
        claves = clientes * 100_000 + meses // 100 * 12 + meses % 100
        datos = SimpleNamespace(X=valores[:, None], clave=claves, indice=pd.Index(claves),
                                montos=['monto'], variables=['monto'])
        resultado, columnas = namespace['bloque_mm3'](datos, np.arange(len(meses)),
                                                     SimpleNamespace(BLOQUE_FILAS=2, MINIMO_MM3=2))['MM3D']
        np.testing.assert_allclose(resultado[:, 0],
                                   [np.nan, 4.5, 6, 12, 16.5, 18,
                                    np.nan, 0, 0, np.nan, np.nan, 2], equal_nan=True)
        self.assertEqual(columnas, ['monto_media_movil3_disponible'])
        self.assertEqual(resultado.dtype, np.float32)
        # Cambiar una foto futura no afecta la media de marzo.
        datos.X[5, 0] = 99999
        parcial = namespace['bloque_mm3'](datos, np.array([2]), SimpleNamespace(BLOQUE_FILAS=2, MINIMO_MM3=2))['MM3D'][0]
        self.assertEqual(parcial[0, 0], 6)


if __name__ == '__main__':
    unittest.main()
