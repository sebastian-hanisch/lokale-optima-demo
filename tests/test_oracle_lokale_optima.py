"""Orakel (ORACLE-PLAYBOOK): unabhängige Gegenrechnungen und Sätze gegen die ganze Demo.

* Die Lokalsuche (Gewinne fortgeschrieben) gleicht einer zweiten Lokalsuche, die jeden Gewinn aus der Definition des Schnittwerts neu rechnet: gleiche Flips, gleicher Endzustand, für alle vier Regeln.
* Sätze: jede Folge hat höchstens Σw Flips, jeder verbessernde Flip erhöht den Schnitt um mindestens 1 (strikt wachsend), der Endzustand ist ein lokales Optimum (Brute Force) und schneidet mindestens Σw / 2.
* Aufzählung: kürzeste und längste Folge, Zahl der lokalen Optima und Optimum gegen eine Rekursion mit Gedächtnis bzw. die Definition; jede Regel liegt zwischen kürzester und längster Folge.
* Die Familie exp-min: längste Folge 2^(n/2) + n/2 − 2 und 2^(n/2) lokale Optima für alle geraden n von 4 bis 16 (gemessen).
* Die Auswertung (`pls_evaluation`) läuft über ein Raster von Einstellungen ohne Prüffehler."""

from functools import lru_cache

import pytest

import pls_algorithm as A
import pls_constants as C
import pls_evaluation as ev
from pls_rng import SplitMix64
from pls_scenario import random_graph, random_start


def _naive(w, start, rule, rng=None):
    side = list(start)
    seq = []
    while True:
        base = A.cut_value(w, side)
        diffs = {}
        for v in range(len(w)):
            f = side[:]
            f[v] ^= 1
            d = A.cut_value(w, f) - base
            if d > 0:
                diffs[v] = d
        if not diffs:
            return tuple(side), tuple(seq)
        cand = sorted(diffs)
        if rule == "first":
            v = cand[0]
        elif rule == "best":
            v = min(cand, key=lambda x: (-diffs[x], x))
        elif rule == "worst":
            v = min(cand, key=lambda x: (diffs[x], x))
        else:
            v = cand[rng.below(len(cand))]
        side[v] ^= 1
        seq.append(v)


def _graphs(count, seed, nmax=9):
    rng = SplitMix64(seed)
    for i in range(count):
        n = 3 + rng.below(nmax - 2)
        yield random_graph(n, 20 + 10 * (i % 7), (1, 2, 5, 30, 1000)[i % 5], rng), random_start(n, rng)


def test_local_search_equals_the_recomputing_search_for_every_rule():
    checked = 0
    for w, start in _graphs(300, 1234):
        for rule in A.RULES:
            fast = A.local_search(w, start, rule, SplitMix64(9))
            side, seq = _naive(w, start, rule, SplitMix64(9))
            assert (fast.side, fast.sequence, fast.flips) == (side, seq, len(seq)), (rule, w, start)
            checked += 1
    assert checked == 1200


def test_theorems_on_every_search():
    for w, start in _graphs(300, 99):
        total = A.total_weight(w)
        for rule in A.RULES:
            s = A.local_search(w, start, rule, SplitMix64(3))
            trace = A.cut_trace(w, start, s.sequence)
            assert all(b - a >= 1 for a, b in zip(trace, trace[1:])), (rule, w)
            assert s.flips <= total and s.flips <= s.cut_end - s.cut_start and trace[-1] == s.cut_end == A.cut_value(w, s.side)
            assert A.is_local_optimum(w, s.side) and 2 * s.cut_end >= total


def test_a_local_optimum_cannot_be_improved_and_its_gains_are_not_positive():
    for w, start in _graphs(100, 5):
        s = A.local_search(w, start, "first")
        assert all(g <= 0 for g in A.gains(w, s.side)) and A.local_search(w, s.side, "worst").flips == 0


