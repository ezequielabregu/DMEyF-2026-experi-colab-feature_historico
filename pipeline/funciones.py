"""Funciones del pipeline. No definen parámetros: los reciben en `p` (el módulo parametros).

Salen del notebook 22 sin cambios de lógica (fichas/etapa_31_pipeline_main.md). Secciones:
0. firmas y escritura   1. datos base (01)   2. bloques de variables (02)   3. modelos (03)   4. evaluación (04)

Para agregar un bloque (propuestas #2 a #5 y #8): escribir una función con la firma
`productor(d, filas, p) -> {nombre_bloque: (matriz float32, nombres)}`, agregarla a PRODUCTORES
y su nombre a BLOQUE_DE. Si se cambia la lógica de un bloque que ya existe, va con otro nombre:
el 02 rehace el bloque y corta si no da lo mismo que resultados/pipeline/huellas_bloques.csv.
"""
from dataclasses import dataclass
import hashlib
import inspect
import json
import os
import platform
import resource
import sys
import types

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd


def memoria_gb():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(r / (1e9 if sys.platform == 'darwin' else 1e6), 1)


def huella(x):
    """Huella de un arreglo, bit a bit. Sirve para comparar corridas entre máquinas."""
    x = np.ascontiguousarray(x)
    return hashlib.blake2b(x.tobytes(), digest_size=16).hexdigest()


def semillas(p, n):
    """Las semillas del 22: primos de 6 dígitos sorteados con la semilla primigenia."""
    criba = np.ones(1_000_000, dtype=bool)
    criba[:2] = False
    for i in range(2, 1_001):
        if criba[i]:
            criba[i * i::i] = False
    primos = np.flatnonzero(criba[100_000:]) + 100_000
    todas = np.random.default_rng(p.SEMILLA_PRIMIGENIA).choice(primos, size=20, replace=False).tolist()
    assert todas[:10] == [294103, 342929, 161093, 677561, 431077, 330679, 511579, 312773, 118147, 567529]
    assert n <= 20
    return todas[:n]


# =============================================================================
# 0. Firmas y escritura
# =============================================================================
# Un bloque o una predicción guardados se reusan solo si se hicieron con la misma firma: el mismo código,
# los mismos parámetros y los mismos datos. Así, cambiar algo nunca devuelve resultados viejos sin avisar.

SIN_FIRMA = {'FIJOS': ('num_threads',)}                 # no cambian los resultados


def _temporal(ruta):
    return ruta.with_name(f'.{ruta.stem}.tmp{ruta.suffix}')


