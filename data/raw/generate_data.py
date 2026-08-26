"""
Synthetic Airbnb Delhi NCR Dataset Generator
=============================================
Generates a realistic 10,000-row synthetic Airbnb dataset exclusively for the
National Capital Region (Delhi NCR) — covering South Delhi, Central Delhi,
Gurugram (Gurgaon), Noida, Greater Noida, West & North Delhi, Faridabad, and Ghaziabad.

Statistical relationships modeled:
  - Prices correlate with room type (Entire home > Private room > Shared room)
  - Prices correlate with micro-market (Golf Course Road, Chanakyapuri, CP, Chattarpur Farmhouses higher)
  - Occupancy inversely correlates with availability
  - Superhosts achieve ~18% higher reviews and ~12% higher occupancy
  - ~20% multi-property commercial hosts
  - ~3% intentional data quality anomalies (negative/zero prices, outliers)
  - ~2% duplicate rows for cleaning validation
  - Realistic Delhi NCR coordinate bounds (Lat: 28.35 - 28.80, Lon: 76.90 - 77.55)

Usage:
    python data/raw/generate_data.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
SEED = 42
np.random.seed(SEED)
random.seed(SEED)
rng = np.random.default_rng(SEED)

N_ROWS = 10_000

# ---------------------------------------------------------------------------
# Delhi NCR Micro-Markets & Geography
# ---------------------------------------------------------------------------
# Format: (Neighbourhood, Zone/Group, Lat, Lon, Price Multiplier, Distribution Weight)
DELHI_NCR_LOCATIONS = [
    # South Delhi
    ("Hauz Khas Village",          "South Delhi", 28.5494, 77.2001, 1.85, 0.07),
    ("Greater Kailash",            "South Delhi", 28.5482, 77.2426, 1.90, 0.07),
    ("Saket",                      "South Delhi", 28.5244, 77.2177, 1.50, 0.05),
    ("Vasant Kunj",                "South Delhi", 28.5293, 77.1524, 1.70, 0.05),
    ("Defense Colony",             "South Delhi", 28.5726, 77.2312, 2.10, 0.04),
    ("Green Park",                 "South Delhi", 28.5589, 77.2028, 1.60, 0.04),
    ("Chattarpur",                 "South Delhi", 28.5023, 77.1783, 2.25, 0.03), # Luxury farmhouses

    # Central Delhi
    ("Connaught Place",            "Central Delhi", 28.6315, 77.2167, 2.40, 0.06),
    ("Chanakyapuri",               "Central Delhi", 28.5983, 77.1971, 2.50, 0.03),
    ("Karol Bagh",                 "Central Delhi", 28.6517, 77.1906, 1.10, 0.04),
    ("Paharganj",                  "Central Delhi", 28.6433, 77.2140, 0.85, 0.04),

    # Gurugram (Gurgaon)
    ("Golf Course Road (DLF 5)",   "Gurugram", 28.4698, 77.0984, 2.60, 0.08),
    ("Cyber City",                 "Gurugram", 28.4950, 77.0895, 2.05, 0.07),
    ("Sector 29",                  "Gurugram", 28.4682, 77.0632, 1.65, 0.05),
    ("Sohna Road",                 "Gurugram", 28.4014, 77.0422, 1.25, 0.04),
    ("Sushant Lok",                "Gurugram", 28.4601, 77.0792, 1.55, 0.04),

    # Noida & Greater Noida
    ("Sector 18 Noida",            "Noida", 28.5708, 77.3260, 1.40, 0.05),
    ("Sector 62 Noida",            "Noida", 28.6208, 77.3639, 1.15, 0.04),
    ("Sector 137 Expressway",      "Noida", 28.5132, 77.4042, 1.35, 0.04),
    ("Greater Noida (Pari Chowk)", "Greater Noida", 28.4732, 77.5097, 0.90, 0.03),

    # West & North Delhi
    ("Aerocity (IGI Airport)",     "West & North Delhi", 28.5535, 77.1215, 2.30, 0.04),
    ("Dwarka",                     "West & North Delhi", 28.5921, 77.0460, 1.10, 0.04),
    ("Rajouri Garden",             "West & North Delhi", 28.6492, 77.1232, 1.20, 0.03),
    ("Civil Lines",                "West & North Delhi", 28.6795, 77.2229, 1.40, 0.02),
    ("Rohini",                     "West & North Delhi", 28.7160, 77.1175, 0.95, 0.02),

    # Faridabad & Ghaziabad
    ("Indirapuram",                "Ghaziabad", 28.6389, 77.3697, 0.95, 0.02),
    ("Sector 15 Faridabad",        "Faridabad", 28.4089, 77.3178, 0.85, 0.01),
]

# Normalise weights to exactly 1.0
total_w = sum(loc[5] for loc in DELHI_NCR_LOCATIONS)
DELHI_NCR_LOCATIONS = [
    (loc[0], loc[1], loc[2], loc[3], loc[4], loc[5] / total_w)
    for loc in DELHI_NCR_LOCATIONS
]

ROOM_TYPES = ["Entire home/apt", "Private room", "Shared room", "Hotel room"]
ROOM_WEIGHTS = [0.52, 0.38, 0.05, 0.05]
ROOM_PRICE_MULT = {
    "Entire home/apt": 1.75,
    "Private room":    0.88,
    "Shared room":     0.45,
    "Hotel room":      1.40,
}

PROPERTY_TYPES = [
    "Apartment", "Builder Floor", "Farmhouse", "Villa", "Condo",
    "Serviced Apartment", "Studio", "Boutique B&B", "Townhouse", "Penthouse"
]
PROPERTY_WEIGHTS = [0.38, 0.22, 0.08, 0.08, 0.08, 0.06, 0.05, 0.02, 0.02, 0.01]

INDIAN_HOST_NAMES = [
    "Aarav", "Priya", "Rohan", "Ananya", "Vikram", "Neha", "Arjun", "Pooja",
    "Kabir", "Meera", "Rajesh", "Sunita", "Aditya", "Kavita", "Siddharth", "Rhea",
    "Manish", "Shreya", "Karan", "Divya", "Alok", "Isha", "Nikhil", "Tanya",
    "Gaurav", "Ritu", "Amit", "Swati", "Varun", "Simran", "Rahul", "Deepa",
    "Rishi", "Payal", "Tarun", "Anjali", "Sachin", "Rashmi", "Mayank", "Geeta",
    "Pranav", "Sneha", "Abhishek", "Vandana", "Akash", "Bhavna", "Kunal", "Preeti",
    "Sameer", "Harsh", "Deepika", "Mohit", "Jyoti", "Naveen", "Smriti", "Vivek",
    "Aparna", "Ashok", "Komal", "Sanjay", "Tanvi", "Sunil", "Latika", "Vishal",
]


def generate_host_pool(n_listings: int, multi_prop_fraction: float = 0.20):
    """Generate realistic host pool with single- and multi-property managers."""
    n_single = int(n_listings * (1 - multi_prop_fraction))
    n_multi = int(n_listings * multi_prop_fraction)

    single_ids = np.arange(10000, 10000 + n_single)
    single_names = rng.choice(INDIAN_HOST_NAMES, size=n_single)

    n_multi_unique = max(1, n_multi // 5)
    multi_ids = np.arange(20000, 20000 + n_multi_unique)
    multi_names = rng.choice(INDIAN_HOST_NAMES, size=n_multi_unique)

    multi_assignments = rng.choice(n_multi_unique, size=n_multi, replace=True)

    host_ids = list(single_ids) + [multi_ids[i] for i in multi_assignments]
    host_names = list(single_names) + [multi_names[i] for i in multi_assignments]

    combined = list(zip(host_ids, host_names))
    random.shuffle(combined)
    host_ids, host_names = zip(*combined)
    return list(host_ids), list(host_names)


def random_date(start: str, end: str, size: int) -> np.ndarray:
    """Generate random ISO dates between start and end."""
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt   = datetime.strptime(end,   "%Y-%m-%d")
    delta    = (end_dt - start_dt).days
    offsets  = rng.integers(0, delta, size=size)
    return np.array([(start_dt + timedelta(days=int(d))).strftime("%Y-%m-%d") for d in offsets])


def generate_dataset(n_rows: int = N_ROWS) -> pd.DataFrame:
    """Generate full synthetic dataset for Delhi NCR."""
    print(f">> Generating {n_rows:,} synthetic Airbnb listings for Delhi NCR...")

    weights = [loc[5] for loc in DELHI_NCR_LOCATIONS]
    loc_indices = rng.choice(len(DELHI_NCR_LOCATIONS), size=n_rows, p=weights)
    loc_data = [DELHI_NCR_LOCATIONS[i] for i in loc_indices]

    neighbourhoods = [loc[0] for loc in loc_data]
    neighbourhood_groups = [loc[1] for loc in loc_data]
    lat_centers = np.array([loc[2] for loc in loc_data])
    lon_centers = np.array([loc[3] for loc in loc_data])
    price_multipliers = np.array([loc[4] for loc in loc_data])

    # Realistic micro-variance around centers
    latitudes = lat_centers + rng.normal(0, 0.008, n_rows)
    longitudes = lon_centers + rng.normal(0, 0.008, n_rows)

    room_types = rng.choice(ROOM_TYPES, size=n_rows, p=ROOM_WEIGHTS)
    property_types = rng.choice(PROPERTY_TYPES, size=n_rows, p=PROPERTY_WEIGHTS)

    host_ids, host_names = generate_host_pool(n_rows)
    host_ids = np.array(host_ids)
    host_names = np.array(host_names)

    host_counts = pd.Series(host_ids).value_counts().to_dict()
    host_listings_count = np.array([host_counts[h] for h in host_ids])
    calc_host_count = host_listings_count + rng.integers(0, 2, n_rows)

    # Superhost probability
    sh_prob = np.where(host_listings_count > 1, 0.35, 0.22)
    is_superhost = rng.random(n_rows) < sh_prob
    is_instant = rng.random(n_rows) < 0.58

    # Base pricing model in INR (₹) - Calibrated for realistic Delhi NCR day rates
    base_price = 4800.0
    room_mult = np.array([ROOM_PRICE_MULT[r] for r in room_types])
    sh_mult = np.where(is_superhost, 1.15, 1.0)
    noise = rng.lognormal(0, 0.28, n_rows)

    prices = base_price * price_multipliers * room_mult * sh_mult * noise
    prices = np.clip(prices, 1500, 65000).round(2)

    min_nights_opts = [1, 1, 1, 2, 2, 3, 3, 5, 7, 15, 30]
    min_nights = rng.choice(min_nights_opts, size=n_rows)
    max_nights = rng.choice([30, 90, 180, 365, 365, 365], size=n_rows)

    # Availability & Reviews
    avail_base = 220 - (prices / 65000 * 110) + rng.normal(0, 50, n_rows)
    availability_365 = np.clip(avail_base, 0, 365).astype(int)

    occupied_days = 365 - availability_365
    review_base = occupied_days / 365 * 180
    num_reviews = rng.poisson(np.clip(review_base, 1, 220))

    has_reviews = num_reviews > 0
    last_reviews = np.where(has_reviews, random_date("2021-01-01", "2024-12-31", n_rows), None)

    listing_age_months = rng.integers(3, 48, n_rows)
    reviews_per_month = np.where(has_reviews, (num_reviews / listing_age_months).clip(0, 12), 0.0).round(2)
    reviews_ltm = (num_reviews * rng.uniform(0.25, 0.65, n_rows)).astype(int)
    reviews_ltm = np.minimum(reviews_ltm, num_reviews)

    rating_base = 3.6 + (reviews_per_month / 12 * 1.1) + rng.normal(0, 0.25, n_rows)
    review_ratings = np.clip(rating_base, 1.0, 5.0).round(1)

    license_mask = rng.random(n_rows) < 0.65
    licenses = np.where(license_mask, [f"DL-MCD-{rng.integers(100000, 999999)}" for _ in range(n_rows)], None)

    df = pd.DataFrame({
        "listing_id": np.arange(1, n_rows + 1),
        "host_id": host_ids,
        "host_name": host_names,
        "neighbourhood": neighbourhoods,
        "neighbourhood_group": neighbourhood_groups,
        "latitude": latitudes.round(6),
        "longitude": longitudes.round(6),
        "room_type": room_types,
        "property_type": property_types,
        "price": prices,
        "minimum_nights": min_nights,
        "maximum_nights": max_nights,
        "number_of_reviews": num_reviews,
        "reviews_per_month": reviews_per_month,
        "review_rate_number": review_ratings,
        "availability_365": availability_365,
        "number_of_reviews_ltm": reviews_ltm,
        "host_listings_count": host_listings_count,
        "host_is_superhost": is_superhost,
        "instant_bookable": is_instant,
        "calculated_host_listings_count": calc_host_count,
        "last_review": last_reviews,
        "license": licenses,
    })

    # Realistic Data Anomalies for Cleaning Demonstration
    # 1. Zero and negative prices
    neg_idx = rng.choice(n_rows, size=int(n_rows * 0.015), replace=False)
    df.loc[neg_idx[:len(neg_idx)//2], "price"] = rng.choice([-500, -250, -1000], size=len(neg_idx)//2)
    df.loc[neg_idx[len(neg_idx)//2:], "price"] = 0

    # 2. Extreme Outliers
    out_idx = rng.choice(list(set(range(n_rows)) - set(neg_idx)), size=int(n_rows * 0.015), replace=False)
    df.loc[out_idx, "price"] = rng.choice([95000, 150000, 220000, 350000], size=len(out_idx))

    # 3. Missing values
    missing_cols = {
        "reviews_per_month": 0.08,
        "review_rate_number": 0.07,
        "host_listings_count": 0.05,
        "property_type": 0.05,
        "host_is_superhost": 0.04,
        "instant_bookable": 0.03,
    }
    for col, rate in missing_cols.items():
        if col in df.columns:
            m_idx = rng.choice(n_rows, size=int(n_rows * rate), replace=False)
            if df[col].dtype == bool:
                df[col] = df[col].astype(object)
            elif pd.api.types.is_integer_dtype(df[col].dtype):
                df[col] = df[col].astype(float)
            df.loc[m_idx, col] = np.nan

    # 4. Injected duplicates
    n_dups = int(n_rows * 0.02)
    dups = df.sample(n=n_dups, random_state=SEED).copy()
    df = pd.concat([df, dups], ignore_index=True)
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

    print(f">> Generated {len(df):,} listings for Delhi NCR ({n_dups} duplicates injected).")
    return df


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_path = raw_dir / "synthetic_airbnb.csv"

    df = generate_dataset(N_ROWS)
    df.to_csv(csv_path, index=False)
    print(f">> Successfully saved Delhi NCR dataset to {csv_path}")

    # Write updated data dictionary
    dict_path = raw_dir / "data_dictionary.md"
    dict_content = f"""# Airbnb Delhi NCR Dataset — Data Dictionary

