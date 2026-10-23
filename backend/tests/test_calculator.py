import pytest

from calculator import bmr_mifflin, calculate_targets, scale_nutrients

BASE = dict(sex="male", age=30, height_cm=180, weight_kg=80, activity="moderate")


def test_bmr_mifflin_male_and_female():
    # 10*80 + 6.25*180 - 5*30 = 1775
    assert bmr_mifflin("male", 80, 180, 30) == 1780
    assert bmr_mifflin("female", 80, 180, 30) == 1614


def test_maintain_calories_equal_tdee():
    t = calculate_targets(**BASE, goal="maintain")
    assert t["tdee"]["value"] == round(1780 * 1.55)
    assert t["calories"]["value"] == t["tdee"]["value"]
    assert t["weekly_change_kg"]["value"] == 0


def test_cut_is_a_deficit_and_bulk_is_a_surplus():
    maintain = calculate_targets(**BASE, goal="maintain")["calories"]["value"]
    cut = calculate_targets(**BASE, goal="cut", pace="moderate")
    bulk = calculate_targets(**BASE, goal="bulk", pace="moderate")
    # 0.5% of 80 kg = 0.4 kg/wk -> 0.4*7700/7 = 440 kcal/day deficit
    assert cut["calories"]["value"] == pytest.approx(maintain - 440, abs=1)
    assert cut["weekly_change_kg"]["value"] == pytest.approx(-0.4, abs=0.01)
    assert bulk["calories"]["value"] > maintain
    assert bulk["weekly_change_kg"]["value"] > 0


def test_protein_higher_on_cut():
    cut = calculate_targets(**BASE, goal="cut")
    bulk = calculate_targets(**BASE, goal="bulk")
    assert cut["protein"]["value"] == 176  # 2.2 g/kg
    assert bulk["protein"]["value"] == 144  # 1.8 g/kg


SMALL = dict(sex="female", age=60, height_cm=150, weight_kg=45, goal="cut", pace="aggressive")


def test_calorie_floor_applies_and_weekly_change_reflects_it():
    t = calculate_targets(**SMALL, activity="light")  # TDEE ~1274
    assert t["calories"]["value"] == 1200
    assert t["weekly_change_kg"]["value"] == pytest.approx(-0.07, abs=0.01)


def test_floor_never_turns_a_cut_into_a_surplus():
    t = calculate_targets(**SMALL, activity="sedentary")  # TDEE ~1112, below the floor
    assert t["calories"]["value"] <= t["tdee"]["value"]
    assert t["weekly_change_kg"]["value"] <= 0


def test_macros_add_up_to_calories():
    t = calculate_targets(**BASE, goal="bulk")
    kcal = t["protein"]["value"] * 4 + t["carbs"]["value"] * 4 + t["fat"]["value"] * 9
    assert kcal == pytest.approx(t["calories"]["value"], abs=10)


def test_every_metric_has_a_why_explanation():
    t = calculate_targets(**BASE, goal="cut")
    assert all(m["why"] for m in t.values())


def test_scale_nutrients_handles_missing_values():
    assert scale_nutrients({"calories": 200, "fat": None}, 150) == {"calories": 300, "fat": 0}
