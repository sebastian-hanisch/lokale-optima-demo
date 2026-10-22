"""Verdikte und Zahlenformate an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Zufalls-Seeds. Damit prüft der Test die Grenzen und jede genannte Zahl direkt."""

from fractions import Fraction as F

import pls_algorithm as A
import pls_evaluation as ev
from conftest import P3


def _analysis(w=P3, start=(0, 1, 0), flips=0, sequence=(), cut_start=4, cut_end=4, total=4, exact=None, rule="first", side=None):
    search = A.Search(side or start, flips, sequence, cut_start, cut_end)
    return ev.Analysis(ev.Settings(n=len(w), rule=rule), w, start, search, total, exact)


# --- Formate ------------------------------------------------------------------------------------------------------------------------------


def test_number_formats():
    assert ev.fmt_int(131071) == "131.071" and ev.fmt_int(12) == "12" and ev.fmt_int(0) == "0" and ev.fmt_num(22.7) == "22,7" and ev.fmt_num(3, 2) == "3,00"


def test_fmt_percent():
    assert ev.fmt_percent(F(1, 4)) == "25 %" and ev.fmt_percent(F(4, 7)) == "57,1 %" and ev.fmt_percent(F(1)) == "100 %" and ev.fmt_percent(F(0)) == "0 %" and ev.fmt_percent(F(35, 100), 0) == "35 %"
    assert ev.fmt_percent(F(1, 1000)) == "0,1 %" and ev.fmt_percent(F(1, 2000)) == "0,05 %" and ev.fmt_percent(F(1, 10000)) == "0,01 %"           # genau 0,01 %: noch mit Zahl
    assert ev.fmt_percent(F(1, 10001)) == "weniger als 0,01 %" and ev.fmt_percent(F(30, 69_537_110)) == "weniger als 0,01 %"


def test_fmt_mean_is_integral_from_one_hundred_or_when_exact():
    assert ev.fmt_mean(F(14)) == "14" and ev.fmt_mean(F(3600)) == "3.600" and ev.fmt_mean(F(199, 2)) == "99,5" and ev.fmt_mean(F(100)) == "100" and ev.fmt_mean(F(1001, 10)) == "100"
    assert ev.fmt_mean(F(1999, 10)) == "200" and ev.fmt_mean(F(1, 3)) == "0,3" and ev.fmt_mean(F(299, 10)) == "29,9" and ev.fmt_mean(7) == "7"


def test_exp_min_formula():
    assert [ev.exp_min_formula(n) for n in (4, 6, 8, 10, 12, 14, 16, 18)] == [4, 9, 18, 35, 68, 133, 262, 519]
    try:
        ev.exp_min_formula(5)
    except ValueError:
        pass
    else:
        raise AssertionError("ungerades n muss abgelehnt werden")


# --- verdict_main -------------------------------------------------------------------------------------------------------------------------


def test_verdict_main_triangle_with_the_exact_enumeration():
    kind, text = ev.verdict_main(ev.analyse(ev.Settings(n=3, family="ones")))
    assert kind == "success"
    assert text == ("Die Lokalsuche mit der ersten verbessernden Regel endet nach 1 Flip in einem lokalen Optimum: der Schnitt steigt von 0 auf 2. Mehr als Σw = 3 Flips sind nicht möglich; "
                    "ausgeschöpft sind 33,3 % der Schranke. Der Schnitt ist mindestens die Hälfte von Σw (66,7 % von Σw). Aufzählung aller 8 Schnitte: von diesem Start aus sind genau 1 Flip möglich "
                    "(günstigste bis ungünstigste Wahl der Flips), die längste Folge von irgendeinem Start hat 1 Flip, es gibt 6 lokale Optima, der größte Schnitt ist 2 (100 % davon erreicht).")


def test_verdict_main_plural_range_and_other_rules():
    exact = ev.ExactSummary(4, 14, 33, 20, 190)
    a = _analysis(flips=4, sequence=(0, 1, 2, 3), cut_start=104, cut_end=190, total=228, exact=exact, rule="best")
    kind, text = ev.verdict_main(a)
    assert kind == "success" and text.startswith("Die Lokalsuche mit der besten Regel endet nach 4 Flips in einem lokalen Optimum: der Schnitt steigt von 104 auf 190.")
    assert "ausgeschöpft sind 1,8 % der Schranke." in text and "(83,3 % von Σw)" in text and "sind 4 bis 14 Flips möglich" in text and "hat 33 Flips, es gibt 20 lokale Optima, der größte Schnitt ist 190 (100 % davon erreicht)" in text
    assert "mit der schlechtesten Regel" in ev.verdict_main(_analysis(flips=2, sequence=(0, 1), cut_start=1, cut_end=3, rule="worst"))[1]
    assert "mit der zufälligen Regel" in ev.verdict_main(_analysis(flips=2, sequence=(0, 1), cut_start=1, cut_end=3, rule="random"))[1]


def test_verdict_main_start_is_already_a_local_optimum():
    kind, text = ev.verdict_main(_analysis())
    assert kind == "info"
    assert text == ("Der Startschnitt (4) ist schon ein lokales Optimum: kein Flip hat einen positiven Gewinn. Der Schnitt ist mindestens die Hälfte von Σw (100 % von Σw). "
                    "(Die Aufzählung aller Schnitte läuft nur bis n = 16.)")


