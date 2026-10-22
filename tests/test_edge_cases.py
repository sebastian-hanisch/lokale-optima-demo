"""Randfälle: Reglergrenzen, Rechengrenzen und Szenario."""

import pytest

import pls_algorithm as A
import pls_constants as C
import pls_evaluation as ev
from pls_rng import SplitMix64
from pls_scenario import make_graph


@pytest.mark.parametrize("family", list(C.FAMILIES))
@pytest.mark.parametrize("n", [C.N_MIN, 5, C.EXACT_LIVE_N_MAX, C.N_MAX])
@pytest.mark.parametrize("rule", list(C.RULE_LABELS))
def test_extremes_of_the_sliders_are_clean(n, family, rule):
    a = ev.analyse(ev.Settings(n=n, family=family, rule=rule))
    assert ev.validation_errors(a) == []
    assert ev.verdict_main(a)[0] in ("info", "success")


@pytest.mark.parametrize("seed", [0, C.SEED_MAX])
def test_seed_bounds(seed):
    assert ev.validation_errors(ev.analyse(ev.Settings(seed=seed))) == []


@pytest.mark.parametrize("wmax", C.WMAX_OPTIONS)
@pytest.mark.parametrize("dens", [C.DENS_OPTIONS[0], C.DENS_OPTIONS[-1]])
def test_every_weight_bound_and_the_density_extremes_are_valid(wmax, dens):
    a = ev.analyse(ev.Settings(n=18, wmax=wmax, dens=dens))
    assert ev.validation_errors(a) == [] and a.search.cut_end >= a.total / 2


def test_largest_instance_of_the_gemeine_familie_stays_within_its_bound():
    a = ev.analyse(ev.Settings(n=C.N_MAX, family="expmin", rule="first"))
    assert a.total == 16_777_191
    assert a.search.flips <= 2 ** (C.N_MAX // 2 + 1)                                       # gemessen: rund 2^(n/2) Flips
    assert a.search.flips <= a.total


def test_weight_sums_stay_within_int64():
    assert A.total_weight(A.exp_min(C.N_MAX)) == 16_777_191 < 2 ** 62
    w = make_graph("random", C.N_MAX, 80, 1_000_000, 7)
    assert A.total_weight(w) <= 1_000_000 * C.N_MAX * (C.N_MAX - 1) // 2


def test_graph_without_edges_is_an_immediate_local_optimum():
    w = ((0,) * 4,) * 4
    s = A.local_search(w, (0, 1, 0, 1), "first")
    assert (s.flips, s.cut_end, A.total_weight(w)) == (0, 0, 0) and A.is_local_optimum(w, s.side)


def test_one_and_two_vertices():
    assert A.local_search(((0,),), (0,), "worst").flips == 0
    s = A.local_search(((0, 4), (4, 0)), (0, 0), "best")
    assert (s.flips, s.sequence, s.cut_end) == (1, (0,), 4)


def test_random_rule_visits_every_improving_flip_over_seeds():
    w = ((0, 3, 0), (3, 0, 1), (0, 1, 0))
    firsts = {A.local_search(w, (0, 0, 0), "random", SplitMix64(s)).sequence[0] for s in range(60)}
    assert firsts == {0, 1, 2}
