# Database Schema

The first version uses CSV files instead of a real database. These CSV files are designed so they can later be moved into SQLite, PostgreSQL, or Supabase.

## products.csv

Stores product-level information.

| Column | Description |
|---|---|
| product_id | Unique product ID |
| barcode | Product barcode or demo barcode |
| brand | Product brand |
| name | Product name |
| category | Toner, cleanser, serum, sunscreen, etc. |
| skin_type_tags | Skin types the product may suit |
| concern_tags | Skin concerns the product may target |
| texture | Product texture |
| price_tier | budget, mid, or high |
| fragrance_free | yes/no |
| alcohol_free | yes/no |
| essential_oil_free | yes/no |
| comedogenic_caution | yes/no |
| notes | Extra notes |

## ingredients.csv

Stores ingredient-level information.

| Column | Description |
|---|---|
| ingredient_name | Ingredient name |
| ingredient_category | Humectant, active, fragrance, exfoliant, etc. |
| flags | Machine-readable tags used by recommendation logic |
| benefits | Possible benefit category |
| possible_concerns | Possible caution explanation |

## product_ingredients.csv

Links products to ingredients.

| Column | Description |
|---|---|
| product_id | Product ID from products.csv |
| ingredient_name | Ingredient name from ingredients.csv |
| ingredient_order | Simplified ingredient order |

## user_reactions.csv

Stores the user's product history.

| Column | Description |
|---|---|
| reaction_id | Unique reaction record ID |
| user_id | Demo user ID |
| product_id | Product used |
| reaction_result | Good, Neutral, or Bad |
| reaction_type | Reaction category |
| severity | 1 to 5 |
| notes | User notes |
| date_added | Date saved |

## Future Database Tables

For a production version, convert the CSV files into tables:

```text
users
skin_profiles
products
ingredients
product_ingredients
user_reactions
recommendation_history
```
