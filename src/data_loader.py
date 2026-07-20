from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
PRODUCTS_PATH = DATA_DIR / "products.csv"
INGREDIENTS_PATH = DATA_DIR / "ingredients.csv"
PRODUCT_INGREDIENTS_PATH = DATA_DIR / "product_ingredients.csv"
REACTIONS_PATH = DATA_DIR / "user_reactions.csv"


def split_tags(value: str) -> List[str]:
    """Convert a comma-separated CSV tag value into a clean lowercase list."""
    if pd.isna(value) or value == "":
        return []
    return [tag.strip().lower() for tag in str(value).split(",") if tag.strip()]


def load_products() -> pd.DataFrame:
    products = pd.read_csv(PRODUCTS_PATH, dtype={"barcode": str})
    return products


def load_ingredients() -> pd.DataFrame:
    ingredients = pd.read_csv(INGREDIENTS_PATH)
    ingredients["flags_list"] = ingredients["flags"].apply(split_tags)
    return ingredients


def load_product_ingredients() -> pd.DataFrame:
    return pd.read_csv(PRODUCT_INGREDIENTS_PATH)


def load_reactions() -> pd.DataFrame:
    if not REACTIONS_PATH.exists() or REACTIONS_PATH.stat().st_size == 0:
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
    return pd.read_csv(REACTIONS_PATH)


def save_reaction(reaction: Dict) -> None:
    reactions = load_reactions()
    next_id = 1 if reactions.empty else int(reactions["reaction_id"].max()) + 1
    reaction["reaction_id"] = next_id
    updated = pd.concat([reactions, pd.DataFrame([reaction])], ignore_index=True)
    updated.to_csv(REACTIONS_PATH, index=False)
