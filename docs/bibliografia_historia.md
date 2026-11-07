# Bibliografía metodológica verificada

Fuentes primarias consultadas el 7 de noviembre de 2026. Respaldan conceptos y
herramientas; las métricas del trabajo provienen de los agregados y manifiestos
del repositorio. Esta revisión no recalcula los contrastes de los compañeros.

- Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q. y Liu, T.-Y.
  (2017). [LightGBM: A Highly Efficient Gradient Boosting Decision Tree](https://proceedings.neurips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html).
  Advances in Neural Information Processing Systems 30. Artículo del software usado.
- Proyecto LightGBM. [Parameters](https://lightgbm.readthedocs.io/en/stable/Parameters.html).
  Documenta seed, data_random_seed y muestreo para construir bins. La auditoría
  concreta del trabajo se verificó además mediante predicciones idénticas.
- Proyecto scikit-learn. [roc_auc_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html).
  Define el cálculo de ROC-AUC desde scores. No sustituye la función económica
  particular de la consigna, que se documenta por separado.
- Proyecto SciPy. [scipy.stats.wilcoxon](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html).
  Describe el contraste de rangos con signo para pares y las precauciones con
  ceros, empates y método exacto. Los p del informe se atribuyen a sus tablas fuente.
- Proyecto statsmodels. [multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html).
  Documenta Holm como corrección escalonada basada en Bonferroni para múltiples
  contrastes. La regla de seis contrastes es una decisión del grupo.
- Proyecto scikit-learn. [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html).
  Referencia conceptual sobre particiones con orden temporal. No se afirma haber
  usado esta clase: el trabajo usa los meses y particiones descritos en su protocolo.

Las páginas de documentación pueden mostrar versiones posteriores al entorno de
entrenamiento. Las versiones efectivamente usadas siguen registradas en cada
config.json; consultar estas referencias no cambia la configuración de las corridas.
