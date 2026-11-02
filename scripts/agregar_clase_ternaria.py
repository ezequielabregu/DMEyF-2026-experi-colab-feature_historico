"""Etiquetas por presencia cliente-mes, preservando valores y orden del CSV."""
import argparse
import csv
import gzip
import hashlib
import json
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd


def label_keys(keys, client='numero_de_cliente', month='foto_mes'):
    if keys[[client, month]].isna().any().any():
        raise ValueError('Claves nulas')
    if keys.duplicated([client, month]).any():
        raise ValueError('Combinaciones cliente-mes duplicadas')
    dates = pd.to_datetime(keys[month].astype(str), format='%Y%m', errors='raise')
    periods = dates.dt.to_period('M').astype('int64')
    available = set(periods)
    index = pd.MultiIndex.from_arrays([keys[client], periods])
    next_present = pd.MultiIndex.from_arrays([keys[client], periods + 1]).isin(index)
    second_present = pd.MultiIndex.from_arrays([keys[client], periods + 2]).isin(index)
    next_available = (periods + 1).isin(available).to_numpy()
    second_available = (periods + 2).isin(available).to_numpy()
    labels = np.full(len(keys), '', dtype=object)
    labels[next_available & ~next_present] = 'BAJA+1'
    known = next_available & next_present & second_available
    labels[known & ~second_present] = 'BAJA+2'
    labels[known & second_present] = 'CONTINUA'
    return labels


def open_csv(path, mode):
    options = dict(newline='', encoding='utf-8')
    if path.suffix == '.gz':
        return gzip.open(path, mode + 't', compresslevel=1, **options)
    return open(path, mode + 't', **options)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        parser.error('La salida debe ser un archivo nuevo')
    print('Leyendo y verificando claves...', flush=True)
    keys = pd.read_csv(args.input, usecols=['numero_de_cliente', 'foto_mes'],
                       dtype={'numero_de_cliente': 'int64', 'foto_mes': 'int64'})
    labels = label_keys(keys)
    clients, month_keys = keys.numero_de_cliente.to_numpy(), keys.foto_mes.to_numpy()
    months = sorted(keys.foto_mes.unique().tolist())
    full = pd.period_range(str(months[0]), str(months[-1]), freq='M')
    missing = sorted(set(int(p.strftime('%Y%m')) for p in full) - set(months))
    report = keys.assign(clase_ternaria=np.where(labels == '', 'NULO', labels))\
        .groupby(['foto_mes', 'clase_ternaria']).size().unstack(fill_value=0)\
        .reindex(columns=['BAJA+1', 'BAJA+2', 'CONTINUA', 'NULO'], fill_value=0)
    print(report.to_string(), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    digest_in, digest_out = hashlib.sha256(), hashlib.sha256()
    print('Escribiendo copia etiquetada sin convertir las otras variables...', flush=True)
    with open_csv(args.input, 'r') as src, open_csv(args.output, 'x') as dst:
        reader, writer = csv.reader(src), csv.writer(dst)
        header = next(reader)
        if 'clase_ternaria' in header:
            raise ValueError('El original ya contiene clase_ternaria')
        ci, mi = header.index('numero_de_cliente'), header.index('foto_mes')
        writer.writerow(header + ['clase_ternaria'])
        count = 0
        for count, row in enumerate(reader, start=1):
            i = count - 1
            if i >= len(keys) or Decimal(row[ci]) != int(clients[i]) or Decimal(row[mi]) != int(month_keys[i]):
                raise ValueError('Cambió el orden o las claves durante la lectura')
            payload = json.dumps(row, ensure_ascii=False).encode()
            digest_in.update(payload)
            writer.writerow(row + [labels[i]])
    if count != len(keys):
        raise ValueError('Cambió el número de filas')
    print('Verificando el archivo escrito...', flush=True)
    with open_csv(args.output, 'r') as dst:
        reader = csv.reader(dst)
        assert next(reader) == header + ['clase_ternaria']
        written = 0
        for written, row in enumerate(reader, start=1):
            digest_out.update(json.dumps(row[:-1], ensure_ascii=False).encode())
            if row[-1] != labels[written - 1]:
                raise ValueError('Etiqueta escrita incorrecta')
    if written != len(keys) or digest_in.digest() != digest_out.digest():
        raise ValueError('La copia no conserva valores, filas y orden')
    args.report_dir.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.report_dir / 'conteos_por_mes.csv')
    summary = dict(input=str(args.input.resolve()), output=str(args.output.resolve()),
                   rows=len(keys), months=months, missing_months=missing,
                   original_values_sha256=digest_in.hexdigest(), verified=True,
                   limitation='La continuidad del calendario no demuestra que las fotos estén completas. '
                   'No hay evidencia independiente de extracción íntegra ni de que toda ausencia sea una baja. '
                   'Etiquetas operativas por presencia; no se usan otras variables.')
    (args.report_dir / 'verificacion.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
