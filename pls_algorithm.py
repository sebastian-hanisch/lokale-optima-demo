"""Kern: Max-Cut mit Flip-Nachbarschaft (ganzzahlige Gewichte), Lokalsuche mit vier Pivotregeln, Prüfer der Lokaloptimalität und die Aufzählung aller Schnitte (kürzeste und längste verbessernde Folge).

Jede Einheit ist eine Funktion (DEMO-PLAYBOOK §1b). Gezählt werden **Flips** (verbessernde Schritte), nie Sekunden.

Ein Graph ist eine symmetrische Matrix `w` (Tupel von Tupeln ganzer Zahlen, Diagonale 0, Eintrag 0 = keine Kante). Ein Schnitt ist eine Zweiteilung `side` (Tupel aus 0 und 1, eine Seite je Knoten); sein Wert ist das
Gewicht der Kanten zwischen den Seiten. Ein **Flip** setzt einen Knoten auf die andere Seite; sein **Gewinn** ist das Gewicht der Kanten zu Knoten auf der eigenen Seite minus das der Kanten zur anderen Seite (um so viel
steigt der Schnitt). Ein Schnitt ohne Flip mit Gewinn > 0 ist ein **lokales Optimum**. Pivotregeln wählen unter den verbessernden Flips: „first“ (kleinster Knotenindex), „best“ (größter Gewinn, bei Gleichstand der kleinste
Index), „worst“ (kleinster positiver Gewinn, bei Gleichstand der kleinste Index) und „random“ (gleichverteilt)."""

from dataclasses import dataclass

import numpy as np

RULES = ("first", "best", "worst", "random")
EXACT_N_MAX = 18                                   # Aufzählung aller 2^n Schnitte nur bis hierhin


@dataclass(frozen=True)
class Search:
    side: tuple                                    # Endzustand
    flips: int
    sequence: tuple                                # die geflippten Knoten in der Reihenfolge der Flips
    cut_start: int
    cut_end: int


@dataclass(frozen=True)
class Exact:
    cut: np.ndarray                                # Schnittwert je Zustand (Bit i = Seite von Knoten i)
    longest: np.ndarray                            # längste verbessernde Folge von diesem Zustand aus (0 im lokalen Optimum)
    shortest: np.ndarray                           # kürzeste Folge bis zu einem lokalen Optimum
    local_optima: int


# --- Schnitt und Gewinne ------------------------------------------------------------------------------------------------------------------


def cut_value(w, side) -> int:
    """Wert des Schnitts aus der Definition: Summe der Gewichte der Kanten zwischen den Seiten."""
    n = len(w)
    return sum(w[i][j] for i in range(n) for j in range(i + 1, n) if side[i] != side[j])


def total_weight(w) -> int:
    """Σw: Summe aller Kantengewichte (obere Schranke für jeden Schnitt und für die Zahl der Flips)."""
    n = len(w)
    return sum(w[i][j] for i in range(n) for j in range(i + 1, n))


def gains(w, side) -> list:
    """Gewinn des Flips jedes Knotens: Gewicht zu Knoten der eigenen Seite minus Gewicht zu Knoten der anderen Seite."""
    n = len(w)
    return [sum(w[v][u] if side[u] == side[v] else -w[v][u] for u in range(n) if u != v) for v in range(n)]


def improving(gain) -> list:
    """Knoten mit positivem Gewinn, aufsteigend."""
    return [v for v, g in enumerate(gain) if g > 0]


def choose(rule: str, gain, candidates, rng=None) -> int:
    """Pivotregel: wählt aus den verbessernden Knoten `candidates` (aufsteigend, nicht leer) einen aus."""
    if rule == "first":
        return candidates[0]
    if rule == "best":
        return max(candidates, key=lambda v: (gain[v], -v))
    if rule == "worst":
        return min(candidates, key=lambda v: (gain[v], v))
    if rule == "random":
        return candidates[rng.below(len(candidates))]
    raise ValueError(f"unbekannte Pivotregel: {rule}")


