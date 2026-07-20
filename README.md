# Wednesday Skinmatch 🌿

Wednesday Skinmatch is a portfolio prototype for a personalised Korean skincare recommendation app. It recommends products based on a user's skin type, skin concerns, sensitivities, ingredient flags, and logged good/bad product reactions.

> Important: This is an educational software project, not medical advice. The demo product data is simplified and should be verified before real-world use.

## Features

- Skin profile form
- Product search by name, brand, category, or barcode
- Ingredient flag viewer
- Reaction logger for good, neutral, and bad reactions
- Rule-based recommendation engine
- Explainable recommendation output
- Demo Korean skincare product dataset
- Beginner-friendly GitHub structure

## Tech Stack

- Python
- Streamlit
- Pandas
- CSV-based demo database

## Project Structure

```text
wednesday-skinmatch/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── products.csv
│   ├── ingredients.csv
│   ├── product_ingredients.csv
│   └── user_reactions.csv
├── src/
│   ├── data_loader.py
│   └── recommender.py
├── docs/
│   ├── GITHUB_STEPS.md
│   ├── PROJECT_PROPOSAL.md
│   ├── DATABASE_SCHEMA.md
│   └── RECOMMENDATION_LOGIC.md
└── screenshots/
```

## How to Run Locally

### 1. Open Terminal

Go to the project folder:

```bash
cd wednesday-skinmatch
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app should open in your browser.

## Demo Flow

1. Go to **Skin Profile**.
2. Select your skin type, concerns, sensitivities, and preferences.
3. Go to **Product Search**.
4. Search for a product or barcode.
5. Check the match score and ingredient cautions.
6. Go to **Reaction Logger**.
7. Save good or bad reactions.
8. Go to **Recommendations**.
9. See personalised product matches.

## Example Product Barcode Values

You can test barcode lookup with these demo barcodes:

```text
8801000000011 - Anua Heartleaf 77 Soothing Toner
8801000000028 - Round Lab Birch Juice Moisturizing Sunscreen
8801000000325 - VT Cosmetics Reedle Shot 300
```

## Recommendation Logic

The app starts with a base score and adjusts it using:

- Skin type match
- Concern match
- Fragrance/alcohol/essential oil preferences
- Sensitivity flags
- User avoid ingredients
- Ingredients shared with products the user liked
- Ingredients shared with products the user reacted badly to
- Texture/comedogenic caution

The goal is not to say a product is perfectly good or bad. The goal is to explain why a product may or may not suit a specific user.

## Future Improvements

- Real barcode scanner using a mobile app
- Supabase or PostgreSQL backend
- User login
- Admin dashboard for adding products
- Product image upload
- Real product database/API integration
- More detailed ingredient dictionary
- Unit tests
- Deployment to Streamlit Community Cloud

## Resume Description

```text
Wednesday Skinmatch – Personalised Korean Skincare Recommendation App
Built a Streamlit-based skincare recommendation prototype that matches Korean skincare products to users based on skin type, sensitivities, ingredient flags, and logged reaction history. Developed CSV-backed product datasets, reaction tracking, and a rule-based explainable recommendation engine using Python and Pandas.
```
