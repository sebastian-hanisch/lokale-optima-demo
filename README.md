# Lokale Optima finden: PLS – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-lokale-optima-demo.streamlit.app/)** -->

Elftes (optionales) Stück der **Komplexitätsklassen-Reihe** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Stück 5 ([fptas-rucksack-demo](https://github.com/sebastian-hanisch/fptas-rucksack-demo)) zeigt, was „pseudopolynomiell“ heißt (Laufzeit in der Größe der Zahlen), Stück 8 ([zufallsverfahren-demo](https://github.com/sebastian-hanisch/zufallsverfahren-demo)) den Zufall als Werkzeug. Dieses Stück fügt die **Lokalsuche als Suchproblem** hinzu: **Eine Lokalsuche endet immer in einem lokalen Optimum, aber wie lange dauert der Weg, und woran liegt es?** Anders als die Fall-Demos zeigt es **eine Frage der Komplexitätstheorie** an einem kleinen Beispiel. Die Lokalsuche auf Touren und die Metaheuristiken stehen in [hill-climbing-demo](https://github.com/sebastian-hanisch/hill-climbing-demo), [tabu-search-demo](https://github.com/sebastian-hanisch/tabu-search-demo) und [iterated-local-search-demo](https://github.com/sebastian-hanisch/iterated-local-search-demo); hier werden sie nicht nachgebaut.

## Warum dieses Problem

Beim **Max-Cut** wird ein Graph mit ganzzahligen Kantengewichten in zwei Seiten geteilt, und der Schnitt zählt die Gewichte der Kanten, die zwischen den Seiten liegen. Die **Flip-Nachbarschaft** setzt einen Knoten auf die andere Seite; sein **Gewinn** ist das Gewicht der Kanten zur eigenen Seite minus das zur anderen. Ein **lokales Optimum** hat keinen Flip mit Gewinn über 0. Es **existiert immer** (der Schnitt steigt mit jedem Flip, und es gibt nur endlich viele Schnitte); offen ist der Weg. Jeder verbessernde Flip hebt den Schnitt um mindestens 1, also endet **jede** Folge nach höchstens Σw Flips (Σw = Summe der Gewichte): das ist **pseudopolynomiell**, polynomiell in der Größe der Zahlen, nicht in ihrer Länge. Die Demo **zählt Flips**, nie Sekunden, und fragt dreierlei: Wie nahe kommt die Praxis dieser Schranke? Was entscheidet über die Länge, die **Pivotregel** (welcher der verbessernden Flips gewählt wird) oder die Größe der Gewichte? Und gibt es Graphen, auf denen natürliche Regeln **exponentiell** lange Folgen laufen? **Der Hook ist ehrlich benannt:** auf Zufallsgraphen ist die Schranke Σw nie nahe, die langen Folgen sind eine Konstruktion.

## Modell

- **Graphen.** n = 3 bis 24 Knoten. Drei Familien: **Zufallsgraph** (jede Kante mit Wahrscheinlichkeit 20 bis 80 %, Gewicht gleichverteilt 1 bis W mit W ∈ {1, 10, 100, 1.000, 1.000.000}), **vollständiger Graph mit allen Gewichten 1** und die **gemeine Familie exp-min**: vollständig, Kante {i, j} (Knoten 0 bis n − 1) mit Gewicht 2^min(i, j). Zufällig ist nur der Start (eigener SplitMix64-Generator, deshalb auf jeder Plattform dieselben Graphen und Starts). **Jede Zahl gilt für diese Familien**, nicht für alle Graphen.
- **Gewinn und Flip.** Gewinn eines Knotens = Gewicht zu seiner Seite minus Gewicht zur anderen; der Flip hebt den Schnitt genau um den Gewinn. Die Gewinne werden nach einem Flip nur für die Nachbarn fortgeschrieben (± 2w).
- **Pivotregeln.** **Erste** (kleinster Knotenindex mit Gewinn über 0), **beste** (größter Gewinn, Gleichstand: kleinster Index), **schlechteste** (kleinster positiver Gewinn, Gleichstand: kleinster Index), **zufällige** (gleichverteilt unter den verbessernden Flips, Zufalls-Seed).
- **Schranken.** Flips ≤ Σw (jeder Flip hebt den Schnitt um mindestens 1); jedes lokale Optimum schneidet mindestens Σw / 2 (jeder Knoten hat höchstens die Hälfte seines Kantengewichts auf der eigenen Seite).
- **Exakte Folgen.** Aufzählung **aller 2ⁿ Schnitte** (live bis n = 16, in der Messreihe bis n = 18): die **längste** und die **kürzeste** mögliche Folge von jedem Start (Rückwärtsrechnung über die verbessernden Flips in absteigender Schnittfolge), die Zahl der lokalen Optima und das Optimum. Die längste Folge von irgendeinem Start ist die Schrittzahl der schlimmsten Pivotregel im schlimmsten Fall.
- Mathematik (Gewinn, Schranken, exakte Folgen) und Annahmentabelle: Expander **📐 Mathematische Formulierung** in der App.

## Methodik

| Baustein | Datei | Anmerkung |
|---|---|---|
| Schnittwert aus der Definition, Gewinne, Flip, vier Pivotregeln, Lokalsuche, Prüfung auf lokales Optimum, Aufzählung aller Schnitte, die Familie exp-min | `pls_algorithm.py` | eine Regel = eine Funktion; `cut_value` ist der unabhängige Prüfer |
| Zufallsgraphen und Zufallsstarts aus Familie, n, Dichte, W und Zufalls-Seed | `pls_scenario.py` | Gewichte und Kanten ganzzahlig |
| SplitMix64 | `pls_rng.py` | **wörtliche Kopie** von reduktionskette-demo/red_scenario.py; Regressionstest `tests/test_copies.py` |
| Kennzahlen, Messreihen, Prüfung vor der Anzeige, Verdikte | `pls_evaluation.py` | Mittelwerte und Anteile als `Fraction`; alle Verdikte reine Funktionen |

Experimente in der App: **Schranke gegen Praxis** (Knopf, Pivotregeln auf Zufallsgraphen über n und W), **Eine gemeine Familie** (Knopf, exp-min: die vier Regeln bis n = 24 und die exakten Folgen bis n = 18), **Wie gut ist ein lokales Optimum?** (Knopf), **Einordnung** (PLS, geglättete Analyse, Gleichgewichte; nur Text).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`. Die Messreihen laufen über feste Graphen aus dem eigenen Generator, die Presets sind Einzelinstanzen und als solche ausgewiesen.

| Frage | Befund |
|---|---|
| **Wie nahe kommt die Praxis der Schranke Σw?** (H2) | Zufallsgraphen G(n, 50 %), Gewichte 1 bis W, je Zelle 100 feste Graphen, zufälliger Start. **W = 1.000**, n = 10 / 20 / 40 / 80: Σw im Mittel 11.075 / 47.867 / 194.750 / 788.474; Flips der besten Regel **3,2 / 6,9 / 14,2 / 29,9**, der zufälligen 4,3 / 10,3 / 21,8 / 49,9, der ersten 4,3 / 10,4 / 25,3 / 66,2, der schlechtesten **6,4 / 22,5 / 84,5 / 353,2**. Der größte Anteil Flips / Σw über alle Graphen und Regeln liegt bei W = 1.000 bei **höchstens 0,14 %** (n = 10; n = 80: 0,06 %). **Bei W = 1 ist die Schranke nicht so fern:** bis **47,4 %** (n = 10), sinkend mit n (n = 10 / 20 / 40 / 80: 47,4 / 24,7 / 14,8 / 9,9 %) (`test_claim_rules_table`, `test_claim_the_bound_is_not_reached_on_large_weights`). |
| **Hängt die Länge von der Gewichtsgröße ab?** (H3) | Kaum, außer bei der schlechtesten Regel. n = 80, W = 1 / 10 / 1.000: beste Regel **25,8 / 29,3 / 29,9** Flips bei 500-fachem Σw, schlechteste **96,7 / 292,0 / 353,2**; größte Folge der schlechtesten Regel bei W = 1.000: 484 (`test_claim_rule_order_and_weight_dependence`). |
| **Entscheidet die Pivotregel?** (H4) | Ja. n = 80, W = 1.000: beste 29,9 < zufällige 49,9 < erste 66,2 < schlechteste 353,2. In **allen 12 Zellen** ist die beste Regel die kürzeste und die schlechteste die längste; die zufällige ist ab n = 20 kürzer als die erste, **bei n = 10 knapp länger** (W = 1: 3,13 gegen 3,12) (`test_claim_rule_order_holds_in_every_cell_except_random_against_first_at_n_10`). |
| **Wie gut ist ein lokales Optimum?** (H5) | n = 14, Gewichte bis 10, 100 feste Graphen, erste Regel, Optimum durch Aufzählung: in **100 von 100** ein lokales Optimum mit Schnitt ≥ Σw / 2; im Mittel **96 %** des Optimums, mindestens **84,1 %** (37/44) (`test_claim_quality`). |
| **Gibt es lange Folgen?** (H6, H8) | Ja, auf exp-min. **Längste mögliche Folge** für gerades n = 4 bis 18 (aufgezählt): **4 / 9 / 18 / 35 / 68 / 133 / 262 / 519** = **2^(n/2) + n/2 − 2** (gemessen für diese acht Größen, nicht als Satz bewiesen), kürzeste vom schlimmsten Start n / 2, **2^(n/2) lokale Optima** (4 bis 512); Σw 11 bis 262.125. Auf vollständigen Graphen mit Zufallsgewichten 1 bis 100 dagegen (Maximum über 5 Graphen) n = 6 / 8 / 10 / 12 / 14: **11 / 20 / 30 / 46 / 60**, also 0,30 bis 0,32 · n² (`test_claim_family_exact`, `test_claim_random_weights_stay_quadratic`). |
| **Laufen natürliche Regeln auf exp-min exponentiell?** (H7) | Die erste und die schlechteste: ja. 20 feste Zufallsstarts, n = 8 / 12 / 16 / 20 / 24: **erste 9,1 / 41,4 / 118,7 / 590,6 / 2.513**, schlechteste 9,1 / 41,4 / 118,7 / 590,6 / **2.426** (bei n = 8 bis 20 **gleich**), Faktor 276 von n = 8 auf 24, im Mittel 4,1 je vier Knoten (Σw bei n = 24: 16.777.191, größte Folge der schlechtesten Regel 4.097). **Die beste und die zufällige nicht:** beste 1,8 / 3,1 / 4,2 / 4,8 / 6,0, zufällige 2,8 / 5,6 / 8,9 / 12,6 / 14,1 (`test_claim_family_rules`, `test_claim_first_equals_worst_for_small_n_and_grows_fourfold_per_four_vertices`, `test_claim_the_whole_family_comparison_in_one_sentence`). |
| **Presets (Einzelinstanzen)** | Flips / Schnitt vorher → nachher / Σw: **Standardfall** (n = 20, Zufallsgraph, W = 100, erste Regel, Zufalls-Seed 35): 7 / 2.097 → 3.214 / 4.368. **Lehrbeispiel** (Dreieck): 1 / 0 → 2 / 3, 6 von 8 Schnitten lokale Optima. **Gemeine Familie, erste Regel** (n = 20): 514 / 556.858 → 699.040 / 1.048.555; **dieselbe Familie mit der besten Regel**: 6 Flips bis zum selben Schnitt. **Alle Gewichte 1** (n = 16): 3 / 55 → 64 / 120. **Schlechteste Regel, große Gewichte** (n = 24, W = 1.000.000): 30 / 37.136.994 → 47.192.507 / 69.537.110. **Klein genug zum Aufzählen** (n = 14, W = 10, beste Regel): 4 Flips, vom Start 4 bis 14 möglich, von irgendeinem Start höchstens 33, 20 lokale Optima, Optimum 190 (= erreichter Schnitt) (`test_claim_presets_are_single_instances_with_these_values`). |
| **Vollständiger Graph, alle Gewichte 1, n = 16** | Die **12.870 = C(16, 8)** ausgeglichenen Zweiteilungen sind genau die lokalen Optima; Maximum 64 = 8 · 8; längste Folge 8 (`test_claim_k16_has_exactly_the_balanced_cuts_as_local_optima`). |
| **Handwerte** | Dreieck, Start (0, 0, 0): Gewinn 2 je Flip, 1 Flip bis Schnitt 2. Pfad 0 —3— 1 —1— 2: erste Regel 2 Flips, beste 1, schlechteste 3, jeweils Schnitt 4. K₄ (Gewichte 1): 2 Flips bis Schnitt 4. exp-min (n = 4): Σw = 11, längste Folge 4, 4 lokale Optima (`test_claim_hand_values_of_the_small_graphs`). |

### Hypothesen des Plans

| | Hypothese | Ergebnis |
|---|---|---|
| H1 | Jeder verbessernde Flip hebt den Schnitt um genau seinen Gewinn (≥ 1), jede Folge endet in einem lokalen Optimum, die Schrittzahl ist höchstens Σw | **Ja**: in jeder Lokalsuche des Orakel-Tests und des großen Laufs |
| H2 | Auf Zufallsgraphen liegt die Schrittzahl weit unter Σw | **Teilweise**: bei W = 1.000 höchstens 0,14 % von Σw, aber bei W = 1 bis 47,4 % (n = 10); der Plan sagte „nie nahe“, das gilt nur für große Gewichte und wachsendes n |
| H3 | Die Schrittzahl hängt kaum von der Gewichtsgröße ab (außer bei der schlechtesten Regel) | **Ja**: beste Regel 25,8 → 29,9 bei 500-fachem Σw; schlechteste 96,7 → 353,2 |
| H4 | beste < zufällig < erste < schlechteste | **Ja, mit einer Ausnahme**: beste kürzeste, schlechteste längste in allen 12 Zellen; zufällig < erste erst ab n = 20 |
| H5 | Jedes lokale Optimum schneidet ≥ Σw / 2 und liegt nahe am Optimum | **Ja**: 100 von 100, im Mittel 96 %, mindestens 84,1 % |
| H6 | Die längste Folge ist auf Zufallsgewichten polynomiell, auf einer expliziten Familie exponentiell | **Ja**: 0,30 bis 0,32 · n² gegen 2^(n/2) + n/2 − 2 (n = 4 bis 18, gerade) |
| H7 | Auf exp-min laufen natürliche Regeln (erste, schlechteste) exponentiell, die beste und die zufällige nicht | **Ja**: 9,1 → 2.513 gegen 1,8 → 6,0 und 2,8 → 14,1 (n = 8 → 24) |
| H8 | Die Familie exp-min hat 2^(n/2) lokale Optima | **Ja**: für gerades n = 4 bis 18 aufgezählt |
| H9 | Max-Cut mit Flip ist PLS-vollständig; geglättet sind lange Folgen selten | **Literatur, nicht gemessen**: die Demo misst Flips auf kleinen Graphen, nicht Klassen |

## Ehrliche Grenzen

- **Zufallsgraphen und eine Familie sind nicht „alle“ Graphen.** Die Familie exp-min ist eine Konstruktion, kein Beleg für typische Instanzen; die Aussagen gelten für diese Familien und für die vier Regeln.
- **Die Formel 2^(n/2) + n/2 − 2 ist gemessen, nicht bewiesen**, und nur für gerades n = 4 bis 18.
- **Auf kleinen Graphen mit kleinen Gewichten ist die Schranke Σw nicht fern** (bis 47,4 % bei W = 1, n = 10); „weit darunter“ gilt für große Gewichte.
- **Flips sind kein Zeitmaß.** Ein Flip kostet O(n) beim Fortschreiben der Gewinne; gezählt werden Flips einer einfachen Umsetzung, keine Sekunden.
- **Die vier Regeln sind vier von vielen.** Auch „beste“ kann auf anderen Gewichten lang laufen; die Demo behauptet das Gegenteil nicht.
- **PLS-Zugehörigkeit und -Vollständigkeit, die geglättete Analyse und PPAD sind Literatur**, keine Messung der Demo. Die PLS-Vollständigkeit von 2-opt wird **nicht** behauptet.
- **Die exakte Aufzählung ist klein**: live bis n = 16, in der Messreihe bis n = 18 (2ⁿ Schnitte).
- **Die Messreihen sind klein** (100 Graphen je Zelle, 20 Starts, 5 Graphen für die exakten Folgen auf Zufallsgewichten): die Mediane und Maxima der Zellen sind Stichproben.

## Befunde und Korrekturen gegenüber dem Plan

- **Regler n = 3 bis 24** statt 4 bis 24 (das Dreieck ist das Lehrbeispiel von Hand). **Exakte Aufzählung live bis n = 16** (Plan: 14) und in der Messreihe bis n = 18.
- **„Die Schranke ist nie nahe“ (Plan, Vormessung) ist zu stark:** bei W = 1 und n = 10 sind es bis zu 47,4 % von Σw; bei W = 1.000 höchstens 0,14 %. Die App sagt es so.
- **Auf exp-min sind erste und schlechteste Regel bei den 20 festen Starts von n = 8 bis 20 im Mittel gleich** (nicht nur ähnlich); erst bei n = 24 trennen sie sich (2.513 gegen 2.426). Das ist eine Eigenschaft dieser Starts: auf einzelnen anderen Starts unterscheiden sie sich schon bei kleinem n (z. B. n = 12, Zufalls-Seed 5: 60 gegen 58 Flips, `test_family_worst_max_belongs_to_the_worst_rule_alone`). Die Vormessung hatte die beiden Spalten ähnlich, aber nicht als gleich ausgewiesen.
- **Andere Mittelwerte als in der Vormessung** (andere Graphen aus dem eigenen Generator): beste Regel bei n = 80, W = 1.000: 29,9 (Vormessung 29,9); schlechteste 353,2 (356,2); größte Folge der schlechtesten Regel 484 (547); Qualität im Mittel 96 % (95,4 %) und mindestens 84,1 % (79 %). Alle Zahlen im README stammen aus der Bau-Messung.
- **Voreinstellung und Preset „Schlechteste Regel, große Gewichte“** statt „Gleichgewichte der Regeln“ (n = 24, W = 1.000.000 zeigt die Distanz zur Schranke deutlicher).
- **Die geglättete Analyse** wird Etscheid und Röglin zugeschrieben (nicht Englert, Röglin und Vöcking, wie im Plan): Max-Cut mit Flip, quasi-polynomiell in beliebigen Graphen; sie ist nur als Einordnung genannt.
- **Kein 2-opt:** das Vehikel ist Max-Cut mit Flip; 2-opt steht in `hill-climbing-demo`.

## Verifikation

- **Kern:** jede Einheit gegen Handrechnung an Mini-Graphen (`tests/conftest.py`, `tests/test_algorithm.py`): Dreieck, Pfad mit drei Knoten, K₄, exp-min mit n = 4; Gewinne, Fortschreiben, die vier Regeln mit Gleichständen, Schnittverlauf, Aufzählung (längste, kürzeste, lokale Optima), Randfälle.
- **Orakel** (`tests/test_oracle_lokale_optima.py`): die fortgeschriebene Lokalsuche gegen eine **neu rechnende** (der Schnittwert nach jedem Flip aus der Definition) für alle vier Regeln; auf jeder Suche die Sätze (jeder Schritt ≥ 1, Flips ≤ Σw, Ergebnis ist lokales Optimum, Schnitt ≥ Σw / 2); die exakten Folgen gegen eine Rekursion mit Gedächtnis; die Zahl der lokalen Optima gegen die Definition; jede Regel liegt zwischen der kürzesten und der längsten Folge; die Formel und 2^(n/2) auf exp-min; die Auswertung über ein Raster ohne Prüffehler; die volle Qualitätsmessreihe.
- **Eigenschaften** (`tests/test_eigenschaften_lokale_optima.py`): Umnummerieren der Knoten, Skalieren aller Gewichte, Vertauschen der Seiten, ein isolierter Knoten verdoppelt die lokalen Optima, ein Graph ohne Kanten, eine schwere Kante, Determinismus bei festem Zufalls-Seed.
- **Kopie** (`tests/test_copies.py`): wortgleich mit dem Original, solange es im Portfolio-Ordner liegt, dazu die bekannten ersten Werte der SplitMix64-Konvention.
- **Prüfung vor der Anzeige:** `validation_errors` prüft die Sätze auf der gezeigten Suche, den Schnittverlauf, die Grenzen der exakten Folgen und deren Zähler; jede Meldung wird einzeln ausgelöst, auch an den Grenzen (`tests/test_evaluation.py`).
- **Messreihen** gegen unabhängige Nachrechnungen; **Verdikte** als reine Funktionen, jede Zahl im Text und jede Schwelle an handgesetzten Werten (`tests/test_verdicts.py`); **Claims:** jede Zahl dieser README (`tests/test_claims.py`).
- **Presets:** vollständig, gültige Werte, Hilfetexte erst nach der Messung geschrieben, erstes Preset gleich Standard, jedes Preset ohne Prüffehler (`tests/test_presets.py`); Randfälle (`tests/test_edge_cases.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an den Grenzen), alle drei Messreihen-Knöpfe einzeln (`tests/test_app_sweeps.py`), Permalink mit Begrenzung, Layout, Footer, Abbildungen und PDF (`tests/test_visualization.py`).
- **Browser:** Standardansicht mit und ohne Graph, alle drei Messreihen per Klick, Preset-Wechsel; keine Konsolenmeldung nach dem Erstrendern.

## Mutationsprüfung und großer Lauf

- **Großer Lauf im Scratch-Ordner (nicht im Repo):** 1.205.004 Prüfungen, **0 Abweichungen**: alle 4.096 gewichteten K₄ mit Gewichten 0 bis 3 (alle 16 Starts, alle Regeln, die Flipzahl liegt zwischen der kürzesten und der längsten Folge), alle 1.024 Graphen auf fünf Knoten mit Gewichten 0 oder 1 (alle 32 Starts, alle Regeln; die Zahl der lokalen Optima gegen die Definition), 3.000 Zufallsgraphen mit n = 3 bis 12 und allen fünf Gewichtsgrenzen (alle Regeln: schnelle gegen neu rechnende Suche, Sätze), 60 exakte Folgen gegen die Rekursion (n = 4 bis 9), die Formel und 2^(n/2) auf exp-min für gerades n = 4 bis 18, dazu die Auswertung samt Prüfung vor der Anzeige für jede Familie, jedes n von 3 bis 24 und jede Regel.
- **Mutationsprüfung** (`tools/mutate_demo.py`, über `pls_algorithm.py`, `pls_evaluation.py` und die übrigen Rechenmodule; Darstellung und Oberfläche mutiert das Werkzeug nicht, sie sind durch Rauch-, Verdikt-, Claims- und Orakel-Tests abgesichert; die wörtliche Kopie `pls_rng.py` ist ausgenommen, ihre Tests liegen in Stück 3): **211 Stellen**, davon **179 gefangen**, **8 als äquivalent festgehalten** (`tests/mutation_state.json`), **22 durch wortgleiche Zeilen in Nachbar-Demos gesichert** (die Zahlenformate) und **2 mit Zeitüberschreitung** (`g > 0` → `g >= 0` in `improving`: eine Suche mit Gewinn 0 flippt ewig; das Werkzeug zählt das nicht als gefangen, es ist aber eine Endlosschleife). Der erste Lauf ließ 13 Stellen überleben; geschlossen wurden die Lücken mit Grenztests: das Maximum der schlechtesten Regel gehört nur ihr (ein Start, bei dem die erste Regel 60 und die schlechteste 58 Flips braucht), die Diagonale und die Kanten des **letzten** Knotens in der Gestaltprüfung, genau ein lokales Optimum in der Prüfung der exakten Grenzen, die Wortwahl „höchstens“ gegen „mindestens“ bei einem Schnitt zwischen einem Drittel und der Hälfte von Σw. Äquivalent sind: Schleifen, deren letzter Durchlauf keinen Partner hat (`range(n)` → `range(n - 1)` in `cut_value`, `total_weight`, beim Füllen der Zufallsgewichte und beim Symmetrietest), der Beginn der Doppelschleife bei `j = i` statt `j = i + 1` (die Diagonale ist 0), `and` → `or` beim Fortschreiben der Gewinne (Gewicht 0 ändert nichts) und `2 * Schnitt ≥ Σw` gegen `3 * Schnitt ≥ Σw` in der Zählung der Messreihe (der Satz „lokales Optimum schneidet ≥ Σw / 2“ macht beide gleich; dass er gilt, prüfen die Orakel-Tests).

## Einordnung und Quellen (anhand der Quellen geprüft)

**Bibliografisch geprüft** (Verlags- bzw. Bibliothekseinträge, Inhalte nicht im Original gelesen): Johnson, Papadimitriou und Yannakakis, *How easy is local search?*, Journal of Computer and System Sciences 37, 1988, S. 79 bis 100 (die Klasse PLS); Schäffer und Yannakakis, *Simple Local Search Problems that are Hard to Solve*, SIAM Journal on Computing 20 (1), 1991, S. 56 bis 87 (nach dem Bibliothekseintrag; die Seitenzahlen wurden beim Verlag nicht bestätigt); Etscheid und Röglin, *Smoothed Analysis of Local Search for the Maximum-Cut Problem*, ACM Transactions on Algorithms 13 (2), 2017 (geglättete Analyse, quasi-polynomielle Laufzeit der Flip-Lokalsuche in beliebigen Graphen). **Nicht bestätigt:** dass die PLS-Vollständigkeit von Max-Cut mit Flip genau in der Arbeit von Schäffer und Yannakakis steht, wurde an der Quelle nicht gelesen (Lehrbuchwissen und Rückschauen nennen es so); deshalb steht in der App „nach der Literatur“. **Nicht nachgeschlagen:** Daskalakis, Goldberg und Papadimitriou (Nash-Gleichgewichte sind PPAD-vollständig; nur eine Einordnungszeile, im Plan als geprüft vermerkt). Die Arbeit von Englert, Röglin und Vöcking über 2-opt (Algorithmica 68 (1), 2014) wird nur erwähnt, um zu sagen, dass die PLS-Vollständigkeit von 2-opt hier **nicht** behauptet wird. Zahlen aus diesen Arbeiten sind nicht übernommen.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Graph und Kennzahlen, Verlauf des Schnitts, drei Experimente, Einordnung, Annahmentabelle, Formeln |
| `pls_algorithm.py` | Kern: Schnittwert, Gewinne, vier Pivotregeln, Lokalsuche, Aufzählung aller Schnitte, die Familie exp-min |
| `pls_constants.py` | Regler-Grenzen, Rechengrenzen, Messreihen-Parameter, Farben, Presets mit Hilfetexten |
| `pls_evaluation.py` | Analyse, Messreihen, Prüfung vor der Anzeige, Verdikte, Zahlenformate |
| `pls_layout.py` | Fester Kopf (Stylesheet) |
| `pls_pdf_export.py` | PDF-Bericht (fpdf2) |
| `pls_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `pls_rng.py` | wörtliche Kopie: SplitMix64 aus Stück 3 |
| `pls_scenario.py` | Zufallsgraphen und Zufallsstarts |
| `pls_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Graphen, Orakel, Eigenschaften, Kopie, Auswertung, Verdikte, Claims, Presets, Randfälle, Layout, AppTest-Smoke-Test und Messreihen-Knöpfe, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Lokalsuche auf Touren (2-opt, Or-opt) und Metaheuristiken** (Tabu-Suche, Simulated Annealing, iterierte Lokalsuche): stehen in `hill-climbing-demo` und seinen Nachfolgern.
- **Andere Nachbarschaften für Max-Cut** (Vertauschen zweier Knoten, Kernighan-Lin): wären eigene Messreihen.
- **PLS-Reduktionen und -Beweise:** die Demo misst Flips, sie beweist keine Klassenzugehörigkeit.
- **Die geglättete Analyse** (zufällige Störung der Gewichte, Messung der Folgenlänge): genannt, nicht nachgebaut.
- **PPAD und Nash-Gleichgewichte:** eine Einordnungszeile; die Verfahren stehen in `nash-demo`.
- **Beschleunigungen der Lokalsuche** (Bucket-Strukturen für die Gewinne): die Flipzahlen sollen einfach und erklärbar bleiben.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
