from __future__ import annotations

from datetime import date
from typing import Dict

import pandas as pd

from src.data_loader import (
    DEFAULT_PROFILE,
    load_profile_local,
    load_user_reactions_local,
    normalize_profile,
    save_profile_local,
    save_reaction,
)


REACTION_COLUMNS = [
    "reaction_id",
    "user_id",
    "product_id",
    "reaction_result",
    "reaction_type",
    "severity",
    "notes",
    "date_added",
]


def empty_reactions() -> pd.DataFrame:
    return pd.DataFrame(columns=REACTION_COLUMNS)


def cloud_available(client: object | None, use_cloud: bool = False) -> bool:
    return client is not None and use_cloud is True


def load_profile(
    user_id: str,
    client: object | None = None,
    use_cloud: bool = False,
) -> Dict:
    if cloud_available(client, use_cloud):
        response = (
            client.table("skin_profiles")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if rows:
            row = rows[0]
            return normalize_profile(
                {
                    "skin_type": row.get("skin_type"),
                    "concerns": row.get("concerns") or [],
                    "sensitivities": row.get("sensitivities") or [],
                    "preferences": row.get("preferences") or [],
                    "avoid_ingredients": row.get("avoid_ingredients") or [],
                }
            )

        return DEFAULT_PROFILE.copy()

    return load_profile_local(user_id)


def save_profile(
    user_id: str,
    profile: Dict,
    client: object | None = None,
    use_cloud: bool = False,
) -> None:
    profile = normalize_profile(profile)

    if cloud_available(client, use_cloud):
        row = {
            "user_id": user_id,
            "skin_type": profile.get("skin_type"),
            "concerns": profile.get("concerns", []),
            "sensitivities": profile.get("sensitivities", []),
            "preferences": profile.get("preferences", []),
            "avoid_ingredients": profile.get("avoid_ingredients", []),
        }

        client.table("skin_profiles").upsert(
            row,
            on_conflict="user_id",
        ).execute()

        return

    save_profile_local(user_id, profile)


def load_reactions(
    user_id: str,
    client: object | None = None,
    use_cloud: bool = False,
) -> pd.DataFrame:
    if cloud_available(client, use_cloud):
        response = (
            client.table("user_reactions")
            .select(
                "reaction_id,user_id,product_id,reaction_result,"
                "reaction_type,severity,notes,date_added"
            )
            .eq("user_id", user_id)
            .order("date_added", desc=True)
            .execute()
        )

        rows = response.data or []

        if not rows:
            return empty_reactions()

        df = pd.DataFrame(rows)

        df["product_id"] = (
            pd.to_numeric(df["product_id"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        return df

    return load_user_reactions_local(user_id)


def save_user_reaction(
    user_id: str,
    product_id: int,
    reaction_result: str,
    reaction_type: str,
    severity: int,
    notes: str,
    client: object | None = None,
    use_cloud: bool = False,
) -> None:
    reaction = {
        "user_id": user_id,
        "product_id": int(product_id),
        "reaction_result": reaction_result,
        "reaction_type": reaction_type,
        "severity": int(severity),
        "notes": notes,
        "date_added": str(date.today()),
    }

    if cloud_available(client, use_cloud):
        client.table("user_reactions").insert(reaction).execute()
        return

    save_reaction(reaction)