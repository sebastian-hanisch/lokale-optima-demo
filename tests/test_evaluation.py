"""Auswertung: Kennzahlen an Handwerten, jeder Zweig von validation_errors (mit Grenzfällen), Messreihen gegen eine unabhängige Nachrechnung."""

import itertools
from dataclasses import replace
from fractions import Fraction as F
from functools import lru_cache

import pytest

import pls_algorithm as A
import pls_constants as C
import pls_evaluation as ev
from pls_rng import SplitMix64
from pls_scenario import make_graph, make_start, random_graph, random_start


def _base(**kw):
    return ev.analyse(ev.Settings(**kw))


def _errors(a):
    return ev.validation_errors(a)


def _has(a, part):
    return any(part in e for e in _errors(a))


def _with_search(a, **kw):
    return replace(a, search=replace(a.search, **kw))


# --- Szenario ----------------------------------------------------------------------------------------------------------------------------------


def test_random_graph_draw_order_and_shape():
    rng = SplitMix64(7)
    expected = [[0] * 5 for _ in range(5)]
    for i in range(5):
        for j in range(i + 1, 5):
            if rng.below(100) < 60:
                expected[i][j] = expected[j][i] = 1 + rng.below(9)
    assert random_graph(5, 60, 9, SplitMix64(7)) == tuple(map(tuple, expected))
    g = random_graph(12, 50, 20, SplitMix64(3))
    assert all(g[i][i] == 0 and g[i][j] == g[j][i] and 0 <= g[i][j] <= 20 for i in range(12) for j in range(12))


def test_random_graph_density_extremes_and_weight_bound():
    assert random_graph(6, 0, 5, SplitMix64(1)) == ((0,) * 6,) * 6
    full = random_graph(6, 100, 5, SplitMix64(1))
    assert all(full[i][j] >= 1 for i in range(6) for j in range(6) if i != j) and max(max(r) for r in full) <= 5
    assert set(x for r in random_graph(8, 100, 1, SplitMix64(2)) for x in r) == {0, 1}


def test_random_start_and_make_start():
    rng = SplitMix64(4)
    assert random_start(6, SplitMix64(4)) == tuple(rng.below(2) for _ in range(6)) and set(random_start(60, SplitMix64(1))) == {0, 1}
    assert make_start(6, 4) == random_start(6, SplitMix64(4 ^ 0x5DEECE66D)) and make_start(6, 4) != make_start(6, 5)


def test_make_graph_dispatch():
    assert make_graph("ones", 4, 99, 99, 1) == A.ones(4) and make_graph("expmin", 4, 99, 99, 1) == A.exp_min(4)
    assert make_graph("random", 6, 50, 9, 3) == random_graph(6, 50, 9, SplitMix64(3)) and make_graph("ones", 4, 10, 10, 2) == make_graph("ones", 4, 90, 90, 3)
    with pytest.raises(ValueError):
        make_graph("bogus", 4, 50, 9, 3)


# --- Kennzahlen an Handwerten --------------------------------------------------------------------------------------------------------------


def test_triangle():
    a = _base(n=3, family="ones")
    assert (a.search.flips, a.search.cut_start, a.search.cut_end, a.total) == (1, 0, 2, 3)
    assert a.exact == ev.ExactSummary(1, 1, 1, 6, 2)


def test_standard_case():
    a = _base()
    assert (a.search.flips, a.search.cut_start, a.search.cut_end, a.total) == (7, 2097, 3214, 4368) and a.exact is None


def test_exact_summary_limit():
    assert _base(n=C.EXACT_LIVE_N_MAX, family="ones").exact is not None and _base(n=C.EXACT_LIVE_N_MAX + 1, family="ones").exact is None


def test_analysis_uses_all_settings():
    a = _base(n=8, seed=11, family="random", dens=70, wmax=9, rule="worst")
    w = make_graph("random", 8, 70, 9, 11)
    assert a.w == w and a.start == make_start(8, 11) and a.total == A.total_weight(w)
    assert a.search == A.local_search(w, a.start, "worst", SplitMix64(11 ^ 0x9E3779B1))


