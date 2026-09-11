"""
Update sidebar CSS and layout for high visibility and buttons in dashboard/app.py.
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

# Replacement modern CSS for sidebar
sidebar_css_new = """    /* Sidebar Styling - Enterprise SaaS Dark Mode */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
        padding-top: 1rem;
    }
    
    /* Sidebar Headers & Labels */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: #E2E8F0 !important;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Sidebar Input Fields & Selectboxes */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border-color: #334155 !important;
        color: #FFFFFF !important;
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="popover"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="popover"] li {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="popover"] li:hover {
        background-color: #334155 !important;
        color: #FF385C !important;
    }

    /* Multiselect Tags */
    section[data-testid="stSidebar"] span[data-baseweb="tag"] {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border-radius: 6px;
        border: 1px solid #475569;
    }
    section[data-testid="stSidebar"] span[data-baseweb="tag"] span {
        color: #F8FAFC !important;
    }

    /* Radio Buttons */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        background-color: #1E293B;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label span {
        color: #F1F5F9 !important;
        font-size: 0.85rem;
    }

    /* Buttons inside Sidebar */
    section[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        padding: 0.5rem 0.8rem !important;
        transition: all 0.2s ease !important;
        width: 100%;
        margin-bottom: 0.4rem;
    }
    section[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #FF385C 0%, #E11D48 100%) !important;
        border-color: #FF385C !important;
        box-shadow: 0 4px 12px rgba(255, 56, 92, 0.35) !important;
        transform: translateY(-1px);
    }

    /* Sliders */
    section[data-testid="stSidebar"] div[data-testid="stSlider"] {
        padding: 0.2rem 0;
    }
    section[data-testid="stSidebar"] div[data-testid="stSlider"] label {
        color: #E2E8F0 !important;
    }

    /* Collapse button */
    button[data-testid="stSidebarCollapseButton"] {
        color: #FFFFFF !important;
        background: #1E293B !important;
        border-radius: 8px !important;
    }
    button[data-testid="stSidebarCollapseButton"]:hover {
        background: #334155 !important;
    }

    /* Sidebar Divider */
    section[data-testid="stSidebar"] hr {
        border-color: #1E293B !important;
        margin: 1rem 0 !important;
    }

    .sidebar-header-box {
        padding: 0.5rem 0 1rem 0;
        text-align: left;
    }
    .sidebar-header-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .sidebar-header-subtitle {
        font-size: 0.75rem;
        color: #94A3B8 !important;
        margin-top: 0.2rem;
    }"""

# Replace old sidebar CSS
code = re.sub(r'/\* Sidebar Styling \*/.*?\.sidebar-header-subtitle\s*\{[^}]*\}', sidebar_css_new, code, flags=re.DOTALL)

# Replacement render_sidebar function with quick presets and enhanced visibility
sidebar_func_new = """def render_sidebar(df: pd.DataFrame):
    \"\"\"Render high-contrast sidebar with navigation, quick presets, and filters.\"\"\"
    with st.sidebar:
        st.markdown(
            \"\"\"
            <div class="sidebar-header-box">
                <div class="sidebar-header-title">🏠 Airbnb Analytics</div>
                <div class="sidebar-header-subtitle">Delhi NCR Pricing & Revenue Intelligence</div>
            </div>
            \"\"\",
            unsafe_allow_html=True,
        )

        nav_options = [
            "🏠 Executive Overview",
            "💰 Pricing Analysis",
            "💵 Revenue Analysis",
            "🗺️ Location Intelligence",
            "👤 Host Analytics",
            "📈 Demand Analysis",
            "🔍 Listing Explorer",
            "🎯 Pricing Opportunity",
            "🤖 ML & Advanced Analytics",
            "🔧 Data Quality",
        ]
        
        page = st.selectbox(
            "Select Analytics Module",
            nav_options,
            key="nav_page",
        )

        st.markdown("---")
        st.markdown("<p style='font-size:0.8rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em;'>⚡ Quick Regional Presets</p>", unsafe_allow_html=True)
        
        col_p1, col_p2 = st.columns(2)
        preset_south = col_p1.button("🏙️ South Delhi", use_container_width=True)
        preset_gurugram = col_p2.button("🏢 Gurugram DLF", use_container_width=True)
        col_p3, col_p4 = st.columns(2)
        preset_superhost = col_p3.button("⭐ Superhosts", use_container_width=True)
        preset_reset = col_p4.button("🔄 Reset All", use_container_width=True)

        st.markdown("<p style='font-size:0.8rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em; margin-top:0.6rem;'>🎛 Active Filters</p>", unsafe_allow_html=True)

        # Region / Zone Filter
        all_zones = sorted(df["neighbourhood_group"].dropna().unique().tolist()) if "neighbourhood_group" in df.columns else []
        default_zones = []
        if preset_south:
            default_zones = ["South Delhi"]
        elif preset_gurugram:
            default_zones = ["Gurugram"]
        elif preset_reset:
            default_zones = []

        selected_zones = st.multiselect("Delhi NCR Zone", all_zones, default=default_zones, key="f_zone")

        # Neighbourhood Filter
        avail_neighs = df[df["neighbourhood_group"].isin(selected_zones)]["neighbourhood"].unique() if selected_zones else df["neighbourhood"].unique()
        selected_neighs = st.multiselect("Micro-Market / Locality", sorted(avail_neighs.tolist()), default=[], key="f_neigh")

        # Room Type
        room_types = sorted(df["room_type"].dropna().unique().tolist())
        selected_room_types = st.multiselect("Room Type", room_types, default=[], key="f_room")

        # Price Slider
        p_min = int(df["price"].min())
        p_max = int(df["price"].quantile(0.99))
        price_range = st.slider("Nightly Price (₹)", p_min, p_max, (p_min, p_max), step=250, key="f_price")

        # Superhost
        default_sh_idx = 1 if preset_superhost else 0
        sh_choice = st.radio("Host Quality Filter", ["All Listings", "Superhosts Only", "Regular Hosts Only"], index=default_sh_idx, key="f_sh")

        # Availability
        avail_range = st.slider("Annual Availability (Days)", 0, 365, (0, 365), key="f_avail")

        st.markdown("---")
        st.markdown(
            \"\"\"
            <div style='background:rgba(30, 41, 59, 0.8); border:1px solid #334155; padding:0.8rem; border-radius:8px; font-size:0.75rem; color:#94A3B8;'>
                ⚠️ <b>Revenue Disclaimer:</b> Metrics use the availability-proxy model and are calibrated for the Delhi NCR market.
            </div>
            \"\"\",
            unsafe_allow_html=True,
        )

    # Apply global filtering
    filtered = df.copy()
    if selected_zones:
        filtered = filtered[filtered["neighbourhood_group"].isin(selected_zones)]
    if selected_neighs:
        filtered = filtered[filtered["neighbourhood"].isin(selected_neighs)]
    if selected_room_types:
        filtered = filtered[filtered["room_type"].isin(selected_room_types)]

    filtered = filtered[(filtered["price"] >= price_range[0]) & (filtered["price"] <= price_range[1])]
    filtered = filtered[(filtered["availability_365"] >= avail_range[0]) & (filtered["availability_365"] <= avail_range[1])]

    if sh_choice == "Superhosts Only":
        filtered = filtered[filtered["host_is_superhost"] == True]
    elif sh_choice == "Regular Hosts Only":
        filtered = filtered[filtered["host_is_superhost"] == False]

    return page, filtered"""

# Replace old render_sidebar
code = re.sub(r'def render_sidebar\(df: pd\.DataFrame\):.*?return page, filtered', sidebar_func_new, code, flags=re.DOTALL)

app_path.write_text(code, encoding="utf-8")
print(">> Successfully replaced sidebar with high-contrast UI and buttons!")
