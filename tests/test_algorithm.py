"""Jede Einheit des Kerns an Handwerten (tests/conftest.py) und an ihren Zweigen."""

import pytest
from conftest import K4, P3, T3

import pls_algorithm as A
from pls_rng import SplitMix64

# --- Schnitt, Gewichte, Gewinne -----------------------------------------------------------------------------------------------------------


def test_cut_value_hand_values():
    assert A.cut_value(T3, (0, 0, 0)) == 0 and A.cut_value(T3, (1, 0, 0)) == 2 and A.cut_value(T3, (0, 1, 1)) == 2
    assert [A.cut_value(P3, s) for s in ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1))] == [0, 1, 4, 3, 3, 4, 1, 0]
    assert A.cut_value(K4, (0, 0, 1, 1)) == 4 and A.cut_value(K4, (1, 0, 0, 0)) == 3


def test_total_weight():
    assert A.total_weight(T3) == 3 and A.total_weight(P3) == 4 and A.total_weight(K4) == 6 and A.total_weight(A.exp_min(4)) == 11 and A.total_weight(((0,),)) == 0


def test_gains_hand_values():
    assert A.gains(T3, (0, 0, 0)) == [2, 2, 2] and A.gains(T3, (1, 0, 0)) == [-2, 0, 0]
    assert A.gains(P3, (0, 0, 0)) == [3, 4, 1] and A.gains(P3, (1, 0, 0)) == [-3, -2, 1]
    assert A.gains(K4, (0, 0, 0, 0)) == [3, 3, 3, 3]


def test_gain_equals_the_change_of_the_cut():
    rng = SplitMix64(3)
    w = tuple(tuple(0 for _ in range(6)) for _ in range(6))
    w = [list(r) for r in w]
    for i in range(6):
        for j in range(i + 1, 6):
            w[i][j] = w[j][i] = rng.below(5)
    w = tuple(map(tuple, w))
    side = tuple(rng.below(2) for _ in range(6))
    g = A.gains(w, side)
    for v in range(6):
        flipped = list(side)
        flipped[v] ^= 1
        assert A.cut_value(w, flipped) - A.cut_value(w, side) == g[v]


def test_improving():
    assert A.improving([2, 0, -1, 5]) == [0, 3] and A.improving([0, -3]) == [] and A.improving([]) == []


# --- Pivotregeln -----------------------------------------------------------------------------------------------------------------------------


def test_choose_hand_values():
    gain = [0, 3, 1, 3]
    cand = [1, 2, 3]
    assert A.choose("first", gain, cand) == 1
    assert A.choose("best", gain, cand) == 1                                   # Gewinn 3 bei den Knoten 1 und 3: der kleinere Index
    assert A.choose("worst", gain, cand) == 2                                  # kleinster positiver Gewinn
    assert A.choose("worst", [0, 2, 2], [1, 2]) == 1                           # Gleichstand: der kleinere Index
    assert A.choose("best", [0, 2, 2], [1, 2]) == 1


def test_choose_random_uses_the_generator():
    cand = [2, 5, 7, 9]
    rng = SplitMix64(4)
    expected = [cand[SplitMix64(4).below(4)]]
    assert A.choose("random", [0] * 10, cand, rng) == expected[0]
    picks = {A.choose("random", [0] * 10, cand, SplitMix64(s)) for s in range(40)}
    assert picks == set(cand)


def test_choose_rejects_unknown_rule():
    with pytest.raises(ValueError):
        A.choose("bogus", [1], [0])
    with pytest.raises(ValueError):
        A.local_search(T3, (0, 0, 0), "bogus")


# --- Lokalsuche ------------------------------------------------------------------------------------------------------------------------------


def test_local_search_on_the_triangle():
    for rule in ("first", "best", "worst"):
        r = A.local_search(T3, (0, 0, 0), rule)
        assert (r.flips, r.sequence, r.cut_start, r.cut_end, r.side) == (1, (0,), 0, 2, (1, 0, 0))


def test_local_search_on_the_path_by_rule():
    r = A.local_search(P3, (0, 0, 0), "first")
    assert (r.flips, r.sequence, r.cut_end, r.side) == (2, (0, 2), 4, (1, 0, 1))
    r = A.local_search(P3, (0, 0, 0), "best")
    assert (r.flips, r.sequence, r.cut_end, r.side) == (1, (1,), 4, (0, 1, 0))
    r = A.local_search(P3, (0, 0, 0), "worst")
    assert (r.flips, r.sequence, r.cut_end, r.side) == (3, (2, 1, 2), 4, (0, 1, 0))


def test_local_search_on_k4():
    r = A.local_search(K4, (0, 0, 0, 0), "first")
    assert (r.flips, r.sequence, r.cut_end) == (2, (0, 1), 4) and r.side == (1, 1, 0, 0)


def test_local_search_random_rule_reaches_a_local_optimum_and_is_deterministic():
    a = A.local_search(P3, (0, 0, 0), "random", SplitMix64(9))
    b = A.local_search(P3, (0, 0, 0), "random", SplitMix64(9))
    assert a == b and a.cut_end == 4 and 1 <= a.flips <= 3 and A.is_local_optimum(P3, a.side)


