"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Permalink-Begrenzung."""

import pytest

import pls_constants as C
import pls_evaluation as ev
import pls_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name] and "TODO" not in C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert C.N_MIN <= p["n"] <= C.N_MAX and 0 <= p["seed"] <= C.SEED_MAX and p["family"] in C.FAMILIES and p["rule"] in C.RULE_LABELS, name
        assert p["dens"] in C.DENS_OPTIONS and p["wmax"] in C.WMAX_OPTIONS, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_every_preset_analyses_without_validation_errors():
    for name, p in C.PRESETS.items():
        assert ev.validation_errors(ev.analyse(ev.Settings(**p))) == [], name


def test_rule_tables_are_consistent():
    assert set(C.RULE_LABELS) == set(C.RULE_SHORT) == set(C.COLOR_RULES) == {"first", "best", "worst", "random"}


@pytest.mark.parametrize("raw, expected", [("7", 7), ("0", 3), ("99", 24), (["5"], 5), ("abc", None), (None, None)])
def test_permalink_values_are_clamped_to_the_slider(raw, expected):
    assert P._coerce(P.SETTING_SPECS["n_slider"], raw) == expected


def test_permalink_choice_values_must_be_listed():
    assert P._coerce(P.SETTING_SPECS["family_select"], "expmin") == "expmin" and P._coerce(P.SETTING_SPECS["family_select"], "bogus") is None
    assert P._coerce(P.SETTING_SPECS["rule_select"], "worst") == "worst" and P._coerce(P.SETTING_SPECS["rule_select"], "x") is None
    assert P._coerce(P.SETTING_SPECS["wmax_select"], "1000000") == 1_000_000 and P._coerce(P.SETTING_SPECS["wmax_select"], "5") is None
    assert P._coerce(P.SETTING_SPECS["dens_select"], "50") == 50 and P._coerce(P.SETTING_SPECS["dens_select"], "55") is None
