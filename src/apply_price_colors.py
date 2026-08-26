"""
Apply Green (Low), Orange (Mid), and Wine Red (High) color hierarchy across the dashboard.
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

# Fix residual $ in f-strings
code = code.replace("Median: ${median_price:,.0f}", "Median: ₹{median_price:,.0f}")
code = code.replace("₹{df['price'].quantile(0.25):,.0f} - ${df['price'].quantile(0.75):,.0f}", "₹{df['price'].quantile(0.25):,.0f} - ₹{df['price'].quantile(0.75):,.0f}")

# Define color constants
palette_definition = """
PRICE_COLOR_SCALE = [
    [0.0, "#10B981"],   # Emerald Green (Low/Budget prices)
    [0.35, "#F59E0B"],  # Warm Orange (Mid-range prices)
    [0.70, "#E11D48"],  # Coral / Crimson Red (Premium)
    [1.0, "#881337"],   # Deep Wine Red (Luxury prices)
]

PRICE_TIER_COLORS = {
    "Budget": "#10B981",       # Emerald Green
    "Mid-Range": "#F59E0B",    # Warm Orange
    "Premium": "#E11D48",      # Crimson Red
    "Luxury": "#881337",       # Wine Red
}
"""

if "PRICE_COLOR_SCALE" not in code:
    code = code.replace('PALETTE_BLUES = ["#EFF6FF", "#DBEAFE", "#BFDBFE", "#93C5FD", "#60A5FA", "#3B82F6", "#2563EB", "#1D4ED8"]', 'PALETTE_BLUES = ["#EFF6FF", "#DBEAFE", "#BFDBFE", "#93C5FD", "#60A5FA", "#3B82F6", "#2563EB", "#1D4ED8"]' + "\n" + palette_definition)

# Update map default color scale to PRICE_COLOR_SCALE
code = code.replace('color_scale="Reds"', 'color_scale=PRICE_COLOR_SCALE')

# Update Price Breakdown by Room Type to use Green for Budget / Orange for Mid / Wine Red for High
room_price_chart = """        rt_stats = df.groupby("room_type")["price"].agg(["mean", "median"]).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Mean Price", 
            x=rt_stats["room_type"], 
            y=rt_stats["mean"], 
            marker_color=["#10B981" if "Shared" in r else ("#F59E0B" if "Private" in r else "#881337") for r in rt_stats["room_type"]],
            text=rt_stats["mean"].apply(lambda v: f"₹{v:,.0f}"), 
            textposition="auto"
        ))
        fig.add_trace(go.Bar(
            name="Median Price", 
            x=rt_stats["room_type"], 
            y=rt_stats["median"], 
            marker_color="#6366F1",
            text=rt_stats["median"].apply(lambda v: f"₹{v:,.0f}"), 
            textposition="auto"
        ))
        fig.update_layout(barmode="group", yaxis_tickprefix="₹")"""

code = re.sub(r'rt_stats = df\.groupby\("room_type"\)\["price"\]\.agg\(\["mean", "median"\]\)\.reset_index\(\).*?fig\.update_layout\(barmode="group", yaxis_tickprefix="₹"\)', room_price_chart, code, flags=re.DOTALL)

# Update Property Formats chart color scale to PRICE_COLOR_SCALE
code = code.replace('color_continuous_scale=PALETTE_BLUES', 'color_continuous_scale=PRICE_COLOR_SCALE')

# Update Opportunity scatter colors
code = code.replace('color_discrete_map={"Underpriced": "#10B981", "Fairly Priced": "#6366F1", "Overpriced": "#FF385C"}', 'color_discrete_map={"Underpriced": "#10B981", "Fairly Priced": "#F59E0B", "Overpriced": "#881337"}')

app_path.write_text(code, encoding="utf-8")
print(">> Applied Green, Orange, and Wine Red price color hierarchy!")
