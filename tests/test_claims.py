"""Jede Zahl der README steht hier und wird über dieselben Auswertungsfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Alle Graphen kommen aus dem eigenen SplitMix64-Generator (plattform- und versionsunabhängig); Flips, Gewichte und Schnitte sind exakte ganze Zahlen, Mittel und Anteile exakte Brüche."""

from fractions import Fraction as F

import pytest

import pls_algorithm as A
import pls_constants as C
import pls_evaluation as ev

# --- Befund 1: Schranke gegen Praxis -------------------------------------------------------------------------------------------------------

# (W, n): (100 · Σw im Mittel, 100 · Flips: beste, zufällige, erste, schlechteste Regel, größte Flipzahl der schlechtesten, größter Anteil Flips / Σw über alle Instanzen und Regeln als (Zähler, Nenner));
# je 100 feste Zufallsgraphen G(n, 50 %) mit zufälligem Start
RULES = {
    (1, 10): (2284, 242, 313, 312, 398, 10, (9, 19)), (1, 20): (9601, 532, 720, 749, 1103, 21, (21, 85)), (1, 40): (38981, 1148, 1750, 1933, 3366, 57, (57, 386)),
    (1, 80): (158035, 2576, 3988, 4914, 9672, 153, (153, 1550)), (10, 10): (12471, 304, 437, 430, 662, 17, (8, 45)), (10, 20): (51592, 610, 935, 975, 1942, 35, (17, 213)),
    (10, 40): (214351, 1384, 2210, 2454, 7264, 123, (41, 711)), (10, 80): (866913, 2932, 4858, 6567, 29197, 394, (382, 8593)), (1000, 10): (1107473, 324, 427, 425, 635, 15, (1, 723)),
    (1000, 20): (4786656, 686, 1029, 1040, 2246, 44, (11, 11034)), (1000, 40): (19475004, 1420, 2184, 2528, 8453, 145, (29, 38298)), (1000, 80): (78847394, 2989, 4986, 6615, 35321, 484, (479, 770270)),
}


@pytest.fixture(scope="module")
def rules():
    return ev.sweep_rules()


def test_claim_rules_table(rules):
    """README, Befund 1: je Gewichtsgrenze W und Größe n 100 feste Graphen."""
    got = {(r["wmax"], r["n"]): (r["sigma"] * 100, *(r["flips"][k] * 100 for k in ("best", "random", "first", "worst")), r["worst_max"], (r["share_max"].numerator, r["share_max"].denominator)) for r in rules}
    assert got == {k: (F(v[0]), F(v[1]), F(v[2]), F(v[3]), F(v[4]), v[5], v[6]) for k, v in RULES.items()}
    assert all(r["count"] == 100 for r in rules) and len(rules) == 12


def test_claim_the_bound_is_not_reached_on_large_weights(rules):
    """README: bei W = 1.000 liegt der größte Anteil Flips / Σw über alle Instanzen und Regeln bei höchstens 0,14 % (n = 10: 1/723), bei n = 80: 0,06 %; bei W = 1 und n = 10 dagegen bei 47,4 % (9/19), und er
    sinkt mit n (n = 10 / 20 / 40 / 80: 47,4 / 24,7 / 14,8 / 9,9 %)."""
    by = {(r["wmax"], r["n"]): r for r in rules}
    assert max(r["share_max"] for r in rules if r["wmax"] == 1000) == F(1, 723) and ev.fmt_percent(F(1, 723), 2) == "0,14 %" and ev.fmt_percent(by[(1000, 80)]["share_max"], 2) == "0,06 %"
    assert [ev.fmt_percent(by[(1, n)]["share_max"]) for n in (10, 20, 40, 80)] == ["47,4 %", "24,7 %", "14,8 %", "9,9 %"]
    assert all(by[(w, 80)]["share_max"] < by[(w, 10)]["share_max"] for w in (1, 10, 1000)) and max(r["share_max"] for r in rules) == F(9, 19)