# --- validation_errors: Grundfall und jeder Zweig ----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("kw", [{}, {"n": 3, "family": "ones"}, {"n": 16, "family": "expmin", "rule": "worst"}, {"n": 24, "family": "expmin", "rule": "first"}, {"n": 17, "rule": "random"},
                                {"n": 14, "wmax": 1, "rule": "best"}, {"n": 5, "dens": 20, "wmax": 1_000_000, "rule": "random"}, {"n": 24, "wmax": 1_000_000, "rule": "worst"}])
def test_valid_analyses_have_no_errors(kw):
    assert _errors(_base(**kw)) == []


def test_graph_and_start_shape_is_checked():
    a = _base(n=5)
    shape = "nicht symmetrisch"
    w = [list(r) for r in a.w]
    asym = [r[:] for r in w]
    asym[0][1] += 1
    neg = [r[:] for r in w]
    neg[1][2] = neg[2][1] = -1
    diag = [r[:] for r in w]
    diag[0][0] = 1
    for bad in (asym, neg, diag):
        assert _errors(replace(a, w=tuple(map(tuple, bad)))) == [_errors(replace(a, w=tuple(map(tuple, bad))))[0]] and _has(replace(a, w=tuple(map(tuple, bad))), shape)
    assert _has(replace(a, start=a.start[:-1]), shape) and _has(replace(a, start=(2,) + a.start[1:]), shape)
    assert _has(replace(a, w=a.w[:-1] + (a.w[-1][:-1],)), shape)
    last = [r[:] for r in w]
    last[4][4] = 1                                                                                                 # nur die Diagonale des letzten Knotens
    assert _has(replace(a, w=tuple(map(tuple, last))), shape)
    edge = [r[:] for r in w]
    edge[0][4] = edge[4][0] = -1                                                                                    # negative Kante zum letzten Knoten
    assert _has(replace(a, w=tuple(map(tuple, edge))), shape)


def test_total_and_start_cut_are_recomputed():
    a = _base()
    assert _has(replace(a, total=a.total + 1), "Σw widerspricht") and _has(_with_search(a, cut_start=a.search.cut_start + 1), "Startschnitt widerspricht")


def test_every_flip_must_be_improving_and_follow_the_rule():
    a = _base(n=3, family="ones")
    wrong = "kein verbessernder Flip"
    assert not _has(a, wrong)
    assert _has(_with_search(a, sequence=(0, 1), flips=2), wrong)                           # nach dem ersten Flip hat Knoten 1 Gewinn 0: nicht verbessernd
    w = _base(n=14, wmax=10, rule="first")
    seq = w.search.sequence
    assert len(seq) >= 2 and not _has(w, wrong)
    swapped = (seq[1], seq[0]) + seq[2:]
    assert _has(_with_search(w, sequence=swapped), wrong)                                    # andere Reihenfolge: nicht mehr die Wahl der Regel „first“
    r = _base(n=14, wmax=10, rule="random")
    assert not _has(r, wrong)                                                                  # bei der zufälligen Regel wird nur geprüft, dass jeder Flip verbessert


def test_gain_exactly_one_is_improving():
    """Pfad 0 —3— 1 —1— 2, Start (0, 0, 0), schlechteste Regel: der erste Flip hat Gewinn 1 (Knoten 2) und ist erlaubt."""
    w = ((0, 3, 0), (3, 0, 1), (0, 1, 0))
    search = A.local_search(w, (0, 0, 0), "worst")
    a = ev.Analysis(ev.Settings(n=3, rule="worst"), w, (0, 0, 0), search, 4, None)
    assert search.sequence == (2, 1, 2) and _errors(a) == []


def test_end_state_flips_and_cut_must_match_the_replay():
    a = _base()
    out = "widersprechen dem Nachspielen"
    assert _has(_with_search(a, flips=a.search.flips + 1), out) and _has(_with_search(a, cut_end=a.search.cut_end + 1), out)
    side = list(a.search.side)
    side[0] ^= 1
    assert _has(_with_search(a, side=tuple(side)), out)