def test_local_search_from_a_local_optimum_does_nothing():
    for rule in A.RULES:
        r = A.local_search(P3, (0, 1, 0), rule, SplitMix64(1))
        assert (r.flips, r.sequence, r.cut_start, r.cut_end, r.side) == (0, (), 4, 4, (0, 1, 0))


def test_local_search_does_not_change_its_input_and_handles_one_vertex():
    side = [0, 0, 0]
    A.local_search(P3, side, "first")
    assert side == [0, 0, 0]
    r = A.local_search(((0,),), (0,), "first")
    assert (r.flips, r.cut_end) == (0, 0)


def test_local_search_cut_end_is_the_cut_of_the_end_state_and_every_flip_gains_at_least_one():
    rng = SplitMix64(21)
    for _ in range(40):
        n = 4 + rng.below(6)
        w = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                w[i][j] = w[j][i] = rng.below(8)
        w = tuple(map(tuple, w))
        start = tuple(rng.below(2) for _ in range(n))
        for rule in A.RULES:
            r = A.local_search(w, start, rule, SplitMix64(5))
            assert r.cut_end == A.cut_value(w, r.side) and r.cut_end - r.cut_start >= r.flips and r.flips <= A.total_weight(w) and A.is_local_optimum(w, r.side)


def test_is_local_optimum():
    assert A.is_local_optimum(T3, (1, 0, 0)) and not A.is_local_optimum(T3, (0, 0, 0))
    assert A.is_local_optimum(P3, (0, 1, 0)) and A.is_local_optimum(P3, (1, 0, 1)) and not A.is_local_optimum(P3, (0, 1, 1))
    assert A.is_local_optimum(((0, 0), (0, 0)), (0, 0))                             # ohne Kanten: jeder Schnitt ist optimal


# --- Familien ------------------------------------------------------------------------------------------------------------------------------


def test_families():
    assert A.ones(3) == T3 and A.ones(4) == K4 and A.ones(1) == ((0,),)
    assert A.exp_min(4) == ((0, 1, 1, 1), (1, 0, 2, 2), (1, 2, 0, 4), (1, 2, 4, 0))
    w = A.exp_min(6)
    assert all(w[i][j] == w[j][i] == 2 ** min(i, j) for i in range(6) for j in range(6) if i != j) and all(w[i][i] == 0 for i in range(6))


# --- Aufzählung aller Schnitte ------------------------------------------------------------------------------------------------------------


def test_state_encoding():
    assert A.state_of((1, 0, 1)) == 5 and A.side_of(5, 3) == (1, 0, 1) and A.state_of(()) == 0 and A.side_of(0, 2) == (0, 0)
    assert all(A.side_of(A.state_of(A.side_of(s, 5)), 5) == A.side_of(s, 5) for s in range(32))


def test_all_cuts_hand_values():
    # Zustand s: Bit i = Seite von Knoten i, also s = 1 ist (1, 0, 0), s = 2 ist (0, 1, 0), s = 4 ist (0, 0, 1)
    assert list(A.all_cuts(P3)) == [0, 3, 4, 1, 1, 4, 3, 0]
    cuts = A.all_cuts(P3)
    for s in range(8):
        assert cuts[s] == A.cut_value(P3, A.side_of(s, 3))
    assert list(A.all_cuts(T3)) == [0, 2, 2, 2, 2, 2, 2, 0]


def test_all_cuts_limit():
    with pytest.raises(ValueError):
        A.all_cuts(A.ones(A.EXACT_N_MAX + 1))


def test_exact_sequences_hand_values_on_the_path():
    e = A.exact_sequences(P3)
    s000 = A.state_of((0, 0, 0))
    assert e.local_optima == 2 and int(e.longest.max()) == 3
    assert (int(e.longest[s000]), int(e.shortest[s000])) == (3, 1)
    assert int(e.longest[A.state_of((0, 1, 0))]) == 0 and int(e.shortest[A.state_of((1, 0, 1))]) == 0                 # lokale Optima


def test_exact_sequences_hand_values_on_the_triangle_and_exp_min_4():
    e = A.exact_sequences(T3)
    assert e.local_optima == 6 and int(e.longest.max()) == 1 and int(e.longest[0]) == 1 and int(e.shortest[7]) == 1
    e = A.exact_sequences(A.exp_min(4))
    assert e.local_optima == 4 and int(e.longest.max()) == 4 and int(e.shortest.max()) == 2


def test_exact_sequences_bound_the_flips_of_every_rule():
    rng = SplitMix64(17)
    for _ in range(15):
        n = 5 + rng.below(4)
        w = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                w[i][j] = w[j][i] = rng.below(6)
        w = tuple(map(tuple, w))
        e = A.exact_sequences(w)
        start = tuple(rng.below(2) for _ in range(n))
        s = A.state_of(start)
        for rule in A.RULES:
            r = A.local_search(w, start, rule, SplitMix64(2))
            assert int(e.shortest[s]) <= r.flips <= int(e.longest[s])


def test_exact_sequences_with_one_and_two_vertices():
    e = A.exact_sequences(((0,),))
    assert e.local_optima == 2 and int(e.longest.max()) == 0
    e = A.exact_sequences(((0, 5), (5, 0)))
    assert e.local_optima == 2 and int(e.longest.max()) == 1 and int(e.longest[0]) == 1 and int(e.longest[1]) == 0
