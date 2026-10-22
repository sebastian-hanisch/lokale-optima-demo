"""Kennzahlen, Messreihen und Verdikte (alle Verdikte sind reine Funktionen (Art, Text), DEMO-PLAYBOOK §12).

Mittelwerte und Anteile sind **Brüche** (`Fraction`); Flips, Schnitte und Gewichte sind ganze Zahlen."""

from dataclasses import dataclass
from fractions import Fraction

import pls_algorithm as A
import pls_constants as C
from pls_rng import SplitMix64
from pls_scenario import make_graph, make_start, random_graph, random_start


@dataclass(frozen=True, kw_only=True)
class Settings:
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    family: str = C.DEFAULT_FAMILY
    dens: int = C.DEFAULT_DENS
    wmax: int = C.DEFAULT_WMAX
    rule: str = C.DEFAULT_RULE


@dataclass(frozen=True)
class ExactSummary:
    shortest: int                    # kürzeste Folge vom Start (beste Pivotregel)
    longest: int                     # längste Folge vom Start (schlimmste Pivotregel)
    longest_overall: int             # längste Folge von irgendeinem Start
    local_optima: int                # Zahl der lokalen Optima unter allen 2^n Schnitten
    optimum: int                     # größter Schnitt


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    w: tuple
    start: tuple
    search: A.Search
    total: int                       # Σw
    exact: ExactSummary | None       # None bei n > EXACT_LIVE_N_MAX


# --- Zahlen im deutschen Format ------------------------------------------------------------------------------------------------------------