def test_claim_rule_order_and_weight_dependence(rules):
    """README: n = 80, W = 1.000: beste 29,9 < zufällig 49,9 < erste 66,2 < schlechteste 353,2 Flips (Σw 788.474); die beste Regel hängt kaum von W ab (n = 80: 25,8 / 29,3 / 29,9 bei W = 1 / 10 / 1.000), die schlechteste
    deutlich (96,7 / 292,0 / 353,2)."""
    by = {(r["wmax"], r["n"]): r for r in rules}
    f = by[(1000, 80)]["flips"]
    assert [ev.fmt_mean(f[k]) for k in ("best", "random", "first", "worst")] == ["29,9", "49,9", "66,2", "353"] and ev.fmt_mean(by[(1000, 80)]["sigma"]) == "788.474"
    assert f["best"] < f["random"] < f["first"] < f["worst"] and by[(1000, 80)]["worst_max"] == 484
    assert [round(float(by[(w, 80)]["flips"]["best"]), 1) for w in (1, 10, 1000)] == [25.8, 29.3, 29.9] and [round(float(by[(w, 80)]["flips"]["worst"]), 1) for w in (1, 10, 1000)] == [96.7, 292.0, 353.2]
    text = ev.verdict_rules(rules)[1]
    assert "Über alle 1.200 Graphen und vier Regeln ist der größte Anteil Flips / Σw 47,4 % (n = 10, W = 1)." in text


def test_claim_rule_order_holds_in_every_cell_except_random_against_first_at_n_10(rules):
    """README: in allen 12 Zellen ist die beste Regel die kürzeste und die schlechteste die längste; die zufällige ist ab n = 20 kürzer als die erste, bei n = 10 (alle drei W) knapp länger (z. B. W = 1: 3,13 gegen 3,12)."""
    for r in rules:
        f = r["flips"]
        assert f["best"] < f["random"] and f["best"] < f["first"] and max(f["random"], f["first"]) < f["worst"], (r["wmax"], r["n"])
        assert (f["random"] > f["first"]) == (r["n"] == 10), (r["wmax"], r["n"])


# --- Befund 2: die gemeine Familie ---------------------------------------------------------------------------------------------------------

# n: (Σw, 20 · Flips: beste, zufällige, erste, schlechteste Regel, größte Flipzahl der schlechtesten); 20 feste Zufallsstarts
FAMILY_RULES = {8: (247, 36, 56, 182, 182, 16), 12: (4083, 62, 112, 828, 828, 65), 16: (65519, 84, 178, 2374, 2374, 258), 20: (1048555, 97, 251, 11811, 11811, 1024), 24: (16777191, 119, 281, 50261, 48525, 4097)}
# n: (längste Folge, kürzeste Folge (Maximum über Starts), lokale Optima, Σw)
FAMILY_EXACT = {4: (4, 2, 4, 11), 6: (9, 3, 8, 57), 8: (18, 4, 16, 247), 10: (35, 5, 32, 1013), 12: (68, 6, 64, 4083), 14: (133, 7, 128, 16369), 16: (262, 8, 256, 65519), 18: (519, 9, 512, 262125)}
FAMILY_RANDOM = {6: (11, F(11, 36)), 8: (20, F(5, 16)), 10: (30, F(3, 10)), 12: (46, F(23, 72)), 14: (60, F(15, 49))}


@pytest.fixture(scope="module")
def family():
    return ev.sweep_family()


def test_claim_family_rules(family):
    """README, Befund 2: Familie exp-min, 20 feste Zufallsstarts: erste und schlechteste Regel wachsen etwa mit 2^(n/2), die beste und die zufällige kaum."""
    got = {r["n"]: (r["sigma"], *(r["flips"][k] * 20 for k in ("best", "random", "first", "worst")), r["worst_max"]) for r in family["rules"]}
    assert got == {n: (v[0], F(v[1]), F(v[2]), F(v[3]), F(v[4]), v[5]) for n, v in FAMILY_RULES.items()} and all(r["starts"] == 20 for r in family["rules"])


