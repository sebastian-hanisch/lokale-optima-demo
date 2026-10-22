"""Szenario: Graphen (Zufallsgraph, vollständig mit Gewicht 1, die Familie exp-min) und der zufällige Startschnitt, mit eigenem Zufallsgenerator (SplitMix64, wörtliche Kopie in pls_rng.py), damit alle Instanzen
auf jeder Plattform gleich sind."""

import pls_algorithm as A
from pls_rng import SplitMix64


def random_graph(n: int, dens: int, wmax: int, rng: SplitMix64) -> tuple:
    """Für jedes Paar i < j (zeilenweise): erst `below(100) < dens` (Kante ja/nein), nur bei einer Kante dann das Gewicht `1 + below(wmax)`."""
    w = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.below(100) < dens:
                w[i][j] = w[j][i] = 1 + rng.below(wmax)
    return tuple(map(tuple, w))


def random_start(n: int, rng: SplitMix64) -> tuple:
    """Zufällige Zweiteilung: je Knoten `below(2)`."""
    return tuple(rng.below(2) for _ in range(n))


def make_graph(family: str, n: int, dens: int, wmax: int, seed: int) -> tuple:
    """Deterministisch aus (Familie, n, Dichte, Gewichtsgrenze, Zufalls-Seed); nur der Zufallsgraph benutzt Dichte, Gewichtsgrenze und Zufalls-Seed."""
    if family == "random":
        return random_graph(n, dens, wmax, SplitMix64(seed))
    if family == "ones":
        return A.ones(n)
    if family == "expmin":
        return A.exp_min(n)
    raise ValueError(f"unbekannte Graphfamilie: {family}")


def make_start(n: int, seed: int) -> tuple:
    """Startschnitt aus einem eigenen Strom (Zufalls-Seed XOR einer Konstante), unabhängig vom Graphen."""
    return random_start(n, SplitMix64(seed ^ 0x5DEECE66D))