def local_search(w, side, rule: str, rng=None) -> Search:
    """Verbessernde Flips nach der Pivotregel, bis kein Flip mit Gewinn > 0 bleibt. Die Gewinne werden nach jedem Flip fortgeschrieben (nur die Nachbarn des geflippten Knotens ändern sich um ±2 · Gewicht)."""
    if rule not in RULES:
        raise ValueError(f"unbekannte Pivotregel: {rule}")
    n = len(w)
    side = list(side)
    gain = gains(w, side)
    cut_start = cut_value(w, side)
    cut = cut_start
    sequence = []
    while True:
        candidates = improving(gain)
        if not candidates:
            break
        v = choose(rule, gain, candidates, rng)
        cut += gain[v]
        side[v] ^= 1
        gain[v] = -gain[v]
        for u in range(n):
            if u != v and w[v][u]:
                gain[u] += 2 * w[v][u] if side[u] == side[v] else -2 * w[v][u]
        sequence.append(v)
    return Search(tuple(side), len(sequence), tuple(sequence), cut_start, cut)


def cut_trace(w, start, sequence) -> list:
    """Schnittwert vor dem ersten und nach jedem Flip der Folge (jeweils aus der Definition neu berechnet): Länge = Zahl der Flips + 1."""
    side = list(start)
    values = [cut_value(w, side)]
    for v in sequence:
        side[v] ^= 1
        values.append(cut_value(w, side))
    return values


def is_local_optimum(w, side) -> bool:
    """Prüfer (Brute Force): kein einzelner Flip erhöht den Schnittwert, jeweils aus der Definition neu berechnet."""
    base = cut_value(w, side)
    for v in range(len(w)):
        flipped = list(side)
        flipped[v] ^= 1
        if cut_value(w, flipped) > base:
            return False
    return True


# --- Graphfamilien ---------------------------------------------------------------------------------------------------------------------------


def ones(n: int) -> tuple:
    """Vollständiger Graph, alle Gewichte 1."""
    return tuple(tuple(int(i != j) for j in range(n)) for i in range(n))


def exp_min(n: int) -> tuple:
    """Vollständiger Graph, Kante {i, j} (Knoten 0 bis n − 1) mit dem Gewicht 2^min(i, j)."""
    return tuple(tuple(0 if i == j else 2 ** min(i, j) for j in range(n)) for i in range(n))


# --- Aufzählung aller Schnitte --------------------------------------------------------------------------------------------------------------


def state_of(side) -> int:
    """Zustandsnummer eines Schnitts: Bit i = Seite von Knoten i."""
    return sum(s << i for i, s in enumerate(side))


def side_of(state: int, n: int) -> tuple:
    return tuple((state >> i) & 1 for i in range(n))


def all_cuts(w) -> np.ndarray:
    """Schnittwert aller 2^n Zustände (nur n ≤ EXACT_N_MAX)."""
    n = len(w)
    if n > EXACT_N_MAX:
        raise ValueError(f"n muss höchstens {EXACT_N_MAX} sein")
    states = np.arange(1 << n, dtype=np.int64)
    cut = np.zeros(1 << n, dtype=np.int64)
    for i in range(n):
        for j in range(i + 1, n):
            if w[i][j]:
                cut += w[i][j] * (((states >> i) & 1) != ((states >> j) & 1))
    return cut


def exact_sequences(w) -> Exact:
    """Für jeden Zustand die längste und die kürzeste verbessernde Folge bis zu einem lokalen Optimum (Rückwärtsrechnung über die Zustände in absteigendem Schnittwert; ein verbessernder Flip erhöht den Wert
    strikt, Nachfolger kommen also vorher dran). Die längste Folge ist die Schrittzahl der schlimmsten Pivotregel, die kürzeste die der besten."""
    n = len(w)
    cut = all_cuts(w)
    size = 1 << n
    longest = np.zeros(size, dtype=np.int64)
    shortest = np.zeros(size, dtype=np.int64)
    masks = np.array([1 << v for v in range(n)], dtype=np.int64)
    local = 0
    for s in np.argsort(-cut, kind="stable"):
        nxt = s ^ masks
        better = nxt[cut[nxt] > cut[s]]
        if better.size:
            longest[s] = 1 + longest[better].max()
            shortest[s] = 1 + shortest[better].min()
        else:
            local += 1
    return Exact(cut, longest, shortest, local)