def test_claim_first_equals_worst_for_small_n_and_grows_fourfold_per_four_vertices(family):
    """README: bei n = 8 bis 20 ist die Zahl der Flips der ersten und der schlechtesten Regel auf exp-min gleich (9,1 / 41,4 / 118,7 / 590,6; angezeigt 9,1 / 41,4 / 119 / 591), bei n = 24 2.513 gegen 2.426; Faktor 276 von n = 8 auf 24, im Mittel 4,1 je vier Knoten; die beste Regel 1,8 bis 6,0."""
    by = {r["n"]: r for r in family["rules"]}
    assert all(by[n]["flips"]["first"] == by[n]["flips"]["worst"] for n in (8, 12, 16, 20)) and by[24]["flips"]["first"] != by[24]["flips"]["worst"]
    assert [ev.fmt_mean(by[n]["flips"]["first"]) for n in (8, 12, 16, 20, 24)] == ["9,1", "41,4", "119", "591", "2.513"] and ev.fmt_mean(by[24]["flips"]["worst"]) == "2.426"
    growth = by[24]["flips"]["first"] / by[8]["flips"]["first"]
    assert round(float(growth)) == 276 and round(float(growth) ** 0.25, 1) == 4.1                      # n = 8 → 24: Faktor 276, im Mittel 4,1 je vier Knoten
    assert [ev.fmt_mean(by[n]["flips"]["best"]) for n in (8, 12, 16, 20, 24)] == ["1,8", "3,1", "4,2", "4,8", "6,0"] and by[24]["worst_max"] == 4097


