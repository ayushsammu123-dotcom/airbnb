"""
Script to create clean, standard Jupyter Notebooks for the Airbnb Analytics project.
"""
import json
from pathlib import Path

notebooks_dir = Path(r"C:\Users\91950\.gemini\antigravity\scratch\airbnb-pricing-revenue-analytics\notebooks")
notebooks_dir.mkdir(parents=True, exist_ok=True)

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [s + "\n" for s in source.split("\n")]
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [s + "\n" for s in source.split("\n")]
    }

# 1. 01_data_cleaning.ipynb
nb1_cells = [
    md_cell("# 01. Airbnb Data Cleaning & Validation Pipeline\n\nThis notebook demonstrates the end-to-end data cleaning, handling of missing values, duplicate removal, coordinate bounding, and price outlier treatment for Airbnb listing data."),
    code_cell("import sys\nfrom pathlib import Path\n\n# Add project root to sys.path\nproject_root = Path('..').resolve()\nif str(project_root) not in sys.path:\n    sys.path.insert(0, str(project_root))\n\nimport pandas as pd\nimport numpy as np\nfrom src.data_cleaning import DataCleaner, clean_data\nfrom src.utils import PROJECT_ROOT"),
    md_cell("## 1. Load Raw Dataset"),
    code_cell("raw_path = project_root / 'data' / 'raw' / 'synthetic_airbnb.csv'\nraw_df = pd.read_csv(raw_path)\nprint(f'Raw dataset loaded: {len(raw_df):,} rows, {raw_df.shape[1]} columns')\nraw_df.head()"),
    md_cell("## 2. Inspect Raw Data Quality Issues\nCheck missing values, duplicate IDs, and price anomalies."),
    code_cell("print('--- Missing Values by Column ---')\nprint(raw_df.isnull().sum()[raw_df.isnull().sum() > 0])\n\nprint('\\n--- Duplicates Count ---')\nprint(f'Duplicate listing IDs: {raw_df[\"listing_id\"].duplicated().sum():,}')\n\nprint('\\n--- Price Anomalies ---')\nprint(f'Negative / Zero prices: {(raw_df[\"price\"] <= 0).sum():,}')\nprint(f'Extreme prices (> $1000): {(raw_df[\"price\"] > 1000).sum():,}')"),
    md_cell("## 3. Execute Modular Cleaning Pipeline"),
    code_cell("cleaner = DataCleaner(raw_df)\ncleaned_df = cleaner.clean()\nreport = cleaner.generate_report()\n\nprint(f'Cleaned dataset: {len(cleaned_df):,} rows')\nprint('Cleaning Report Summary:')\nfor k, v in report.items():\n    if k != 'steps':\n        print(f'  {k}: {v}')"),
    md_cell("## 4. Save Processed Clean Dataset"),
    code_cell("out_path = project_root / 'data' / 'processed' / 'airbnb_cleaned.csv'\nout_path.parent.mkdir(parents=True, exist_ok=True)\ncleaned_df.to_csv(out_path, index=False)\nprint(f'Cleaned dataset saved to {out_path}')")
]

with open(notebooks_dir / "01_data_cleaning.ipynb", "w", encoding="utf-8") as f:
    json.dump(make_notebook(nb1_cells), f, indent=2)

# 2. 02_eda.ipynb
nb2_cells = [
    md_cell("# 02. Exploratory Data Analysis (EDA)\n\nComprehensive exploration of listing distributions, prices by neighbourhood and room type, availability patterns, and host metrics."),
    code_cell("import sys\nfrom pathlib import Path\n\nproject_root = Path('..').resolve()\nif str(project_root) not in sys.path:\n    sys.path.insert(0, str(project_root))\n\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport plotly.express as px\n\nfrom src.feature_engineering import engineer_features\n\n# Load cleaned data and engineer features\ndf = pd.read_csv(project_root / 'data' / 'processed' / 'airbnb_cleaned.csv')\ndf = engineer_features(df)\nprint(f'Dataset loaded: {len(df):,} records')"),
    md_cell("## 1. Price Distribution & Boxplots"),
    code_cell("plt.figure(figsize=(12, 5))\nplt.subplot(1, 2, 1)\nsns.histplot(df['price'], bins=40, kde=True, color='#FF385C')\nplt.title('Nightly Price Distribution ($)')\n\nplt.subplot(1, 2, 2)\nsns.boxplot(data=df, x='room_type', y='price', palette='Set2')\nplt.title('Price by Room Type')\nplt.xticks(rotation=15)\nplt.tight_layout()\nplt.show()"),
    md_cell("## 2. Neighbourhood Listing Count & Average Price"),
    code_cell("neigh_summary = df.groupby('neighbourhood').agg(count=('listing_id', 'count'), avg_price=('price', 'mean')).sort_values('count', ascending=False)\nprint(neigh_summary.head(15))"),
    md_cell("## 3. Superhost vs Regular Host Performance"),
    code_cell("df.groupby('host_is_superhost').agg(avg_price=('price', 'mean'), avg_reviews=('number_of_reviews', 'mean'), avg_occupancy=('estimated_occupancy_rate', 'mean'))")
]

with open(notebooks_dir / "02_eda.ipynb", "w", encoding="utf-8") as f:
    json.dump(make_notebook(nb2_cells), f, indent=2)

