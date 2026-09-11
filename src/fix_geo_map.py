"""
Bulletproof Geographic Map Engine for Delhi NCR with OpenStreetMap and fallback tabs.
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

# Replacement render_spatial_map implementation
spatial_map_new = """def render_spatial_map(df, lat_col="latitude", lon_col="longitude", color_col="price", color_scale=None, height=520, zoom=9.8):
    \"\"\"
    Bulletproof OpenStreetMap scatter map centered on Delhi NCR with 100% reliability.
    \"\"\"
    if color_scale is None:
        color_scale = PRICE_COLOR_SCALE

    # Clean valid coordinates
    valid_geo = df.dropna(subset=[lat_col, lon_col]).copy()
    if valid_geo.empty:
        fig = go.Figure()
        fig.add_annotation(text="No geographic coordinates available in current filter.", showarrow=False, font=dict(size=14, color="#64748B"))
        apply_chart_theme(fig, height=height)
        return fig

    # 1. Try px.scatter_map (Plotly 6+ / 7+)
    if hasattr(px, "scatter_map"):
        try:
            fig = px.scatter_map(
                valid_geo,
                lat=lat_col,
                lon=lon_col,
                color=color_col,
                color_continuous_scale=color_scale,
                hover_name="neighbourhood" if "neighbourhood" in valid_geo.columns else None,
                hover_data={"room_type": True, color_col: ":,.0f", lat_col: False, lon_col: False},
                map_style="open-street-map",
                zoom=zoom,
                center=dict(lat=28.58, lon=77.20),
                height=height,
            )
            fig.update_traces(marker=dict(size=9, opacity=0.85))
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            return fig
        except Exception:
            pass

    # 2. Try px.scatter_mapbox (Plotly 5-)
    if hasattr(px, "scatter_mapbox"):
        try:
            fig = px.scatter_mapbox(
                valid_geo,
                lat=lat_col,
                lon=lon_col,
                color=color_col,
                color_continuous_scale=color_scale,
                hover_name="neighbourhood" if "neighbourhood" in valid_geo.columns else None,
                hover_data={"room_type": True, color_col: ":,.0f", lat_col: False, lon_col: False},
                mapbox_style="open-street-map",
                zoom=zoom,
                center=dict(lat=28.58, lon=77.20),
                height=height,
            )
            fig.update_traces(marker=dict(size=9, opacity=0.85))
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            return fig
        except Exception:
            pass

    # 3. Universal Fallback
    fig = px.scatter(
        valid_geo,
        x=lon_col,
        y=lat_col,
        color=color_col,
        color_continuous_scale=color_scale,
        hover_name="neighbourhood" if "neighbourhood" in valid_geo.columns else None,
        hover_data={"room_type": True, color_col: True},
        height=height,
    )
    fig.update_traces(marker=dict(size=9, opacity=0.85))
    apply_chart_theme(fig, height=height, title="Spatial Coordinates Scatter (Longitude vs Latitude)")
    return fig"""

# Replace render_spatial_map in app.py
code = re.sub(r'def render_spatial_map\(.*?\n\n\n# ===========================================================================', spatial_map_new + "\n\n\n# ===========================================================================", code, flags=re.DOTALL)

# Update Executive Overview map section with tabs
map_section_exec = """    # Map Section with Dual-View
    st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
    render_card_header("🗺️ Geographic Revenue & Pricing Intelligence", "Spatial distribution and pricing power across Delhi NCR")
    
    tab_map, tab_geo_chart = st.tabs(["🗺️ Interactive OpenStreetMap", "📊 Micro-Market Price Distribution"])
    
    with tab_map:
        if "latitude" in df.columns and "longitude" in df.columns:
            sample_map = df.dropna(subset=["latitude", "longitude"]).head(3000)
            fig_map = render_spatial_map(
                sample_map,
                lat_col="latitude",
                lon_col="longitude",
                color_col="price",
                color_scale=PRICE_COLOR_SCALE,
                height=520,
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No spatial coordinates available in active dataset.")

    with tab_geo_chart:
        if "neighbourhood" in df.columns:
            geo_summary = df.groupby("neighbourhood").agg(
                Avg_Price=("price", "mean"),
                Median_Price=("price", "median"),
                Listings=("listing_id", "count"),
                Total_Revenue=("estimated_annual_revenue", "sum")
            ).reset_index().sort_values("Avg_Price", ascending=False).head(15)
            
            fig_geo = px.bar(
                geo_summary,
                x="Avg_Price",
                y="neighbourhood",
                orientation="h",
                color="Avg_Price",
                color_continuous_scale=PRICE_COLOR_SCALE,
                text=geo_summary["Avg_Price"].apply(lambda v: f"₹{v:,.0f}"),
            )
            fig_geo.update_layout(coloraxis_showscale=False, xaxis_tickprefix="₹")
            fig_geo.update_yaxes(categoryorder="total ascending")
            apply_chart_theme(fig_geo, height=480, title="Top Micro-Markets Ranked by Average Nightly Rate")
            st.plotly_chart(fig_geo, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)"""

code = re.sub(r'# Map Section\s*st\.markdown\("<div class=\'ui-card\'>", unsafe_allow_html=True\).*?st\.markdown\("</div>", unsafe_allow_html=True\)', map_section_exec, code, flags=re.DOTALL)

app_path.write_text(code, encoding="utf-8")
print(">> Successfully updated map engine to OpenStreetMap with fallback views!")
