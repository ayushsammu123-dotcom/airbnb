# 🚀 GitHub & Cloud Deployment Guide

This project is configured for **1-click cloud deployment** on [Streamlit Community Cloud](https://share.streamlit.io/) (free hosting for interactive Python data apps).

---

## 📌 Step 1: Create a New GitHub Repository

1. Go to [github.com/new](https://github.com/new).
2. Name your repository (e.g., `airbnb-pricing-revenue-analytics`).
3. Set visibility to **Public** (required for free Streamlit Cloud hosting) or **Private**.
4. **Do not** check "Initialize with README" (we already have a complete repo with documentation).
5. Click **Create repository**.

---

## 📌 Step 2: Push Your Local Code to GitHub

Open PowerShell or Command Prompt in this folder (`C:\Users\91950\.gemini\antigravity\scratch\airbnb-pricing-revenue-analytics`):

```powershell
# 1. Initialize Git
git init

# 2. Add all project files
git add .

# 3. Create initial commit
git commit -m "feat: Airbnb Pricing & Revenue Analytics Platform (Delhi NCR)"

# 4. Set main branch
git branch -M main

# 5. Link to your GitHub repository (replace with your actual GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/airbnb-pricing-revenue-analytics.git

# 6. Push to GitHub
git push -u origin main
```

---

## 📌 Step 3: Deploy for Free on Streamlit Cloud

1. Visit **[share.streamlit.io](https://share.streamlit.io/)** and sign in with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `YOUR_USERNAME/airbnb-pricing-revenue-analytics`.
4. Branch: `main`.
5. Main file path: `dashboard/app.py`.
6. Click **"Deploy!"**.

Your live dashboard will be accessible via a custom public URL (e.g., `https://airbnb-delhi-analytics.streamlit.app`)!

---

## 🛠 Project Config Reference

- **Production Config**: `.streamlit/config.toml` (Theme & server settings)
- **Dependencies**: `requirements.txt`
- **Entry Point**: `dashboard/app.py`
- **Data Pipeline**: Pre-populated SQLite DB (`data/airbnb.db`) and processed dataset (`data/processed/airbnb_cleaned.csv`) are bundled and ready to serve immediately.
