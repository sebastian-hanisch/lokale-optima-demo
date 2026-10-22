"""Eigenschaften (ORACLE-PLAYBOOK, Schicht „Eigenschaften“): Dinge, die sich bei Umformungen der Eingabe nicht oder genau vorhersagbar ändern."""

import pytest

import pls_algorithm as A
from pls_rng import SplitMix64
from pls_scenario import random_graph, random_start


def _graphs(count, seed):
    rng = SplitMix64(seed)
    for _ in range(count):
        n = 4 + rng.below(5)
        yield random_graph(n, 60, 9, rng), random_start(n, rng)


def _permute(w, perm):
    n = len(w)
    return tuple(tuple(w[perm[i]][perm[j]] for j in range(n)) for i in range(n))


def test_relabelling_the_vertices_keeps_the_exact_numbers():
    for w, _ in _graphs(20, 1):
        n = len(w)
        perm = list(range(n))[::-1]
        a, b = A.exact_sequences(w), A.exact_sequences(_permute(w, perm))
        assert (int(a.longest.max()), a.local_optima, int(a.cut.max())) == (int(b.longest.max()), b.local_optima, int(b.cut.max()))
        assert sorted(int(x) for x in a.shortest) == sorted(int(x) for x in b.shortest)


def test_scaling_all_weights_keeps_the_path_of_the_deterministic_rules():
    for w, start in _graphs(40, 2):
        scaled = tuple(tuple(5 * x for x in row) for row in w)
        for rule in ("first", "best", "worst"):
            a, b = A.local_search(w, start, rule), A.local_search(scaled, start, rule)
            assert a.sequence == b.sequence and b.cut_end == 5 * a.cut_end


def test_swapping_the_two_sides_changes_nothing():
    for w, start in _graphs(40, 3):
        flipped = tuple(1 - x for x in start)
        assert A.gains(w, start) == A.gains(w, flipped) and A.cut_value(w, start) == A.cut_value(w, flipped)
        for rule in ("first", "best", "worst"):
            a, b = A.local_search(w, start, rule), A.local_search(w, flipped, rule)
            assert a.sequence == b.sequence and a.cut_end == b.cut_end


def test_an_isolated_vertex_doubles_the_local_optima_and_never_moves():
    for w, start in _graphs(15, 4):
        n = len(w)
        bigger = tuple(tuple(list(row) + [0]) for row in w) + ((0,) * (n + 1),)
        assert A.exact_sequences(bigger).local_optima == 2 * A.exact_sequences(w).local_optima
        s = A.local_search(bigger, start + (0,), "first")
        assert n not in s.sequence


def test_adding_a_weight_to_every_edge_of_the_complete_graph_keeps_the_balanced_cuts_optimal():
    for n in (4, 6, 8):
        for c in (1, 3):
            w = tuple(tuple(0 if i == j else c for j in range(n)) for i in range(n))
            e = A.exact_sequences(w)
            assert int(e.cut.max()) == c * (n // 2) * (n - n // 2)                               # größter Schnitt des vollständigen Graphen: c · ⌊n/2⌋ · ⌈n/2⌉


def test_a_graph_without_edges_has_only_local_optima():
    e = A.exact_sequences(tuple((0,) * 5 for _ in range(5)))
    assert e.local_optima == 32 and int(e.longest.max()) == 0


def test_a_single_heavy_edge_dominates():
    """Eine Kante mit Gewicht 100, alle anderen 1: jedes lokale Optimum schneidet die schwere Kante."""
    n = 6
    w = [[0 if i == j else 1 for j in range(n)] for i in range(n)]
    w[0][1] = w[1][0] = 100
    e = A.exact_sequences(tuple(map(tuple, w)))
    for s in range(1 << n):
        if e.longest[s] == 0:
            side = A.side_of(s, n)
            assert side[0] != side[1]


@pytest.mark.parametrize("rule", A.RULES)
def test_the_search_is_deterministic_for_a_fixed_seed(rule):
    for w, start in _graphs(10, 6):
        assert A.local_search(w, start, rule, SplitMix64(4)) == A.local_search(w, start, rule, SplitMix64(4))
