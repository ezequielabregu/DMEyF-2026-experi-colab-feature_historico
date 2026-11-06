"""Extensión reproducible de las diez semillas originales a veinte."""
import numpy as np


def seeds20():
    sieve = np.ones(1000000, dtype=bool)
    sieve[:2] = False
    for i in range(2, 1001):
        if sieve[i]:
            sieve[i*i::i] = False
    primes = np.flatnonzero(sieve[100000:]) + 100000
    seeds = np.random.default_rng(979201).choice(primes, size=20, replace=False).tolist()
    assert seeds[:10] == [294103, 342929, 161093, 677561, 431077, 330679, 511579, 312773, 118147, 567529]
    return seeds
