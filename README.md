# 🏠 Airbnb Pricing & Revenue Analytics

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Streamlit-1.30%2B-red?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/Pandas-2.0%2B-green?style=for-the-badge&logo=pandas" />
  <img src="https://img.shields.io/badge/Plotly-5.18%2B-purple?style=for-the-badge&logo=plotly" />
  <img src="https://img.shields.io/badge/SQLite-3.x-orange?style=for-the-badge&logo=sqlite" />
  <img src="https://img.shields.io/badge/scikit--learn-1.3%2B-yellow?style=for-the-badge&logo=scikit-learn" />
</p>

> **An end-to-end Data Analytics portfolio project** for analyzing Airbnb listing data to help hosts, property managers, and business stakeholders understand pricing, revenue potential, occupancy, customer demand, and location-based performance.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Business Problem](#-business-problem)
- [Objectives](#-objectives)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Dataset Description](#-dataset-description)
- [Data Dictionary](#-data-dictionary)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [Data Cleaning Methodology](#-data-cleaning-methodology)
- [Feature Engineering](#-feature-engineering)
- [Revenue Estimation Methodology](#-revenue-estimation-methodology)
- [Exploratory Data Analysis](#-exploratory-data-analysis)
- [SQL Analysis](#-sql-analysis)
- [ML Methodology](#-ml-methodology)
- [Model Evaluation](#-model-evaluation)
- [Key Insights](#-key-insights)
- [Business Recommendations](#-business-recommendations)
- [Dashboard Screenshots](#-dashboard-screenshots)
- [Limitations](#-limitations)
- [Future Improvements](#-future-improvements)
- [How to Add a New Dataset](#-how-to-add-a-new-dataset)
- [Author](#-author)

---

## 🎯 Project Overview

This project is a **complete, production-quality Data Analytics portfolio** built to demonstrate the skills of a professional Data Analyst:

- ✅ Data Engineering (cleaning, validation, pipeline)
- ✅ Feature Engineering (revenue, occupancy, scoring)
- ✅ Exploratory Data Analysis (EDA)
- ✅ Statistical Analysis (correlation, distribution)
- ✅ SQL Analytics (20+ business queries)
- ✅ Machine Learning (pricing models, clustering)
- ✅ Business Intelligence (KPIs, dashboards, recommendations)
- ✅ Interactive Dashboard (10-page Streamlit app)

---

## 💼 Business Problem

Airbnb hosts and property managers often struggle to:
1. Price their listings competitively
2. Understand which factors drive revenue
3. Identify underperforming listings
4. Benchmark against local competition
5. Forecast potential revenue before investing in a property

This platform gives hosts and analysts **data-driven answers** to these questions.

---

## 🎯 Objectives

This project answers 15 key business questions:

| # | Business Question |
|---|---|
| 1 | Which locations generate the highest revenue? |
| 2 | Which neighborhoods have the highest average nightly prices? |
| 3 | Which property types are most profitable? |
| 4 | What factors influence Airbnb pricing? |
| 5 | Which listings have the highest occupancy potential? |
| 6 | What is the estimated monthly and annual revenue of listings? |
| 7 | How does price vary by location? |
| 8 | How does availability affect revenue? |
| 9 | Which room types perform best? |
| 10 | Which hosts are performing best? |
| 11 | What min/max price ranges maximize potential revenue? |
| 12 | How do reviews relate to price and demand? |
| 13 | Which areas appear underpriced or overpriced? |
| 14 | What seasonal patterns exist? |
| 15 | What recommendations can be given to Airbnb hosts? |

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| Dashboard | Streamlit |
| Data Processing | Python, Pandas, NumPy |
| Visualization | Plotly, Matplotlib, Seaborn |
| Database | SQLite |
| Machine Learning | Scikit-learn |
| Statistics | SciPy, Statsmodels |
| Geographic Maps | Plotly Mapbox |
| Testing | Pytest |
| Documentation | Markdown |

---

## 🏗 Project Architecture

```
airbnb-pricing-revenue-analytics/
│
├── data/
│   ├── raw/
│   │   ├── synthetic_airbnb.csv    ← Synthetic dataset (10,000 records)
│   │   ├── generate_data.py        ← Dataset generator script
│   │   └── data_dictionary.md      ← Column definitions
│   ├── processed/
│   │   └── airbnb_cleaned.csv      ← Cleaned & feature-engineered data
│   └── airbnb.db                   ← SQLite database
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_pricing_analysis.ipynb
│   ├── 04_revenue_analysis.ipynb
│   └── 05_advanced_analysis.ipynb
│
├── src/
│   ├── __init__.py
│   ├── utils.py              ← Shared helpers & constants
│   ├── data_cleaning.py      ← Full cleaning pipeline
│   ├── feature_engineering.py← Revenue, occupancy, scoring
│   ├── analysis.py           ← EDA, clustering, pricing gap
│   ├── database.py           ← SQLite management
│   ├── forecasting.py        ← ML pricing models
│   └── utils.py
│
├── sql/
│   ├── schema.sql
│   ├── basic_analysis.sql
│   ├── pricing_analysis.sql
│   ├── revenue_analysis.sql
│   └── advanced_analysis.sql
│
├── dashboard/
│   └── app.py                ← 10-page Streamlit dashboard
│
├── tests/
│   └── test_analysis.py      ← Pytest test suite
│
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

---

## 📊 Dataset Description

> ⚠️ **This project uses a synthetic dataset** generated to mimic real Airbnb NYC listings data. The synthetic data has been designed with realistic statistical relationships between variables. It is clearly labeled as synthetic in the code and UI.
>
> **To use a real dataset:** Download from [Inside Airbnb](http://insideairbnb.com/get-the-data/) and place `listings.csv` in `data/raw/`. The cleaning pipeline will handle it automatically.

### Dataset Characteristics
- **Records:** 10,000 listings
- **Location:** New York City (5 boroughs, 20 neighborhoods)
- **Format:** CSV
- **Data Quality Issues Intentionally Added:** ~3% invalid prices, ~2% duplicates, ~5-10% missing values

---

## 📖 Data Dictionary

| Column | Type | Description |
|---|---|---|
| `listing_id` | int | Unique identifier for each listing |
| `host_id` | int | Unique identifier for each host |
| `host_name` | str | First name of the host |
| `neighbourhood` | str | Neighborhood name |
| `neighbourhood_group` | str | Borough (Manhattan, Brooklyn, etc.) |
| `latitude` | float | Geographic latitude |
| `longitude` | float | Geographic longitude |
| `room_type` | str | Type: Entire home/apt, Private room, Shared room, Hotel room |
| `property_type` | str | Property type: Apartment, House, Condo, Loft, Studio |
| `price` | float | Nightly listing price in USD |
| `minimum_nights` | int | Minimum nights per booking |
| `maximum_nights` | int | Maximum nights per booking |
| `number_of_reviews` | int | Total reviews received |
| `reviews_per_month` | float | Average reviews per month |
| `review_rate_number` | float | Average star rating (1-5) |
| `availability_365` | int | Days available for booking in next 365 days |
| `number_of_reviews_ltm` | int | Reviews in the last 12 months |
| `host_listings_count` | int | Total listings by this host |
| `host_is_superhost` | bool | Whether host has Superhost status |
| `instant_bookable` | bool | Whether listing allows instant booking |
| `calculated_host_listings_count` | int | Calculated host listing count |
| `last_review` | date | Date of most recent review |
| `license` | str | Local license number (often null) |
| **Engineered Features** | | |
| `estimated_occupied_days` | int | 365 - availability_365 |
| `estimated_occupancy_rate` | float | estimated_occupied_days / 365 |
| `estimated_annual_revenue` | float | price × estimated_occupied_days |
| `estimated_monthly_revenue` | float | estimated_annual_revenue / 12 |
| `revenue_per_available_day` | float | estimated_annual_revenue / 365 |
| `price_category` | str | Budget / Mid-Range / Premium / Luxury |
| `occupancy_category` | str | Low / Medium / High |
| `host_category` | str | Single-Property / Multi-Property |
| `demand_score` | float | Composite demand proxy score (0-100) |
| `host_performance_score` | float | Host-level performance score (0-100) |
| `location_score` | float | Neighbourhood attractiveness score (0-100) |
| `price_competitiveness_score` | float | Price vs neighbourhood peers (0-100) |
| `pricing_gap` | float | Actual price - ML predicted price |
| `pricing_opportunity` | str | Underpriced / Fairly Priced / Overpriced |
| `cluster_label` | int | K-Means cluster number |
| `cluster_name` | str | Business-friendly cluster name |

---

## ⚙️ Installation

### Prerequisites
- Python 3.9+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/airbnb-pricing-revenue-analytics.git
cd airbnb-pricing-revenue-analytics

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 How to Run

### 1. Generate the Dataset (first time only)

```bash
python data/raw/generate_data.py
```

This creates `data/raw/synthetic_airbnb.csv`.

### 2. Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

The app will automatically:
- Clean and process the data
- Build the SQLite database
- Train the ML pricing models
- Open in your browser at `http://localhost:8501`

### 3. Run Tests

```bash
pytest tests/ -v
```

### 4. Optional: Run the Jupyter Notebooks

```bash
jupyter notebook notebooks/
```

---

## 🧹 Data Cleaning Methodology

The cleaning pipeline (`src/data_cleaning.py`) follows this sequence:

| Step | Action | Decision |
|---|---|---|
| 1 | Remove duplicate `listing_id` records | Keep first occurrence |
| 2 | Remove invalid `listing_id` or `host_id` (null) | Drop row |
| 3 | Remove zero or negative prices | Drop row |
| 4 | Cap extreme price outliers | Winsorize at 99th percentile |
| 5 | Validate latitude/longitude ranges | Drop out-of-range coordinates |
| 6 | Parse date columns | Convert to datetime |
| 7 | Convert numeric columns to correct types | Coerce errors to NaN |
| 8 | Impute missing numeric values | Median imputation |
| 9 | Impute missing categorical values | Mode imputation |
| 10 | Normalize room_type and property_type strings | Title case, strip whitespace |

### Cleaning Report

The pipeline generates a cleaning report including:
- Original row count
- Final row count
- Duplicates removed
- Invalid records removed
- Outliers handled
- Missing values before/after

---

## 🔧 Feature Engineering

Key engineered features and their formulas:

### Revenue Estimation

```
estimated_occupied_days     = 365 - availability_365   (clipped 0-365)
estimated_occupancy_rate    = estimated_occupied_days / 365
estimated_annual_revenue    = price × estimated_occupied_days
estimated_monthly_revenue   = estimated_annual_revenue / 12
revenue_per_available_day   = estimated_annual_revenue / 365
```

### Scoring

| Score | Inputs | Method |
|---|---|---|
| `demand_score` | reviews_per_month, number_of_reviews, occupancy_rate, availability_365 | Weighted normalized sum × 100 |
| `host_performance_score` | host-level avg revenue, avg reviews, avg occupancy | Min-max normalized per host × 100 |
| `location_score` | neighbourhood avg revenue, reviews, occupancy | Min-max normalized per neighbourhood × 100 |
| `price_competitiveness_score` | listing price vs neighbourhood median | Percentile rank × 100 |

---

## 💰 Revenue Estimation Methodology

> ⚠️ **IMPORTANT DISCLAIMER:** Revenue figures in this project are **ESTIMATES ONLY**. Airbnb does not publicly disclose actual booking data, revenue, or occupancy rates for individual listings.
>
> The methodology used is based on the commonly used **availability proxy approach**: a listing's "busyness" is inferred from how many days it is NOT available. This is an approximation and subject to significant uncertainty.

### Approach 1: Availability-Based (Primary)

```python
estimated_occupied_days  = max(0, 365 - availability_365)
estimated_annual_revenue = price × estimated_occupied_days
```

**Assumptions:**
- Unavailable days = booked days (hosts may block dates for other reasons)
- Price is the listed price (actual rates may vary with seasonal pricing)
- 100% of occupied nights are booked at listed price

### Approach 2: Review-Based (Cross-check)

```python
# Estimate average stay length from minimum_nights
avg_stay = median(minimum_nights)  # typically 2-3 nights
estimated_bookings = reviews_per_month × 12  # not all guests leave reviews
# Then compute revenue similarly
```

### Known Limitations
- Hosts may block unavailable dates for personal use
- Dynamic pricing means actual revenue may differ
- Review rates vary; some guests never review
- Platform fees (~3% host fee) are not deducted

---

## 📈 Exploratory Data Analysis

The EDA covers 5 dimensions:

### A. Listing Distribution
- Listings by neighborhood and borough
- Listings by room type and property type
- Single vs multi-property host breakdown

### B. Pricing
- Price distribution (histogram, box plots)
- Price by neighborhood (bar charts, heatmaps)
- Price by room type and property type
- Outlier detection

### C. Reviews
- Review count distribution
- Reviews per month by room type
- Review score distribution
- Correlation: reviews vs price

### D. Availability
- Availability distribution
- Availability by neighborhood
- Availability vs revenue correlation

### E. Host Behavior
- Superhost vs regular host comparison
- Multi-property host analysis
- Host portfolio concentration

---

## 🗄 SQL Analysis

20+ business queries are stored in `sql/` and answer:

| File | Queries |
|---|---|
| `basic_analysis.sql` | Dataset overview, room type distribution, top reviewed listings |
| `pricing_analysis.sql` | Neighborhood prices, room type pricing, superhost vs regular, underpriced areas |
| `revenue_analysis.sql` | Top revenue neighborhoods, listings, hosts, revenue by room/property type |
| `advanced_analysis.sql` | Underpriced/overpriced listings, host portfolios, cluster analysis, business opportunities |

---

## 🤖 ML Methodology

The pricing model (`src/forecasting.py`) predicts expected listing price.

### Features Used
- Neighborhood (label encoded)
- Room type (label encoded)
- Minimum nights
- Availability 365
- Number of reviews
- Reviews per month
- Host listings count
- Host is superhost
- Latitude, longitude

### Target Variable
`log(price)` — log-transformed to normalize price distribution

### Models Compared

| Model | Notes |
|---|---|
| Linear Regression | Baseline model |
| Random Forest Regressor | Non-linear, handles interactions |
| Gradient Boosting Regressor | Often best overall |

### Pricing Gap (Opportunity Analysis)
```
pricing_gap        = actual_price - predicted_price
Underpriced        : pricing_gap < -50 (potential revenue left on table)
Fairly Priced      : -50 ≤ pricing_gap ≤ +50
Overpriced         : pricing_gap > +50 (may deter bookings)
```

---

## 📊 Model Evaluation

| Metric | Description |
|---|---|
| MAE | Mean Absolute Error — average absolute price prediction error |
| RMSE | Root Mean Squared Error — penalizes large errors |
| R² | Coefficient of determination — proportion of variance explained |

> The ML model is used for **pricing opportunity analysis only** — it is NOT presented as a production pricing engine. Pricing depends on many factors not captured in listing data.

---

## 💡 Key Insights

> *(Generated from synthetic data — results will vary with real Airbnb data)*

1. **Manhattan listings command 2-3× the price** of outer-borough equivalents.
2. **Entire home/apt listings generate ~4× the annual revenue** of shared rooms.
3. **Superhosts earn ~15-25% more per night** and have higher occupancy rates.
4. **Multi-property hosts dominate top revenue rankings** — scale matters.
5. **High demand + low price areas** offer the best opportunity for new hosts.
6. **Listings with 0-50 reviews** are often underpriced relative to peers.
7. **Instant bookable listings** tend to have higher occupancy and revenue.
8. **Availability below 200 days/year** strongly correlates with higher estimated revenue.

---

## 📋 Business Recommendations

### For New Hosts
- **Target Mid-Range pricing ($75-$150/night)** in high-demand neighborhoods for fastest occupancy growth.
- **Enable instant booking** to increase visibility and bookings.
- **Aim for Superhost status** — the revenue premium is significant.

### For Existing Hosts
- **Review the Pricing Opportunity page** to identify if your listing is underpriced.
- **Optimize availability settings** — too many blocked days reduce revenue.
- **Monitor the demand score** for your neighborhood to time price increases.

### For Property Investors
- **Focus on neighborhoods with high demand scores and below-median prices** — these are underserved markets.
- **Entire home/apt listings generate the highest absolute revenue.**
- **Queens and Bronx** offer lower competition with growing demand.

---

## 🖥 Dashboard Screenshots

*Run `streamlit run dashboard/app.py` to view the live dashboard.*

| Page | Description |
|---|---|
| Executive Overview | KPI cards + revenue map + top charts |
| Pricing Analysis | Price distributions, correlations, predictions |
| Revenue Analysis | Estimated revenue by neighborhood, host, room type |
| Location Intelligence | Interactive Plotly map with filters |
| Host Analytics | Portfolio analysis, superhost comparison |
| Demand Analysis | Demand score map and analysis |
| Listing Explorer | Searchable/filterable table with CSV export |
| Pricing Opportunity | Underpriced/overpriced analysis |
| ML & Advanced | Model evaluation, feature importance, clusters |
| Data Quality | Cleaning report, data quality score |

---

## ⚠️ Limitations

1. **Synthetic data** — all insights are illustrative. Real patterns may differ.
2. **Revenue estimates** are approximations based on availability data, not actual bookings.
3. **No actual booking data** — Airbnb does not publicly share transaction records.
4. **No seasonal decomposition** — the dataset does not include time-series booking data.
5. **ML models** are trained on listing characteristics only — location microfeatures (transit, restaurants) are not included.
6. **Price is static** — dynamic/seasonal pricing by hosts is not modeled.

---

## 🔮 Future Improvements

- [ ] Integrate real Inside Airbnb dataset with auto-download
- [ ] Add time-series analysis with multiple monthly snapshots
- [ ] Implement seasonal pricing model
- [ ] Add neighborhood walkability/transit score integration
- [ ] Build automated host recommendation engine
- [ ] Add competitive pricing alerts
- [ ] Deploy to Streamlit Cloud or AWS
- [ ] Add PDF report export
- [ ] Integrate real review sentiment analysis (NLP)

---

## 📥 How to Add a New Dataset

1. Download a real dataset from [Inside Airbnb](http://insideairbnb.com/get-the-data/).
2. Place the file in `data/raw/` (e.g., `data/raw/listings.csv`).
3. In `dashboard/app.py`, update the `DATA_PATH` constant.
4. The cleaning pipeline will handle any schema differences (it drops unknown columns gracefully).
5. Re-run the dashboard: `streamlit run dashboard/app.py`.

**Expected minimum columns:**
`listing_id`, `host_id`, `neighbourhood`, `latitude`, `longitude`, `room_type`, `price`, `availability_365`, `number_of_reviews`, `reviews_per_month`

---

## 👤 Author

**Data Analytics Portfolio Project**

Built to demonstrate end-to-end Data Analyst skills including:
- Data Engineering & Cleaning
- Exploratory Data Analysis
- Feature Engineering
- SQL Analytics
- Machine Learning
- Business Intelligence
- Streamlit Dashboard Development

---

*⚠️ This project uses a synthetic dataset. All revenue figures are estimates based on publicly available listing data using the availability-proxy methodology. They do not represent actual Airbnb revenue or booking data.*