def test_verdict_main_half_boundary_and_zero_total():
    assert "ist mindestens die Hälfte" in ev.verdict_main(_analysis(flips=1, sequence=(0,), cut_start=1, cut_end=2, total=4))[1]               # 2 · 2 = 4: genau die Hälfte
    assert "ist höchstens die Hälfte" in ev.verdict_main(_analysis(flips=1, sequence=(0,), cut_start=0, cut_end=1, total=4))[1]               # 2 · 1 < 4
    assert "ist höchstens die Hälfte" in ev.verdict_main(_analysis(flips=1, sequence=(0,), cut_start=0, cut_end=2, total=5))[1]               # 2 · 2 < 5, aber 3 · 2 ≥ 5
    text = ev.verdict_main(_analysis(w=((0, 0), (0, 0)), start=(0, 0), cut_start=0, cut_end=0, total=0))[1]
    assert "Startschnitt (0)" in text and "(0 % von Σw)" in text


def test_verdict_main_exact_enumeration_with_optimum_zero():
    exact = ev.ExactSummary(0, 0, 0, 4, 0)
    text = ev.verdict_main(_analysis(w=((0, 0), (0, 0)), start=(0, 0), cut_start=0, cut_end=0, total=0, exact=exact))[1]
    assert "(100 % davon erreicht)" in text and "es gibt 4 lokale Optima" in text and "genau 0 Flips" in text


# --- verdict_rules -------------------------------------------------------------------------------------------------------------------------


def _rules_rows():
    def row(n, wmax, sigma, f, worst_max, share):
        return {"n": n, "wmax": wmax, "count": 100, "sigma": F(sigma), "flips": {k: F(v) for k, v in f.items()}, "worst_max": worst_max, "share_max": F(share)}
    return [row(10, 1, 23, {"best": 2, "random": 3, "first": 3, "worst": 4}, 10, "9/19"), row(80, 1, 1580, {"best": 26, "random": 40, "first": 49, "worst": 97}, 153, "1/10"),
            row(80, 1000, 788474, {"best": F(299, 10), "random": F(499, 10), "first": F(662, 10), "worst": F(35321, 100)}, 484, "1/1600")]


def test_verdict_rules_quotes_the_largest_cell_and_the_largest_share():
    kind, text = ev.verdict_rules(_rules_rows())
    assert kind == "info"
    assert "Bei n = 80 und Gewichten bis 1.000 (Σw im Mittel 788.474) brauchen die Regeln im Mittel 29,9 (beste), 49,9 (zufällig), 66,2 (erste) und 353 (schlechteste) Flips; die schlechteste Regel höchstens 484." in text
    assert "Über alle 300 Graphen und vier Regeln ist der größte Anteil Flips / Σw 47,4 % (n = 10, W = 1)." in text


# --- verdict_family ------------------------------------------------------------------------------------------------------------------------


def _family(exact_ok=True):
    rules = [{"n": 20, "starts": 20, "sigma": 1048555, "flips": {"first": F(59055, 100), "best": F(97, 20), "worst": F(59055, 100), "random": F(251, 20)}, "worst_max": 1024},
             {"n": 24, "starts": 20, "sigma": 16777191, "flips": {"first": F(250305, 100), "best": F(119, 20), "worst": F(242625, 100), "random": F(281, 20)}, "worst_max": 4097}]
    exact = [{"n": n, "longest": 2 ** (n // 2) + n // 2 - 2 + (0 if exact_ok else 1), "shortest": n // 2, "local_optima": 2 ** (n // 2), "sigma": 2 ** n, "formula": 2 ** (n // 2) + n // 2 - 2} for n in (4, 6, 8)]
    exact.append({"n": 9, "longest": 9, "shortest": 4, "local_optima": 100, "sigma": 511, "formula": None})                              # ungerades n hat keine Formel und wird nicht verglichen
    return {"rules": rules, "exact": exact, "random": [{"n": 6, "graphs": 5, "longest": 11, "per_n2": F(11, 36)}, {"n": 14, "graphs": 5, "longest": 60, "per_n2": F(60, 196)}]}


def test_verdict_family_quotes_rules_formula_and_comparison():
    kind, text = ev.verdict_family(_family())
    assert kind == "info"
    assert "bei n = 24 im Mittel 2.503 und 2.426 Flips (Σw = 16.777.191), die beste 6,0 und die zufällige 14,1." in text
    assert "bei allen 3 geraden Größen von n = 4 bis 8 genau 2^(n/2) + n/2 − 2 (bei n = 8: 18), die Zahl der lokalen Optima 2^(n/2) (16)" in text
    assert "rund 0,31 · n² (n = 14: 60)" in text


def test_verdict_family_warns_if_the_formula_fails():
    kind, text = ev.verdict_family(_family(exact_ok=False))
    assert kind == "warning" and "gilt hier nicht" in text


# --- verdict_quality -----------------------------------------------------------------------------------------------------------------------


def _quality(half_ok=100, local_ok=100):
    return {"n": 14, "wmax": 10, "count": 100, "half_ok": half_ok, "local_ok": local_ok, "ratio_min": F(37, 44), "ratio_mean": F(96, 100)}


def test_verdict_quality_info_and_each_failure_alone_is_an_error():
    kind, text = ev.verdict_quality(_quality())
    assert kind == "info" and "In allen 100 Graphen (n = 14, Gewichte bis 10)" in text and "im Mittel 96 %, mindestens 84,1 %." in text
    assert ev.verdict_quality(_quality(half_ok=99))[0] == "error" and ev.verdict_quality(_quality(local_ok=99))[0] == "error"
    assert "darf nicht sein" in ev.verdict_quality(_quality(half_ok=0))[1]
