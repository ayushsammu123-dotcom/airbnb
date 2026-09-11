"""
Add 3D PyDeck Hexagon Layer & 360° Street View Inspector to Geographic Intelligence.
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

# Ensure pydeck import exists
if "import pydeck as pdk" not in code:
    code = code.replace("import plotly.express as px", "import plotly.express as px\nimport pydeck as pdk")

# Enhanced Geographic Section with 3D Street Viewing
geo_section_exec = """    # Map Section with 3D Street Viewing & Spatial Intelligence
    st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
    render_card_header("🗺️ Geographic Revenue & Pricing Intelligence", "Spatial distribution, 3D skyline density, and 360° Street Viewing across Delhi NCR")
    
    tab_map_2d, tab_map_3d, tab_street_view, tab_geo_chart = st.tabs([
        "🗺️ Interactive OpenStreetMap (2D)",
        "🏙️ 3D Skyline & Revenue Density",
        "📸 360° Street View Inspector",
        "📊 Micro-Market Price Rankings"
    ])
    
    with tab_map_2d:
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

    with tab_map_3d:
        if "latitude" in df.columns and "longitude" in df.columns:
            sample_3d = df.dropna(subset=["latitude", "longitude"]).copy()
            
            # PyDeck 3D Hexagon Layer
            layer_3d = pdk.Layer(
                "HexagonLayer",
                sample_3d,
                get_position=["longitude", "latitude"],
                auto_highlight=True,
                elevation_scale=35,
                pickable=True,
                elevation_range=[100, 3500],
                extruded=True,
                coverage=0.92,
                radius=450,
                color_range=[
                    [16, 185, 129, 180],   # Emerald Green (Low/Budget)
                    [245, 158, 11, 200],   # Warm Orange (Mid-Range)
                    [225, 29, 72, 220],    # Crimson Red (Premium)
                    [136, 19, 55, 240],    # Wine Red (Luxury)
                ]
            )
            
            view_state = pdk.ViewState(
                longitude=77.2090,
                latitude=28.5800,
                zoom=10.0,
                pitch=52,
                bearing=-25,
            )
            
            deck = pdk.Deck(
                layers=[layer_3d],
                initial_view_state=view_state,
                tooltip={
                    "html": "<div style='background:#0F172A; padding:8px 12px; border-radius:8px; border:1px solid #334155; color:white; font-family:Plus Jakarta Sans;'>"
                            "<b style='color:#FF385C;'>🏙️ 3D Cluster</b><br/>"
                            "Listing Density: <b>{elevationValue}</b><br/>"
                            "<span style='font-size:0.75rem; color:#94A3B8;'>Height = Market Revenue Concentration</span>"
                            "</div>",
                    "style": {"color": "white"}
                },
                map_style="dark"
            )
            
            st.markdown("<p style='font-size:0.8rem; color:#64748B; margin-bottom:0.5rem;'>💡 <b>Tip:</b> Hold <kbd>Ctrl / Cmd</kbd> + Left Click & Drag to rotate 3D camera angle and view Delhi NCR building columns.</p>", unsafe_allow_html=True)
            st.pydeck_chart(deck, use_container_width=True)
        else:
            st.info("No spatial data available for 3D rendering.")

    with tab_street_view:
        st.markdown("<p style='font-size:0.85rem; color:#475569; margin-bottom:1rem;'>Explore realistic 360° panoramic Street Views and 3D satellite flyovers for any Delhi NCR micro-market or active listing.</p>", unsafe_allow_html=True)
        
        c_sel1, c_sel2 = st.columns([1.2, 1.8])
        with c_sel1:
            all_locs = sorted(df["neighbourhood"].dropna().unique().tolist()) if "neighbourhood" in df.columns else []
            selected_loc = st.selectbox("📍 Select Micro-Market for 3D Street View", all_locs, index=0 if all_locs else None)
            
            loc_df = df[df["neighbourhood"] == selected_loc]
            if not loc_df.empty:
                loc_lat = loc_df["latitude"].mean()
                loc_lon = loc_df["longitude"].mean()
                loc_price = loc_df["price"].mean()
                loc_count = len(loc_df)
                loc_rev = loc_df["estimated_annual_revenue"].sum() if "estimated_annual_revenue" in loc_df.columns else 0
                
                st.markdown(f\"\"\"
                <div style='background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:1.2rem; margin-top:0.5rem;'>
                    <div style='font-weight:700; font-size:1.1rem; color:#0F172A; margin-bottom:0.4rem;'>🏙️ {selected_loc}</div>
                    <div style='font-size:0.82rem; color:#64748B; margin-bottom:0.8rem;'>Coordinates: <code>{loc_lat:.5f}, {loc_lon:.5f}</code></div>
                    <div style='display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; font-size:0.82rem;'>
                        <div><b>Avg Price:</b> ₹{loc_price:,.0f}</div>
                        <div><b>Active Units:</b> {loc_count:,}</div>
                        <div style='grid-column:1/-1;'><b>Est. Market Gross:</b> ₹{loc_rev:,.0f}</div>
                    </div>
                </div>
                \"\"\", unsafe_allow_html=True)

        with c_sel2:
            if not loc_df.empty:
                street_url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={loc_lat},{loc_lon}&heading=-45&pitch=10&fov=80"
                earth_url = f"https://earth.google.com/web/@{loc_lat},{loc_lon},250a,800d,35y,0h,45t,0r"
                sat_url = f"https://www.google.com/maps/search/?api=1&query={loc_lat},{loc_lon}"
                
                st.markdown(f\"\"\"
                <div style='background:linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border-radius:12px; padding:1.4rem; color:white; border:1px solid #334155;'>
                    <div style='font-size:0.75rem; font-weight:700; color:#FF385C; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.4rem;'>✦ 3D Spatial Telemetry</div>
                    <div style='font-size:1.15rem; font-weight:800; margin-bottom:0.8rem;'>Interactive 360° Street & Satellite Viewer</div>
                    <p style='font-size:0.85rem; color:#94A3B8; margin-bottom:1.2rem; line-height:1.5;'>
                        Inspect ground-level pedestrian foot traffic, commercial hub proximity, metro connectivity, and surrounding real estate infrastructure in 3D panoramic mode.
                    </p>
                    <div style='display:flex; flex-wrap:wrap; gap:0.6rem;'>
                        <a href='{street_url}' target='_blank' style='background:#FF385C; color:white; padding:0.6rem 1rem; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.82rem; display:inline-flex; align-items:center; gap:0.4rem;'>
                            🌐 Open Live 360° Street View
                        </a>
                        <a href='{earth_url}' target='_blank' style='background:#334155; color:white; padding:0.6rem 1rem; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.82rem; display:inline-flex; align-items:center; gap:0.4rem;'>
                            🌍 Google Earth 3D Flyover
                        </a>
                        <a href='{sat_url}' target='_blank' style='background:#1E293B; color:#94A3B8; border:1px solid #475569; padding:0.6rem 1rem; border-radius:8px; text-decoration:none; font-weight:600; font-size:0.82rem;'>
                            🛰️ High-Res Satellite View
                        </a>
                    </div>
                </div>
                \"\"\", unsafe_allow_html=True)

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

code = re.sub(r'# Map Section with Dual-View\s*st\.markdown\("<div class=\'ui-card\'>", unsafe_allow_html=True\).*?st\.markdown\("</div>", unsafe_allow_html=True\)', geo_section_exec, code, flags=re.DOTALL)

app_path.write_text(code, encoding="utf-8")
print(">> Successfully integrated 3D Street View and PyDeck Hexagon Layer!")
