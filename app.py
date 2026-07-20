import html
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
    recommend_products,
    score_product,
)
from src.storage import load_profile, load_reactions, save_profile, save_user_reaction

try:
    from supabase import create_client
except ImportError:
    create_client = None


APP_NAME = "Wednesday Skinmatch"
LOCAL_DEMO_USER = "demo_user"


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌸",
    layout="wide",
)


def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #fff7f9 0%, #ffffff 45%);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1120px;
        }

        .app-title {
            font-size: 2.45rem;
            font-weight: 800;
            color: #2f2f2f;
            margin-bottom: 0.2rem;
            letter-spacing: -0.04em;
        }

        .subtitle {
            font-size: 1rem;
            color: #5f5f5f;
            margin-bottom: 1.5rem;
            max-width: 780px;
            line-height: 1.6;
        }

        .skin-card {
            background: #ffffff;
            border: 1.5px solid #efd2dc;
            border-radius: 20px;
            padding: 1.2rem 1.3rem;
            box-shadow: 0 8px 24px rgba(217, 108, 140, 0.08);
            margin-bottom: 1rem;
        }

        .skin-card h3 {
            margin-top: 0;
            margin-bottom: 0.4rem;
            color: #2f2f2f;
            font-size: 1.05rem;
        }

        .muted-text {
            color: #666666;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .product-title {
            font-size: 1.35rem;
            font-weight: 750;
            color: #2f2f2f;
            margin-bottom: 0.25rem;
        }

        .product-subtitle {
            color: #666666;
            font-size: 0.92rem;
            margin-bottom: 0.9rem;
        }

        .badge {
            display: inline-block;
            padding: 0.38rem 0.68rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            margin: 0.18rem 0.2rem 0.18rem 0;
            line-height: 1.4;
            white-space: normal;
        }

        .badge-good {
            background: #ecfdf3;
            color: #157347;
            border: 1px solid #b7ebca;
        }

        .badge-watch {
            background: #fff8e7;
            color: #946200;
            border: 1px solid #f4d58d;
        }

        .badge-risk {
            background: #fff0f3;
            color: #b4233c;
            border: 1px solid #ffc2cd;
        }

        .badge-neutral {
            background: #f3f4f6;
            color: #555555;
            border: 1px solid #dcdfe5;
        }

        .score-box {
            background: #ffffff;
            border: 1.5px solid #eeb9c8;
            border-radius: 18px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 8px 20px rgba(217, 108, 140, 0.08);
            margin-bottom: 1rem;
        }

        .score-number {
            font-size: 2.2rem;
            font-weight: 800;
            color: #d96c8c;
            line-height: 1;
        }

        .score-label {
            color: #666666;
            font-size: 0.85rem;
            margin-top: 0.35rem;
        }

        /* Buttons */
        div.stButton > button {
            border-radius: 999px;
            border: 1px solid #d96c8c;
            background: #d96c8c;
            color: white;
            font-weight: 700;
            padding: 0.55rem 1.1rem;
            transition: 0.15s ease-in-out;
        }

        div.stButton > button:hover {
            background: #c95d7d;
            border-color: #c95d7d;
            color: white;
            transform: translateY(-1px);
        }

        /* Make input boxes easier to see */
        .stTextInput input,
        .stTextArea textarea {
            background-color: #ffffff !important;
            border: 1.8px solid #dca7b8 !important;
            border-radius: 14px !important;
            color: #2f2f2f !important;
            box-shadow: 0 3px 10px rgba(217, 108, 140, 0.08);
        }

        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border: 2px solid #d96c8c !important;
            box-shadow: 0 0 0 3px rgba(217, 108, 140, 0.15) !important;
        }

        .stTextArea textarea {
            min-height: 120px !important;
        }

        /* Make dropdowns and multiselect boxes more visible */
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            border: 1.8px solid #dca7b8 !important;
            border-radius: 14px !important;
            min-height: 48px !important;
            box-shadow: 0 3px 10px rgba(217, 108, 140, 0.08);
        }

        div[data-baseweb="select"] > div:hover {
            border-color: #d96c8c !important;
        }

        div[data-baseweb="select"] span {
            color: #2f2f2f !important;
        }

        div[data-baseweb="tag"] {
            background-color: #d96c8c !important;
            color: white !important;
            border-radius: 10px !important;
            max-width: 100% !important;
            font-weight: 650 !important;
        }

        div[data-baseweb="tag"] span {
            color: white !important;
            max-width: 100% !important;
        }

        label, .stMarkdown, .stRadio, .stSelectbox, .stMultiSelect, .stTextInput, .stTextArea {
            color: #2f2f2f !important;
        }

        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #efd2dc;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #eee;
        }

        div[data-testid="stAlert"] {
            border-radius: 16px;
        }

        @media only screen and (max-width: 768px) {
            .app-title {
                font-size: 2rem;
            }

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .skin-card {
                padding: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_css()


@st.cache_data
def get_products() -> pd.DataFrame:
    return load_products()


@st.cache_data
def get_ingredients() -> pd.DataFrame:
    return load_ingredients()


@st.cache_data
def get_product_ingredients() -> pd.DataFrame:
    return load_product_ingredients()


def get_supabase_client():
    if create_client is None:
        return None

    try:
        url = st.secrets["supabase"]["url"]
        anon_key = st.secrets["supabase"]["anon_key"]

        if not url or not anon_key:
            return None

        if "YOUR-" in url or "YOUR-" in anon_key:
            return None

        return create_client(url, anon_key)
    except Exception:
        return None


def init_session_state():
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = get_supabase_client()

    if "user_id" not in st.session_state:
        st.session_state.user_id = LOCAL_DEMO_USER

    if "user_email" not in st.session_state:
        st.session_state.user_email = "Local demo user"

    if "use_cloud" not in st.session_state:
        st.session_state.use_cloud = False

    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    if "access_token" not in st.session_state:
        st.session_state.access_token = None

    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = None

    cloud_client = st.session_state.supabase_client

    if (
        cloud_client is not None
        and st.session_state.access_token
        and st.session_state.refresh_token
        and st.session_state.is_authenticated
    ):
        try:
            cloud_client.auth.set_session(
                st.session_state.access_token,
                st.session_state.refresh_token,
            )
        except Exception:
            st.session_state.use_cloud = False
            st.session_state.is_authenticated = False
            st.session_state.user_id = LOCAL_DEMO_USER
            st.session_state.user_email = "Local demo user"


def current_user_id() -> str:
    if using_cloud():
        return st.session_state.user_id

    return LOCAL_DEMO_USER


def using_cloud() -> bool:
    return (
        bool(st.session_state.get("use_cloud", False))
        and bool(st.session_state.get("is_authenticated", False))
        and st.session_state.get("user_id") != LOCAL_DEMO_USER
        and st.session_state.get("supabase_client") is not None
    )


def client():
    return st.session_state.get("supabase_client")


def show_header():
    st.markdown(
        """
        <div class="app-title">Wednesday Skinmatch</div>
        <div class="subtitle">
            A Korean skincare matching prototype that uses skin profiles, ingredient notes,
            product comparison, and reaction history to make recommendations easier to understand.
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str):
    safe_title = html.escape(str(title))
    safe_body = html.escape(str(body))

    st.markdown(
        f"""
        <div class="skin-card">
            <h3>{safe_title}</h3>
            <div class="muted-text">{safe_body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def score_card(score: int, label: str = "match score"):
    st.markdown(
        f"""
        <div class="score-box">
            <div class="score-number">{score}/100</div>
            <div class="score-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(text: str, badge_type: str = "neutral"):
    class_name = {
        "good": "badge-good",
        "watch": "badge-watch",
        "risk": "badge-risk",
        "neutral": "badge-neutral",
    }.get(badge_type, "badge-neutral")

    safe_text = html.escape(str(text))

    st.markdown(
        f'<span class="badge {class_name}">{safe_text}</span>',
        unsafe_allow_html=True,
    )


def product_title(product: pd.Series):
    brand = html.escape(str(product.get("brand", "")))
    name = html.escape(str(product.get("name", "")))
    category = html.escape(str(product.get("category", "Product")))
    barcode = html.escape(str(product.get("barcode", "N/A")))

    st.markdown(
        f"""
        <div class="product-title">{brand} {name}</div>
        <div class="product-subtitle">
            {category} · Barcode: {barcode}
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_product_options(products: pd.DataFrame) -> List[str]:
    return [
        f'{row["brand"]} - {row["name"]}'
        for _, row in products.sort_values(["brand", "name"]).iterrows()
    ]


def product_from_option(products: pd.DataFrame, option: str) -> pd.Series:
    brand, name = option.split(" - ", 1)
    row = products[
        (products["brand"].astype(str) == brand)
        & (products["name"].astype(str) == name)
    ].iloc[0]
    return row


def load_current_profile() -> Dict:
    return load_profile(
        current_user_id(),
        client=client(),
        use_cloud=using_cloud(),
    )


def load_current_reactions() -> pd.DataFrame:
    return load_reactions(
        current_user_id(),
        client=client(),
        use_cloud=using_cloud(),
    )


def home_page():
    show_header()

    col1, col2, col3 = st.columns(3)

    with col1:
        card(
            "Skin profile",
            "Save skin type, concerns, sensitivities, preferences, and ingredients you want to avoid.",
        )

    with col2:
        card(
            "Product matching",
            "Search Korean skincare products and see why each product may or may not fit your profile.",
        )

    with col3:
        card(
            "Reaction history",
            "Log products that worked or caused irritation so future recommendations can adjust.",
        )

    st.info(
        "This is a student portfolio prototype using simplified demo data. It does not diagnose skin conditions or allergies."
    )

    st.markdown("### Suggested test flow")
    st.write(
        "Start with **Login**, then save a **Skin Profile**, search a product, compare two products, and generate a routine."
    )


def login_page():
    show_header()
    st.markdown("### Login")

    cloud_client = client()

    if using_cloud():
        st.success(f"Signed in as {st.session_state.user_email}")

        if st.button("Sign out"):
            try:
                cloud_client.auth.sign_out()
            except Exception:
                pass

            st.session_state.use_cloud = False
            st.session_state.is_authenticated = False
            st.session_state.user_id = LOCAL_DEMO_USER
            st.session_state.user_email = "Local demo user"
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.success("Signed out. The app is now using local demo mode.")
            st.rerun()

        return

    local_col, cloud_col = st.columns(2)

    with local_col:
        card(
            "Local demo",
            "Use this while building the project. Profile and reaction data are saved into local CSV files.",
        )

        if st.button("Use local demo mode"):
            st.session_state.use_cloud = False
            st.session_state.is_authenticated = False
            st.session_state.user_id = LOCAL_DEMO_USER
            st.session_state.user_email = "Local demo user"
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.success("Using local demo mode.")
            st.rerun()

    with cloud_col:
        card(
            "Cloud account",
            "Use this after Supabase is connected. Profile and reaction data are saved under the signed-in user.",
        )

    if cloud_client is None:
        st.warning(
            "Supabase is not connected yet. Create `.streamlit/secrets.toml` with your Supabase URL and anon key."
        )
        st.code(
            """
[supabase]
url = "https://YOUR-PROJECT-REF.supabase.co"
anon_key = "YOUR-SUPABASE-ANON-KEY"
            """.strip(),
            language="toml",
        )
        return

    st.markdown("### Supabase login")

    auth_mode = st.radio("Choose action", ["Sign in", "Sign up"], horizontal=True)

    email = st.text_input("Email", placeholder="you@example.com")
    password = st.text_input("Password", type="password")

    if st.button(auth_mode):
        if not email or not password:
            st.error("Enter both email and password.")
            return

        try:
            if auth_mode == "Sign up":
                response = cloud_client.auth.sign_up(
                    {"email": email, "password": password}
                )

                if response.session is None:
                    st.info(
                        "Account created. If email confirmation is turned on in Supabase, confirm your email first, then sign in."
                    )
                    return

            else:
                response = cloud_client.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )

            if response.user is None or response.session is None:
                st.error("Login did not return an active session.")
                return

            cloud_client.auth.set_session(
                response.session.access_token,
                response.session.refresh_token,
            )

            st.session_state.use_cloud = True
            st.session_state.is_authenticated = True
            st.session_state.user_id = response.user.id
            st.session_state.user_email = response.user.email or email
            st.session_state.access_token = response.session.access_token
            st.session_state.refresh_token = response.session.refresh_token

            st.success(f"Signed in as {st.session_state.user_email}")
            st.rerun()

        except Exception as exc:
            st.error(f"Login error: {exc}")


def skin_profile_page():
    show_header()
    st.markdown("### Skin profile")

    profile = normalize_profile(load_current_profile())

    skin_type = st.selectbox(
        "Skin type",
        ["Dry", "Oily", "Combination", "Normal", "Dehydrated", "Not sure"],
        index=["Dry", "Oily", "Combination", "Normal", "Dehydrated", "Not sure"].index(
            profile.get("skin_type", "Combination")
        )
        if profile.get("skin_type", "Combination")
        in ["Dry", "Oily", "Combination", "Normal", "Dehydrated", "Not sure"]
        else 2,
    )

    concern_options = [
        "acne",
        "closed comedones",
        "blackheads",
        "whiteheads",
        "redness",
        "texture",
        "pores",
        "barrier",
        "hydration",
        "hyperpigmentation",
        "sensitive",
    ]

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

    preference_options = [
        "Fragrance-free",
        "Alcohol-free",
        "Essential-oil-free",
        "Budget-friendly",
        "Lightweight texture",
        "Barrier-focused",
    ]

    concerns = st.multiselect(
        "Skin concerns",
        concern_options,
        default=[
            item for item in profile.get("concerns", []) if item in concern_options
        ],
    )

    sensitivities = st.multiselect(
        "Sensitivities",
        sensitivity_options,
        default=[
            item
            for item in profile.get("sensitivities", [])
            if item in sensitivity_options
        ],
    )

    preferences = st.multiselect(
        "Product preferences",
        preference_options,
        default=[
            item for item in profile.get("preferences", []) if item in preference_options
        ],
    )

    avoid_text = st.text_area(
        "Avoid ingredients",
        value=", ".join(profile.get("avoid_ingredients", [])),
        help="Example: fragrance, alcohol denat., shea butter",
    )

    avoid_ingredients = [
        item.strip()
        for item in avoid_text.split(",")
        if item.strip()
    ]

    if st.button("Save profile"):
        updated_profile = {
            "skin_type": skin_type,
            "concerns": concerns,
            "sensitivities": sensitivities,
            "preferences": preferences,
            "avoid_ingredients": avoid_ingredients,
        }

        save_profile(
            current_user_id(),
            updated_profile,
            client=client(),
            use_cloud=using_cloud(),
        )

        st.success("Profile saved.")


def product_search_page():
    show_header()
    st.markdown("### Product search")

    products = get_products()
    ingredients = get_ingredients()
    product_ingredients = get_product_ingredients()
    profile = load_current_profile()
    reactions = load_current_reactions()

    search = st.text_input(
        "Search by product, brand, category, or barcode",
        placeholder="Example: sunscreen, Anua, 880000000001",
    )

    filtered = products.copy()

    if search:
        search_lower = search.lower()

        filtered = products[
            products.apply(
                lambda row: search_lower
                in " ".join(
                    [
                        str(row.get("brand", "")),
                        str(row.get("name", "")),
                        str(row.get("category", "")),
                        str(row.get("barcode", "")),
                    ]
                ).lower(),
                axis=1,
            )
        ]

    if filtered.empty:
        st.warning("No product found.")
        return

    options = get_product_options(filtered)
    selected = st.selectbox("Choose product", options)

    product = product_from_option(filtered, selected)
    result = score_product(
        product,
        profile,
        reactions,
        product_ingredients,
        ingredients,
        user_id=current_user_id(),
    )

    left, right = st.columns([2, 1])

    with left:
        product_title(product)

        st.markdown("#### Why it may suit you")
        for item in result["positives"]:
            badge(item, "good")

        st.markdown("#### Things to watch")
        for item in result["cautions"]:
            badge(item, "watch")

    with right:
        score_card(result["score"])

    with st.expander("Ingredient list"):
        details = result["ingredient_details"]

        if details.empty:
            st.write("No ingredients available for this product yet.")
        else:
            st.dataframe(
                details[
                    [
                        "ingredient_order",
                        "ingredient_name",
                        "category",
                        "benefits",
                        "possible_concerns",
                        "flags",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

    with st.expander("Ingredient notes"):
        risk = result["risk_breakdown"]

        if risk.empty:
            st.write("No ingredient notes available.")
        else:
            st.dataframe(
                risk[
                    [
                        "ingredient_order",
                        "ingredient",
                        "risk_level",
                        "score_impact",
                        "reasons",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )


def ingredient_risk_page():
    show_header()
    st.markdown("### Ingredient risk notes")

    products = get_products()
    ingredients = get_ingredients()
    product_ingredients = get_product_ingredients()
    profile = load_current_profile()
    reactions = load_current_reactions()

    selected = st.selectbox("Choose product", get_product_options(products))
    product = product_from_option(products, selected)

    product_title(product)

    breakdown = ingredient_risk_breakdown(
        product,
        profile,
        reactions,
        product_ingredients,
        ingredients,
        user_id=current_user_id(),
    )

    if breakdown.empty:
        st.write("No ingredient notes available.")
        return

    high = breakdown[breakdown["risk_level"] == "High caution"]
    watch = breakdown[breakdown["risk_level"] == "Watch"]
    helpful = breakdown[breakdown["risk_level"] == "Helpful"]

    col1, col2, col3 = st.columns(3)

    with col1:
        score_card(len(high), "high caution ingredients")

    with col2:
        score_card(len(watch), "watch ingredients")

    with col3:
        score_card(len(helpful), "helpful ingredients")

    st.dataframe(
        breakdown[
            [
                "ingredient_order",
                "ingredient",
                "risk_level",
                "score_impact",
                "reasons",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def product_comparison_page():
    show_header()
    st.markdown("### Product comparison")

    products = get_products()
    ingredients = get_ingredients()
    product_ingredients = get_product_ingredients()
    profile = load_current_profile()
    reactions = load_current_reactions()

    options = get_product_options(products)

    col1, col2 = st.columns(2)

    with col1:
        first_option = st.selectbox("First product", options, key="first_product")

    with col2:
        second_option = st.selectbox(
            "Second product",
            options,
            index=1 if len(options) > 1 else 0,
            key="second_product",
        )

    first = product_from_option(products, first_option)
    second = product_from_option(products, second_option)

    first_result = score_product(
        first,
        profile,
        reactions,
        product_ingredients,
        ingredients,
        user_id=current_user_id(),
    )

    second_result = score_product(
        second,
        profile,
        reactions,
        product_ingredients,
        ingredients,
        user_id=current_user_id(),
    )

    col1, col2 = st.columns(2)

    with col1:
        product_title(first)
        score_card(first_result["score"])
        st.markdown("#### Pros")
        for item in first_result["positives"][:3]:
            badge(item, "good")

        st.markdown("#### Cautions")
        for item in first_result["cautions"][:3]:
            badge(item, "watch")

    with col2:
        product_title(second)
        score_card(second_result["score"])
        st.markdown("#### Pros")
        for item in second_result["positives"][:3]:
            badge(item, "good")

        st.markdown("#### Cautions")
        for item in second_result["cautions"][:3]:
            badge(item, "watch")

    first_ingredients = set(
        first_result["ingredient_details"]["ingredient_name"].dropna().tolist()
    )

    second_ingredients = set(
        second_result["ingredient_details"]["ingredient_name"].dropna().tolist()
    )

    overlap = sorted(first_ingredients.intersection(second_ingredients))

    st.markdown("### Ingredient overlap")

    if overlap:
        st.write(", ".join(overlap))
    else:
        st.write("No overlapping ingredients found in the current dataset.")

    if first_result["score"] > second_result["score"]:
        st.success(f'{first["brand"]} {first["name"]} is the better match for the current profile.')
    elif second_result["score"] > first_result["score"]:
        st.success(f'{second["brand"]} {second["name"]} is the better match for the current profile.')
    else:
        st.info("Both products have the same match score for the current profile.")


def routine_builder_page():
    show_header()
    st.markdown("### Routine builder")

    products = get_products()
    ingredients = get_ingredients()
    product_ingredients = get_product_ingredients()
    profile = load_current_profile()
    reactions = load_current_reactions()

    routine_type = st.radio(
        "Routine type",
        ["Minimal", "Balanced", "Full"],
        horizontal=True,
    )

    if routine_type == "Minimal":
        steps = [
            ("Cleanser", ["Cleanser"]),
            ("Moisturiser", ["Moisturiser", "Cream"]),
            ("Sunscreen", ["Sunscreen"]),
        ]
    elif routine_type == "Balanced":
        steps = [
            ("Cleanser", ["Cleanser"]),
            ("Toner", ["Toner"]),
            ("Serum or essence", ["Serum", "Essence"]),
            ("Moisturiser", ["Moisturiser", "Cream"]),
            ("Sunscreen", ["Sunscreen"]),
        ]
    else:
        steps = [
            ("Cleanser", ["Cleanser"]),
            ("Toner", ["Toner"]),
            ("Essence", ["Essence"]),
            ("Serum", ["Serum"]),
            ("Moisturiser", ["Moisturiser", "Cream"]),
            ("Sunscreen", ["Sunscreen"]),
        ]

    st.info(
        "This routine is based on the current demo dataset. It is meant as a project feature, not skincare advice."
    )

    for step_name, categories in steps:
        chosen = best_product_for_category(
            categories,
            products,
            profile,
            reactions,
            product_ingredients,
            ingredients,
            current_user_id(),
        )

        if chosen is None:
            card(step_name, "No product available for this step yet.")
            continue

        st.markdown(f"### {step_name}")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(
                f"""
                <div class="skin-card">
                    <h3>{chosen.get("brand", "")} {chosen.get("name", "")}</h3>
                    <div class="muted-text">
                        {chosen.get("category", "")}<br>
                        {chosen.get("why", "")}<br>
                        {chosen.get("watch_out", "")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            score_card(int(chosen.get("match_score", 0)))


def reaction_logger_page():
    show_header()
    st.markdown("### Reaction logger")

    products = get_products()

    selected = st.selectbox("Product", get_product_options(products))
    product = product_from_option(products, selected)

    reaction_result = st.radio(
        "How did your skin react?",
        ["Good", "Neutral", "Bad"],
        horizontal=True,
    )

    reaction_type = st.selectbox(
        "Reaction type",
        [
            "No issue",
            "Redness",
            "Burning",
            "Itching",
            "Dryness",
            "Breakout",
            "Closed comedones",
            "Eye stinging",
            "Other",
        ],
    )

    severity = st.slider("Severity", 1, 5, 3)
    notes = st.text_area("Notes", placeholder="Example: stung around my eyes after 2 days")

    if st.button("Save reaction"):
        save_user_reaction(
            current_user_id(),
            int(product["product_id"]),
            reaction_result,
            reaction_type,
            severity,
            notes,
            client=client(),
            use_cloud=using_cloud(),
        )

        st.success("Reaction saved.")


def recommendations_page():
    show_header()
    st.markdown("### Recommendations")

    products = get_products()
    ingredients = get_ingredients()
    product_ingredients = get_product_ingredients()
    profile = load_current_profile()
    reactions = load_current_reactions()

    ranked = recommend_products(
        products,
        profile,
        reactions,
        product_ingredients,
        ingredients,
        user_id=current_user_id(),
    )

    if ranked.empty:
        st.warning("No recommendations available yet.")
        return

    top_n = st.slider("Number of products", 3, 10, 5)
    ranked = ranked.head(top_n)

    for _, product in ranked.iterrows():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(
                f"""
                <div class="skin-card">
                    <h3>{product.get("brand", "")} {product.get("name", "")}</h3>
                    <div class="muted-text">
                        {product.get("category", "")}<br>
                        {product.get("why", "")}<br>
                        {product.get("watch_out", "")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            score_card(int(product.get("match_score", 0)))


def reaction_history_page():
    show_header()
    st.markdown("### Reaction history")

    products = get_products()
    reactions = load_current_reactions()

    if reactions.empty:
        st.info("No reactions saved yet.")
        return

    display = reactions.merge(
        products[["product_id", "brand", "name", "category"]],
        on="product_id",
        how="left",
    )

    st.dataframe(
        display[
            [
                "date_added",
                "brand",
                "name",
                "category",
                "reaction_result",
                "reaction_type",
                "severity",
                "notes",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def sidebar_navigation() -> str:
    st.sidebar.title("Wednesday Skinmatch")
    st.sidebar.caption("Streamlit prototype for a Korean skincare recommender.")

    st.sidebar.markdown("---")

    st.sidebar.write(f"User: **{st.session_state.get('user_email', 'Local demo user')}**")

    mode = "Cloud / Supabase" if using_cloud() else "Local CSV"
    st.sidebar.write(f"Storage: **{mode}**")

    st.sidebar.markdown("---")

    return st.sidebar.radio(
        "Pages",
        [
            "Home",
            "Login",
            "Skin Profile",
            "Product Search",
            "Ingredient Risk",
            "Product Comparison",
            "Routine Builder",
            "Reaction Logger",
            "Recommendations",
            "Reaction History",
        ],
    )

def main():
    init_session_state()

    page = sidebar_navigation()

    if page == "Home":
        home_page()
    elif page == "Login":
        login_page()
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
    elif page == "Reaction History":
        reaction_history_page()


if __name__ == "__main__":
    main()