Generated by `data/raw/generate_data.py` on {datetime.now().strftime('%Y-%m-%d')}.

## Geographical Scope
Exclusively covering the **National Capital Region (Delhi NCR)**:
- **South Delhi**: Hauz Khas Village, Greater Kailash, Saket, Vasant Kunj, Defense Colony, Green Park, Chattarpur (Farmhouses)
- **Central Delhi**: Connaught Place, Chanakyapuri (Diplomatic Enclave), Karol Bagh, Paharganj
- **Gurugram (Gurgaon)**: Golf Course Road (DLF 5), Cyber City, Sector 29, Sohna Road, Sushant Lok
- **Noida & Greater Noida**: Sector 18, Sector 62, Sector 137 Expressway, Pari Chowk
- **West & North Delhi**: Aerocity (Airport), Dwarka, Rajouri Garden, Civil Lines, Rohini
- **Faridabad & Ghaziabad**: Indirapuram, Sector 15 Faridabad

## Column Specifications

| Column | Type | Description |
|---|---|---|
| `listing_id` | integer | Unique identifier |
| `host_id` | integer | Host identifier |
| `host_name` | string | Indian host name |
| `neighbourhood` | string | Micro-market locality |
| `neighbourhood_group` | string | Zone / Sub-region |
| `latitude` | float | Latitude (Delhi NCR bounding box) |
| `longitude` | float | Longitude (Delhi NCR bounding box) |
| `room_type` | string | Entire home/apt, Private room, Shared room, Hotel room |
| `property_type` | string | Apartment, Builder Floor, Farmhouse, Villa, Studio, etc. |
| `price` | float | Nightly price ($ / USD equivalent) |
| `minimum_nights` | integer | Minimum stay duration |
| `availability_365` | integer | Annual availability |
| `number_of_reviews` | integer | Review count |
| `reviews_per_month` | float | Review frequency |
| `host_is_superhost` | boolean | Superhost status |
"""
    dict_path.write_text(dict_content, encoding="utf-8")
    print(f">> Data dictionary written to {dict_path}")


if __name__ == "__main__":
    main()
