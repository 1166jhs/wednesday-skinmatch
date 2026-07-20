# Wednesday Skinmatch

Wednesday Skinmatch is a personalised Korean skincare recommendation prototype. It recommends products based on skin type, concerns, sensitivities, avoid ingredients, and logged good/bad product reactions.

> This is a portfolio prototype, not medical advice. Product and ingredient records are simplified demo data. Always patch test and check official product labels.

## Features

- Skin profile builder
- Product search and typed barcode lookup
- Ingredient risk explanation
- Product comparison
- Routine builder for morning/night routines
- Reaction logger for good, neutral, and bad product reactions
- Personalised recommendation scoring
- Local CSV storage for development
- Optional Supabase login and cloud database storage

## Tech stack

- Python
- Streamlit
- Pandas
- Local CSV files for MVP storage
- Optional Supabase Auth + Database for cloud mode

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```text
wednesday-skinmatch/
├── app.py
├── requirements.txt
├── data/
│   ├── products.csv
│   ├── ingredients.csv
│   ├── product_ingredients.csv
│   ├── user_profiles.csv
│   └── user_reactions.csv
├── src/
│   ├── data_loader.py
│   ├── recommender.py
│   └── storage.py
├── docs/
│   ├── SUPABASE_SETUP.md
│   ├── VSCODE_GIT_WORKFLOW.md
│   ├── GITHUB_STEPS.md
│   ├── DATABASE_SCHEMA.md
│   └── RECOMMENDATION_LOGIC.md
└── .streamlit/
    └── secrets.example.toml
```

## How scoring works

The app starts each product with a base score, then adjusts the score based on:

- skin type match
- concern tag match
- preferences such as fragrance-free or alcohol-free
- sensitivity flags
- manual avoid ingredients
- overlap with ingredients from products the user liked
- overlap with ingredients from products the user reacted badly to
- ingredient-level risk explanation

## Supabase cloud setup

The app runs in local CSV mode by default. To enable cloud login and database storage, follow:

```text
docs/SUPABASE_SETUP.md
```

## GitHub workflow

For VSCode and GitHub commands, follow:

```text
docs/VSCODE_GIT_WORKFLOW.md
```

## Future improvements

- Real mobile barcode scanning
- Larger Korean skincare product dataset
- Admin screen for adding products
- Public deployment through Streamlit Community Cloud
- Mobile app version using Flutter
