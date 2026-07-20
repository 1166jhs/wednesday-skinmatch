from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_loader import (
    load_ingredients,
    load_product_ingredients,
    load_products,
    load_reactions,
    save_reaction,
)
from src.recommender import product_ingredient_details, recommend_products, score_product

APP_NAME = "Wednesday Skinmatch"
USER_ID = "demo_user"

st.set_page_config(page_title=APP_NAME, page_icon="🌿", layout="wide")

st.markdown(
    """
    <style>
    .main-title {font-size: 2.4rem; font-weight: 800; margin-bottom: 0.25rem;}
    .subtitle {font-size: 1.05rem; color: #666; margin-bottom: 1.25rem;}
    .small-note {font-size: 0.85rem; color: #777;}
    .score-card {padding: 1rem; border-radius: 14px; border: 1px solid #e6e6e6; margin-bottom: 1rem;}
    .good {color: #176b45; font-weight: 700;}
    .warn {color: #9a5b00; font-weight: 700;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def cached_products() -> pd.DataFrame:
    return load_products()


@st.cache_data
def cached_ingredients() -> pd.DataFrame:
    return load_ingredients()


@st.cache_data
def cached_product_ingredients() -> pd.DataFrame:
    return load_product_ingredients()


def get_profile() -> dict:
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "skin_type": "Combination",
            "concerns": ["acne", "texture"],
            "sensitivities": ["Fragrance-sensitive"],
            "preferences": ["Fragrance-free", "Alcohol-free"],
            "avoid_ingredients": [],
        }
    return st.session_state.profile


def save_profile(profile: dict) -> None:
    st.session_state.profile = profile


def show_header() -> None:
    st.markdown(f'<div class="main-title">🌿 {APP_NAME}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Personalised Korean skincare matching based on skin profile, ingredient flags, and reaction history.</div>',
        unsafe_allow_html=True,
    )


def product_label(row: pd.Series) -> str:
    return f"{row['brand']} — {row['name']} ({row['category']})"


def show_score(product: pd.Series, profile: dict, reactions: pd.DataFrame, products_df: pd.DataFrame) -> None:
    ingredients_df = cached_ingredients()
    product_ingredients_df = cached_product_ingredients()
    result = score_product(product, profile, reactions, product_ingredients_df, ingredients_df, USER_ID)

    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("Match score", f"{result['score']}/100")
    c2.metric("Price tier", str(product["price_tier"]).title())
    c3.write(f"**Texture:** {product['texture']}")
    c3.write(f"**Notes:** {product['notes']}")

    st.markdown("**Why it may suit you**")
    for item in result["positives"]:
        st.write("✅ " + item)

    st.markdown("**Things to watch**")
    for item in result["cautions"]:
        st.write("⚠️ " + item)

    with st.expander("Ingredient details"):
        details = result["ingredient_details"]
        if details.empty:
            st.info("No ingredients stored for this product yet.")
        else:
            st.dataframe(
                details[["ingredient_order", "ingredient_name", "ingredient_category", "flags", "possible_concerns"]],
                use_container_width=True,
                hide_index=True,
            )


def home_page() -> None:
    show_header()
    st.info(
        "This is a portfolio prototype. Product and ingredient records are simplified demo data, not medical advice. Always patch test and check official product labels."
    )

    st.subheader("What this app does")
    st.write(
        "Wednesday Skinmatch recommends Korean skincare products by comparing a user's skin profile, sensitivities, ingredient flags, and logged good/bad reactions."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Products in demo database", len(cached_products()))
    c2.metric("Ingredient links", len(cached_product_ingredients()))
    c3.metric("Logged reactions", len(load_reactions()))

    st.subheader("Recommended demo flow")
    st.write("1. Open **Skin Profile** and save your skin type, concerns, sensitivities, and avoid ingredients.")
    st.write("2. Open **Product Search** to search by name or barcode and see the match score.")
    st.write("3. Open **Reaction Logger** to record good or bad reactions.")
    st.write("4. Open **Recommendations** to get ranked product suggestions.")


def skin_profile_page() -> None:
    show_header()
    st.subheader("Skin Profile")
    profile = get_profile()

    skin_type = st.selectbox(
        "Skin type",
        ["Dry", "Oily", "Combination", "Normal", "Sensitive", "Dehydrated", "Not sure"],
        index=["Dry", "Oily", "Combination", "Normal", "Sensitive", "Dehydrated", "Not sure"].index(profile.get("skin_type", "Combination")),
    )

    concern_options = [
        "acne",
        "closed comedones",
        "blackheads",
        "whiteheads",
        "pores",
        "redness",
        "texture",
        "barrier",
        "hydration",
        "dryness",
        "hyperpigmentation",
        "acne_marks",
        "acne_scars",
        "dullness",
        "eczema_prone",
        "sun_protection",
    ]
    concerns = st.multiselect("Skin concerns", concern_options, default=profile.get("concerns", []))

    sensitivity_options = [
        "Fragrance-sensitive",
        "Essential oil-sensitive",
        "Alcohol-sensitive",
        "Niacinamide-sensitive",
        "Vitamin C-sensitive",
        "Retinoid-sensitive",
        "AHA/BHA/PHA-sensitive",
        "Shea butter-sensitive",
        "Sunscreen stings my eyes",
    ]
    sensitivities = st.multiselect("Sensitivities / reactions", sensitivity_options, default=profile.get("sensitivities", []))

    preference_options = [
        "Fragrance-free",
        "Alcohol-free",
        "Essential-oil-free",
        "Budget-friendly",
        "Korean brands only",
    ]
    preferences = st.multiselect("Preferences", preference_options, default=profile.get("preferences", []))

    avoid_text = st.text_input(
        "Ingredients you want to avoid, separated by commas",
        value=", ".join(profile.get("avoid_ingredients", [])),
        placeholder="Example: Fragrance, Limonene, Shea Butter",
    )

    if st.button("Save skin profile", type="primary"):
        avoid_ingredients = [item.strip() for item in avoid_text.split(",") if item.strip()]
        save_profile(
            {
                "skin_type": skin_type,
                "concerns": concerns,
                "sensitivities": sensitivities,
                "preferences": preferences,
                "avoid_ingredients": avoid_ingredients,
            }
        )
        st.success("Skin profile saved.")

    with st.expander("Current profile JSON"):
        st.json(get_profile())


def product_search_page() -> None:
    show_header()
    st.subheader("Product Search / Barcode Lookup")

    products = cached_products()
    reactions = load_reactions()
    profile = get_profile()

    search = st.text_input("Search by product name, brand, category, or barcode", placeholder="Example: Anua, sunscreen, 8801000000011")
    category_filter = st.selectbox("Category filter", ["All"] + sorted(products["category"].unique().tolist()))

    filtered = products.copy()
    if category_filter != "All":
        filtered = filtered[filtered["category"] == category_filter]
    if search:
        search_lower = search.lower().strip()
        filtered = filtered[
            filtered.apply(
                lambda row: search_lower in str(row["name"]).lower()
                or search_lower in str(row["brand"]).lower()
                or search_lower in str(row["category"]).lower()
                or search_lower in str(row["barcode"]).lower(),
                axis=1,
            )
        ]

    st.write(f"Showing {len(filtered)} product(s).")

    if filtered.empty:
        st.warning("No product found. Try a brand name, category, or sample barcode.")
        return

    selected_label = st.selectbox("Choose a product", [product_label(row) for _, row in filtered.iterrows()])
    selected_index = [product_label(row) for _, row in filtered.iterrows()].index(selected_label)
    product = filtered.iloc[selected_index]

    st.markdown(f"### {product['brand']} — {product['name']}")
    st.write(f"**Barcode:** `{product['barcode']}`")
    show_score(product, profile, reactions, products)


def reaction_logger_page() -> None:
    show_header()
    st.subheader("Reaction Logger")
    products = cached_products()

    selected_label = st.selectbox("Product you used", [product_label(row) for _, row in products.iterrows()])
    selected_index = [product_label(row) for _, row in products.iterrows()].index(selected_label)
    product = products.iloc[selected_index]

    c1, c2, c3 = st.columns(3)
    reaction_result = c1.selectbox("Reaction result", ["Good", "Neutral", "Bad"])
    reaction_type = c2.selectbox(
        "Reaction type",
        [
            "No issue",
            "Hydrating",
            "Calming",
            "Redness",
            "Burning",
            "Itching",
            "Dryness",
            "Peeling",
            "Closed comedones",
            "Acne flare",
            "Eye stinging",
            "Swelling",
            "Other",
        ],
    )
    severity = c3.slider("Severity", 1, 5, 3)
    notes = st.text_area("Notes", placeholder="Example: Used for 3 days. Skin felt itchy around cheeks.")

    if st.button("Save reaction", type="primary"):
        save_reaction(
            {
                "user_id": USER_ID,
                "product_id": int(product["product_id"]),
                "reaction_result": reaction_result,
                "reaction_type": reaction_type,
                "severity": int(severity),
                "notes": notes,
                "date_added": str(date.today()),
            }
        )
        st.success("Reaction saved. Go to Recommendations to see how this changes your matches.")

    st.subheader("Saved reactions")
    reactions = load_reactions()
    if reactions.empty:
        st.info("No reactions saved yet.")
    else:
        display = reactions.merge(products[["product_id", "brand", "name"]], on="product_id", how="left")
        st.dataframe(
            display[["date_added", "brand", "name", "reaction_result", "reaction_type", "severity", "notes"]],
            use_container_width=True,
            hide_index=True,
        )


def recommendations_page() -> None:
    show_header()
    st.subheader("Personalised Recommendations")

    products = cached_products()
    ingredients = cached_ingredients()
    product_ingredients = cached_product_ingredients()
    reactions = load_reactions()
    profile = get_profile()

    recommended = recommend_products(products, profile, reactions, product_ingredients, ingredients, USER_ID)

    if recommended.empty:
        st.info("No recommendations yet. Add more products or clear existing reaction history.")
        return

    top_n = st.slider("How many recommendations to show?", 3, 15, 5)
    st.write("Products already logged in your reaction history are hidden from this recommendation list.")

    for _, row in recommended.head(top_n).iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"### {row['brand']} — {row['name']}")
            c1.write(f"**Category:** {row['category']} | **Texture:** {row['texture']} | **Price:** {row['price_tier']}")
            c2.metric("Score", f"{row['match_score']}/100")
            st.markdown("<span class='good'>Why:</span> " + row["why"], unsafe_allow_html=True)
            st.markdown("<span class='warn'>Watch out:</span> " + row["watch_out"], unsafe_allow_html=True)

    with st.expander("Full recommendation table"):
        st.dataframe(
            recommended[["brand", "name", "category", "texture", "price_tier", "match_score", "why", "watch_out"]],
            use_container_width=True,
            hide_index=True,
        )


def data_explorer_page() -> None:
    show_header()
    st.subheader("Demo Data Explorer")
    products = cached_products()
    ingredients = cached_ingredients()
    product_ingredients = cached_product_ingredients()

    tab1, tab2, tab3 = st.tabs(["Products", "Ingredients", "Product ingredients"])
    with tab1:
        st.dataframe(products, use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(ingredients.drop(columns=["flags_list"], errors="ignore"), use_container_width=True, hide_index=True)
    with tab3:
        st.dataframe(product_ingredients, use_container_width=True, hide_index=True)


def main() -> None:
    st.sidebar.title(APP_NAME)
    page = st.sidebar.radio(
        "Navigation",
        ["Home", "Skin Profile", "Product Search", "Reaction Logger", "Recommendations", "Data Explorer"],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Demo prototype for a Korean skincare recommender portfolio project.")

    if page == "Home":
        home_page()
    elif page == "Skin Profile":
        skin_profile_page()
    elif page == "Product Search":
        product_search_page()
    elif page == "Reaction Logger":
        reaction_logger_page()
    elif page == "Recommendations":
        recommendations_page()
    elif page == "Data Explorer":
        data_explorer_page()


if __name__ == "__main__":
    main()
