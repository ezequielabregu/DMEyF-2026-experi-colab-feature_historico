"""Diseño de búsqueda fijado antes de ejecutar el experimento del 13/11."""

N_TRIALS = 30
N_STARTUP_TRIALS = 8
N_CANDIDATES = 3
SEARCH_MONTHS = [201906, 201907, 201908]
FINAL_MONTHS = [201909, 201910]
SEARCH_SEED_INDICES = [0, 1]
REEVALUATION_SEED_INDICES = [2, 3, 4, 5, 6]
FINAL_SEED_INDICES = list(range(10))
SPACE = {
    'num_leaves': (24, 128, True, True),
    'min_data_in_leaf': (200, 3000, True, True),
    'learning_rate': (0.005, 0.05, True, False),
    'feature_fraction': (0.20, 0.90, False, False),
    'bagging_fraction': (0.50, 1.0, False, False),
    'arboles': (150, 900, True, True),
}
