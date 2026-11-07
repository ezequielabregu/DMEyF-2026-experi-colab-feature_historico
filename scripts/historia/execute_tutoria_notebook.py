"""Ejecuta la documentación en un kernel aislado, sin registrar entornos de usuario."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
dependencies = ROOT / 'tmp/notebookdeps'
if dependencies.exists():
    sys.path.insert(0, str(dependencies))
    os.environ['PYTHONPATH'] = str(dependencies)
os.environ['HISTORIA_DOC_ROOT'] = str(ROOT)
for name, relative in [('IPYTHONDIR', 'tmp/jupyter/ipython'), ('JUPYTER_RUNTIME_DIR', 'tmp/jupyter/runtime'), ('MPLCONFIGDIR', 'tmp/jupyter/matplotlib')]:
    folder = ROOT / relative
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(folder)
os.environ['MPLBACKEND'] = 'Agg'

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager


def execute(path, data_root=None):
    data_root = Path(data_root).resolve() if data_root else ROOT
    os.environ['HISTORIA_DOC_ROOT'] = str(data_root)
    kernel_root = ROOT / 'tmp/jupyter/kernels'
    spec = kernel_root / 'historia-doc'
    spec.mkdir(parents=True, exist_ok=True)
    (spec / 'kernel.json').write_text(json.dumps(dict(
        argv=[sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        display_name='Historia documentación', language='python')), encoding='utf-8')
    manager = KernelManager(kernel_name='historia-doc',
                            kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel_root)]))
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    client = NotebookClient(notebook, km=manager, timeout=180,
                            resources={'metadata': {'path': str(data_root)}}, allow_errors=False)
    try:
        client.execute()
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
    nbformat.validate(notebook)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == 'code']
    assert all(cell.execution_count for cell in code_cells)
    assert not [output for cell in code_cells for output in cell.outputs if output.output_type == 'error']
    images = sum('image/png' in output.get('data', {}) for cell in code_cells for output in cell.outputs)
    assert images >= 2
    nbformat.write(notebook, path)
    print(f'Notebook ejecutado: {len(code_cells)} celdas de código, {images} gráficos, cero errores.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--notebook', type=Path, default=Path('notebooks/tutoria_historia.ipynb'))
    parser.add_argument('--data-root', type=Path)
    args = parser.parse_args()
    execute(args.notebook, args.data_root)