def guardar_npy(ruta, x):
    """Escritura atómica: si la VM se apaga a mitad, no queda un archivo cortado con el nombre final."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = _temporal(ruta)
    np.save(tmp, x)
    os.replace(tmp, ruta)


def escribir_texto(ruta, texto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = _temporal(ruta)
    tmp.write_text(texto)
    os.replace(tmp, ruta)


def huella_archivo(ruta):
    h = hashlib.blake2b(digest_size=16)
    with open(ruta, 'rb') as f:
        for parte in iter(lambda: f.read(1 << 24), b''):
            h.update(parte)
    return h.hexdigest()


def _nombres(code):
    nombres = set(code.co_names)
    for k in code.co_consts:
        if isinstance(k, types.CodeType):
            nombres |= _nombres(k)
    return nombres


def _repr(x):
    """repr estable entre sesiones: un set se ordena (su orden depende del hash de cada sesión)."""
    return repr(sorted(x, key=repr)) if isinstance(x, (set, frozenset)) else repr(x)


def codigo_y_parametros(objetos, p):
    """El código de las funciones (y de las de este módulo que llaman) y el valor de los parámetros que leen."""
    modulo = globals()
    pendientes, vistos = list(objetos), set()
    codigo, parametros, constantes = {}, {}, {}
    while pendientes:
        f = pendientes.pop()
        if f.__qualname__ in vistos:
            continue
        vistos.add(f.__qualname__)
        codigo[f.__qualname__] = inspect.getsource(f)
        codes = [f.__code__] if inspect.isfunction(f) else [m.__code__ for m in vars(f).values() if inspect.isfunction(m)]
        for nombre in sorted(set().union(*(_nombres(c) for c in codes))):
            if not nombre.startswith('_') and nombre.isupper() and hasattr(p, nombre):
                valor = getattr(p, nombre)
                if nombre in SIN_FIRMA:
                    valor = {k: v for k, v in valor.items() if k not in SIN_FIRMA[nombre]}
                parametros[nombre] = _repr(valor)
            x = modulo.get(nombre)
            if (inspect.isfunction(x) or inspect.isclass(x)) and getattr(x, '__module__', None) == __name__:
                pendientes.append(x)
            elif isinstance(x, (list, tuple, dict, set, str, int, float)) and nombre.isupper():
                constantes[nombre] = _repr(x)
    return {'codigo': codigo, 'parametros': parametros, 'constantes': constantes}


def firma(detalle):
    texto = json.dumps(detalle, sort_keys=True, default=str)
    return hashlib.blake2b(texto.encode(), digest_size=8).hexdigest()


def _normalizar(detalle):
    return json.loads(json.dumps(detalle, sort_keys=True, default=str))


def diferencias(a, b, ruta=''):
    """Dónde difieren dos detalles de firma (para el mensaje de error)."""
    if isinstance(a, dict) and isinstance(b, dict):
        salida = []
        for k in sorted(set(a) | set(b)):
            salida += diferencias(a.get(k), b.get(k), f'{ruta}/{k}' if ruta else str(k))
        return salida
    return [] if a == b else [ruta]


def versiones():
    return {'python': platform.python_version(), 'lightgbm': lgb.__version__, 'numpy': np.__version__,
            'pandas': pd.__version__, 'duckdb': duckdb.__version__, 'maquina': platform.machine()}


# =============================================================================
# 1. Datos base (notebook 01; sale del 01_clase_calidad)
# =============================================================================

ESPERADO_FILAS_POR_MES = {
    201901: 123_916, 201902: 125_020, 201903: 125_622, 201904: 126_116, 201905: 126_763,
    201906: 128_370, 201907: 129_853, 201908: 131_775, 201909: 133_419, 201910: 135_633,
    201911: 137_523, 201912: 139_555,
}
# 201911 y 201912 son del dashboard: están en el parquet solo como filas sin clase (la clase de 201910
# necesita saber quién sigue en 201911 y 201912, y la regla de meses rotos mira el mes vecino de 201910).
ESPERADO_CLASES = {
    201901: {'BAJA+1': 647, 'BAJA+2': 697, 'CONTINUA': 122_572},
    201902: {'BAJA+1': 700, 'BAJA+2': 696, 'CONTINUA': 123_624},
    201903: {'BAJA+1': 700, 'BAJA+2': 774, 'CONTINUA': 124_148},
    201904: {'BAJA+1': 776, 'BAJA+2': 575, 'CONTINUA': 124_765},
    201905: {'BAJA+1': 576, 'BAJA+2': 658, 'CONTINUA': 125_529},
    201906: {'BAJA+1': 665, 'BAJA+2': 589, 'CONTINUA': 127_116},
    201907: {'BAJA+1': 595, 'BAJA+2': 656, 'CONTINUA': 128_602},
    201908: {'BAJA+1': 659, 'BAJA+2': 543, 'CONTINUA': 130_573},
    201909: {'BAJA+1': 548, 'BAJA+2': 615, 'CONTINUA': 132_256},
    201910: {'BAJA+1': 621, 'BAJA+2': 632, 'CONTINUA': 134_380},
    201911: {None: 137_523},
    201912: {None: 139_555},
}
ESPERADO_ROTOS_REGLA = {
    (v, 'ceros', mes)
    for mes in (201905, 201910)
    for v in ('mrentabilidad', 'mrentabilidad_annual', 'mpasivos_margen', 'mactivos_margen',
              'mcomisiones', 'mcomisiones_otras', 'ccomisiones_otras')
} | {('chomebanking_transacciones', 'ceros', 201910),
     ('ctarjeta_visa_debitos_automaticos', 'ceros', 201904),
     ('mttarjeta_visa_debitos_automaticos', 'ceros', 201904)}


def clases_por_mes(con, tabla):
    salida = {}
    for mes, clase, n in con.execute(f"select foto_mes, clase_ternaria, count(*) from {tabla} group by all order by all").fetchall():
        salida.setdefault(int(mes), {})[clase] = int(n)
    return salida


def construir_base(p):
    """Del crudo al parquet base de 2019: clase ternaria de la cátedra, tipos y orden por mes y cliente.
    La clase se calcula con 2019 entero y se guarda solo hasta MES_TOPE."""
    con = duckdb.connect()
    lector = f"read_csv('{p.CRUDO.as_posix()}', sample_size=-1, types={{'numero_de_cliente': 'BIGINT'}})"
    con.execute(f"create table crudo as select * from {lector} where foto_mes between {p.MES_DESDE} and {p.MES_HASTA}")
    por_mes = dict(con.execute("select foto_mes, count(*) from crudo group by 1 order by 1").fetchall())
    assert por_mes == ESPERADO_FILAS_POR_MES, por_mes
    ultimo = con.execute("select max((foto_mes // 100) * 12 + foto_mes % 100) from crudo").fetchone()[0]
    con.execute(f"""
        create table con_clase as
        with periodos as (select *, (foto_mes // 100) * 12 + foto_mes % 100 as p0 from crudo),
        futuros as (
            select *, lead(p0, 1) over w as p1, lead(p0, 2) over w as p2
            from periodos window w as (partition by numero_de_cliente order by p0))
        select * exclude (p0, p1, p2),
               case
                   when p0 < {ultimo} - 1 and p1 = p0 + 1 and (p2 is null or p2 > p0 + 2) then 'BAJA+2'
                   when p0 < {ultimo}     and (p1 is null or p1 > p0 + 1)                  then 'BAJA+1'
                   when p0 < {ultimo} - 1                                                    then 'CONTINUA'
                   else null
               end as clase_ternaria
        from futuros""")
    con.execute("drop table crudo")
    claves = ['numero_de_cliente', 'foto_mes', 'clase_ternaria']
    variables = [c[0] for c in con.execute("describe con_clase").fetchall() if c[0] not in claves]
    assert len(variables) == 152
    tipado = ', '.join(['numero_de_cliente::BIGINT as numero_de_cliente', 'foto_mes::INTEGER as foto_mes']
                       + [f'"{c}"::FLOAT as "{c}"' for c in variables]
                       + [f'case when foto_mes <= {p.MES_TOPE} then clase_ternaria end as clase_ternaria'])
    con.execute(f"create table base as select {tipado} from con_clase order by foto_mes, numero_de_cliente")
    assert clases_por_mes(con, 'base') == ESPERADO_CLASES
    p.BASE_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    tmp = _temporal(p.BASE_PARQUET)
    con.execute(f"copy base to '{tmp.as_posix()}' (format parquet, compression zstd)")
    con.close()
    os.replace(tmp, p.BASE_PARQUET)


def clase_despues_del_tope(p):
    """Filas con clase posterior a MES_TOPE en el parquet (los parquet anteriores al 2026-11-12 la tenían en 201911)."""
    con = duckdb.connect()
    n = con.execute(f"""select count(*) from read_parquet('{p.BASE_PARQUET.as_posix()}')
                        where foto_mes > {p.MES_TOPE} and clase_ternaria is not null""").fetchone()[0]
    con.close()
    return int(n)


def verificar_base(p):
    """Filas por mes, clases y columnas del parquet base."""
    con = duckdb.connect()
    tabla = f"read_parquet('{p.BASE_PARQUET.as_posix()}')"
    por_mes = dict(con.execute(f"select foto_mes, count(*) from {tabla} group by 1 order by 1").fetchall())
    assert por_mes == ESPERADO_FILAS_POR_MES, por_mes
    assert clases_por_mes(con, tabla) == ESPERADO_CLASES
    tipos = con.execute(f"describe select * from {tabla}").df().set_index('column_name')['column_type']
    con.close()
    assert len(tipos) == 155 and tipos['numero_de_cliente'] == 'BIGINT' and tipos['foto_mes'] == 'INTEGER'
    assert (tipos.drop(['numero_de_cliente', 'foto_mes', 'clase_ternaria']) == 'FLOAT').all()
    return por_mes


def meses_rotos(p):
    """Variable y mes con UMBRAL_ROTO % o más de ceros o de nulos, con los vecinos por debajo de UMBRAL_VECINOS,
    más los de ROTOS_A_MANO."""
    con = duckdb.connect()
    tabla = f"read_parquet('{p.BASE_PARQUET.as_posix()}')"
    claves = ['numero_de_cliente', 'foto_mes', 'clase_ternaria']
    variables = [c[0] for c in con.execute(f"describe select * from {tabla}").fetchall() if c[0] not in claves]
    agregados = ', '.join(f'avg(("{c}" is null)::INT) as "nulos__{c}", avg(coalesce("{c}" = 0, false)::INT) as "ceros__{c}"'
                          for c in variables)
    ancho = con.execute(f"select foto_mes, {agregados} from {tabla} group by 1 order by 1").df()
    con.close()
    calidad = (ancho.melt(id_vars='foto_mes', var_name='medida_variable', value_name='proporcion')
                    .assign(medida=lambda x: x['medida_variable'].str.split('__').str[0],
                            variable=lambda x: x['medida_variable'].str.split('__').str[1])
                    .pivot_table(index=['variable', 'medida'], columns='foto_mes', values='proporcion')
                    .mul(100).round(2))
    meses = list(calidad.columns)
    regla = []
    for (variable, medida), fila in calidad.iterrows():
        for i, mes in enumerate(meses):
            vecinos = [fila[meses[j]] for j in (i - 1, i + 1) if 0 <= j < len(meses)]
            if fila[mes] >= p.UMBRAL_ROTO and all(v < p.UMBRAL_VECINOS for v in vecinos):
                regla.append((variable, medida, mes, fila[mes], 'regla'))
    assert {(v, m, mes) for v, m, mes, *_ in regla} == ESPERADO_ROTOS_REGLA
    a_mano = [(v, m, mes, calidad.loc[(v, m), mes], 'a mano') for v, m, mes in p.ROTOS_A_MANO]
    rotos = pd.DataFrame(regla + a_mano, columns=['variable', 'medida', 'foto_mes', 'porcentaje', 'origen'])
    assert len(rotos) == 23
    return rotos


# =============================================================================
# 2. Bloques de variables (notebook 02)
# =============================================================================

BANDERAS = ['active_quarter', 'cliente_vip', 'internet', 'cdescubierto_preacordado',
            'tcallcenter', 'thomebanking', 'tmobile_app', 'ccajas_transacciones']
ESTADOS = ['tcuentas', 'Visa_status', 'Master_status', 'Visa_delinquency', 'Master_delinquency']
FECHAS = [f'{t}_{c}' for t in ('Visa', 'Master') for c in ('Fvencimiento', 'Finiciomora', 'fultimo_cierre', 'fechaalta')]
EDADES = ['cliente_edad', 'cliente_antiguedad']


@dataclass
class Datos:
    """El dataset hasta MES_TOPE, con los meses rotos a NA. Una fila por cliente y mes."""
    X: np.ndarray            # float32, columnas en el orden de `variables`
    foto_mes: np.ndarray
    clave: np.ndarray        # cliente * 100_000 + período consecutivo: clave - k es la foto de k meses antes
    indice: pd.Index
    clase: np.ndarray
    variables: list
    montos: list
    curadas: list
    rotos: list              # [(variable, mes)], incluidos los extra


def cargar_datos(p):
    con = duckdb.connect()
    base = con.execute(f"""select * from read_parquet('{p.BASE_PARQUET.as_posix()}')
                           where foto_mes <= {p.MES_TOPE} order by foto_mes, numero_de_cliente""").df()
    con.close()
    assert base['foto_mes'].max() == p.MES_TOPE
    assert base['foto_mes'].value_counts().sort_index().to_dict() == {m: n for m, n in ESPERADO_FILAS_POR_MES.items()
                                                                      if m <= p.MES_TOPE}
    claves = ['numero_de_cliente', 'foto_mes', 'clase_ternaria']
    variables = [c for c in base.columns if c not in claves]
    montos = [v for v in variables if v not in BANDERAS + ESTADOS + FECHAS + EDADES]
    assert len(variables) == 152 and len(montos) == 129

    rotos = pd.read_csv(p.RESULTADOS / 'meses_rotos.csv')[['variable', 'foto_mes']]
    assert len(rotos) == 23
    rotos = list(rotos.itertuples(index=False, name=None)) + list(p.ROTOS_EXTRA)
    for v, mes in rotos:
        base.loc[base['foto_mes'] == mes, v] = np.nan

    curadas = pd.read_csv(p.RESULTADOS_ANTERIORES / '08_variables.csv')['variable'].tolist()
    assert len(curadas) == p.N_CURADAS and set(curadas) <= set(montos)

    foto_mes = base['foto_mes'].to_numpy()
    periodo = (foto_mes // 100 * 12 + foto_mes % 100).astype(np.int64)
    clave = base['numero_de_cliente'].to_numpy(np.int64) * 100_000 + periodo
    indice = pd.Index(clave)
    assert indice.is_unique
    X = np.asfortranarray(base[variables].to_numpy(np.float32))
    clase = base['clase_ternaria'].to_numpy()
    return Datos(X, foto_mes, clave, indice, clase, variables, montos, curadas, [(v, int(m)) for v, m in rotos])


def cortar(d, mes):
    """Los datos hasta `mes` inclusive: para comprobar que ningún bloque mira el futuro."""
    hasta = d.foto_mes <= mes
    return Datos(d.X[hasta], d.foto_mes[hasta], d.clave[hasta], pd.Index(d.clave[hasta]), d.clase[hasta],
                 d.variables, d.montos, d.curadas, d.rotos)


def filas_tabla(d, meses):
    return np.flatnonzero(np.isin(d.foto_mes, meses))


def _posiciones(d, filas, k_max):
    """pos[k]: la fila de la foto de k meses antes de cada fila (-1 si no existe)."""
    return {k: d.indice.get_indexer(d.clave[filas] - k) for k in range(k_max + 1)}


def _historia(d, pos, sl, j, k_max):
    """hk[k]: la variable j, k meses antes, para las filas `sl` (NA si la foto no existe)."""
    hk = {}
    for k in range(k_max + 1):
        q = pos[k][sl]
        col = d.X[q, j]
        col[q < 0] = np.nan
        hk[k] = col
    return hk


def bloque_ac(d, filas, p):
    """AC: las 152 variables del mes, más su lag y su delta de 1 y 2 meses (760 columnas)."""
    nombres = list(d.variables) + [f'{v}_{op}{k}' for k in (1, 2) for op in ('lag', 'delta') for v in d.variables]
    ubic = {n: i for i, n in enumerate(nombres)}
    F = np.empty((len(filas), len(nombres)), dtype=np.float32)
    pos = _posiciones(d, filas, 2)
    for inicio in range(0, len(filas), p.BLOQUE_FILAS):
        sl = slice(inicio, inicio + p.BLOQUE_FILAS)
        for j, v in enumerate(d.variables):
            F[sl, ubic[v]] = d.X[filas[sl], j]
            hk = _historia(d, pos, sl, j, 2)
            for k in (1, 2):
                F[sl, ubic[f'{v}_lag{k}']] = hk[k]
                F[sl, ubic[f'{v}_delta{k}']] = hk[0] - hk[k]
    return {'AC': (F, nombres)}


def bloque_curada(d, filas, p):
    """Historia curada: ratio3, z4, relmax4 y mes_ratio3 de las 30 variables curadas (120 columnas)."""
    nombres = [f'{v}_{op}' for op in ('ratio3', 'z4', 'relmax4', 'mes_ratio3') for v in d.curadas]
    ubic = {n: i for i, n in enumerate(nombres)}
    F = np.empty((len(filas), len(nombres)), dtype=np.float32)
    pos = _posiciones(d, filas, 4)
    with np.errstate(invalid='ignore', divide='ignore'):
        for inicio in range(0, len(filas), p.BLOQUE_FILAS):
            sl = slice(inicio, inicio + p.BLOQUE_FILAS)
            for v in d.curadas:
                hk = _historia(d, pos, sl, d.variables.index(v), 4)
                a, b, c = (hk[k].astype(np.float64) for k in range(3))
                media3 = (a + b + c) / 3                  # NA si falta alguna foto
                F[sl, ubic[f'{v}_ratio3']] = np.where(np.abs(media3) > p.EPSILON, a / media3, np.nan)
                x = a
                P = np.stack([hk[k] for k in range(1, 5)]).astype(np.float64)
                valido = ~np.isnan(P)
                cuantos = valido.sum(axis=0)
                alcanza = (cuantos >= p.MINIMO_PREVIOS) & ~np.isnan(x)
                media = np.where(valido, P, 0.0).sum(axis=0) / cuantos
                desvio = np.sqrt(np.where(valido, (P - media) ** 2, 0.0).sum(axis=0) / cuantos)
                maximo = np.where(valido, P, -np.inf).max(axis=0)
                F[sl, ubic[f'{v}_z4']] = np.where(alcanza & (desvio > p.EPSILON), (x - media) / desvio, np.nan)
                F[sl, ubic[f'{v}_relmax4']] = np.where(alcanza & (maximo > p.EPSILON), x / maximo, np.nan)
    mes = d.foto_mes[filas]
    for v in d.curadas:                                   # el percentil necesita el mes entero
        F[:, ubic[f'{v}_mes_ratio3']] = pd.Series(F[:, ubic[f'{v}_ratio3']]).groupby(mes).rank(pct=True).to_numpy(np.float32)
    return {'CURADA': (F, nombres)}


def cero_fijo(x, mes):
    """Percentil dentro del mes: positivos de 0 a 1, negativos de 0 a -1, y el cero en 0."""
    s = pd.Series(x)
    arriba = s.where(s > 0).groupby(mes).rank(pct=True).fillna(0)
    abajo = (-s).where(s < 0).groupby(mes).rank(pct=True).fillna(0)
    return (arriba - abajo).where(s.notna()).to_numpy()


def bloques_ach4(d, filas, p):
    """Los cuatro bloques del 13 sobre las 30 curadas: inestabilidad, quiebre, toda la historia y contra el resto del mes."""
    pos = [d.indice.get_indexer(d.clave[filas] - k) for k in range(p.FOTOS + 1)]
    mes = d.foto_mes[filas]
    salida = {b: {} for b in ('ACH_V', 'ACH_Q', 'ACH_T', 'ACH_Z')}
    with np.errstate(invalid='ignore', divide='ignore'):
        for v in d.curadas:
            j = d.variables.index(v)
            H = np.stack([np.where(q >= 0, d.X[q, j], np.nan) for q in pos]).astype(np.float64)
            a, b, c, e = H[:4]
            dif = np.stack([a - b, b - c, c - e])
            valido = ~np.isnan(dif)
            cuantos = valido.sum(axis=0)
            alcanza = cuantos >= p.MINIMO_PREVIOS
            media = np.where(valido, dif, 0.0).sum(axis=0) / cuantos
            desvio = np.sqrt(np.where(valido, (dif - media) ** 2, 0.0).sum(axis=0) / cuantos)
            salida['ACH_V'][f'{v}_std3'] = np.stack([a, b, c]).std(axis=0)
            salida['ACH_V'][f'{v}_dstd3'] = np.where(alcanza, desvio, np.nan)
            salida['ACH_Q'][f'{v}_q4'] = (a + b) / 2 - (c + e) / 2
            salida['ACH_Q'][f'{v}_peor3'] = np.where(alcanza, np.where(valido, dif, np.inf).min(axis=0), np.nan)
            salida['ACH_Q'][f'{v}_caidas3'] = np.where(alcanza, (dif < 0).sum(axis=0), np.nan)
            P = H[1:]
            valido = ~np.isnan(P)
            cuantos = valido.sum(axis=0)
            alcanza = (cuantos >= p.MINIMO_PREVIOS) & ~np.isnan(a)
            maximo = np.where(valido, P, -np.inf).max(axis=0)
            media = np.where(valido, P, 0.0).sum(axis=0) / cuantos
            salida['ACH_T'][f'{v}_relmaxT'] = np.where(alcanza & (maximo > p.EPSILON), a / maximo, np.nan)
            salida['ACH_T'][f'{v}_relmediaT'] = np.where(alcanza & (np.abs(media) > p.EPSILON), a / media, np.nan)
            salida['ACH_T'][f'{v}_desdemaxT'] = np.where(alcanza, np.where(np.isnan(H), -np.inf, H).argmax(axis=0), np.nan)
            salida['ACH_Z'][f'{v}_zc1'] = cero_fijo(a - b, mes)
            salida['ACH_Z'][f'{v}_zc2'] = cero_fijo(a - c, mes)
    return {b: (np.column_stack(list(c.values())).astype(np.float32), list(c)) for b, c in salida.items()}


MV_SUMAS = ['mfinanciacion_limite', 'msaldototal', 'msaldopesos', 'msaldodolares', 'mconsumospesos', 'mconsumosdolares',
            'mlimitecompra', 'madelantopesos', 'madelantodolares', 'mpagado', 'mpagospesos', 'mpagosdolares',
            'mconsumototal', 'cconsumos', 'cadelantosefectivo', 'mpagominimo']
MV_MINIMOS = ['Fvencimiento', 'Finiciomora']
MV_MAXIMOS = ['fultimo_cierre', 'fechaalta']
MV_COCIENTES = [('mvr_Master_mlimitecompra', 'Master_mlimitecompra', 'mv_mlimitecompra'),
                ('mvr_Visa_mlimitecompra', 'Visa_mlimitecompra', 'mv_mlimitecompra'),
                ('mvr_msaldototal', 'mv_msaldototal', 'mv_mlimitecompra'),
                ('mvr_msaldopesos', 'mv_msaldopesos', 'mv_mlimitecompra'),
                ('mvr_msaldopesos2', 'mv_msaldopesos', 'mv_msaldototal'),
                ('mvr_msaldodolares', 'mv_msaldodolares', 'mv_mlimitecompra'),
                ('mvr_msaldodolares2', 'mv_msaldodolares', 'mv_msaldototal'),
                ('mvr_mconsumospesos', 'mv_mconsumospesos', 'mv_mlimitecompra'),
                ('mvr_mconsumosdolares', 'mv_mconsumosdolares', 'mv_mlimitecompra'),
                ('mvr_madelantopesos', 'mv_madelantopesos', 'mv_mlimitecompra'),
                ('mvr_madelantodolares', 'mv_madelantodolares', 'mv_mlimitecompra'),
                ('mvr_mpagado', 'mv_mpagado', 'mv_mlimitecompra'),
                ('mvr_mpagospesos', 'mv_mpagospesos', 'mv_mlimitecompra'),
                ('mvr_mpagosdolares', 'mv_mpagosdolares', 'mv_mlimitecompra'),
                ('mvr_mconsumototal', 'mv_mconsumototal', 'mv_mlimitecompra'),
                ('mvr_mpagominimo', 'mv_mpagominimo', 'mv_mlimitecompra')]


def combinaciones(d, p):
    """Las 43 combinaciones de Visa y Master del mes (receta 951_dataset_epic.r). Solo usan la foto de cada fila."""
    rotos_mv = set(d.rotos) | {tuple(p.ROTO_NUEVO)}
    col = lambda v: d.X[:, d.variables.index(v)].astype(np.float64)
    roto = lambda v: np.isin(d.foto_mes, [m for w, m in rotos_mv if w == v])
    s = {}
    ms, vs = col('Master_status'), col('Visa_status')
    m10, v10 = np.where(np.isnan(ms), 10, ms), np.where(np.isnan(vs), 10, vs)
    s['mv_status01'] = np.fmax(ms, vs)
    s['mv_status02'] = ms + vs
    s['mv_status03'] = np.maximum(m10, v10)
    s['mv_status04'] = m10 + v10
    s['mv_status05'] = m10 + 100 * v10
    s['mv_status06'] = np.where(np.isnan(vs), m10, vs)
    s['mv_status07'] = np.where(np.isnan(ms), v10, ms)
    for c in MV_SUMAS:
        s[f'mv_{c}'] = np.nan_to_num(col(f'Master_{c}')) + np.nan_to_num(col(f'Visa_{c}'))
    for c in MV_MINIMOS:
        s[f'mv_{c}'] = np.fmin(col(f'Master_{c}'), col(f'Visa_{c}'))
    for c in MV_MAXIMOS:
        s[f'mv_{c}'] = np.fmax(col(f'Master_{c}'), col(f'Visa_{c}'))
    for c in MV_SUMAS + MV_MINIMOS + MV_MAXIMOS:
        s[f'mv_{c}'][roto(f'Master_{c}') | roto(f'Visa_{c}')] = np.nan
    with np.errstate(invalid='ignore', divide='ignore'):
        for nombre_c, num, den in MV_COCIENTES:
            n = s[num] if num in s else col(num)
            s[nombre_c] = np.where(np.abs(s[den]) > p.EPSILON, n / s[den], np.nan)
    return np.column_stack(list(s.values())).astype(np.float32), list(s)


def bloque_mvh(d, filas, p):
    """Las 43 combinaciones de Visa y Master, más su lag y su delta de 1 y 2 meses (215 columnas)."""
    C, nombres = combinaciones(d, p)
    H = {}
    for k in [0] + p.LAGS_MV:
        q = d.indice.get_indexer(d.clave[filas] - k)
        H[k] = np.where((q >= 0)[:, None], C[np.maximum(q, 0)], np.float32(np.nan))
    partes, columnas = [H[0]], list(nombres)
    for k in p.LAGS_MV:
        partes += [H[k], H[0] - H[k]]
        columnas += [f'{n}_lag{k}' for n in nombres] + [f'{n}_delta{k}' for n in nombres]
    return {'MVH': (np.hstack(partes).astype(np.float32), columnas)}


def relativo(a, b):
    """Cambio simétrico acotado en [-1, 1]; dos ceros observados dan cero; un faltante da NaN."""
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    den = np.abs(a) + np.abs(b)
    salida = np.full(a.shape, np.nan)
    valido = np.isfinite(a) & np.isfinite(b)
    salida[valido & (den == 0)] = 0.0
    np.divide(a - b, den, out=salida, where=valido & (den > 0))
    return salida


def bloque_r(d, filas, p):
    """Cambios relativos de Tomás: r1 y r2 de los 129 montos (258 columnas). En el 22 se comprobó que da
    lo mismo que calcularlos desde los lags de la tabla."""
    j = [d.variables.index(v) for v in d.montos]
    actual = d.X[filas][:, j]
    partes = []
    for k in p.LAGS_R:
        q = d.indice.get_indexer(d.clave[filas] - k)
        previo = np.where((q >= 0)[:, None], d.X[np.maximum(q, 0)][:, j], np.nan)
        partes.append(relativo(actual, previo).astype(np.float32))
    nombres = [f'{v}_rel_sim{k}' for k in p.LAGS_R for v in d.montos]
    return {'R': (np.hstack(partes), nombres)}


# Productor de cada bloque. Para un bloque nuevo: agregar su función y su nombre acá.
PRODUCTORES = {'AC': bloque_ac, 'CURADA': bloque_curada, 'ACH_4X': bloques_ach4, 'MVH': bloque_mvh, 'R': bloque_r}
BLOQUE_DE = {'AC': 'AC', 'CURADA': 'CURADA', 'ACH_V': 'ACH_4X', 'ACH_Q': 'ACH_4X', 'ACH_T': 'ACH_4X',
             'ACH_Z': 'ACH_4X', 'MVH': 'MVH', 'R': 'R'}
ESPERADO_COLUMNAS = {'AC': 760, 'CURADA': 120, 'ACH_V': 60, 'ACH_Q': 90, 'ACH_T': 90, 'ACH_Z': 60, 'MVH': 215, 'R': 258}


def control_fuga(d, productor, completo, filas, p, cortes=(201905, 201906, 201909)):
    """Con los datos cortados en un mes, el bloque de ese mes tiene que dar lo mismo: no mira el futuro."""
    mes_fila = d.foto_mes[filas]
    for corte in cortes:
        dc = cortar(d, corte)
        parcial = PRODUCTORES[productor](dc, np.flatnonzero(dc.foto_mes == corte), p)
        for b, (F, _) in parcial.items():
            assert np.array_equal(F, completo[b][0][mes_fila == corte], equal_nan=True), (b, corte)


def carpeta_bloques(p):
    return p.EXP / 'bloques'


def guardar_bloque(p, nombre, F, nombres):
    carpeta = carpeta_bloques(p)
    guardar_npy(carpeta / f'{nombre}.npy', F)
    escribir_texto(carpeta / f'{nombre}.json', json.dumps(nombres))


def leer_bloque(p, nombre):
    """El bloque guardado, sin cargarlo entero en memoria (mmap)."""
    carpeta = carpeta_bloques(p)
    return np.load(carpeta / f'{nombre}.npy', mmap_mode='r'), json.loads((carpeta / f'{nombre}.json').read_text())


def guardar_filas(p, info):
    """Las filas de la tabla (mes, clase y cliente) y su huella."""
    ruta = carpeta_bloques(p) / 'filas.npz'
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = _temporal(ruta)
    np.savez(tmp, **info)
    os.replace(tmp, ruta)
    h = huella(np.concatenate([info['mes_fila'].astype(np.int64), info['cliente'].astype(np.int64)])) + \
        huella(np.asarray(info['clase'], dtype='U8'))
    escribir_texto(carpeta_bloques(p) / 'filas.firma.json', json.dumps({'huella': h}))


def leer_filas(p):
    z = np.load(carpeta_bloques(p) / 'filas.npz', allow_pickle=True)
    return {k: z[k] for k in z.files}


def huella_filas(p):
    return json.loads((carpeta_bloques(p) / 'filas.firma.json').read_text())['huella']


def datos_de_bloques(p):
    """Los archivos de los que salen los bloques (además del código y los parámetros)."""
    return {'parquet': huella_archivo(p.BASE_PARQUET),
            'meses_rotos': huella_archivo(p.RESULTADOS / 'meses_rotos.csv'),
            'curadas': huella_archivo(p.RESULTADOS_ANTERIORES / '08_variables.csv')}


def detalle_productor(p, productor, datos):
    return {'codigo': codigo_y_parametros([PRODUCTORES[productor], cargar_datos, filas_tabla], p), 'datos': datos}


def bloques_de(productor):
    return [b for b, q in BLOQUE_DE.items() if q == productor]


def _ruta_firma_productor(p, productor):
    return carpeta_bloques(p) / f'{productor}.firma.json'


def productor_vigente(p, productor, detalle):
    """True si los bloques del productor están guardados y se hicieron con esta misma firma."""
    ruta = _ruta_firma_productor(p, productor)
    archivos = [carpeta_bloques(p) / f'{b}.{x}' for b in bloques_de(productor) for x in ('npy', 'json')]
    if not ruta.exists() or not all(a.exists() for a in archivos):
        return False
    return json.loads(ruta.read_text())['firma'] == firma(_normalizar(detalle))


def guardar_firma_productor(p, productor, detalle, huellas):
    """Se escribe al final: si la corrida se corta antes, el 02 rehace el bloque la próxima vez."""
    escribir_texto(_ruta_firma_productor(p, productor),
                   json.dumps({'firma': firma(_normalizar(detalle)), 'huellas': huellas, 'detalle': detalle},
                              indent=1, default=str))


def huella_bloque(p, bloque):
    ruta = _ruta_firma_productor(p, BLOQUE_DE[bloque])
    assert ruta.exists(), f'Falta el bloque {bloque}: correr el 02'
    return json.loads(ruta.read_text())['huellas'][bloque]


# =============================================================================
# 3. Modelos (notebook 03)
# =============================================================================

CAMPOS_ESTRATEGIA = ('bloques', 'peso_b2', 'ventana', 'hiper', 'arboles')


def estrategia(c):
    """Lo que define las predicciones de una configuración (sin el nombre ni los meses evaluados)."""
    return {k: c[k] for k in CAMPOS_ESTRATEGIA}


def configuraciones(p):
    """Lo que corren el 02 y el 03: en el main, el main y las referencias; en un branch, el branch y el main
    (si el main no está entrenado en esta máquina, el 03 lo entrena y lo compara con las huellas versionadas)."""
    c = p.CORRIDA
    assert not p.MAIN.get('eligio_entre_varias'), "'eligio_entre_varias' es solo de los branches: sacarlo de MAIN"
    assert c['nombre'] not in p.REFERENCIAS, f"{c['nombre']} es el nombre de una referencia"
    assert all(ch.isalnum() or ch in '_-' for ch in c['nombre']), \
        f"{c['nombre']}: el nombre de la corrida va sin '/' (el branch feat/rango se corre como 'rango')"
    if c['nombre'] == 'main':
        assert c == p.MAIN, 'La corrida se llama main pero no es MAIN: un branch necesita otro nombre'
        return [p.MAIN] + list(p.REFERENCIAS.values())
    return [c, p.MAIN]


def ventana(config, mes, p):
    """Meses de entrenamiento para evaluar `mes`."""
    v = config['ventana']
    if v == 'reciente':
        meses = [x for x in p.MESES_TABLA if x <= mes - p.DISTANCIA]
    elif v == 'consigna':
        meses = list(p.MESES_CONSIGNA)
    else:
        meses = list(v)
    assert meses and max(meses) <= mes - p.DISTANCIA, (config['nombre'], mes, meses)   # sin fuga
    return meses


class Tabla:
    """Las columnas de una configuración, leídas de los bloques guardados."""

    def __init__(self, p, bloques):
        self.bloques = [leer_bloque(p, b) for b in bloques]
        self.columnas = [n for _, nombres in self.bloques for n in nombres]
        assert len(self.columnas) == len(set(self.columnas)), 'Columnas repetidas entre bloques'

    def filas(self, filas):
        """Matriz float32 de las filas pedidas (índices de la tabla), por partes para no duplicar memoria."""
        filas = np.flatnonzero(filas) if filas.dtype == bool else filas
        X = np.empty((len(filas), len(self.columnas)), dtype=np.float32)
        j0 = 0
        for M, nombres in self.bloques:
            for inicio in range(0, len(filas), 100_000):
                f = filas[inicio:inicio + 100_000]
                X[inicio:inicio + len(f), j0:j0 + len(nombres)] = M[f]
            j0 += len(nombres)
        return X


def bins(p):
    return {'max_bin': p.FIJOS['max_bin'], 'feature_pre_filter': p.FIJOS['feature_pre_filter'],
            'data_random_seed': p.SEMILLA_PRIMIGENIA}


def dataset(tabla, filas_entrena, clase, peso_b2, p):
    d = lgb.Dataset(tabla.filas(filas_entrena), label=np.isin(clase, p.POSITIVOS).astype(np.int8),
                    feature_name=list(tabla.columnas), params=bins(p), free_raw_data=True).construct()
    if peso_b2 > 1:
        d.set_weight(np.where(clase == 'BAJA+2', peso_b2, 1).astype(np.float32))
    return d


def entrenar(d, config, semilla, p):
    params = {**p.FIJOS, **config['hiper'], 'seed': semilla, 'data_random_seed': p.SEMILLA_PRIMIGENIA}
    return lgb.train(params, d, num_boost_round=config['arboles'])


def ruta_pred(p, corrida, mes, semilla):
    return p.EXP / corrida / 'pred' / str(mes) / f'{semilla}.npy'


def detalle_config(p, c):
    """Todo lo que define las predicciones de la configuración `c`."""
    return {'estrategia': estrategia(c),
            'codigo': codigo_y_parametros([dataset, entrenar, ventana, Tabla, bins], p),
            'bloques': {b: huella_bloque(p, b) for b in c['bloques']},
            'filas': huella_filas(p)}


def revisar_config(p, c, crear=True):
    """Corta si las predicciones guardadas de `c` se hicieron con otra configuración. Devuelve la firma.
    Si todavía no hay config.json, lo crea (crear=True) o corta (crear=False)."""
    carpeta = p.EXP / c['nombre']
    ruta = carpeta / 'config.json'
    detalle = _normalizar(detalle_config(p, c))
    actual = firma(detalle)
    if ruta.exists():
        guardado = json.loads(ruta.read_text())
        if guardado['firma'] != actual:
            donde = diferencias(guardado['detalle'], detalle)
            raise AssertionError(
                f"{c['nombre']}: lo guardado en {carpeta} es de otra configuración (cambió: {', '.join(donde[:8])}). "
                f"Si es el main después de un merge, renombrar la carpeta (por ejemplo a {carpeta.name}_anterior) y "
                f"volver a correr; si es un branch, borrar su carpeta o usar otro nombre.")
        return actual
    assert crear, f"{c['nombre']}: no hay predicciones en {carpeta}: correr el 03"
    if (carpeta / 'pred').exists():
        print(f"{c['nombre']}: config.json creado para las predicciones que ya estaban (se verifican abajo)")
    escribir_texto(ruta, json.dumps({'firma': actual, 'versiones': versiones(), 'detalle': detalle}, indent=1))
    return actual


def prediccion_anterior(p, c, mes, semilla):
    """La misma predicción en el 22 o el 15, si la estrategia es PAQ_P3, AC o A-consigna (si no, None)."""
    e = estrategia(c)
    if e == estrategia(p.PAQ_P3):
        carpeta = p.EXP_22 / 'pred' / 'PAQ_P3'
    elif e == estrategia(p.REFERENCIAS['AC']):
        carpeta = p.EXP_15 / 'pred' / 'AC'
    elif e == estrategia(p.REFERENCIAS['A_CONSIGNA']):     # en 201908 es el mismo modelo que AC
        carpeta = p.EXP_15 / 'pred' / 'AC' if mes == 201908 else p.EXP_22 / 'pred' / 'A_CONSIGNA'
    else:
        return None
    return carpeta / str(mes) / f'{semilla}.npy'


def revisar_huellas_pred(p, c, firma_c, semillas_, reemplazar):
    """Compara las predicciones de `c` con resultados/pipeline/<corrida>_huellas_pred.csv (versionado).
    Con la misma firma tienen que ser iguales bit a bit. Con otra firma, se reemplaza el archivo si
    `reemplazar` (configuración nueva) o se corta (el main versionado no es el de este parámetros.py)."""
    archivo = p.RESULTADOS / f"{c['nombre']}_huellas_pred.csv"
    nuevas = pd.DataFrame([{'corrida': c['nombre'], 'foto_mes': m, 'semilla': s, 'firma_config': firma_c,
                            'huella': huella(np.load(ruta_pred(p, c['nombre'], m, s)))}
                           for m in c['meses'] for s in semillas_])
    estado = 'guardadas por primera vez'
    if archivo.exists():
        previas = pd.read_csv(archivo, dtype=str)
        misma = 'firma_config' in previas and len(previas) and (previas['firma_config'] == firma_c).all()
        if misma:
            previas[['foto_mes', 'semilla']] = previas[['foto_mes', 'semilla']].astype(int)
            comun = nuevas.merge(previas, on=['foto_mes', 'semilla'], suffixes=('', '_previa'))
            distintas = comun[comun['huella'] != comun['huella_previa']]
            assert distintas.empty, (
                f"{c['nombre']}: {len(distintas)} predicciones distintas de las versionadas con la misma configuración. "
                f"Esta máquina da otros números: avisar antes de comparar branches.")
            resto = previas.merge(nuevas[['foto_mes', 'semilla']], how='left', indicator=True)
            nuevas = pd.concat([resto[resto['_merge'] == 'left_only'].drop(columns='_merge'), nuevas], ignore_index=True)
            estado = f'{len(comun)} iguales bit a bit a las versionadas'
        elif reemplazar:
            estado = 'configuración nueva: se reemplazan las huellas versionadas (versionar el archivo nuevo)'
        else:
            raise AssertionError(
                f"{c['nombre']}: las huellas versionadas son de otra configuración. ¿El branch está al día con el main? "
                f"(git merge main en el branch)")
    nuevas.sort_values(['foto_mes', 'semilla']).to_csv(archivo, index=False)
    return estado


# =============================================================================
# 4. Evaluación (notebook 04)
# =============================================================================

def curva(prob, es_b2, p):
    orden = np.argsort(-prob, kind='stable')
    return np.cumsum(np.where(es_b2[orden], p.GANANCIA_ACIERTO, -p.COSTO_ESTIMULO))[:p.LARGO_CURVA].astype(np.float64)


def banda(cv, p):
    return cv[..., p.BANDA[0] - 1:p.BANDA[1]].mean(axis=-1)


class Evaluacion:
    """Ganancias por mes y por semilla, y comparaciones pareadas con el error de clientes y de semilla."""

    def __init__(self, p, filas_info, semillas_):
        self.p = p
        self.mes_fila = filas_info['mes_fila']
        self.es_b2 = filas_info['clase'] == 'BAJA+2'
        self.clientes, self.pos_cliente = np.unique(filas_info['cliente'], return_inverse=True)
        self.semillas = semillas_
        self.puntaje = {}
        posicion = np.arange(1, p.BANDA[1] + 1)
        self.peso = (p.BANDA[1] - np.maximum(posicion, p.BANDA[0]) + 1) / (p.BANDA[1] - p.BANDA[0] + 1)

    def leer(self, corrida, meses, carpeta=None):
        for m in meses:
            if carpeta is None:
                archivos = [ruta_pred(self.p, corrida, m, s) for s in self.semillas]
            else:
                archivos = [carpeta / str(m) / f'{s}.npy' for s in self.semillas]
            P = np.stack([np.load(a) for a in archivos])
            assert P.shape == (len(self.semillas), (self.mes_fila == m).sum()) and not np.isnan(P).any()
            self.puntaje[(corrida, m)] = P

    def es_mes(self, m):
        return self.mes_fila == m

    def banda_mes(self, c, m):
        return np.array([banda(curva(x, self.es_b2[self.es_mes(m)], self.p), self.p) / 1e6 for x in self.puntaje[(c, m)]])

    def por_semilla(self, c, meses):
        return np.mean([self.banda_mes(c, m) for m in meses], axis=0)

    def ensamble(self, c, meses):
        return float(np.mean([banda(curva(self.puntaje[(c, m)].mean(axis=0), self.es_b2[self.es_mes(m)], self.p), self.p) / 1e6
                              for m in meses]))

    def por_cliente(self, c, meses):
        """Lo que cada cliente aporta al promedio mensual de la banda."""
        v = np.zeros(len(self.clientes))
        for m in meses:
            idx = np.flatnonzero(self.es_mes(m))
            for x in self.puntaje[(c, m)]:
                orden = np.argsort(-x, kind='stable')[:self.p.BANDA[1]]
                np.add.at(v, self.pos_cliente[idx[orden]],
                          self.peso * np.where(self.es_b2[idx[orden]], self.p.GANANCIA_ACIERTO, -self.p.COSTO_ESTIMULO))
        return v / (len(meses) * len(self.semillas))

    def comparar(self, c, contra, meses, semilla_bootstrap):
        """d, IC 95 % (clientes por bootstrap pareado y semilla), semillas a favor y diferencia por mes."""
        p = self.p
        d_cliente = self.por_cliente(c, meses) - self.por_cliente(contra, meses)
        d = d_cliente.sum() / 1e6
        a, b = self.por_semilla(c, meses), self.por_semilla(contra, meses)
        assert abs(d - (a.mean() - b.mean())) < 1e-6
        rng = np.random.default_rng(semilla_bootstrap)
        n, con_valor = len(d_cliente), np.flatnonzero(d_cliente)
        boot = np.empty(p.N_BOOTSTRAP)
        for i in range(p.N_BOOTSTRAP):
            veces = np.bincount(rng.integers(0, n, size=n), minlength=n)
            boot[i] = veces[con_valor] @ d_cliente[con_valor]
        e_c = (boot / 1e6).std()
        k = len(self.semillas)
        e_s_notebook = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2) * np.sqrt(2 / k)
        e_s_pareado = (a - b).std(ddof=1) / np.sqrt(k)
        e_s = max(e_s_notebook, e_s_pareado)          # la mayor de las dos, como en la comparación final del 22
        e_t = float(np.hypot(e_c, e_s))
        return {'config': c, 'contra': contra, 'meses': '-'.join(map(str, [meses[0], meses[-1]])), 'n_meses': len(meses),
                'd_M': d, 'error_clientes_M': e_c, 'error_semilla_M': e_s, 'error_total_M': e_t,
                'ic95_inf_M': d - 1.96 * e_t, 'ic95_sup_M': d + 1.96 * e_t,
                'd_ensamble_M': self.ensamble(c, meses) - self.ensamble(contra, meses),
                'semillas_a_favor': int((a > b).sum()),
                **{f'd_{m}': self.banda_mes(c, m).mean() - self.banda_mes(contra, m).mean() for m in meses}}

    def curva_media(self, c, meses):
        return np.mean([curva(x, self.es_b2[self.es_mes(m)], self.p) for m in meses for x in self.puntaje[(c, m)]], axis=0) / 1e6


def meses_regla(p, c):
    """Decisión 2 de la ficha: si el branch eligió entre varias configuraciones, se juzga solo en 201909-10."""
    return list(p.MESES_REGLA_SI_ELIGIO) if c.get('eligio_entre_varias') else list(p.MESES_EVALUADOS)


def comparaciones(p):
    """(corrida, contra, meses). En el main, contra las referencias; en un branch, contra el main."""
    c = p.CORRIDA
    if c['nombre'] == 'main':
        salida = [('main', r['nombre'], [m for m in r['meses'] if m in p.MAIN['meses']]) for r in p.REFERENCIAS.values()]
        return [x for x in salida if x[2]]
    meses = meses_regla(p, c)
    assert set(meses) <= set(c['meses']) & set(p.MAIN['meses']), (meses, c['meses'])
    return [(c['nombre'], 'main', meses)]


def regla_merge(fila, p):
    """Regla de acumulación (decisiones.md:500): d > 0 y al menos MINIMO_SEMILLAS semillas a favor."""
    return bool(fila['d_M'] > 0 and fila['semillas_a_favor'] >= p.MINIMO_SEMILLAS)
