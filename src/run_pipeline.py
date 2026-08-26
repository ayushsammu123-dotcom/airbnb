"""
Pipeline runner script to execute data cleaning, feature engineering, ML models,
clustering, and database population end-to-end.
"""
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
from src.data_cleaning import clean_data
from src.feature_engineering import (
    engineer_features,
    compute_demand_score,
    compute_host_performance_score,
    compute_location_score,
    compute_price_competitiveness,
)
from src.forecasting import train_pricing_model
from src.database import initialize_database
from src.analysis import segment_listings_kmeans

def main():
    raw_path = project_root / "data" / "raw" / "synthetic_airbnb.csv"
    processed_path = project_root / "data" / "processed" / "airbnb_cleaned.csv"

    print("=" * 60)
    print(">> Starting Airbnb Analytics Pipeline")
    print("=" * 60)

    # 1. Clean data
    print("\n1. Cleaning raw data...")
    df, report = clean_data(str(raw_path), str(processed_path))
    print(f"   Cleaned rows: {len(df):,} (from {report.get('original_rows', 'N/A'):,})")

    # 2. Feature Engineering
    print("\n2. Engineering features...")
    df = engineer_features(df)
    df["demand_score"] = compute_demand_score(df).values
    df["host_performance_score"] = compute_host_performance_score(df).values
    df["location_score"] = compute_location_score(df).values
    df["price_competitiveness_score"] = compute_price_competitiveness(df).values
    print("   Engineered revenue, occupancy, demand, host, and location scores.")

    # 3. Machine Learning Models
    print("\n3. Training ML pricing models...")
    model = train_pricing_model(df)
    print(f"   Best Model: {model.get_best_model_name()}")
    for name, v in model.results.items():
        metrics = v.get("metrics", v)
        print(f"     - {name}: MAE=${metrics.get('mae', 0):.2f}, RMSE=${metrics.get('rmse', 0):.2f}, R2={metrics.get('r2', 0):.4f}")

    df["predicted_price"] = model.predict_prices(df).values
    df["pricing_gap"] = model.compute_pricing_gaps(df).values
    df["pricing_opportunity"] = df["pricing_gap"].apply(
        lambda g: "Underpriced" if g < -50 else ("Overpriced" if g > 50 else "Fairly Priced")
    )
    print(f"   Pricing opportunity classified: Underpriced={(df['pricing_opportunity']=='Underpriced').sum():,}, Overpriced={(df['pricing_opportunity']=='Overpriced').sum():,}")

    # 4. Clustering
    print("\n4. Performing K-Means listing segmentation...")
    df = segment_listings_kmeans(df)
    print(f"   Segments generated: {df['cluster_name'].unique().tolist()}")

    # 5. Save processed CSV
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"\n5. Saved processed dataset to: {processed_path}")

    # 6. Initialize SQLite Database
    print("\n6. Initializing SQLite database...")
    db = initialize_database(df)
    cnt = db.execute_query("SELECT COUNT(*) as cnt FROM listings")["cnt"].iloc[0]
    print(f"   Database populated at {db.db_path} with {cnt:,} listings.")
    db.close()

    print("\n" + "=" * 60)
    print(">> Full Pipeline Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
