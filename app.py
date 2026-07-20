from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from src.data_loader import (
    DEFAULT_PROFILE,
    load_ingredients,
    load_product_ingredients,
    load_products,
    normalize_profile,
)
from src.recommender import (
    best_product_for_category,
    ingredient_risk_breakdown,
    product_ingredient_details,
    recommend_products,
    score_product,
)
from src.storage import load_profile, load_reactions, save_profile, save_user_reaction

APP_NAME = "Wednesday Skinmatch"
LOCAL_DEMO_USER = "demo_user"

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
    .danger {color: #a52828; font-weight: 700;}
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


def show_header() -> None:
    st.markdown(f'<div class="main-title">🌿 {APP_NAME}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Personalised Korean skincare matching based on skin profile, ingredient flags, and reaction history.</div>',
        unsafe_allow_html=True,
    )


def product_label(row: pd.Series) -> str:
    return f"{row['brand']} — {row['name']} ({row['category']})"


def get_supabase_client():
    """Return a Supabase client only when .streamlit/secrets.toml is configured."""
    try:
        url = st.secrets["supabase"]["url"]
        anon_key = st.secrets["supabase"]["anon_key"]
    except Exception:
        return None

    try:
        from supabase import create_client

        return create_client(url, anon_key)
    except Exception as exc:
        st.error(f"Supabase client could not start: {exc}")
        return None


def current_user_id() -> str:
    return st.session_state.get("user_id", LOCAL_DEMO_USER)


def current_storage_mode() -> str:
    return st.session_state.get("storage_mode", "local")


def current_supabase_client():
    return st.session_state.get("supabase_client")


def using_cloud() -> bool:
    return current_storage_mode() == "supabase" and current_supabase_client() is not None


def reset_loaded_profile() -> None:
    st.session_state.pop("profile", None)
    st.session_state.pop("profile_loaded_for", None)


def get_profile() -> dict:
    user_id = current_user_id()
    if st.session_state.get("profile_loaded_for") != user_id:
        try:
            st.session_state.profile = load_profile(user_id, current_supabase_client(), using_cloud())
        except Exception as exc:
            st.warning(f"Could not load cloud profile, using default profile instead. Error: {exc}")
            st.session_state.profile = DEFAULT_PROFILE.copy()
        st.session_state.profile_loaded_for = user_id
    return normalize_profile(st.session_state.profile)


def persist_profile(profile: dict) -> None:
    save_profile(current_user_id(), profile, current_supabase_client(), using_cloud())
    st.session_state.profile = normalize_profile(profile)
    st.session_state.profile_loaded_for = current_user_id()


def get_reactions_for_current_user() -> pd.DataFrame:
    try:
        return load_reactions(current_user_id(), current_supabase_client(), using_cloud())
    except Exception as exc:
        st.warning(f"Could not load cloud reactions. Error: {exc}")
        return pd.DataFrame(
            columns=["reaction_id", "user_id", "product_id", "reaction_result", "reaction_type", "severity", "notes", "date_added"]
        )


def login_page() -> None:
    show_header()
    st.subheader("Login / Storage Mode")
    st.write(
        "Use **local demo login** while coding in VSCode. Use **Supabase login** later when you want cloud database storage."
    )

    tab1, tab2 = st.tabs(["Local demo login", "Supabase cloud login"])

    with tab1:
        st.write("This mode saves profile and reaction data into CSV files inside the `data/` folder.")
        display_name = st.text_input("Demo username", value="demo_user", help="Use letters/numbers only for a cleaner CSV user id.")
        if st.button("Use local demo account", type="primary"):
            cleaned = "".join(ch if ch.isalnum() or ch in ["_", "-"] else "_" for ch in display_name.strip())
            st.session_state.user_id = cleaned or LOCAL_DEMO_USER
            st.session_state.user_email = "local demo account"
            st.session_state.storage_mode = "local"
            st.session_state.supabase_client = None
            reset_loaded_profile()
            st.success("Local demo account selected.")
            st.rerun()

    with tab2:
        supabase = get_supabase_client()
        if supabase is None:
            st.warning(
                "Supabase is not configured yet. Add `.streamlit/secrets.toml` by following `docs/SUPABASE_SETUP.md`."
            )
        else:
            mode = st.radio("Action", ["Sign in", "Create account"], horizontal=True)
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button(mode, type="primary"):
                if not email or not password:
                    st.error("Enter both email and password.")
                else:
                    try:
                        if mode == "Create account":
                            auth_response = supabase.auth.sign_up({"email": email, "password": password})
                            st.info("Account created. If email confirmation is enabled in Supabase, confirm your email before signing in.")
                        else:
                            auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})

                        user = auth_response.user
                        if user:
                            st.session_state.user_id = user.id
                            st.session_state.user_email = user.email
                            st.session_state.storage_mode = "supabase"
                            st.session_state.supabase_client = supabase
                            reset_loaded_profile()
                            st.success("Signed in with Supabase cloud storage.")
                            st.rerun()
                    except Exception as exc:
                        st.error(f"Supabase login failed: {exc}")


