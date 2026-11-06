# Dataset original de la competencia 02

URL de descarga (recuperada del historial de trabajo del 2 de noviembre de 2026):

https://storage.googleapis.com/open-courses/dmeyf2026-9c6f/competencia_02_crudo.csv.gz

Archivo: `competencia_02_crudo.csv.gz`. Es el crudo, sin `clase_ternaria`.

## Descarga en la VM de Google Cloud

```bash
mkdir -p ~/datasets
wget -c \
  -O ~/datasets/competencia_02_crudo.csv.gz \
  https://storage.googleapis.com/open-courses/dmeyf2026-9c6f/competencia_02_crudo.csv.gz
```

Verificar la integridad del gzip y consultar el tamaño, sin descomprimirlo:

```bash
gzip -t ~/datasets/competencia_02_crudo.csv.gz \
  && ls -lh ~/datasets/competencia_02_crudo.csv.gz
```

Registrar la huella del archivo descargado para comparar las réplicas:

```bash
sha256sum ~/datasets/competencia_02_crudo.csv.gz
```

La comprobación gzip detecta daños del archivo comprimido; no certifica su identidad con la copia usada por los compañeros. Para eso hay que comparar las huellas SHA-256.

El dataset se guarda fuera del repositorio. Ver [construcción de etiquetas](etiquetado.md) y [plan de réplica](revision_experimentos_20261104.md) antes de preparar los datos de cada implementación.
