# DMEyF 2026 — Experimento colaborativo: feature_historico

Experimento colaborativo de Data Mining en Economía y Finanzas (UBA, comisión de los lunes).

- **Integrantes:** Tomás H., Clara M. R., Ezequiel A.
- **Tutor:** Alejandro Bolaños.

## Cómo trabajamos con git

- `main` tiene siempre código que corre.
- Cada pieza nueva va en una rama (`feat/<tema>`).
- Una rama se mergea **cuando el código funciona**, gane o pierda el experimento: los resultados negativos también se reportan.
- Antes de empezar una rama: `git switch main && git pull`.

## Cómo reproducir el experimento

El diseño, la regla de decisión y todos los cambios están en `docs/diseno_experimental.md`. El resultado de la regla está en `resultados/04_regla.csv`.

### Preparación

Hace falta Python 3.14 y unos 6 GB de memoria libre. Los tiempos son de una Mac M4 con 8 hilos.

```bash
git clone https://github.com/ezequielabregu/DMEyF-2026-experi-colab-feature_historico.git
cd DMEyF-2026-experi-colab-feature_historico
git switch ezequiel/etapa-1

python3.14 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Dataset:** `competencia_02_crudo.csv`, el de la cátedra (4.707.495 filas y 154 columnas). No está en el repo. Antes de correr el `01`, poné su ruta en el parámetro `CRUDO` de la primera celda de código.

### Notebooks

Se corren en orden, con "Run All", desde la carpeta `notebooks/`. Cada uno frena con un `assert` si algo no da lo esperado.

| Notebook | Qué hace | Salidas principales | Tiempo |
|---|---|---|---|
| `01_clase_calidad` | Calcula la clase ternaria, revisa la calidad y detecta los meses rotos | `data/base_2019.parquet`, `resultados/01_*` | ~4 min |
| `02_experimento_minimo` | Ensayo de A contra LT4 en 201908. Es opcional: nada depende de él | `resultados/02_*` | ~25 min |
| `03_corridas` | Corre Optuna y los 100 modelos, sin cargar la clase de 201909 y 201910 | `exp/03/`, `resultados/03_*` | ~2,5 h |
| `04_evaluacion` | Carga la clase del test, aplica la regla y arma las figuras | `resultados/04_*`, `resultados/figuras/04_*` | Segundos |
| `05_exploratorio` | Ensamble y segundas diferencias. Es exploratorio, posterior a la regla | `exp/05/`, `resultados/05_*`, `resultados/figuras/05_*` | ~10 min |
| `06_exploratorio` | `ratio3` y `zero_streak3` sobre la ventana de la consigna. Es exploratorio, posterior a la regla | `exp/06/`, `resultados/06_*`, `resultados/figuras/06_*` | ~30 min |
| `07_exploratorio` | Hiperparámetros propios para la ventana de la consigna. Es exploratorio, posterior a la regla, y usa las salidas del `06` | `exp/07/`, `resultados/07_*`, `resultados/figuras/07_*` | ~1,5 h |
| `08_exploratorio` | Historia sin resignar meses: mezclas, LT3 y LT4 sobre 201903–06, e historia curada. Es exploratorio, posterior a la regla, y usa las salidas del `03` y del `06` | `exp/08/`, `resultados/08_*`, `resultados/figuras/08_*` | ~35 min |
| `09_exploratorio` | Eventos entre productos, ratios intra-mes, historial del puntaje y hojas de Random Forest sobre la historia curada. Es exploratorio, posterior a la regla, y usa las salidas del `06` y del `08` | `exp/09/`, `resultados/09_*`, `resultados/figuras/09_*` | ~50 min |
| `10_exploratorio` | Separa el puntaje del mes de su pasado y repite `ACP` con otras dos particiones. Es exploratorio, posterior a la regla, y usa las salidas del `06`, del `08` y del `09` | `exp/10/`, `resultados/10_*`, `resultados/figuras/10_*` | ~35 min |
| `11_exploratorio` | Repite `ACPH` con las particiones B y C. Es exploratorio, posterior a la regla, y usa las salidas del `06`, del `08`, del `09` y del `10` | `exp/11/`, `resultados/11_*`, `resultados/figuras/11_*` | ~15 min |
| `12_exploratorio` | Mide un modelo sin lags ni deltas y entrena `AC`, `ACH` y `ACPH` con los meses más recientes. Es exploratorio, posterior a la regla, y usa las salidas del `06`, del `08`, del `09`, del `10` y del `11` | `exp/12/`, `resultados/12_*`, `resultados/figuras/12_*` | ~1,7 h |
| `13_exploratorio` | Banco de pruebas: evalúa ideas de historia en 201903–08, sobre clientes que el modelo no vio. No carga 201909 ni 201910. Es exploratorio, posterior a la regla, y usa las salidas del `03`, del `06` y del `08` | `exp/13/`, `resultados/13_*`, `resultados/figuras/13_*` | ~1 h |
| `14_exploratorio` | Prueba las cuatro ideas del `13` juntas, con 5 semillas y sobre el mismo banco. No carga 201909 ni 201910. Es exploratorio, posterior a la regla, y usa las salidas del `13` | `exp/14/`, `resultados/14_*`, `resultados/figuras/14_*` | ~40 min |
| `15_exploratorio` | Banco temporal: cada modelo entrena hasta dos meses antes del mes evaluado, de 201906 a 201910. Mide `ACH`, `ACH_4`, más peso para `BAJA+2` y tres ventanas. Es exploratorio, posterior a la regla, y usa las salidas del `12` | `exp/15/`, `resultados/15_*`, `resultados/figuras/15_*` | ~2 h |
| `16_exploratorio` | Cantidad de árboles sobre `ACH_4_P3`, en el banco del `15`: decide la regla de árboles proporcionales a las filas de entrenamiento contra 296, y muestra la curva hasta 1.000. Es exploratorio, posterior a la regla, y usa las salidas del `15` | `exp/16/`, `resultados/16_*`, `resultados/figuras/16_*` | ~1 h |
| `17_exploratorio` | Combinaciones de Visa y Master (sumas, fechas y cocientes contra el límite, de la cátedra 2021) sobre `ACH_4_P3`, en el banco del `15`: decide la versión con lags y deltas. Es exploratorio, posterior a la regla, y usa las salidas del `15` | `exp/17/`, `resultados/17_*`, `resultados/figuras/17_*` | ~45 min |
| `18_exploratorio` | `ACH_4_P3` entrenada con todas las bajas y el 10 % de `CONTINUA` (*undersampling*, como la cátedra 2021), con peso 3 o 1 y hojas de 764 o 76 filas, en el banco del `15`. Es exploratorio, posterior a la regla, y usa las salidas del `15` | `exp/18/`, `resultados/18_*`, `resultados/figuras/18_*` | ~20 min |
| `19_exploratorio` | Tamaño de los árboles de `ACH_4_P3`: grilla de `num_leaves` (25 a 400) × `min_data_in_leaf` (100 a 3.000), elegida con 201906–08 y una semilla, y confirmada en 201909–10 con 5 semillas, en el banco del `15`. Es exploratorio, posterior a la regla, y usa las salidas del `15` | `exp/19/`, `resultados/19_*`, `resultados/figuras/19_*` | ~2 h |

Si una corrida del `03`, del `05`, del `06`, del `07`, del `08`, del `09`, del `10`, del `11`, del `12`, del `13` o del `14` se corta, se vuelve a correr entera: las semillas ya hechas no se repiten.

### Qué tener en cuenta

- **Lo que se regenera:** `data/` y `exp/` no están en el repo. El `03` y el `05` necesitan el parquet del `01`, y el `04` y el `05` necesitan las predicciones del `03`, en `exp/03/`.
- **Corrida completa del `03`:** si existe `resultados/03_hiperparametros.json`, no corre Optuna y usa esos valores. Para repetir todo desde cero, antes hay que borrar `resultados/03_*` y `exp/03/`.
- **`requirements.txt`:** el `01` lo reescribe con las versiones instaladas. Si cambia, no hace falta commitearlo.
- **`N_HILOS`:** dejarlo en 8, para comparar con los resultados guardados.

### Replicar el baseline en otra máquina

Sirve para comprobar que el código da lo mismo en otra máquina, sin correr Optuna ni los 100 modelos:

1. Correr el `01`.
2. En la primera celda de código del `03`, cambiar:

   ```python
   CONFIGURACIONES = ['A']
   N_SEMILLAS = 2
   ```

3. Correr el `03`, que usa los hiperparámetros guardados. Tarda alrededor de un minuto.
4. Comparar la AUC de 201908, que aparece impresa en cada semilla, con estos valores:

   | Semilla | AUC 201908 |
   |---|---:|
   | 294103 | 0,909510 |
   | 342929 | 0,906017 |

   Tiene que dar lo mismo, o una diferencia mínima explicada por la plataforma.
5. **No commitear los `resultados/03_*`:** esta corrida los cambia, y `03_N.csv` queda solo con A. Para descartar los cambios: `git restore resultados/ notebooks/ requirements.txt`.
