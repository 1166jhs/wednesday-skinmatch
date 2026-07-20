# Database Schema

The MVP uses CSV files. The cloud version uses Supabase for user profiles and reaction history.

## Local CSV files

### products.csv

Product catalog demo data.

### ingredients.csv

Ingredient names, categories, flags, benefits, and possible concerns.

### product_ingredients.csv

Many-to-many table linking products to ingredients.

### user_profiles.csv

Local demo skin profile storage.

### user_reactions.csv

Local demo reaction history storage.

## Supabase tables

### skin_profiles

```sql
user_id uuid primary key
skin_type text
concerns text[]
sensitivities text[]
preferences text[]
avoid_ingredients text[]
updated_at timestamptz
```

### user_reactions

```sql
reaction_id bigint primary key
user_id uuid
product_id integer
reaction_result text
reaction_type text
severity integer
notes text
date_added date
```

Supabase product data can be added later, but this version keeps product data in CSV so the app is easy to run locally.
