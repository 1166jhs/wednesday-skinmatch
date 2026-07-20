# Wednesday Skinmatch

Wednesday Skinmatch is a personalised Korean skincare recommendation prototype. It recommends products based on skin type, concerns, sensitivities, avoid ingredients, and logged good/bad product reactions.

> This is a portfolio prototype, not medical advice. Product and ingredient records are simplified demo data. Always patch test and check official product labels.

## Live Demo

[Try Wednesday Skinmatch](https://wednesday-skinmatch-gseyizkfmwg3kjyfulej66.streamlit.app/)

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

## Technical Highlights

- Built with **Python** and **Streamlit** for the web app interface
- Used **Pandas** for product data handling, ingredient matching, and recommendation logic
- Connected **Supabase** for user sign up, login, and cloud data storage
- Used **CSV datasets** for the skincare product, ingredient, and reaction data prototype
- Implemented a **rule-based recommendation system** that scores products based on skin type, concerns, sensitivities, avoid ingredients, and past product reactions
- Added **ingredient-level explanations** so users can understand why a product may or may not suit their profile
- Built **product search**, **product comparison**, **morning/night routine builder**, and **reaction history** features
- Used **Git and GitHub** for version control, documentation, and project tracking
- Deployed the app using **Streamlit Community Cloud**

## Skills Demonstrated

- Python programming
- Data handling with Pandas
- Streamlit app development
- Supabase authentication and database setup
- Rule-based recommendation logic
- UI/UX improvement with custom CSS
- Git/GitHub workflow
- Debugging and deployment
- Writing project documentation

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

## Project Background

I came up with the idea for Wednesday Skinmatch from my experience working as a beauty advisor in retail. Many customers were interested in Korean skincare, but they were also unsure about whether certain products would suit their skin type, sensitivities, or previous irritation history.

I wanted to build a prototype that reflects that kind of real customer concern. Instead of only showing product information, the app uses a user's skin profile and reaction history to make more personalised and explainable recommendations.

This project took around 2–3 weeks to research, build, test, and improve. It was a useful learning experience because I worked through the full process of planning the idea, designing the data structure, building the recommendation logic, connecting authentication and cloud storage, improving the UI, fixing bugs, using Git/GitHub, and deploying the app.

## Future improvements

- Real mobile barcode scanning
- Larger Korean skincare product dataset
- Admin screen for adding and editing products
- More detailed ingredient tagging
- Mobile-friendly UI improvements
- Mobile app version using Flutter
