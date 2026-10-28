"""Pure energy/macro math. No I/O so it is trivial to unit test."""

KCAL_PER_KG_FAT = 7700
DAYS_PER_WEEK = 7

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

# kg of bodyweight change per week for each pace, as a fraction of bodyweight
GOAL_PACE_PCT_PER_WEEK = {
    "cut": {"slow": 0.0025, "moderate": 0.005, "aggressive": 0.01},
    "bulk": {"slow": 0.001, "moderate": 0.0025, "aggressive": 0.005},
}

PROTEIN_G_PER_KG = {"cut": 2.2, "maintain": 1.8, "bulk": 1.8}
FAT_PCT_OF_CALORIES = 0.27
FIBER_G_PER_1000_KCAL = 14
WATER_ML_PER_KG = 35
MIN_CALORIES = {"male": 1500, "female": 1200}

WHY = {
    "calories": "Total daily energy target. Energy balance is the main driver of weight change: "
    "eat below maintenance to lose, above it to gain.",
    "protein": "Protein preserves muscle during a cut and supports growth during a bulk. "
    "It is also the most filling macro, which makes a deficit easier to stick to.",
    "fat": "Dietary fat supports hormone production (including testosterone and estrogen) and "
    "absorption of vitamins A, D, E and K. Going too low long-term can hurt both.",
    "carbs": "Carbs are the body's preferred fuel for hard training. They fill the calories "
    "left after protein and fat are set.",
    "fiber": "Fiber improves fullness, digestion and blood sugar control. "
    "About 14 g per 1000 kcal is the common guideline.",
    "water": "Hydration affects performance, appetite and how your scale weight fluctuates. "
    "Roughly 35 ml per kg of bodyweight, more when you sweat.",
    "bmr": "Basal metabolic rate: calories your body burns at complete rest "
    "(Mifflin-St Jeor equation). The floor of your energy needs.",
    "tdee": "Total daily energy expenditure: BMR plus activity. "
    "This is your estimated maintenance calories.",
    "bmi": "Body mass index: weight relative to height. A rough population screen; "
    "it does not distinguish muscle from fat.",
    "weekly_change_kg": "Expected weight change per week at this calorie target, "
    "using ~7700 kcal per kg of body fat.",
}


def bmr_mifflin(sex: str, weight_kg: float, height_cm: float, age: int) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "male" else base - 161


def calculate_targets(
    *,
    sex: str,
    age: int,
    height_cm: float,
    weight_kg: float,
    activity: str,
    goal: str,
    pace: str = "moderate",
) -> dict:
    """Return calorie/macro targets. Each metric is {value, unit, why}."""
    bmr = bmr_mifflin(sex, weight_kg, height_cm, age)
    tdee = bmr * ACTIVITY_MULTIPLIERS[activity]

    weekly_change_kg = 0.0
    if goal in GOAL_PACE_PCT_PER_WEEK:
        weekly_change_kg = weight_kg * GOAL_PACE_PCT_PER_WEEK[goal][pace]
        if goal == "cut":
            weekly_change_kg = -weekly_change_kg
    daily_adjustment = weekly_change_kg * KCAL_PER_KG_FAT / DAYS_PER_WEEK

    # Safety floor, but never let the floor turn a cut into a surplus when
    # maintenance itself is below the floor.
    floor = min(MIN_CALORIES[sex], tdee)
    calories = max(tdee + daily_adjustment, floor)
    # Recompute weekly change in case the safety floor kicked in.
    weekly_change_kg = (calories - tdee) * DAYS_PER_WEEK / KCAL_PER_KG_FAT

    protein_g = weight_kg * PROTEIN_G_PER_KG[goal]
    fat_g = calories * FAT_PCT_OF_CALORIES / 9
    carbs_g = max((calories - protein_g * 4 - fat_g * 9) / 4, 0)
    fiber_g = calories / 1000 * FIBER_G_PER_1000_KCAL
    water_l = weight_kg * WATER_ML_PER_KG / 1000
    bmi = weight_kg / (height_cm / 100) ** 2

    def metric(key: str, value: float, unit: str, digits: int = 0) -> dict:
        return {"value": round(value, digits), "unit": unit, "why": WHY[key]}

    return {
        "calories": metric("calories", calories, "kcal"),
        "protein": metric("protein", protein_g, "g"),
        "fat": metric("fat", fat_g, "g"),
        "carbs": metric("carbs", carbs_g, "g"),
        "fiber": metric("fiber", fiber_g, "g"),
        "water": metric("water", water_l, "L", 1),
        "bmr": metric("bmr", bmr, "kcal"),
        "tdee": metric("tdee", tdee, "kcal"),
        "bmi": metric("bmi", bmi, "", 1),
        "weekly_change_kg": metric("weekly_change_kg", weekly_change_kg, "kg/wk", 2),
    }


def scale_nutrients(per_100g: dict, grams: float) -> dict:
    """Scale per-100 g nutrient values to the amount eaten."""
    factor = grams / 100
    return {k: round((v or 0) * factor, 1) for k, v in per_100g.items()}