def _recursive_longest_shortest(w):
    n = len(w)

    @lru_cache(maxsize=None)
    def go(state):
        base = A.cut_value(w, A.side_of(state, n))
        nxt = [state ^ (1 << v) for v in range(n) if A.cut_value(w, A.side_of(state ^ (1 << v), n)) > base]
        if not nxt:
            return 0, 0
        return 1 + max(go(t)[0] for t in nxt), 1 + min(go(t)[1] for t in nxt)

    return [go(s) for s in range(1 << n)]


def test_exact_sequences_equal_a_memoized_recursion():
    graphs = [A.ones(5), A.exp_min(6), A.exp_min(7)] + [g for g, _ in _graphs(25, 777, nmax=7)]
    for w in graphs:
        e = A.exact_sequences(w)
        ref = _recursive_longest_shortest(w)
        assert [int(x) for x in e.longest] == [r[0] for r in ref] and [int(x) for x in e.shortest] == [r[1] for r in ref]
        assert e.local_optima == sum(1 for r in ref if r[0] == 0) and int(e.cut.max()) == max(A.cut_value(w, A.side_of(s, len(w))) for s in range(1 << len(w)))


def test_local_optima_by_definition_equal_the_enumeration():
    for w, _ in _graphs(40, 31, nmax=9):
        n = len(w)
        by_definition = sum(1 for s in range(1 << n) if A.is_local_optimum(w, A.side_of(s, n)))
        assert A.exact_sequences(w).local_optima == by_definition


def test_every_rule_lies_between_the_shortest_and_the_longest_sequence():
    for w, start in _graphs(80, 2024, nmax=10):
        e = A.exact_sequences(w)
        s = A.state_of(start)
        for rule in A.RULES:
            f = A.local_search(w, start, rule, SplitMix64(1)).flips
            assert int(e.shortest[s]) <= f <= int(e.longest[s]), (rule, w, start)


@pytest.mark.parametrize("n", [4, 6, 8, 10, 12, 14, 16])
def test_exp_min_formula_and_local_optima(n):
    e = A.exact_sequences(A.exp_min(n))
    assert int(e.longest.max()) == 2 ** (n // 2) + n // 2 - 2 == ev.exp_min_formula(n) and e.local_optima == 2 ** (n // 2) and int(e.shortest.max()) == n // 2


def test_exp_min_rules_from_the_all_zero_start():
    """Die erste und die schlechteste Regel zählen auf exp-min exponentiell, die beste nicht (n = 8 bis 16, Start (0, …, 0))."""
    flips = {n: {r: A.local_search(A.exp_min(n), (0,) * n, r, SplitMix64(1)).flips for r in A.RULES} for n in (8, 12, 16)}
    assert flips[16]["first"] > 4 * flips[12]["first"] // 2 and flips[12]["first"] > 3 * flips[8]["first"] // 2
    assert all(flips[n]["best"] <= n for n in flips) and all(flips[n]["random"] < flips[n]["first"] for n in flips)


def test_the_evaluation_runs_over_a_grid_without_validation_errors():
    for family in C.FAMILIES:
        for n in (3, 4, 9, 14, 16, 17, 24):
            for rule in C.RULE_LABELS:
                for wmax in ((1, 1_000_000) if family == "random" else (100,)):
                    a = ev.analyse(ev.Settings(n=n, seed=50 + n, family=family, wmax=wmax, rule=rule, dens=40))
                    assert ev.validation_errors(a) == [], (family, n, rule, wmax)
                    assert ev.verdict_main(a)[0] in ("info", "success")


def test_the_full_quality_sweep_holds_the_theorem():
    res = ev.sweep_quality()
    assert res["half_ok"] == res["local_ok"] == res["count"] and ev.verdict_quality(res)[0] == "info"
    assert all(2 * A.local_search(g, s, "first").cut_end >= A.total_weight(g) for g, s in _graphs(50, 8))
