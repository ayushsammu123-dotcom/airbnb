"""
Redesign Airbnb Dashboard to look like an authentic, clean, human-designed analytics platform.
Removes AI buzzwords, glowing neon badges, and pseudo-telemetry.
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

# Professional Clean CSS (Modern SaaS / BI style - Like Stripe/Tableau)
clean_human_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #1E293B;
    }

    /* Main Canvas */
    .stApp {
        background-color: #F8FAFC;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1320px !important;
    }

    /* Clean, Professional Page Header */
    .dashboard-header {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .dashboard-header h1 {
        color: #0F172A;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0 0 0.3rem 0;
    }
    .dashboard-header p {
        color: #64748B;
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.4;
    }
    .header-meta-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid #F1F5F9;
    }
    .meta-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.6rem;
        background: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #475569;
    }
    .meta-chip-primary {
        background: #EFF6FF;
        border-color: #BFDBFE;
        color: #1D4ED8;
    }

    /* Professional Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        height: 100%;
    }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }
    .metric-subtext {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 500;
    }
    .metric-badge-green {
        display: inline-block;
        padding: 0.1rem 0.35rem;
        background: #DCFCE7;
        color: #166534;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.72rem;
        margin-right: 0.25rem;
    }

    /* Clean Card Sections */
    .content-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    .content-box-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .content-box-desc {
        font-size: 0.8rem;
        color: #64748B;
        margin-bottom: 0.9rem;
    }

    /* Note & Summary Boxes */
    .note-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 3px solid #0284C7;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }
    .note-box-title {
        font-size: 0.84rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.15rem;
    }
    .note-box-body {
        font-size: 0.8rem;
        color: #475569;
        line-height: 1.45;
    }

    /* Clean Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #E2E8F0 !important;
        font-size: 0.83rem;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        color: #FFFFFF !important;
    }
    .stSidebar [data-testid="stVerticalBlock"] .stButton > button {
        background: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        padding: 0.4rem 0.6rem !important;
    }
    .stSidebar [data-testid="stVerticalBlock"] .stButton > button:hover {
        background: #334155 !important;
        border-color: #475569 !important;
    }

    /* Clean Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #F1F5F9;
        padding: 4px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 36px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0 14px;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* Hide standard footer */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
"""

# Replace CSS block in app.py
css_pattern = r'<style>.*?</style>'
new_style_block = f"<style>{clean_human_css}\n    </style>"
code = re.sub(css_pattern, new_style_block, code, flags=re.DOTALL)

# Replace render_hero with clean human header
clean_render_hero = """def render_hero(title: str, subtitle: str, badge: str = "Market Overview"):
    \"\"\"Render clean, human-designed executive header.\"\"\"
    st.markdown(
        f\"\"\"
        <div class="dashboard-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <div class="header-meta-row">
                <span class="meta-chip meta-chip-primary">Delhi NCR Market</span>
                <span class="meta-chip">Currency: INR (₹)</span>
                <span class="meta-chip">27 Micro-Markets</span>
                <span class="meta-chip">9,850 Active Listings Analyzed</span>
            </div>
        </div>
        \"\"\",
        unsafe_allow_html=True,
    )"""

code = re.sub(r'def render_hero\(.*?\n\n\ndef render_kpi', clean_render_hero + "\n\n\ndef render_kpi", code, flags=re.DOTALL)

# Replace render_kpi with clean metric card
clean_render_kpi = """def render_kpi(label: str, value: str, subtext: str = "", tag: str = "", accent: str = "rose", icon: str = ""):
    \"\"\"Render clean, authentic metric scorecard.\"\"\"
    tag_html = f'<span class="metric-badge-green">{tag}</span>' if tag else ""
    return f\"\"\"
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtext">{tag_html}{subtext}</div>
    </div>
    \"\"\""""

code = re.sub(r'def render_kpi\(.*?\n\n\ndef render_card_header', clean_render_kpi + "\n\n\ndef render_card_header", code, flags=re.DOTALL)

# Replace render_card_header and render_insight_card with clean boxes
clean_helpers = """def render_card_header(title: str, desc: str = ""):
    \"\"\"Render clean section header.\"\"\"
    desc_html = f'<div class="content-box-desc">{desc}</div>' if desc else ''
    st.markdown(
        f\"\"\"
        <div class="content-box-title">{title}</div>
        {desc_html}
        \"\"\",
        unsafe_allow_html=True,
    )


def render_insight_card(title: str, text: str, icon: str = ""):
    \"\"\"Render clean summary note.\"\"\"
    st.markdown(
        f\"\"\"
        <div class="note-box">
            <div class="note-box-title">{title}</div>
            <div class="note-box-body">{text}</div>
        </div>
        \"\"\",
        unsafe_allow_html=True,
    )"""

code = re.sub(r'def render_card_header\(.*?\n\n\n# ===========================================================================\n# Sidebar Navigation', clean_helpers + "\n\n\n# ===========================================================================\n# Sidebar Navigation", code, flags=re.DOTALL)

# Clean up sidebar title
clean_sidebar_header = """            <div style="padding: 0.6rem 0 1rem 0; border-bottom: 1px solid #1E293B; margin-bottom: 1rem;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">Airbnb Market Analytics</div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 0.2rem;">Delhi NCR Real Estate & Pricing</div>
            </div>"""

code = re.sub(r'<div class="sidebar-header-box">.*?</div>\s*""",\s*unsafe_allow_html=True,', clean_sidebar_header + '\n            """,\n            unsafe_allow_html=True,', code, flags=re.DOTALL)

# Clean up tab titles and AI terminology
code = code.replace("🗺️ Interactive OpenStreetMap (2D)", "OpenStreetMap View")
code = code.replace("🏙️ 3D Skyline & Revenue Density", "3D Density Map")
code = code.replace("📸 360° Street View Inspector", "Street View & Localities")
code = code.replace("📊 Micro-Market Price Rankings", "Locality Price Rankings")

code = code.replace("⚡ Strategic Executive Insights", "Key Market Takeaways")
code = code.replace("Automated real-time market synthesis", "Summary of revenue drivers and pricing patterns")
code = code.replace("📋 Host Action Matrix", "Host Pricing & Operating Notes")
code = code.replace("Data-driven operational priorities", "Observations from historical booking and review data")
code = code.replace("Highest Revenue Engine", "Top Revenue Locality")
code = code.replace("Superhost Yield Advantage", "Superhost Premium")
code = code.replace("Pricing Upside Opportunity", "Pricing Adjustment Opportunities")

# Replace ui-card class with content-box
code = code.replace("class='ui-card'", "class='content-box'")

app_path.write_text(code, encoding="utf-8")
print(">> Redesigned dashboard to clean, human, authentic BI product style!")