def test_flips_must_not_exceed_the_total_and_every_flip_gains_at_least_one():
    a = _base(n=3, family="ones")                                                              # 1 Flip, Schnitt 0 → 2, Σw = 3
    bound = "Schranke Σw"
    assert not _has(a, bound)
    assert not _has(replace(a, total=1), bound) and _has(replace(a, total=0), bound)             # Flips = Σw ist erlaubt, darüber nicht
    assert not _has(_with_search(a, cut_start=1), bound) and _has(_with_search(a, cut_start=2), bound)        # Endschnitt − Start = Flips (1) erlaubt, darunter nicht


def test_end_state_must_be_a_local_optimum_and_cut_at_least_half():
    a = _base(n=3, family="ones")
    assert _has(_with_search(a, side=a.start, flips=0, sequence=(), cut_end=a.search.cut_start), "kein lokales Optimum")
    assert not _has(a, "kein lokales Optimum")
    b = _base(n=14, wmax=10, rule="best")
    assert not _has(b, "weniger als die Hälfte")
    assert _has(replace(b, total=2 * b.search.cut_end + 1), "weniger als die Hälfte") and not _has(replace(b, total=2 * b.search.cut_end), "weniger als die Hälfte")


def test_exact_bounds_are_checked_inclusively():
    a = _base(n=14, wmax=10, rule="best")
    e, f = a.exact, a.search.flips
    out = "Grenzen der exakten Aufzählung"
    assert not _has(a, out)
    assert not _has(replace(a, exact=replace(e, shortest=f)), out) and _has(replace(a, exact=replace(e, shortest=f + 1)), out)
    assert not _has(replace(a, exact=replace(e, longest=f, longest_overall=max(f, e.longest_overall))), out) and _has(replace(a, exact=replace(e, longest=f - 1)), out)
    assert _has(replace(a, exact=replace(e, longest_overall=e.longest - 1)), out) and _has(replace(a, exact=replace(e, local_optima=0)), out)
    assert not _has(replace(a, exact=replace(e, local_optima=1)), out)                                              # nur null lokale Optima widersprechen der Existenz
    assert not _has(replace(a, exact=replace(e, optimum=a.search.cut_end)), out) and _has(replace(a, exact=replace(e, optimum=a.search.cut_end - 1)), out)


# --- Messreihen gegen eine unabhängige Nachrechnung -------------------------------------------------------------------------------------------


def _naive_search(w, start, rule, rng=None):
    """Zweite Lokalsuche: jeder Gewinn als Differenz der Schnittwerte aus der Definition (keine Fortschreibung)."""
    side = list(start)
    flips = 0
    while True:
        base = A.cut_value(w, side)
        diffs = {}
        for v in range(len(w)):
            flipped = side[:]
            flipped[v] ^= 1
            d = A.cut_value(w, flipped) - base
            if d > 0:
                diffs[v] = d
        if not diffs:
            return flips, tuple(side)
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
        flips += 1


def test_naive_search_helper_agrees_with_the_hand_values(mini):
    assert _naive_search(mini["P3"], (0, 0, 0), "first")[0] == 2 and _naive_search(mini["P3"], (0, 0, 0), "best")[0] == 1 and _naive_search(mini["P3"], (0, 0, 0), "worst")[0] == 3


def test_sweep_rules_matches_a_recount():
    rows = ev.sweep_rules(sizes=(5, 7), wmaxes=(1, 3), count=6, dens=60, seed=77)
    assert [(r["wmax"], r["n"]) for r in rows] == [(1, 5), (1, 7), (3, 5), (3, 7)]
    for r in rows:
        sigma, flips, worst_max, share_max = 0, {k: 0 for k in A.RULES}, 0, F(0)
        for i in range(6):
            base = 77 + 100_003 * r["wmax"] + 1000 * r["n"] + i
            w = random_graph(r["n"], 60, r["wmax"], SplitMix64(base))
            start = random_start(r["n"], SplitMix64(base ^ 0x5DEECE66D))
            total = A.total_weight(w)
            sigma += total
            for rule in A.RULES:
                f, side = _naive_search(w, start, rule, SplitMix64(base ^ 0x9E3779B1))
                flips[rule] += f
                if total:
                    share_max = max(share_max, F(f, total))
                if rule == "worst":
                    worst_max = max(worst_max, f)
        assert r["count"] == 6 and r["sigma"] == F(sigma, 6) and r["flips"] == {k: F(v, 6) for k, v in flips.items()} and r["worst_max"] == worst_max and r["share_max"] == share_max


