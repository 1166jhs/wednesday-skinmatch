from typing import Dict, List, Tuple

import pandas as pd

from src.data_loader import split_tags

SENSITIVITY_TO_FLAGS = {
    "Fragrance-sensitive": ["fragrance"],
    "Essential oil-sensitive": ["essential_oil"],
    "Alcohol-sensitive": ["drying_alcohol"],
    "Niacinamide-sensitive": ["brightening"],
    "Vitamin C-sensitive": ["vitamin_c"],
    "Retinoid-sensitive": ["retinoid"],
    "AHA/BHA/PHA-sensitive": ["aha", "bha", "pha", "exfoliating"],
    "Shea butter-sensitive": ["rich", "comedogenic_caution"],
    "Sunscreen stings my eyes": [],
}

PREFERENCE_TO_COLUMNS = {
    "Fragrance-free": "fragrance_free",
    "Alcohol-free": "alcohol_free",
    "Essential-oil-free": "essential_oil_free",
}


def product_ingredient_details(
    product_id: int, product_ingredients: pd.DataFrame, ingredients: pd.DataFrame
) -> pd.DataFrame:
    rows = product_ingredients[product_ingredients["product_id"] == product_id].copy()
    return rows.merge(ingredients, on="ingredient_name", how="left").sort_values("ingredient_order")


def get_product_flags(product_id: int, product_ingredients: pd.DataFrame, ingredients: pd.DataFrame) -> List[str]:
    details = product_ingredient_details(product_id, product_ingredients, ingredients)
    flags: List[str] = []
    for value in details["flags"].fillna(""):
        flags.extend(split_tags(value))
    return sorted(set(flags))


def get_reaction_ingredient_patterns(
    user_id: str,
    reactions: pd.DataFrame,
    product_ingredients: pd.DataFrame,
) -> Tuple[set, set]:
    """Return ingredients linked to products the user liked and disliked."""
    if reactions.empty:
        return set(), set()

    user_reactions = reactions[reactions["user_id"] == user_id]
    liked_products = set(user_reactions[user_reactions["reaction_result"] == "Good"]["product_id"].astype(int))
    bad_products = set(user_reactions[user_reactions["reaction_result"] == "Bad"]["product_id"].astype(int))

    liked_ingredients = set(
        product_ingredients[product_ingredients["product_id"].isin(liked_products)]["ingredient_name"]
    )
    bad_ingredients = set(
        product_ingredients[product_ingredients["product_id"].isin(bad_products)]["ingredient_name"]
    )
    return liked_ingredients, bad_ingredients


def score_product(
    product: pd.Series,
    profile: Dict,
    reactions: pd.DataFrame,
    product_ingredients: pd.DataFrame,
    ingredients: pd.DataFrame,
    user_id: str = "demo_user",
) -> Dict:
    score = 50
    positives: List[str] = []
    cautions: List[str] = []

    skin_type = profile.get("skin_type", "").lower()
    concerns = [c.lower() for c in profile.get("concerns", [])]
    sensitivities = profile.get("sensitivities", [])
    preferences = profile.get("preferences", [])
    avoid_ingredients = [a.strip().lower() for a in profile.get("avoid_ingredients", []) if a.strip()]

    product_skin_tags = split_tags(product.get("skin_type_tags", ""))
    product_concern_tags = split_tags(product.get("concern_tags", ""))
    product_flags = get_product_flags(int(product["product_id"]), product_ingredients, ingredients)
    details = product_ingredient_details(int(product["product_id"]), product_ingredients, ingredients)
    ingredient_names = [str(x).lower() for x in details["ingredient_name"].tolist()]

    if skin_type and skin_type in product_skin_tags:
        score += 15
        positives.append(f"Matches your {profile.get('skin_type')} skin type.")

    matched_concerns = sorted(set(concerns).intersection(product_concern_tags))
    if matched_concerns:
        points = min(24, len(matched_concerns) * 8)
        score += points
        positives.append("Targets your concern(s): " + ", ".join(matched_concerns) + ".")

    for preference, column in PREFERENCE_TO_COLUMNS.items():
        if preference in preferences and str(product.get(column, "")).lower() == "yes":
            score += 5
            positives.append(f"Fits your preference: {preference}.")
        elif preference in preferences:
            score -= 8
            cautions.append(f"Does not fully fit your preference: {preference}.")

    for sensitivity in sensitivities:
        risky_flags = SENSITIVITY_TO_FLAGS.get(sensitivity, [])
        matched_flags = sorted(set(risky_flags).intersection(product_flags))
        if matched_flags:
            score -= 12
            cautions.append(
                f"You selected {sensitivity}; this product has flag(s): {', '.join(matched_flags)}."
            )

    if "Sunscreen stings my eyes" in sensitivities and str(product.get("category", "")).lower() == "sunscreen":
        score -= 5
        cautions.append("You reported eye stinging with sunscreens, so patch test around the eye area carefully.")

    if avoid_ingredients:
        matched_avoids = sorted(set(avoid_ingredients).intersection(set(ingredient_names)))
        if matched_avoids:
            score -= 25
            cautions.append("Contains ingredient(s) you marked to avoid: " + ", ".join(matched_avoids) + ".")

    liked_ingredients, bad_ingredients = get_reaction_ingredient_patterns(user_id, reactions, product_ingredients)
    current_ingredients = set(details["ingredient_name"].dropna().tolist())
    liked_overlap = sorted(current_ingredients.intersection(liked_ingredients))
    bad_overlap = sorted(current_ingredients.intersection(bad_ingredients))

    if liked_overlap:
        score += min(12, len(liked_overlap) * 3)
        positives.append("Shares ingredient(s) with products you liked: " + ", ".join(liked_overlap[:5]) + ".")

    if bad_overlap:
        score -= min(24, len(bad_overlap) * 6)
        cautions.append("Shares ingredient(s) with products you reacted badly to: " + ", ".join(bad_overlap[:5]) + ".")

    if str(product.get("comedogenic_caution", "")).lower() == "yes" and any(
        c in concerns for c in ["acne", "closed comedones", "blackheads", "pores"]
    ):
        score -= 8
        cautions.append("Has a comedogenic/heavy-texture caution and you selected acne/pores-related concerns.")

    score = max(0, min(100, int(score)))

    if not positives:
        positives.append("No strong positive match found yet, but it may still work depending on your skin.")
    if not cautions:
        cautions.append("No major caution found from your current profile.")

    return {
        "score": score,
        "positives": positives,
        "cautions": cautions,
        "flags": product_flags,
        "ingredient_details": details,
    }


def recommend_products(
    products: pd.DataFrame,
    profile: Dict,
    reactions: pd.DataFrame,
    product_ingredients: pd.DataFrame,
    ingredients: pd.DataFrame,
    user_id: str = "demo_user",
) -> pd.DataFrame:
    scored_rows = []
    reacted_product_ids = set()
    if not reactions.empty:
        reacted_product_ids = set(reactions[reactions["user_id"] == user_id]["product_id"].astype(int))

    for _, product in products.iterrows():
        if int(product["product_id"]) in reacted_product_ids:
            continue
        result = score_product(product, profile, reactions, product_ingredients, ingredients, user_id)
        row = product.to_dict()
        row["match_score"] = result["score"]
        row["why"] = " ".join(result["positives"][:2])
        row["watch_out"] = " ".join(result["cautions"][:2])
        scored_rows.append(row)

    if not scored_rows:
        return pd.DataFrame()
    return pd.DataFrame(scored_rows).sort_values("match_score", ascending=False)
