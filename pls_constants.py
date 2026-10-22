"""Konstanten: Regler-Grenzen, Rechengrenzen, Messreihen-Parameter, Farben und Presets.

Rechengrenze am Regler-Maximum (DEMO-PLAYBOOK §1c): n = 24 auf der Familie exp-min: rund 4.100 Flips im schlimmsten Fall (jeder Flip aktualisiert die Gewinne in O(n)); die Aufzählung aller 2^n Schnitte für die
exakten Folgen bis n = 16 live (65.536 Zustände, rund 0,3 Sekunden) und bis n = 18 in der Messreihe (262.144 Zustände, rund 1 Sekunde)."""

N_MIN, N_MAX, DEFAULT_N = 3, 24, 20                   # Knoten des Graphen
SEED_MAX, DEFAULT_SEED = 999999, 35
FAMILIES = {
    "random": "Zufallsgraph (Dichte und Gewichtsgrenze einstellbar)",
    "ones": "vollständig, alle Gewichte 1",
    "expmin": "vollständig, Gewicht 2^min(i, j) (die gemeine Familie)",
}
DEFAULT_FAMILY = "random"
DENS_OPTIONS = (20, 30, 40, 50, 60, 70, 80)           # Kantenwahrscheinlichkeit in Prozent (nur Zufallsgraph)
DEFAULT_DENS = 50
WMAX_OPTIONS = (1, 10, 100, 1_000, 1_000_000)         # größtes Kantengewicht (nur Zufallsgraph): Gewichte 1 bis W
DEFAULT_WMAX = 100
RULE_LABELS = {
    "first": "erste verbessernde (kleinster Knotenindex)",
    "best": "beste (größter Gewinn)",
    "worst": "schlechteste (kleinster positiver Gewinn)",
    "random": "zufällige verbessernde",
}
RULE_SHORT = {"first": "ersten verbessernden Regel", "best": "besten Regel", "worst": "schlechtesten Regel", "random": "zufälligen Regel"}
DEFAULT_RULE = "first"
EXACT_LIVE_N_MAX = 16                                 # exakte Folgen (alle Schnitte) live nur bis hierhin

# Messreihen (alle Instanzen aus dem eigenen Generator: auf jeder Plattform dieselben)
RULES_SIZES = (10, 20, 40, 80)
RULES_WMAX = (1, 10, 1_000)
RULES_COUNT = 100
RULES_DENS = 50
RULES_SEED = 1000
FAMILY_RULE_SIZES = (8, 12, 16, 20, 24)
FAMILY_STARTS = 20
FAMILY_EXACT_SIZES = (4, 6, 8, 10, 12, 14, 16, 18)
FAMILY_SEED = 2000
RANDOM_EXACT_SIZES = (6, 8, 10, 12, 14)
RANDOM_EXACT_GRAPHS = 5
RANDOM_EXACT_WMAX = 100
QUALITY_N = 14
QUALITY_WMAX = 10
QUALITY_COUNT = 100
QUALITY_SEED = 3000

COLOR_FIRST = "#C0392B"
COLOR_BEST = "#2F6B65"
COLOR_WORST = "#7a5195"
COLOR_RANDOM = "#4c78a8"
COLOR_BOUND = "#B8860B"
COLOR_RULES = {"first": COLOR_FIRST, "best": COLOR_BEST, "worst": COLOR_WORST, "random": COLOR_RANDOM}
COLOR_SERIES = ("#2F6B65", "#4c78a8", "#B8860B", "#C0392B", "#7a5195")

PRESETS = {
    "Standardfall (Voreinstellung)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "family": DEFAULT_FAMILY, "dens": DEFAULT_DENS, "wmax": DEFAULT_WMAX, "rule": DEFAULT_RULE},
    "Lehrbeispiel (Dreieck)": {"n": 3, "seed": DEFAULT_SEED, "family": "ones", "dens": DEFAULT_DENS, "wmax": DEFAULT_WMAX, "rule": "first"},
    "Die gemeine Familie: erste Regel": {"n": 20, "seed": DEFAULT_SEED, "family": "expmin", "dens": DEFAULT_DENS, "wmax": DEFAULT_WMAX, "rule": "first"},
    "Die gemeine Familie: beste Regel": {"n": 20, "seed": DEFAULT_SEED, "family": "expmin", "dens": DEFAULT_DENS, "wmax": DEFAULT_WMAX, "rule": "best"},
    "Alle Gewichte 1": {"n": 16, "seed": DEFAULT_SEED, "family": "ones", "dens": DEFAULT_DENS, "wmax": DEFAULT_WMAX, "rule": "first"},
    "Schlechteste Regel, große Gewichte": {"n": 24, "seed": DEFAULT_SEED, "family": "random", "dens": DEFAULT_DENS, "wmax": 1_000_000, "rule": "worst"},
    "Klein genug zum Aufzählen": {"n": 14, "seed": DEFAULT_SEED, "family": "random", "dens": DEFAULT_DENS, "wmax": 10, "rule": "best"},
}
PRESET_HELP = {   # nach der Messung geschrieben (DEMO-PLAYBOOK: Hilfetexte nie vor der Messung); jede Zahl steht in tests/test_claims.py
    "Standardfall (Voreinstellung)": "Zufallsgraph mit 20 Knoten (Dichte 50 %, Gewichte bis 100): die erste verbessernde Regel braucht 7 Flips (Schnitt 2.097 → 3.214) bei Σw = 4.368.",
    "Lehrbeispiel (Dreieck)": "Das Dreieck mit Gewichten 1: ein Flip (Gewinn 2) bringt den Schnitt von 0 auf 2, das Maximum; von den 8 Schnitten sind 6 lokale Optima.",
    "Die gemeine Familie: erste Regel": "20 Knoten, Kantengewicht 2^min(i, j): die erste verbessernde Regel braucht 514 Flips (Schnitt 556.858 → 699.040) bei Σw = 1.048.555.",
    "Die gemeine Familie: beste Regel": "Dieselbe Familie, derselbe Start, die beste Regel: 6 Flips bis zum selben Schnitt 699.040.",
    "Alle Gewichte 1": "Vollständiger Graph mit 16 Knoten, alle Gewichte 1: 3 Flips (Schnitt 55 → 64); die längste mögliche Folge von irgendeinem Start hat 8 Flips, es gibt 12.870 lokale Optima, der größte Schnitt ist 64.",
    "Schlechteste Regel, große Gewichte": "24 Knoten, Gewichte bis 1.000.000: die schlechteste Regel braucht 30 Flips bei Σw = 69.537.110; die Schranke ist nicht annähernd erreicht.",
    "Klein genug zum Aufzählen": "14 Knoten, Gewichte bis 10, beste Regel: 4 Flips; vom Start aus sind 4 bis 14 möglich, von irgendeinem Start höchstens 33; 20 lokale Optima, der größte Schnitt ist 190 und wird erreicht.",
}
