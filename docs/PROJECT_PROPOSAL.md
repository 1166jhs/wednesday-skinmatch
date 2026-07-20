# Wednesday Skinmatch Project Proposal

## Project Summary

Wednesday Skinmatch is a personalised Korean skincare recommendation application. The app helps users discover skincare products that may suit their skin profile by analysing product ingredients, sensitivity preferences, and previous good or bad reactions.

## Problem

Many skincare apps only scan ingredients and label them as good or bad. This can be too general because different people react differently to the same ingredient. Someone may love niacinamide, while another person may experience irritation or breakouts.

## Proposed Solution

Wednesday Skinmatch personalises recommendations using:

- Skin type
- Skin concerns
- Sensitivities
- Ingredients the user wants to avoid
- Products the user liked
- Products the user reacted badly to

The app provides explainable recommendations instead of only showing a score.

## Target Users

- Korean skincare users
- People with sensitive or acne-prone skin
- People who want to track product reactions
- People who want ingredient-aware recommendations
- Skincare beginners who need a simple product matching guide

## Core Features

1. Skin profile creation
2. Product search and barcode lookup
3. Ingredient flag detection
4. Reaction logging
5. Recommendation scoring
6. Explanation of why a product may or may not suit the user

## MVP Scope

The first version is a local Streamlit prototype using CSV files. It does not require login, cloud hosting, or a mobile barcode scanner yet.

## Out of Scope for First Version

- Medical diagnosis
- Dermatologist-level advice
- Real-time product database scraping
- Full mobile app
- Payment features
- User accounts

## Future Scope

- Flutter mobile app
- Barcode scanning using phone camera
- Supabase or PostgreSQL backend
- User authentication
- Admin dashboard
- Product submissions
- Real product image database
- More advanced recommendation model
