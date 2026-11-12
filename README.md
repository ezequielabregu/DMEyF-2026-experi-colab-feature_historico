# DMEyF 2026 — Experimento colaborativo: feature_historico

Experimento colaborativo de Data Mining en Economía y Finanzas (UBA, comisión de los lunes).

- **Integrantes:** Tomás H., Clara M. R., Ezequiel A.
- **Tutor:** Alejandro Bolaños.

## Cómo correr el pipeline

Ver `pipeline/README.md`. Hace falta Python 3.14 y `pip install -r requirements.txt`.
Los notebooks exploratorios `01` a `24` (cómo se llegó a `PAQ_P3`) están en el branch `ezequiel/etapa-1`.

## Cómo trabajamos con git

- `main` tiene siempre código que corre.
- Cada pieza nueva va en una rama (`feat/<tema>`).
- Una rama se mergea **cuando el código funciona**, gane o pierda el experimento: los resultados negativos también se reportan.
- Antes de empezar una rama: `git switch main && git pull`.
