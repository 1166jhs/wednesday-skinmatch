# GitHub Step-by-Step Guide

This guide shows how to upload Wednesday Skinmatch to GitHub and keep updating it properly.

## 1. Create the project locally

Put this folder somewhere easy to access, for example:

```bash
cd Desktop
```

Then make sure the project folder is named:

```text
wednesday-skinmatch
```

## 2. Open the project in Terminal

```bash
cd ~/Desktop/wednesday-skinmatch
```

## 3. Initialise Git

```bash
git init
```

## 4. Check files

```bash
git status
```

## 5. Add files

```bash
git add .
```

## 6. First commit

```bash
git commit -m "Initial Wednesday Skinmatch prototype"
```

## 7. Create GitHub repository

Go to GitHub and create a new repository called:

```text
wednesday-skinmatch
```

Do not tick README, .gitignore, or license if they already exist locally.

## 8. Connect local project to GitHub

Replace YOUR-USERNAME with your GitHub username:

```bash
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/wednesday-skinmatch.git
git push -u origin main
```

## 9. How to update GitHub after changes

Every time you change your code:

```bash
git status
git add .
git commit -m "Describe what changed"
git push
```

Example commit messages:

```text
Add product search page
Improve recommendation scoring
Add user reaction logger
Update skincare product dataset
Add ingredient flag explanations
```

## 10. Recommended branches

After the first commit, you can create feature branches:

```bash
git checkout -b feature/barcode-scanner
```

After editing files:

```bash
git add .
git commit -m "Add barcode scanner planning page"
git push -u origin feature/barcode-scanner
```

Then open a pull request on GitHub.

## 11. Suggested GitHub Issues

Create these issues in your repo:

```text
Build Streamlit skin profile form
Add product search and barcode lookup
Create reaction logging system
Implement recommendation scoring
Add ingredient caution explanations
Add screenshots to README
Research mobile barcode scanning
Plan PostgreSQL database migration
```

## 12. Suggested GitHub Project Board

Columns:

```text
Backlog
To Do
In Progress
Done
```

Cards:

```text
Skin profile page
Product search page
Reaction logger
Recommendation engine
Product dataset expansion
README screenshots
Mobile app research
```
