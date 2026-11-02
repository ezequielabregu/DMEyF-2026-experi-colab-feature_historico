"""Capa DuckDB/Parquet para el baseline; cruces por mes calendario exacto."""
import hashlib
import json
from pathlib import Path

import duckdb
import pandas as pd


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def parquet_source(source, cache, threads):
    """Cache de 201901–201910 identificado por hash del archivo de origen."""
    source, cache = Path(source), Path(cache)
    fingerprint = sha256(source)
    if source.suffix == '.parquet':
        return source, fingerprint
    metadata = cache.with_suffix('.source.json')
    if cache.exists() or metadata.exists():
        if cache.exists() and metadata.exists():
            info = json.loads(metadata.read_text())
            if info['source_sha256'] == fingerprint and info['parquet_sha256'] == sha256(cache):
                return cache, fingerprint
        raise ValueError('El cache no coincide con la fuente. Usar otra ruta --cache.')
    columns = pd.read_csv(source, nrows=0).columns.tolist()
    required = {'numero_de_cliente', 'foto_mes', 'clase_ternaria'}
    if not required.issubset(columns):
        raise ValueError(f'Faltan columnas: {required - set(columns)}')
    expressions = []
    for name in columns:
        kind = 'VARCHAR' if name == 'clase_ternaria' else ('BIGINT' if name in required else 'DOUBLE')
        expressions.append(f'CAST({quote(name)} AS {kind}) AS {quote(name)}')
    cache.parent.mkdir(parents=True, exist_ok=True)
    temporary = cache.with_suffix('.partial.parquet')
    if temporary.exists():
        raise ValueError(f'Existe un cache parcial: {temporary}')
    with duckdb.connect() as con:
        con.execute(f'SET threads={int(threads)}')
        con.execute(f"CREATE VIEW source AS SELECT * FROM read_csv({literal(source)}, header=true, all_varchar=true)")
        query = 'SELECT ' + ', '.join(expressions) + ' FROM source WHERE CAST(foto_mes AS BIGINT) BETWEEN 201901 AND 201910'
        con.execute(f"COPY ({query}) TO {literal(temporary)} (FORMAT PARQUET, COMPRESSION ZSTD)")
    temporary.rename(cache)
    metadata.write_text(json.dumps(dict(source=str(source.resolve()), source_sha256=fingerprint,
                                        parquet_sha256=sha256(cache)), indent=2))
    return cache, fingerprint


class BaselineData:
    def __init__(self, path, threads):
        self.con = duckdb.connect()
        self.con.execute(f'SET threads={int(threads)}')
        self.con.execute(f"CREATE VIEW raw AS SELECT * FROM read_parquet({literal(path)}) WHERE foto_mes BETWEEN 201901 AND 201910")
        if self.con.execute('SELECT count(*) FROM (SELECT numero_de_cliente, foto_mes FROM raw GROUP BY ALL HAVING count(*) > 1)').fetchone()[0]:
            raise ValueError('Claves cliente-mes duplicadas')
        if self.con.execute("SELECT count(*) FROM raw WHERE numero_de_cliente IS NULL OR foto_mes IS NULL OR clase_ternaria IS NULL OR clase_ternaria NOT IN ('BAJA+1','BAJA+2','CONTINUA')").fetchone()[0]:
            raise ValueError('Claves o clases faltantes/desconocidas')
        self.counts = dict(self.con.execute('SELECT foto_mes, count(*) FROM raw GROUP BY foto_mes ORDER BY foto_mes').fetchall())
        if set(self.counts) != set(range(201901, 201911)):
            raise ValueError('Faltan fotos mensuales entre 201901 y 201910')
        self.columns = [row[0] for row in self.con.execute('DESCRIBE raw').fetchall()
                        if row[0] not in ['numero_de_cliente', 'foto_mes', 'clase_ternaria']]
        self.con.execute("CREATE VIEW base AS SELECT *, strptime(CAST(foto_mes AS VARCHAR), '%Y%m') AS mes FROM raw")

    def split(self, months):
        expressions = ['a.numero_de_cliente', 'a.foto_mes', 'a.clase_ternaria']
        expressions += [f'CAST(a.{quote(c)} AS FLOAT) AS {quote(c)}' for c in self.columns]
        for lag in [1, 2]:
            for c in self.columns:
                expressions += [f'CAST(p{lag}.{quote(c)} AS FLOAT) AS {quote(c + f"_lag{lag}")}',
                                f'CAST(a.{quote(c)} - p{lag}.{quote(c)} AS FLOAT) AS {quote(c + f"_delta{lag}")}']
        query = 'SELECT ' + ', '.join(expressions) + ' FROM base a '
        for lag in [1, 2]:
            query += f" LEFT JOIN base p{lag} ON a.numero_de_cliente=p{lag}.numero_de_cliente AND p{lag}.mes=a.mes - INTERVAL '{lag} months' "
        query += ' WHERE a.foto_mes IN (' + ','.join(str(int(m)) for m in months) + ') ORDER BY a.foto_mes, a.numero_de_cliente'
        frame = self.con.execute(query).fetchdf()
        labels = frame.pop('clase_ternaria').isin(['BAJA+1', 'BAJA+2']).astype('int8')
        ids = frame[['numero_de_cliente', 'foto_mes']].copy()
        features = frame.drop(columns='numero_de_cliente').replace([float('inf'), -float('inf')], float('nan'))
        if labels.nunique() != 2:
            raise ValueError('Split vacío o con una sola clase')
        return features, labels, ids

    def close(self):
        self.con.close()
