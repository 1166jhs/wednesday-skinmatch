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

BENEFICIAL_FLAGS = {
    "hydrating": "hydration support",
    "barrier_support": "barrier support",
    "soothing": "soothing support",
    "low_risk": "low-risk support",
    "brightening": "brightening support",
}

CAUTION_FLAGS = {
    "fragrance": "fragrance may irritate fragrance-sensitive skin",
    "essential_oil": "essential oils can bother some sensitive skin types",
    "drying_alcohol": "drying alcohol can feel stripping or irritating",
    "exfoliating": "exfoliating actives can irritate overused or damaged barriers",
    "aha": "AHA may irritate sensitive or damaged skin barriers",
    "bha": "BHA can be helpful for pores but may dry or sting",
    "pha": "PHA is gentler but can still irritate reactive skin",
    "retinoid": "retinoids can cause dryness, peeling, or purging",
    "vitamin_c": "vitamin C can sting on reactive skin",
    "comedogenic_caution": "heavier ingredients may bother acne or closed comedone-prone skin",
    "rich": "rich textures may feel heavy for oily/acne-prone skin",
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

    user_reactions = reactions[reactions["user_id"].astype(str) == str(user_id)]
    if user_reactions.empty:
        return set(), set()

    liked_products = set(user_reactions[user_reactions["reaction_result"] == "Good"]["product_id"].astype(int))
    bad_products = set(user_reactions[user_reactions["reaction_result"] == "Bad"]["product_id"].astype(int))

    liked_ingredients = set(
        product_ingredients[product_ingredients["product_id"].isin(liked_products)]["ingredient_name"]
    )
    bad_ingredients = set(
        product_ingredients[product_ingredients["product_id"].isin(bad_products)]["ingredient_name"]
    )
    return liked_ingredients, bad_ingredients


def ingredient_risk_breakdown(
    product: pd.Series,
    profile: Dict,
    reactions: pd.DataFrame,
    product_ingredients: pd.DataFrame,
    ingredients: pd.DataFrame,
    user_id: str = "demo_user",
) -> pd.DataFrame:
    """Explain the ingredient-level reasons behind a product score."""
    details = product_ingredient_details(int(product["product_id"]), product_ingredients, ingredients)
    if details.empty:
        return pd.DataFrame(columns=["ingredient", "risk_level", "score_impact", "reasons"])

    sensitivities = profile.get("sensitivities", [])
    avoid_ingredients = [str(a).strip().lower() for a in profile.get("avoid_ingredients", []) if str(a).strip()]
    concerns = [str(c).lower() for c in profile.get("concerns", [])]
    liked_ingredients, bad_ingredients = get_reaction_ingredient_patterns(user_id, reactions, product_ingredients)

    rows = []
    for _, ing in details.iterrows():
        name = str(ing.get("ingredient_name", ""))
        name_lower = name.lower()
        flags = split_tags(ing.get("flags", ""))
        reasons: List[str] = []
        impact = 0

        # Manual avoid list should be the strongest personalised caution.
        manual_matches = [avoid for avoid in avoid_ingredients if avoid in name_lower]
        if manual_matches:
            impact -= 25
            reasons.append("matches your manual avoid list")

        # Sensitivity-based flags.
        for sensitivity in sensitivities:
            risky_flags = SENSITIVITY_TO_FLAGS.get(sensitivity, [])
            matched_flags = sorted(set(risky_flags).intersection(flags))
            if matched_flags:
                impact -= 12
                reasons.append(f"matches {sensitivity}: {', '.join(matched_flags)}")

        # Profile concern caution.
        if "comedogenic_caution" in flags and any(c in concerns for c in ["acne", "closed comedones", "blackheads", "pores"]):
            impact -= 8
            reasons.append("comedogenic/heavy-texture caution for acne or clogged-pore concerns")

        # Past reactions.
        if name in bad_ingredients:
            impact -= 6
            reasons.append("appeared in a product you reacted badly to")
        if name in liked_ingredients:
            impact += 3
            reasons.append("appeared in a product you liked")

        # General positive flags.
        positive_flags = [BENEFICIAL_FLAGS[flag] for flag in flags if flag in BENEFICIAL_FLAGS]
        if positive_flags:
            impact += min(3, len(positive_flags))
            reasons.append("benefit flags: " + ", ".join(sorted(set(positive_flags))))

        # General caution flags.
        general_cautions = [CAUTION_FLAGS[flag] for flag in flags if flag in CAUTION_FLAGS]
        if general_cautions and impact <= 0:
            reasons.append("general caution: " + "; ".join(sorted(set(general_cautions))[:2]))

        if impact <= -18:
            level = "High caution"
        elif impact < 0:
            level = "Watch"
        elif impact > 0:
            level = "Helpful"
        else:
            level = "Neutral"
            if not reasons:
                reasons.append("no personalised caution found")

        rows.append(
            {
                "ingredient_order": ing.get("ingredient_order", ""),
                "ingredient": name,
                "flags": ing.get("flags", ""),
                "possible_concerns": ing.get("possible_concerns", ""),
                "risk_level": level,
                "score_impact": impact,
                "reasons": "; ".join(reasons),
            }
        )

    return pd.DataFrame(rows)


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
    risk_rows = ingredient_risk_breakdown(product, profile, reactions, product_ingredients, ingredients, user_id)
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
        matched_avoids = sorted([name for name in ingredient_names if any(avoid in name for avoid in avoid_ingredients)])
        if matched_avoids:
            score -= 25
            cautions.append("Contains ingredient(s) you marked to avoid: " + ", ".join(matched_avoids[:5]) + ".")

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

    # Add ingredient-level impacts, but keep the score controlled.
    if not risk_rows.empty:
        risk_total = int(risk_rows["score_impact"].clip(lower=-8, upper=4).sum())
        score += max(-20, min(12, risk_total))

        high_cautions = risk_rows[risk_rows["risk_level"] == "High caution"]["ingredient"].head(3).tolist()
        helpfuls = risk_rows[risk_rows["risk_level"] == "Helpful"]["ingredient"].head(3).tolist()
        if high_cautions:
            cautions.append("Ingredient risk explanation highlights: " + ", ".join(high_cautions) + ".")
        if helpfuls:
            positives.append("Helpful ingredient matches include: " + ", ".join(helpfuls) + ".")

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
        "risk_breakdown": risk_rows,
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
        reacted_product_ids = set(reactions[reactions["user_id"].astype(str) == str(user_id)]["product_id"].astype(int))

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


def best_product_for_category(
    category_names: List[str],
    products: pd.DataFrame,
    profile: Dict,
    reactions: pd.DataFrame,
    product_ingredients: pd.DataFrame,
    ingredients: pd.DataFrame,
    user_id: str,
) -> Dict | None:
    subset = products[products["category"].isin(category_names)].copy()
    if subset.empty:
        return None
    ranked = recommend_products(subset, profile, reactions, product_ingredients, ingredients, user_id)
    if ranked.empty:
        return None
    return ranked.iloc[0].to_dict()