def test_claim_family_exact(family):
    """README: längste mögliche Folge 2^(n/2) + n/2 − 2 (n = 4 bis 18: 4 / 9 / 18 / 35 / 68 / 133 / 262 / 519), kürzeste n / 2 (Maximum über Starts), 2^(n/2) lokale Optima (4 bis 512)."""
    got = {r["n"]: (r["longest"], r["shortest"], r["local_optima"], r["sigma"]) for r in family["exact"]}
    assert got == FAMILY_EXACT
    assert all(r["longest"] == r["formula"] == 2 ** (r["n"] // 2) + r["n"] // 2 - 2 and r["local_optima"] == 2 ** (r["n"] // 2) and r["shortest"] == r["n"] // 2 for r in family["exact"])


def test_claim_random_weights_stay_quadratic(family):
    """README: auf vollständigen Graphen mit Zufallsgewichten 1 bis 100 ist die längste Folge (Maximum über 5 Graphen) n = 6 / 8 / 10 / 12 / 14: 11 / 20 / 30 / 46 / 60, also 0,30 bis 0,32 · n²."""
    got = {r["n"]: (r["longest"], r["per_n2"]) for r in family["random"]}
    assert got == FAMILY_RANDOM and all(r["graphs"] == 5 for r in family["random"])
    assert [ev.fmt_num(float(v[1]), 2) for v in got.values()] == ["0,31", "0,31", "0,30", "0,32", "0,31"]
    assert "rund 0,32 · n² (n = 14: 60)" in ev.verdict_family(family)[1]


def test_claim_the_whole_family_comparison_in_one_sentence(family):
    text = ev.verdict_family(family)[1]
    assert "bei n = 24 im Mittel 2.513 und 2.426 Flips (Σw = 16.777.191), die beste 6,0 und die zufällige 14,1." in text and "bei allen 8 geraden Größen von n = 4 bis 18 genau 2^(n/2) + n/2 − 2 (bei n = 18: 519)" in text


# --- Befund 3: Qualität ---------------------------------------------------------------------------------------------------------------------


def test_claim_quality():
    """README, Befund 3: 100 feste Graphen (n = 14, Gewichte bis 10, erste Regel): in allen 100 ein lokales Optimum mit Schnitt ≥ Σw / 2; im Mittel 96 % des Optimums, mindestens 84,1 % (37/44)."""
    q = ev.sweep_quality()
    assert (q["half_ok"], q["local_ok"], q["count"], q["n"], q["wmax"]) == (100, 100, 100, 14, 10) and q["ratio_min"] == F(37, 44)
    assert ev.fmt_percent(q["ratio_mean"]) == "96 %" and ev.fmt_percent(q["ratio_min"]) == "84,1 %"
    assert "im Mittel 96 %, mindestens 84,1 %" in ev.verdict_quality(q)[1]


# --- Presets (Einzelinstanzen) -----------------------------------------------------------------------------------------------------------------

# Preset: (Flips, Schnitt vorher, nachher, Σw, exakt: kürzeste, längste vom Start, längste von irgendeinem Start, lokale Optima, Optimum)
PRESETS = {
    "Standardfall (Voreinstellung)": (7, 2097, 3214, 4368, None),
    "Lehrbeispiel (Dreieck)": (1, 0, 2, 3, (1, 1, 1, 6, 2)),
    "Die gemeine Familie: erste Regel": (514, 556858, 699040, 1048555, None),
    "Die gemeine Familie: beste Regel": (6, 556858, 699040, 1048555, None),
    "Alle Gewichte 1": (3, 55, 64, 120, (3, 3, 8, 12870, 64)),
    "Schlechteste Regel, große Gewichte": (30, 37136994, 47192507, 69537110, None),
    "Klein genug zum Aufzählen": (4, 104, 190, 228, (4, 14, 33, 20, 190)),
}


@pytest.mark.parametrize("name", list(PRESETS))
def test_claim_presets_are_single_instances_with_these_values(name):
    a = ev.analyse(ev.Settings(**C.PRESETS[name]))
    flips, cs, ce, total, exact = PRESETS[name]
    assert (a.search.flips, a.search.cut_start, a.search.cut_end, a.total) == (flips, cs, ce, total)
    assert (None if a.exact is None else (a.exact.shortest, a.exact.longest, a.exact.longest_overall, a.exact.local_optima, a.exact.optimum)) == exact
    assert ev.validation_errors(a) == []


def test_claim_preset_help_texts_quote_these_numbers():
    h = C.PRESET_HELP
    assert "7 Flips (Schnitt 2.097 → 3.214) bei Σw = 4.368" in h["Standardfall (Voreinstellung)"] and "von 0 auf 2" in h["Lehrbeispiel (Dreieck)"] and "6 lokale Optima" in h["Lehrbeispiel (Dreieck)"]
    assert "514 Flips (Schnitt 556.858 → 699.040) bei Σw = 1.048.555" in h["Die gemeine Familie: erste Regel"] and "6 Flips bis zum selben Schnitt 699.040" in h["Die gemeine Familie: beste Regel"]
    assert "3 Flips (Schnitt 55 → 64)" in h["Alle Gewichte 1"] and "8 Flips" in h["Alle Gewichte 1"] and "12.870 lokale Optima" in h["Alle Gewichte 1"] and "Schnitt ist 64" in h["Alle Gewichte 1"]
    assert "30 Flips bei Σw = 69.537.110" in h["Schlechteste Regel, große Gewichte"] and "4 Flips" in h["Klein genug zum Aufzählen"] and "4 bis 14" in h["Klein genug zum Aufzählen"]
    assert "höchstens 33" in h["Klein genug zum Aufzählen"] and "20 lokale Optima" in h["Klein genug zum Aufzählen"] and "190" in h["Klein genug zum Aufzählen"]


def test_claim_k16_has_exactly_the_balanced_cuts_as_local_optima():
    """README: im vollständigen Graphen mit 16 Knoten und Gewichten 1 sind die 12.870 = C(16, 8) ausgeglichenen Zweiteilungen genau die lokalen Optima; Maximum 64 = 8 · 8; längste Folge 8."""
    e = A.exact_sequences(A.ones(16))
    assert e.local_optima == 12870 and int(e.cut.max()) == 64 and int(e.longest.max()) == 8
    balanced = sum(1 for s in range(1 << 16) if bin(s).count("1") == 8)
    assert balanced == 12870


def test_claim_hand_values_of_the_small_graphs(mini):
    """README (Handwerte): Dreieck, Start (0, 0, 0): Gewinn 2 je Flip, 1 Flip bis Schnitt 2; Pfad 0 —3— 1 —1— 2: erste Regel 2 Flips, beste 1, schlechteste 3, jeweils Schnitt 4; K4: 2 Flips bis Schnitt 4;
    exp-min (n = 4): Σw = 11, längste Folge 4, 4 lokale Optima."""
    assert A.gains(mini["T3"], (0, 0, 0)) == [2, 2, 2] and A.local_search(mini["T3"], (0, 0, 0), "first").cut_end == 2
    assert [A.local_search(mini["P3"], (0, 0, 0), r).flips for r in ("first", "best", "worst")] == [2, 1, 3] and A.local_search(mini["P3"], (0, 0, 0), "worst").cut_end == 4
    assert A.local_search(mini["K4"], (0, 0, 0, 0), "first").flips == 2 and A.local_search(mini["K4"], (0, 0, 0, 0), "first").cut_end == 4
    e = A.exact_sequences(A.exp_min(4))
    assert (A.total_weight(A.exp_min(4)), int(e.longest.max()), e.local_optima) == (11, 4, 4)
