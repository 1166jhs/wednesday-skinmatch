# Recommendation Logic

Wednesday Skinmatch uses a rule-based recommendation system. This is easier to explain than a black-box AI model and is better for the first portfolio version.

## Base Score

Each product starts at 50 points.

## Positive Rules

| Rule | Points |
|---|---:|
| Product matches skin type | +15 |
| Product matches selected concern | +8 per concern, up to +24 |
| Product matches preference such as fragrance-free | +5 |
| Product shares ingredients with products the user liked | +3 per ingredient, up to +12 |

## Negative Rules

| Rule | Points |
|---|---:|
| Product does not match selected preference | -8 |
| Product has sensitivity flag selected by user | -12 |
| Product contains manually avoided ingredient | -25 |
| Product shares ingredients with products the user reacted badly to | -6 per ingredient, up to -24 |
| Product has comedogenic/heavy caution and user selected acne/pores concerns | -8 |
| Product is sunscreen and user selected eye stinging concern | -5 |

## Example

A user has:

```text
Skin type: Combination
Concerns: acne, texture
Sensitivities: Fragrance-sensitive
Preferences: Fragrance-free, Alcohol-free
```

A product may get:

```text
Base score: 50
+15 combination skin match
+8 acne concern match
+5 fragrance-free
+5 alcohol-free
-12 fragrance risk if present
Final score: 71/100
```

## Why Rule-Based First?

- Easy to understand
- Easy to debug
- Good for portfolio explanation
- Does not need thousands of user reviews
- Safer than pretending AI can diagnose skin reactions

## Future Machine Learning Ideas

Later, the app could use:

- Collaborative filtering
- Ingredient similarity models
- Clustering users by reaction patterns
- Natural language processing for user reaction notes
- Hybrid rule-based plus ML ranking