# 3. 03_pricing_analysis.ipynb
nb3_cells = [
    md_cell("# 03. Pricing Analysis & Feature Correlation\n\nInvestigating price elasticity, drivers of listing prices, and statistical relationships across location, room type, reviews, and availability."),
    code_cell("import sys\nfrom pathlib import Path\n\nproject_root = Path('..').resolve()\nif str(project_root) not in sys.path:\n    sys.path.insert(0, str(project_root))\n\nimport pandas as pd\nimport numpy as np\nimport seaborn as sns\nimport matplotlib.pyplot as plt\n\nfrom src.analysis import compute_price_correlation, compute_neighbourhood_stats\nfrom src.feature_engineering import engineer_features\n\ndf = pd.read_csv(project_root / 'data' / 'processed' / 'airbnb_cleaned.csv')\ndf = engineer_features(df)"),
    md_cell("## 1. Feature Correlation Matrix"),
    code_cell("corr_df = compute_price_correlation(df)\nprint('Correlations with Price:')\nprint(corr_df)\n\nnum_cols = ['price', 'minimum_nights', 'number_of_reviews', 'reviews_per_month', 'availability_365', 'host_listings_count']\nplt.figure(figsize=(8, 6))\nsns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm', fmt='.2f')\nplt.title('Correlation Heatmap')\nplt.show()"),
    md_cell("## 2. Statistical Analysis by Neighbourhood"),
    code_cell("n_stats = compute_neighbourhood_stats(df)\nprint(n_stats.sort_values('avg_price', ascending=False).head(10))")
]

with open(notebooks_dir / "03_pricing_analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(make_notebook(nb3_cells), f, indent=2)

# 4. 04_revenue_analysis.ipynb
nb4_cells = [
    md_cell("# 04. Revenue Estimation & Host Portfolio Analytics\n\nDetailed analysis of estimated annual and monthly revenue across neighbourhoods, room types, and host portfolios."),
    code_cell("import sys\nfrom pathlib import Path\n\nproject_root = Path('..').resolve()\nif str(project_root) not in sys.path:\n    sys.path.insert(0, str(project_root))\n\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\nfrom src.feature_engineering import engineer_features\nfrom src.analysis import compute_host_stats, get_top_listings\n\ndf = pd.read_csv(project_root / 'data' / 'processed' / 'airbnb_cleaned.csv')\ndf = engineer_features(df)"),
    md_cell("## 1. Top Revenue-Generating Neighbourhoods"),
    code_cell("rev_neigh = df.groupby('neighbourhood')['estimated_annual_revenue'].agg(['sum', 'mean', 'count']).sort_values('sum', ascending=False)\nrev_neigh.columns = ['Total Revenue', 'Avg Revenue per Listing', 'Listings']\nprint(rev_neigh.head(15))"),
    md_cell("## 2. Top Revenue-Generating Hosts"),
    code_cell("top_hosts = compute_host_stats(df)\nprint(top_hosts.sort_values('total_estimated_revenue', ascending=False).head(10))"),
    md_cell("## 3. Revenue by Room Type & Host Category"),
    code_cell("print(df.groupby(['room_type', 'host_category'])['estimated_annual_revenue'].agg(['mean', 'median', 'count']))")
]

with open(notebooks_dir / "04_revenue_analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(make_notebook(nb4_cells), f, indent=2)

# 5. 05_advanced_analysis.ipynb
nb5_cells = [
    md_cell("# 05. Machine Learning Pricing Model & Segmentation\n\nTraining Regression models (Linear Regression, Random Forest, Gradient Boosting) for pricing valuation, pricing opportunity gap analysis, and K-Means listing clustering."),
    code_cell("import sys\nfrom pathlib import Path\n\nproject_root = Path('..').resolve()\nif str(project_root) not in sys.path:\n    sys.path.insert(0, str(project_root))\n\nimport pandas as pd\nimport numpy as np\n\nfrom src.feature_engineering import engineer_features, compute_demand_score\nfrom src.forecasting import train_pricing_model\nfrom src.analysis import segment_listings_kmeans\n\ndf = pd.read_csv(project_root / 'data' / 'processed' / 'airbnb_cleaned.csv')\ndf = engineer_features(df)\ndf['demand_score'] = compute_demand_score(df)"),
    md_cell("## 1. Train Pricing Models (LR vs RF vs GB)"),
    code_cell("model = train_pricing_model(df)\nprint('Model Evaluation Results:')\nfor name, res in model.results.items():\n    print(f'  {name}: MAE=${res.get(\"mae\",0):.2f}, RMSE=${res.get(\"rmse\",0):.2f}, R2={res.get(\"r2\",0):.4f}')\nprint(f'\\nBest Model: {model.get_best_model_name()}')"),
    md_cell("## 2. Feature Importance"),
    code_cell("best_m = model.models[model.get_best_model_name()]\nfi = model.get_feature_importance(best_m, model.feature_names_)\nprint(fi)"),
    md_cell("## 3. Pricing Gap & Opportunity Identification"),
    code_cell("df['predicted_price'] = model.predict_prices(df)\ndf['pricing_gap'] = model.compute_pricing_gaps(df)\n\nunderpriced = df[df['pricing_gap'] < -50]\nprint(f'Total Underpriced Opportunities Identified: {len(underpriced):,}')\nprint(underpriced[['listing_id', 'neighbourhood', 'room_type', 'price', 'predicted_price', 'pricing_gap']].head(10))"),
    md_cell("## 4. K-Means Listing Clustering"),
    code_cell("clustered_df = segment_listings_kmeans(df)\nprint(clustered_df.groupby('cluster_name')[['price', 'estimated_annual_revenue', 'demand_score', 'estimated_occupancy_rate']].mean())")
]

with open(notebooks_dir / "05_advanced_analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(make_notebook(nb5_cells), f, indent=2)

print("Successfully created all 5 Jupyter Notebooks in notebooks/")