def show_account_box() -> None:
    st.sidebar.markdown("---")
    st.sidebar.caption(f"User: {st.session_state.get('user_email', 'local demo account')}")
    st.sidebar.caption(f"Storage: {current_storage_mode()}")
    if st.sidebar.button("Log out / switch account"):
        st.session_state.clear()
        st.rerun()


def show_score(product: pd.Series, profile: dict, reactions: pd.DataFrame, products_df: pd.DataFrame) -> None:
    ingredients_df = cached_ingredients()
    product_ingredients_df = cached_product_ingredients()
    result = score_product(product, profile, reactions, product_ingredients_df, ingredients_df, current_user_id())

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

    with st.expander("Ingredient risk explanation", expanded=True):
        risk_breakdown = result["risk_breakdown"]
        if risk_breakdown.empty:
            st.info("No ingredient risk data stored for this product yet.")
        else:
            st.dataframe(
                risk_breakdown[["ingredient_order", "ingredient", "risk_level", "score_impact", "reasons"]],
                use_container_width=True,
                hide_index=True,
            )

    with st.expander("Raw ingredient details"):
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

    st.subheader("What this version includes")
    st.write(
        "Wednesday Skinmatch now includes product comparison, routine building, ingredient risk explanations, and optional Supabase login/cloud storage."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", len(cached_products()))
    c2.metric("Ingredient links", len(cached_product_ingredients()))
    c3.metric("Your reactions", len(get_reactions_for_current_user()))
    c4.metric("Storage", current_storage_mode().title())

    st.subheader("Recommended demo flow")
    st.write("1. Open **Login** and choose local demo or Supabase cloud login.")
    st.write("2. Open **Skin Profile** and save concerns, sensitivities, and avoid ingredients.")
    st.write("3. Open **Product Search** or **Ingredient Risk** to view personalised score explanations.")
    st.write("4. Open **Product Comparison** to compare 2 products side-by-side.")
    st.write("5. Open **Routine Builder** to get a morning/night Korean skincare routine.")
    st.write("6. Open **Reaction Logger** to record good/bad reactions and improve future recommendations.")


def skin_profile_page() -> None:
    show_header()
    st.subheader("Skin Profile")
    profile = get_profile()

    skin_type_options = ["Dry", "Oily", "Combination", "Normal", "Sensitive", "Dehydrated", "Not sure"]
    current_skin_type = profile.get("skin_type", "Combination")
    if current_skin_type not in skin_type_options:
        current_skin_type = "Combination"

    skin_type = st.selectbox("Skin type", skin_type_options, index=skin_type_options.index(current_skin_type))

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
        persist_profile(
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
    reactions = get_reactions_for_current_user()
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

    labels = [product_label(row) for _, row in filtered.iterrows()]
    selected_label = st.selectbox("Choose a product", labels)
    selected_index = labels.index(selected_label)
    product = filtered.iloc[selected_index]

    st.markdown(f"### {product['brand']} — {product['name']}")
    st.write(f"**Barcode:** `{product['barcode']}`")
    show_score(product, profile, reactions, products)


def ingredient_risk_page() -> None:
    show_header()
    st.subheader("Ingredient Risk Explanation")
    st.write("This page shows exactly which ingredients changed the personalised score.")

    products = cached_products()
    ingredients = cached_ingredients()
    product_ingredients = cached_product_ingredients()
    reactions = get_reactions_for_current_user()
    profile = get_profile()

    labels = [product_label(row) for _, row in products.iterrows()]
    selected_label = st.selectbox("Choose a product", labels)
    product = products.iloc[labels.index(selected_label)]

    result = score_product(product, profile, reactions, product_ingredients, ingredients, current_user_id())
    c1, c2, c3 = st.columns(3)
    c1.metric("Match score", f"{result['score']}/100")
    c2.metric("High cautions", len(result["risk_breakdown"][result["risk_breakdown"]["risk_level"] == "High caution"]))
    c3.metric("Helpful ingredients", len(result["risk_breakdown"][result["risk_breakdown"]["risk_level"] == "Helpful"]))

    st.markdown("### Score explanation")
    for item in result["positives"]:
        st.write("✅ " + item)
    for item in result["cautions"]:
        st.write("⚠️ " + item)

    st.markdown("### Ingredient-by-ingredient breakdown")
    st.dataframe(
        result["risk_breakdown"][["ingredient_order", "ingredient", "flags", "risk_level", "score_impact", "reasons"]],
        use_container_width=True,
        hide_index=True,
    )


def product_comparison_page() -> None:
    show_header()
    st.subheader("Product Comparison")
    st.write("Compare two Korean skincare products using your current skin profile and reaction history.")

    products = cached_products()
    ingredients = cached_ingredients()
    product_ingredients = cached_product_ingredients()
    reactions = get_reactions_for_current_user()
    profile = get_profile()

    labels = [product_label(row) for _, row in products.iterrows()]
    col_a, col_b = st.columns(2)
    label_a = col_a.selectbox("Product A", labels, index=0)
    label_b = col_b.selectbox("Product B", labels, index=1 if len(labels) > 1 else 0)

    product_a = products.iloc[labels.index(label_a)]
    product_b = products.iloc[labels.index(label_b)]
    score_a = score_product(product_a, profile, reactions, product_ingredients, ingredients, current_user_id())
    score_b = score_product(product_b, profile, reactions, product_ingredients, ingredients, current_user_id())

    a, b = st.columns(2)
    with a:
        st.markdown(f"### A: {product_a['brand']} — {product_a['name']}")
        st.metric("Match score", f"{score_a['score']}/100")
        st.write(f"**Category:** {product_a['category']}")
        st.write(f"**Texture:** {product_a['texture']}")
        st.write(f"**Fragrance-free:** {product_a['fragrance_free']}")
        st.write(f"**Alcohol-free:** {product_a['alcohol_free']}")
        st.markdown("**Top cautions**")
        for item in score_a["cautions"][:3]:
            st.write("⚠️ " + item)
    with b:
        st.markdown(f"### B: {product_b['brand']} — {product_b['name']}")
        st.metric("Match score", f"{score_b['score']}/100")
        st.write(f"**Category:** {product_b['category']}")
        st.write(f"**Texture:** {product_b['texture']}")
        st.write(f"**Fragrance-free:** {product_b['fragrance_free']}")
        st.write(f"**Alcohol-free:** {product_b['alcohol_free']}")
        st.markdown("**Top cautions**")
        for item in score_b["cautions"][:3]:
            st.write("⚠️ " + item)

    if score_a["score"] > score_b["score"]:
        st.success(f"Based on your current profile, Product A looks like the better match by {score_a['score'] - score_b['score']} points.")
    elif score_b["score"] > score_a["score"]:
        st.success(f"Based on your current profile, Product B looks like the better match by {score_b['score'] - score_a['score']} points.")
    else:
        st.info("Both products have the same score. Check the ingredient risk tables below to choose.")

    ingredients_a = set(score_a["ingredient_details"]["ingredient_name"].dropna().tolist())
    ingredients_b = set(score_b["ingredient_details"]["ingredient_name"].dropna().tolist())
    shared = sorted(ingredients_a.intersection(ingredients_b))
    unique_a = sorted(ingredients_a - ingredients_b)
    unique_b = sorted(ingredients_b - ingredients_a)

    st.markdown("### Ingredient overlap")
    c1, c2, c3 = st.columns(3)
    c1.metric("Shared ingredients", len(shared))
    c2.metric("Only in A", len(unique_a))
    c3.metric("Only in B", len(unique_b))
    with st.expander("Show ingredient overlap"):
        st.write("**Shared:** " + (", ".join(shared) if shared else "None"))
        st.write("**Only in A:** " + (", ".join(unique_a) if unique_a else "None"))
        st.write("**Only in B:** " + (", ".join(unique_b) if unique_b else "None"))

    st.markdown("### Risk tables")
    tab_a, tab_b = st.tabs(["Product A risk", "Product B risk"])
    with tab_a:
        st.dataframe(
            score_a["risk_breakdown"][["ingredient_order", "ingredient", "risk_level", "score_impact", "reasons"]],
            use_container_width=True,
            hide_index=True,
        )
    with tab_b:
        st.dataframe(
            score_b["risk_breakdown"][["ingredient_order", "ingredient", "risk_level", "score_impact", "reasons"]],
            use_container_width=True,
            hide_index=True,
        )


def routine_builder_page() -> None:
    show_header()
    st.subheader("Routine Builder")
    st.write("Build a simple routine using the highest-scoring products for your profile.")

    products = cached_products()
    ingredients = cached_ingredients()
    product_ingredients = cached_product_ingredients()
    reactions = get_reactions_for_current_user()
    profile = get_profile()

    routine_type = st.radio("Routine type", ["Minimal", "Balanced", "Full"], horizontal=True)

    if routine_type == "Minimal":
        morning_steps = [
            ("Cleanser", ["Cleanser"]),
            ("Moisturiser", ["Moisturiser"]),
            ("Sunscreen", ["Sunscreen"]),
        ]
        night_steps = [
            ("Cleanser", ["Cleanser", "Oil Cleanser"]),
            ("Treatment/Serum", ["Serum", "Essence", "Ampoule", "Treatment"]),
            ("Moisturiser", ["Moisturiser"]),
        ]
    elif routine_type == "Balanced":
        morning_steps = [
            ("Cleanser", ["Cleanser"]),
            ("Toner", ["Toner", "Toner Pad"]),
            ("Serum/Essence", ["Serum", "Essence", "Ampoule"]),
            ("Moisturiser", ["Moisturiser"]),
            ("Sunscreen", ["Sunscreen"]),
        ]
        night_steps = [
            ("Oil cleanser", ["Oil Cleanser"]),
            ("Cleanser", ["Cleanser"]),
            ("Toner", ["Toner", "Toner Pad"]),
            ("Serum/Essence", ["Serum", "Essence", "Ampoule"]),
            ("Moisturiser", ["Moisturiser"]),
        ]
    else:
        morning_steps = [
            ("Cleanser", ["Cleanser"]),
            ("Toner", ["Toner", "Toner Pad"]),
            ("Serum", ["Serum", "Essence", "Ampoule"]),
            ("Moisturiser", ["Moisturiser"]),
            ("Sunscreen", ["Sunscreen"]),
        ]
        night_steps = [
            ("Oil cleanser", ["Oil Cleanser"]),
            ("Cleanser", ["Cleanser"]),
            ("Toner", ["Toner", "Toner Pad"]),
            ("Treatment", ["Treatment", "Exfoliant"]),
            ("Serum/Essence", ["Serum", "Essence", "Ampoule"]),
            ("Moisturiser", ["Moisturiser", "Mask"]),
        ]

    def render_routine(title: str, steps: List[tuple]) -> None:
        st.markdown(f"### {title}")
        for step_name, categories in steps:
            best = best_product_for_category(categories, products, profile, reactions, product_ingredients, ingredients, current_user_id())
            if not best:
                st.write(f"**{step_name}:** No matching product in demo dataset yet.")
                continue
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{step_name}:** {best['brand']} — {best['name']}")
                c1.caption(f"{best['category']} • {best['texture']} • {best['why']}")
                c2.metric("Score", f"{best['match_score']}/100")
                if best.get("watch_out"):
                    st.caption("Watch out: " + best["watch_out"])

    col1, col2 = st.columns(2)
    with col1:
        render_routine("Morning routine", morning_steps)
    with col2:
        render_routine("Night routine", night_steps)

    st.info(
        "Routine builder is a recommendation helper only. Introduce new products slowly instead of starting many new products on the same day."
    )


def reaction_logger_page() -> None:
    show_header()
    st.subheader("Reaction Logger")
    products = cached_products()

    labels = [product_label(row) for _, row in products.iterrows()]
    selected_label = st.selectbox("Product you used", labels)
    product = products.iloc[labels.index(selected_label)]

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
        try:
            save_user_reaction(
                current_user_id(),
                int(product["product_id"]),
                reaction_result,
                reaction_type,
                int(severity),
                notes,
                current_supabase_client(),
                using_cloud(),
            )
            st.success("Reaction saved. Go to Recommendations to see how this changes your matches.")
        except Exception as exc:
            st.error(f"Could not save reaction: {exc}")

    st.subheader("Saved reactions")
    reactions = get_reactions_for_current_user()
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
    reactions = get_reactions_for_current_user()
    profile = get_profile()

    recommended = recommend_products(products, profile, reactions, product_ingredients, ingredients, current_user_id())

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
    if "user_id" not in st.session_state:
        st.session_state.user_id = LOCAL_DEMO_USER
        st.session_state.user_email = "local demo account"
        st.session_state.storage_mode = "local"
        st.session_state.supabase_client = None

    st.sidebar.title(APP_NAME)
    page = st.sidebar.radio(
        "Navigation",
        [
            "Login",
            "Home",
            "Skin Profile",
            "Product Search",
            "Ingredient Risk",
            "Product Comparison",
            "Routine Builder",
            "Reaction Logger",
            "Recommendations",
            "Data Explorer",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Demo prototype for a Korean skincare recommender portfolio project.")
    show_account_box()

    if page == "Login":
        login_page()
    elif page == "Home":
        home_page()
    elif page == "Skin Profile":
        skin_profile_page()
    elif page == "Product Search":
        product_search_page()
    elif page == "Ingredient Risk":
        ingredient_risk_page()
    elif page == "Product Comparison":
        product_comparison_page()
    elif page == "Routine Builder":
        routine_builder_page()
    elif page == "Reaction Logger":
        reaction_logger_page()
    elif page == "Recommendations":
        recommendations_page()
    elif page == "Data Explorer":
        data_explorer_page()


if __name__ == "__main__":
    main()
