"""
Script to format all currency strings in dashboard/app.py to INR (₹)
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

# Replace currency formatting and labels
code = code.replace("Nightly Price ($)", "Nightly Price (₹)")
code = code.replace("Total gross revenue generated ($)", "Total gross revenue generated (₹)")
code = code.replace("Mean vs Median Nightly Rate ($)", "Mean vs Median Nightly Rate (₹)")
code = code.replace("Gross portfolio revenue estimate ($)", "Gross portfolio revenue estimate (₹)")
code = code.replace("Average annual revenue per listing ($)", "Average annual revenue per listing (₹)")
code = code.replace("Simulated Nightly Price ($)", "Simulated Nightly Price (₹)")
code = code.replace("ML Predicted Nightly Value ($)", "ML Predicted Nightly Value (₹)")
code = code.replace("Actual Nightly Price ($)", "Actual Nightly Price (₹)")
code = code.replace("MAE ($)", "MAE (₹)")
code = code.replace("RMSE ($)", "RMSE (₹)")
code = code.replace('tickprefix="$"', 'tickprefix="₹"')
code = code.replace('tickprefix="$,.0f"', 'tickprefix="₹,.0f"')
code = code.replace('price": ":$,.0f"', 'price": ":₹,.0f"')
code = code.replace('predicted_price": ":$,.0f"', 'predicted_price": ":₹,.0f"')
code = code.replace("New York City", "Delhi NCR")
code = code.replace("across New York City", "across Delhi NCR")
code = code.replace('step=5, key="f_price"', 'step=100, key="f_price"')
code = code.replace('min_value=20, max_value=2000, value=int(df["price"].median()), step=10', 'min_value=500, max_value=100000, value=int(df["price"].median()), step=250')
code = code.replace("by $20–$50", "by ₹1,000–₹2,500")

# Replace $ in f-strings with ₹
code = re.sub(r'f"\$([^{"]*\{)', r'f"₹\1', code)
code = re.sub(r'f"±\$([^{"]*\{)', r'f"±₹\1', code)
code = re.sub(r'<b>\$', r'<b>₹', code)
code = re.sub(r'lambda v: f"\$([^{"]*\{)', r'lambda v: f"₹\1', code)

app_path.write_text(code, encoding="utf-8")
print(">> Successfully updated dashboard/app.py with INR currency!")
