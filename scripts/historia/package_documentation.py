"""Paquete portable de tutoría: notebook ejecutado, documentación y agregados."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    files = {Path('README.md'), Path('notebooks/tutoria_historia.ipynb'), Path('output/pdf/informe_ezequiel_actualizado_20261107.pdf')}
    for name in ['tutoria_historia', 'plantilla_tutoria_fuentes', 'evaluacion_economica_historia',
                 'auditoria_bins_20261107', 'estado_grupal_para_tutoria', 'informe_experimentos_historia',
                 'bibliografia_historia', 'CIERRE_DOCUMENTACION_20261107', 'edicion_reporte_ezequiel']:
        files.add(Path(f'docs/{name}.md'))
    files.update([Path('docs/estado_grupal_para_tutoria.html'), Path('docs/informe_experimentos_historia.html')])
    for root in ['resultados/antecedentes_6cf189c', 'resultados/familias_final_20261106',
                 'resultados/ampliaciones_20261107', 'docs/figuras', 'output/tutoria']:
        files.update(path for path in Path(root).rglob('*') if path.is_file() and path.suffix in ['.csv', '.json', '.png'])
    for name in ['build_tutoria_notebook.py', 'execute_tutoria_notebook.py', 'complete_tutoria_template.py',
                 'build_tutoria_pdf.py', 'package_documentation.py', 'build_report.py', 'group_history_report.py',
                 'requirements-documentacion.txt']:
        files.add(Path('scripts/historia') / name)
    for path in files:
        if not path.is_file() or path.name == 'validation_keys.csv' or path.suffix in ['.npy', '.parquet']:
            raise ValueError(f'Entrada inesperada o ausente: {path}')
    manifest = dict(captured_utc=datetime.now(timezone.utc).isoformat(),
                    scope='Solo documentación y agregados; cuatro familias de diez pares y dos de veinte.',
                    sha256={path.as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)})
    out = Path('output/tutoria/tutoria_historia_documentacion_20261107.zip')
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.as_posix())
        archive.writestr('DOCUMENTACION_MANIFEST.json', json.dumps(manifest, indent=2, ensure_ascii=False))
        archive.writestr('LEER_PRIMERO.md', '# Tutoría: documentación final\n\nAbrir notebooks/tutoria_historia.ipynb. '
                          'Las tablas y los dos gráficos ya están ejecutados. Para recalcular en Colab, subir este ZIP '
                          'cuando lo pida. No requiere dataset ni credenciales. Guía: docs/tutoria_historia.md.\n')
    with zipfile.ZipFile(out) as archive:
        assert archive.testzip() is None
        for name, expected in manifest['sha256'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected
    print(f'{out}: {len(files)} archivos verificados, sin claves ni predicciones individuales.')


if __name__ == '__main__':
    main()
