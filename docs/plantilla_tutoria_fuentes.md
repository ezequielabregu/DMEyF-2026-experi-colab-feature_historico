# Plantilla de tutoría y actualización de fuentes

La versión completada del PDF nuevo está en `estado_grupal_para_tutoria.md` y `estado_grupal_para_tutoria.html`. Conserva los bloques del original: problema/baseline, recorrido de pruebas, obstáculos, preguntas para Alejandro y glosario. Agrega preparación, estado de nuestras cuatro familias y trazabilidad.

El PDF nuevo permitió detectar un desfase de fuentes. El informe y notebook anteriores se basaban en `3b44f21` (hasta 09, sin resultados 09 publicados entonces). El 6/11 se actualizó origin y se obtuvo `6cf189c`, que incluye resultados 09–14. No corresponde seguir diciendo que el 09 carece de resultados sin aclarar el snapshot histórico. La nueva versión incluye esa corrección.

Las tablas fuente recientes están en `resultados/antecedentes_6cf189c`; las de nuestra cola en `resultados/familias_20261106`. No se mezclaron ni fusionaron ramas. La versión completada es de trabajo; los resultados parciales, respuestas del tutor y verificaciones aún no realizadas se señalan como pendientes.

Regeneración:

```bash
python scripts/historia/complete_tutoria_template.py
```

El PDF original no se modifica. Su estructura se adapta en Markdown editable y HTML imprimible, con figuras originales de 13 y 14 conservadas en `docs/figuras`.
