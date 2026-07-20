# Recommendation Logic

Wednesday Skinmatch uses an explainable rule-based recommendation system.

## Score inputs

- Skin type tags
- Skin concern tags
- Product preferences
- Sensitivity flags
- Manual avoid ingredients
- Past good reactions
- Past bad reactions
- Ingredient-level risk breakdown

## Example scoring rules

```text
Base score = 50
+15 if product matches user skin type
+8 per matched concern, up to +24
+5 for each matched preference such as fragrance-free
-8 if a selected preference is not satisfied
-12 for sensitivity flag matches
-25 for manual avoid ingredient matches
+3 per ingredient overlap with liked products
-6 per ingredient overlap with bad reaction products
```

## Ingredient risk explanation

Each ingredient gets a small explanation row:

- Helpful
- Neutral
- Watch
- High caution

The app explains whether an ingredient matched the user's avoid list, sensitivity flags, acne/comedogenic cautions, or past reaction patterns.

## Safety wording

The app should say:

```text
Possible pattern
May be a concern
Patch test recommended
```

It should avoid saying:

```text
You are allergic
This ingredient is definitely bad
This product is medically safe
```