def fmt_int(n: int) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner (1.720.350)."""
    return f"{n:,}".replace(",", ".")


def fmt_num(x: float, digits: int = 1) -> str:
    """Dezimalzahl mit Komma (22,7)."""
    return f"{x:.{digits}f}".replace(".", ",")


def fmt_percent(f, digits: int = 1) -> str:
    """Anteil als Prozentzahl mit Komma, ohne überflüssige Nachkommastelle (57,1 %, 25 %); unter 0,1 % mit zwei Stellen, unter 0,01 % „weniger als 0,01 %“."""
    x = float(f) * 100
    if 0 < x < 0.01:
        return "weniger als 0,01 %"
    if 0 < x < 0.1:
        digits = 2
    x = round(x, digits)
    return (fmt_int(int(x)) if x == int(x) else fmt_num(x, digits)) + " %"


def fmt_mean(f) -> str:
    """Mittelwert: ganze Zahl (gerundet) ab 100 oder wenn er ganzzahlig ist, sonst mit einer Nachkommastelle."""
    f = Fraction(f)
    if f.denominator == 1 or f >= 100:
        return fmt_int(round(f))
    return fmt_num(float(f), 1)


# --- Einzelanalyse -------------------------------------------------------------------------------------------------------------------------


def analyse(settings: Settings) -> Analysis:
    w = make_graph(settings.family, settings.n, settings.dens, settings.wmax, settings.seed)
    start = make_start(settings.n, settings.seed)
    search = A.local_search(w, start, settings.rule, SplitMix64(settings.seed ^ 0x9E3779B1))
    exact = None
    if settings.n <= C.EXACT_LIVE_N_MAX:
        e = A.exact_sequences(w)
        s = A.state_of(start)
        exact = ExactSummary(int(e.shortest[s]), int(e.longest[s]), int(e.longest.max()), e.local_optima, int(e.cut.max()))
    return Analysis(settings, w, start, search, A.total_weight(w), exact)


def validation_errors(a: Analysis) -> list:
    """Ergebnis vor der Anzeige prüfen (DEMO-PLAYBOOK §1d): Gestalt des Graphen, die Folge Flip für Flip nachspielen (Gewinn ≥ 1, bei den festen Regeln die Wahl der Regel, Schnittwert aus der Definition),
    Schranke Σw, lokales Optimum mit Brute Force, Schnitt ≥ Σw / 2 und bei n ≤ 16 die Grenzen der exakten Aufzählung."""
    w, s = a.w, a.search
    n = len(w)
    if (any(len(row) != n for row in w) or any(w[i][i] != 0 or any(w[i][j] != w[j][i] or w[i][j] < 0 for j in range(n)) for i in range(n))
            or len(a.start) != n or any(x not in (0, 1) for x in a.start)):
        return ["Der Graph ist nicht symmetrisch, nicht nichtnegativ ganzzahlig, oder der Startschnitt hat die falsche Gestalt."]
    errors = []
    if a.total != A.total_weight(w):
        errors.append("Σw widerspricht der Neuberechnung.")
    side = list(a.start)
    if s.cut_start != A.cut_value(w, side):
        errors.append("Der Startschnitt widerspricht der Neuberechnung.")
    replay_ok = True
    for v in s.sequence:
        g = A.gains(w, side)
        if g[v] < 1:
            replay_ok = False
            break
        if a.settings.rule != "random" and A.choose(a.settings.rule, g, A.improving(g)) != v:
            replay_ok = False
            break
        before = A.cut_value(w, side)
        side[v] ^= 1
        if A.cut_value(w, side) - before != g[v]:
            replay_ok = False
            break
    if not replay_ok:
        errors.append("Ein Flip der Folge ist kein verbessernder Flip der gewählten Regel (Gewinn ≥ 1, Schnitt um genau den Gewinn gestiegen).")
    if s.flips != len(s.sequence) or tuple(side) != s.side or s.cut_end != A.cut_value(w, s.side):
        errors.append("Endzustand, Zahl der Flips oder Endschnitt widersprechen dem Nachspielen der Folge.")
    if s.flips > a.total or s.cut_end - s.cut_start < s.flips:
        errors.append("Die Zahl der Flips überschreitet die Schranke Σw oder ein Flip hat den Schnitt um weniger als 1 erhöht.")
    if not A.is_local_optimum(w, s.side):
        errors.append("Der Endzustand ist kein lokales Optimum (ein Flip erhöht den Schnitt noch).")
    if 2 * s.cut_end < a.total:
        errors.append("Das lokale Optimum schneidet weniger als die Hälfte von Σw.")
    if a.exact is not None:
        e = a.exact
        if not e.shortest <= s.flips <= e.longest <= e.longest_overall or e.local_optima < 1 or s.cut_end > e.optimum:
            errors.append("Die Zahl der Flips liegt außerhalb der Grenzen der exakten Aufzählung (kürzeste ≤ Flips ≤ längste Folge, Endschnitt ≤ Optimum).")
    return errors


# --- Messreihen ----------------------------------------------------------------------------------------------------------------------------


def sweep_rules(sizes=C.RULES_SIZES, wmaxes=C.RULES_WMAX, count: int = C.RULES_COUNT, dens: int = C.RULES_DENS, seed: int = C.RULES_SEED) -> list:
    """Schrittzahl gegen Σw: je Größe und Gewichtsgrenze `count` feste Zufallsgraphen mit zufälligem Start; mittlere Flips der vier Pivotregeln, mittleres Σw, größte Flipzahl der schlechtesten Regel und der
    größte Anteil Flips / Σw über alle Instanzen und Regeln."""
    rows = []
    for wmax in wmaxes:
        for n in sizes:
            sigma = 0
            flips = {r: 0 for r in A.RULES}
            worst_max, share_max = 0, Fraction(0)
            for i in range(count):
                base = seed + 100_003 * wmax + 1000 * n + i
                w = random_graph(n, dens, wmax, SplitMix64(base))
                start = random_start(n, SplitMix64(base ^ 0x5DEECE66D))
                total = A.total_weight(w)
                sigma += total
                for rule in A.RULES:
                    s = A.local_search(w, start, rule, SplitMix64(base ^ 0x9E3779B1))
                    flips[rule] += s.flips
                    if total:
                        share_max = max(share_max, Fraction(s.flips, total))
                    if rule == "worst":
                        worst_max = max(worst_max, s.flips)
            rows.append({"n": n, "wmax": wmax, "count": count, "sigma": Fraction(sigma, count), "flips": {r: Fraction(f, count) for r, f in flips.items()}, "worst_max": worst_max, "share_max": share_max})
    return rows


def exp_min_formula(n: int) -> int:
    """Gemessene Länge der längsten verbessernden Folge auf exp-min für gerades n: 2^(n/2) + n/2 − 2 (kein Satz; die Reihe prüft sie für n = 4 bis 18)."""
    if n % 2:
        raise ValueError("n muss gerade sein")
    return 2 ** (n // 2) + n // 2 - 2


def sweep_family(rule_sizes=C.FAMILY_RULE_SIZES, starts: int = C.FAMILY_STARTS, exact_sizes=C.FAMILY_EXACT_SIZES, random_sizes=C.RANDOM_EXACT_SIZES, graphs: int = C.RANDOM_EXACT_GRAPHS,
                 random_wmax: int = C.RANDOM_EXACT_WMAX, seed: int = C.FAMILY_SEED) -> dict:
    """Die Familie exp-min: (1) die vier Pivotregeln von `starts` festen Zufallsstarts (mittlere Flips, größte Flipzahl der schlechtesten Regel, Σw); (2) die exakten Folgen aus der Aufzählung aller Schnitte
    (längste, kürzeste vom schlimmsten Start, Zahl der lokalen Optima, Σw, die Formel); (3) zum Vergleich die längste Folge auf vollständigen Graphen mit Zufallsgewichten 1 bis `random_wmax`
    (Maximum über `graphs` Graphen) und ihr Verhältnis zu n²."""
    rules = []
    for n in rule_sizes:
        w = A.exp_min(n)
        flips = {r: 0 for r in A.RULES}
        worst_max = 0
        for i in range(starts):
            base = seed + 1000 * n + i
            start = random_start(n, SplitMix64(base))
            for rule in A.RULES:
                s = A.local_search(w, start, rule, SplitMix64(base ^ 0x9E3779B1))
                flips[rule] += s.flips
                if rule == "worst":
                    worst_max = max(worst_max, s.flips)
        rules.append({"n": n, "starts": starts, "sigma": A.total_weight(w), "flips": {r: Fraction(f, starts) for r, f in flips.items()}, "worst_max": worst_max})
    exact = []
    for n in exact_sizes:
        w = A.exp_min(n)
        e = A.exact_sequences(w)
        exact.append({"n": n, "longest": int(e.longest.max()), "shortest": int(e.shortest.max()), "local_optima": e.local_optima, "sigma": A.total_weight(w), "formula": exp_min_formula(n) if n % 2 == 0 else None})
    random_rows = []
    for n in random_sizes:
        best = 0
        for g in range(graphs):
            rng = SplitMix64(seed + 50_000 + 1000 * n + g)
            w = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    w[i][j] = w[j][i] = 1 + rng.below(random_wmax)
            best = max(best, int(A.exact_sequences(tuple(map(tuple, w))).longest.max()))
        random_rows.append({"n": n, "graphs": graphs, "longest": best, "per_n2": Fraction(best, n * n)})
    return {"rules": rules, "exact": exact, "random": random_rows}


def sweep_quality(n: int = C.QUALITY_N, wmax: int = C.QUALITY_WMAX, count: int = C.QUALITY_COUNT, dens: int = C.RULES_DENS, seed: int = C.QUALITY_SEED) -> dict:
    """Güte des lokalen Optimums: je Instanz `first` von einem zufälligen Start, Endschnitt gegen das Optimum (Aufzählung aller Schnitte) und gegen Σw / 2."""
    ratios, half_ok, local_ok = [], 0, 0
    for i in range(count):
        base = seed + i
        w = random_graph(n, dens, wmax, SplitMix64(base))
        s = A.local_search(w, random_start(n, SplitMix64(base ^ 0x5DEECE66D)), "first")
        optimum = int(A.all_cuts(w).max())
        half_ok += 2 * s.cut_end >= A.total_weight(w)
        local_ok += A.is_local_optimum(w, s.side)
        ratios.append(Fraction(s.cut_end, optimum) if optimum else Fraction(1))
    return {"n": n, "wmax": wmax, "count": count, "half_ok": half_ok, "local_ok": local_ok, "ratio_min": min(ratios), "ratio_mean": sum(ratios) / count}


# --- Verdikte (reine Funktionen: (Art, Text)) ------------------------------------------------------------------------------------------------------


def _flips(n: int) -> str:
    return f"{fmt_int(n)} Flip" + ("" if n == 1 else "s")


def verdict_main(a: Analysis) -> tuple:
    s, rule = a.search, C.RULE_SHORT[a.settings.rule]
    half = "höchstens" if 2 * s.cut_end < a.total else "mindestens"
    if s.flips == 0:
        head = f"Der Startschnitt ({fmt_int(s.cut_start)}) ist schon ein lokales Optimum: kein Flip hat einen positiven Gewinn."
    else:
        used = fmt_percent(Fraction(s.flips, a.total)) if a.total else "0 %"
        head = (f"Die Lokalsuche mit der {rule} endet nach {_flips(s.flips)} in einem lokalen Optimum: der Schnitt steigt von {fmt_int(s.cut_start)} auf {fmt_int(s.cut_end)}. "
                f"Mehr als Σw = {fmt_int(a.total)} Flips sind nicht möglich; ausgeschöpft sind {used} der Schranke.")
    share = fmt_percent(Fraction(s.cut_end, a.total)) if a.total else "0 %"
    cut = f" Der Schnitt ist {half} die Hälfte von Σw ({share} von Σw)."
    if a.exact is None:
        return "info", head + cut + f" (Die Aufzählung aller Schnitte läuft nur bis n = {C.EXACT_LIVE_N_MAX}.)"
    e = a.exact
    span = f"genau {_flips(e.shortest)}" if e.shortest == e.longest else f"{fmt_int(e.shortest)} bis {fmt_int(e.longest)} Flips"
    reached = fmt_percent(Fraction(s.cut_end, e.optimum)) if e.optimum else "100 %"
    exact = (f" Aufzählung aller {fmt_int(2 ** len(a.w))} Schnitte: von diesem Start aus sind {span} möglich (günstigste bis ungünstigste Wahl der Flips), "
             f"die längste Folge von irgendeinem Start hat {_flips(e.longest_overall)}, es gibt {fmt_int(e.local_optima)} lokale Optima, der größte Schnitt ist {fmt_int(e.optimum)} ({reached} davon erreicht).")
    return "success", head + cut + exact


def verdict_rules(rows: list) -> tuple:
    big = max(rows, key=lambda r: (r["wmax"], r["n"]))
    worst = max(rows, key=lambda r: r["share_max"])
    f = big["flips"]
    return "info", (
        f"Bei n = {big['n']} und Gewichten bis {fmt_int(big['wmax'])} (Σw im Mittel {fmt_mean(big['sigma'])}) brauchen die Regeln im Mittel {fmt_mean(f['best'])} (beste), {fmt_mean(f['random'])} (zufällig), "
        f"{fmt_mean(f['first'])} (erste) und {fmt_mean(f['worst'])} (schlechteste) Flips; die schlechteste Regel höchstens {fmt_int(big['worst_max'])}. Über alle {fmt_int(sum(r['count'] for r in rows))} Graphen und vier Regeln "
        f"ist der größte Anteil Flips / Σw {fmt_percent(worst['share_max'])} (n = {worst['n']}, W = {fmt_int(worst['wmax'])})."
    )


def verdict_family(res: dict) -> tuple:
    rules, exact, rnd = res["rules"], res["exact"], res["random"]
    big = rules[-1]
    f = big["flips"]
    even = [r for r in exact if r["formula"] is not None]
    if any(r["longest"] != r["formula"] for r in even):
        return "warning", "Die gemessene längste Folge weicht von 2^(n/2) + n/2 − 2 ab; die Formel gilt hier nicht."
    last = even[-1]
    return "info", (
        f"Auf der Familie exp-min brauchen die erste und die schlechteste Regel bei n = {big['n']} im Mittel {fmt_mean(f['first'])} und {fmt_mean(f['worst'])} Flips (Σw = {fmt_int(big['sigma'])}), die beste {fmt_mean(f['best'])} "
        f"und die zufällige {fmt_mean(f['random'])}. Die längste mögliche Folge ist bei allen {len(even)} geraden Größen von n = {even[0]['n']} bis {last['n']} genau 2^(n/2) + n/2 − 2 (bei n = {last['n']}: {fmt_int(last['longest'])}), "
        f"die Zahl der lokalen Optima 2^(n/2) ({fmt_int(last['local_optima'])}); auf vollständigen Graphen mit Zufallsgewichten ist sie im gemessenen Bereich (n = {rnd[0]['n']} bis {rnd[-1]['n']}) nur rund {fmt_num(float(max(r['per_n2'] for r in rnd)), 2)} · n² "
        f"(n = {rnd[-1]['n']}: {fmt_int(rnd[-1]['longest'])})."
    )


def verdict_quality(res: dict) -> tuple:
    if res["half_ok"] != res["count"] or res["local_ok"] != res["count"]:
        return "error", "Ein Endzustand ist kein lokales Optimum oder schneidet weniger als die Hälfte von Σw: das darf nicht sein."
    return "info", (
        f"In allen {fmt_int(res['count'])} Graphen (n = {res['n']}, Gewichte bis {fmt_int(res['wmax'])}) ist der Endzustand ein lokales Optimum und schneidet mindestens Σw / 2. Gegenüber dem Optimum erreicht er im Mittel "
        f"{fmt_percent(res['ratio_mean'])}, mindestens {fmt_percent(res['ratio_min'])}."
    )
