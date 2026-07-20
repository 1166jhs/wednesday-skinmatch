# VSCode + GitHub Workflow

Use this every time you add a new feature.

## 1. Open the project

```bash
cd ~/Desktop/wednesday-skinmatch
code .
```

## 2. Run the app from the VSCode terminal

```bash
source .venv/bin/activate
streamlit run app.py
```

## 3. Create a feature branch

Example for product comparison:

```bash
git checkout -b feature/product-comparison
```

## 4. Code the feature

Edit files in VSCode. Test the app before committing.

## 5. Check what changed

```bash
git status
git diff
```

## 6. Commit changes

```bash
git add .
git commit -m "Add product comparison page"
```

## 7. Push the branch

```bash
git push origin feature/product-comparison
```

## 8. Merge on GitHub

1. Open your GitHub repo.
2. Click **Compare & pull request**.
3. Add a short description.
4. Merge the pull request.

## Recommended branches for this version

```bash
git checkout -b feature/ingredient-risk-explanation
git checkout -b feature/product-comparison
git checkout -b feature/routine-builder
git checkout -b feature/supabase-login-cloud-db
```

Since this ZIP already contains all features, you can commit it as one update if you prefer:

```bash
git add .
git commit -m "Add comparison routine builder login and risk explanation features"
git push
```