def _longest_by_recursion(w):
    """Zweite Rechnung der längsten verbessernden Folge: Rekursion mit Gedächtnis über die Zustände (nur kleines n)."""
    n = len(w)

    @lru_cache(maxsize=None)
    def go(state):
        side = A.side_of(state, n)
        base = A.cut_value(w, side)
        best = 0
        for v in range(n):
            nxt = state ^ (1 << v)
            if A.cut_value(w, A.side_of(nxt, n)) > base:
                best = max(best, 1 + go(nxt))
        return best

    return max(go(s) for s in range(1 << n))


def test_sweep_family_matches_a_recount():
    res = ev.sweep_family(rule_sizes=(6,), starts=5, exact_sizes=(4, 5, 6), random_sizes=(5,), graphs=2, random_wmax=9, seed=13)
    r = res["rules"][0]
    w = A.exp_min(6)
    flips, worst_max = {k: 0 for k in A.RULES}, 0
    for i in range(5):
        base = 13 + 6000 + i
        start = random_start(6, SplitMix64(base))
        for rule in A.RULES:
            f, _ = _naive_search(w, start, rule, SplitMix64(base ^ 0x9E3779B1))
            flips[rule] += f
            if rule == "worst":
                worst_max = max(worst_max, f)
    assert (r["n"], r["starts"], r["sigma"], r["worst_max"]) == (6, 5, 57, worst_max) and r["flips"] == {k: F(v, 5) for k, v in flips.items()}
    assert [(e["n"], e["longest"], e["formula"]) for e in res["exact"]] == [(4, 4, 4), (5, _longest_by_recursion(A.exp_min(5)), None), (6, 9, 9)]
    assert res["exact"][2]["local_optima"] == 8 and res["exact"][2]["sigma"] == 57 and res["exact"][2]["shortest"] == 3
    best = 0
    for g in range(2):
        rng = SplitMix64(13 + 50_000 + 1000 * 5 + g)
        m = [[0] * 5 for _ in range(5)]
        for i in range(5):
            for j in range(i + 1, 5):
                m[i][j] = m[j][i] = 1 + rng.below(9)
        best = max(best, _longest_by_recursion(tuple(map(tuple, m))))
    assert res["random"] == [{"n": 5, "graphs": 2, "longest": best, "per_n2": F(best, 25)}]


def test_family_worst_max_belongs_to_the_worst_rule_alone():
    """Ein Start (n = 12, Seed 5), bei dem die erste Regel 60 und die schlechteste 58 Flips braucht: das Maximum der schlechtesten Regel ist 58, nicht das der anderen."""
    r = ev.sweep_family(rule_sizes=(12,), starts=1, exact_sizes=(), random_sizes=(), graphs=1, seed=5)["rules"][0]
    assert r["flips"]["first"] == 60 and r["flips"]["worst"] == 58 and r["worst_max"] == 58


def test_sweep_quality_matches_a_recount():
    res = ev.sweep_quality(n=6, wmax=5, count=12, dens=50, seed=21)
    ratios, half = [], 0
    for i in range(12):
        base = 21 + i
        w = random_graph(6, 50, 5, SplitMix64(base))
        f, side = _naive_search(w, random_start(6, SplitMix64(base ^ 0x5DEECE66D)), "first")
        optimum = max(A.cut_value(w, s) for s in itertools.product((0, 1), repeat=6))
        half += 2 * A.cut_value(w, side) >= A.total_weight(w)
        ratios.append(F(A.cut_value(w, side), optimum) if optimum else F(1))
    assert res == {"n": 6, "wmax": 5, "count": 12, "half_ok": half, "local_ok": 12, "ratio_min": min(ratios), "ratio_mean": sum(ratios) / 12}


def test_sweep_quality_edgeless_graph_counts_as_optimal():
    res = ev.sweep_quality(n=4, wmax=3, count=3, dens=0, seed=1)
    assert res["ratio_min"] == 1 and res["ratio_mean"] == 1 and res["half_ok"] == 3 and res["local_ok"] == 3
