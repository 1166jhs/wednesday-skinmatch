from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
PRODUCTS_PATH = DATA_DIR / "products.csv"
INGREDIENTS_PATH = DATA_DIR / "ingredients.csv"
PRODUCT_INGREDIENTS_PATH = DATA_DIR / "product_ingredients.csv"
REACTIONS_PATH = DATA_DIR / "user_reactions.csv"
PROFILES_PATH = DATA_DIR / "user_profiles.csv"

DEFAULT_PROFILE = {
    "skin_type": "Combination",
    "concerns": ["acne", "texture"],
    "sensitivities": ["Fragrance-sensitive"],
    "preferences": ["Fragrance-free", "Alcohol-free"],
    "avoid_ingredients": [],
}


def split_tags(value: str) -> List[str]:
    """Convert a comma-separated CSV tag value into a clean lowercase list."""
    if pd.isna(value) or value == "":
        return []
    return [tag.strip().lower() for tag in str(value).split(",") if tag.strip()]


def split_display_tags(value: str) -> List[str]:
    """Like split_tags, but preserves the original display casing."""
    if pd.isna(value) or value == "":
        return []
    return [tag.strip() for tag in str(value).split(",") if tag.strip()]


def join_tags(values: List[str]) -> str:
    return ",".join([str(value).strip() for value in values if str(value).strip()])


def normalize_profile(profile: Dict | None) -> Dict:
    """Return a profile with every expected key present."""
    if not profile:
        return DEFAULT_PROFILE.copy()
    cleaned = DEFAULT_PROFILE.copy()
    cleaned.update({k: v for k, v in profile.items() if v is not None})
    for key in ["concerns", "sensitivities", "preferences", "avoid_ingredients"]:
        if isinstance(cleaned.get(key), str):
            cleaned[key] = split_display_tags(cleaned[key])
        elif cleaned.get(key) is None:
            cleaned[key] = []
    return cleaned


def load_products() -> pd.DataFrame:
    products = pd.read_csv(PRODUCTS_PATH, dtype={"barcode": str})
    return products


def load_ingredients() -> pd.DataFrame:
    ingredients = pd.read_csv(INGREDIENTS_PATH)
    ingredients["flags_list"] = ingredients["flags"].apply(split_tags)
    return ingredients


def load_product_ingredients() -> pd.DataFrame:
    return pd.read_csv(PRODUCT_INGREDIENTS_PATH)


def _empty_reactions() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "reaction_id",
            "user_id",
            "product_id",
            "reaction_result",
            "reaction_type",
            "severity",
            "notes",
            "date_added",
        ]
    )


def load_reactions() -> pd.DataFrame:
    if not REACTIONS_PATH.exists() or REACTIONS_PATH.stat().st_size == 0:
        return _empty_reactions()
    reactions = pd.read_csv(REACTIONS_PATH)
    if "product_id" in reactions.columns and not reactions.empty:
        reactions["product_id"] = pd.to_numeric(reactions["product_id"], errors="coerce").fillna(0).astype(int)
    return reactions


def load_user_reactions_local(user_id: str) -> pd.DataFrame:
    reactions = load_reactions()
    if reactions.empty:
        return reactions
    return reactions[reactions["user_id"].astype(str) == str(user_id)].copy()


def save_reaction(reaction: Dict) -> None:
    reactions = load_reactions()
    next_id = 1 if reactions.empty else int(pd.to_numeric(reactions["reaction_id"], errors="coerce").max()) + 1
    reaction["reaction_id"] = next_id
    updated = pd.concat([reactions, pd.DataFrame([reaction])], ignore_index=True)
    updated.to_csv(REACTIONS_PATH, index=False)


def _empty_profiles() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["user_id", "skin_type", "concerns", "sensitivities", "preferences", "avoid_ingredients"]
    )


def load_profiles() -> pd.DataFrame:
    if not PROFILES_PATH.exists() or PROFILES_PATH.stat().st_size == 0:
        return _empty_profiles()
    return pd.read_csv(PROFILES_PATH)


def load_profile_local(user_id: str) -> Dict:
    profiles = load_profiles()
    if profiles.empty:
        return DEFAULT_PROFILE.copy()
    rows = profiles[profiles["user_id"].astype(str) == str(user_id)]
    if rows.empty:
        return DEFAULT_PROFILE.copy()
    row = rows.iloc[-1].to_dict()
    return normalize_profile(
        {
            "skin_type": row.get("skin_type", "Combination"),
            "concerns": split_display_tags(row.get("concerns", "")),
            "sensitivities": split_display_tags(row.get("sensitivities", "")),
            "preferences": split_display_tags(row.get("preferences", "")),
            "avoid_ingredients": split_display_tags(row.get("avoid_ingredients", "")),
        }
    )


def save_profile_local(user_id: str, profile: Dict) -> None:
    profile = normalize_profile(profile)
    profiles = load_profiles()
    profiles = profiles[profiles["user_id"].astype(str) != str(user_id)] if not profiles.empty else _empty_profiles()
    row = {
        "user_id": user_id,
        "skin_type": profile.get("skin_type", "Combination"),
        "concerns": join_tags(profile.get("concerns", [])),
        "sensitivities": join_tags(profile.get("sensitivities", [])),
        "preferences": join_tags(profile.get("preferences", [])),
        "avoid_ingredients": join_tags(profile.get("avoid_ingredients", [])),
    }
    updated = pd.concat([profiles, pd.DataFrame([row])], ignore_index=True)
    updated.to_csv(PROFILES_PATH, index=False)
