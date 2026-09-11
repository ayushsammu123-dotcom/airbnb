"""
Professional UI and Sidebar Overhaul for Airbnb Delhi NCR Analytics Suite.
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

# Professional Enterprise CSS
enterprise_css = """
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    * {
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main background */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Main Content Container Spacing */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1350px !important;
    }

    /* Header & Navigation */
    header[data-testid="stHeader"] {
        background: rgba(248, 250, 252, 0.8) !important;
        backdrop-filter: blur(8px) !important;
        z-index: 99 !important;
    }

    /* Top Hero Header */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #334155 100%);
        border-radius: 16px;
        padding: 2.2rem 2.5rem;
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.15);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .hero-banner::after {
        content: "";
        position: absolute;
        top: -60%;
        right: -8%;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(255, 56, 92, 0.3) 0%, rgba(255, 56, 92, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-banner h1 {
        color: #FFFFFF;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0 0 0.4rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .hero-banner p {
        color: #94A3B8;
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
        max-width: 850px;
        line-height: 1.5;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255, 56, 92, 0.15);
        color: #FF385C;
        border: 1px solid rgba(255, 56, 92, 0.3);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }

    /* Live Status Bar */
    .status-bar {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding: 0.75rem 1.2rem;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .status-live {
        background: #ECFDF5;
        color: #059669;
        border: 1px solid #A7F3D0;
    }
    .status-pill-subtle {
        background: #F1F5F9;
        color: #475569;
        border: 1px solid #E2E8F0;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 8px #10B981;
        display: inline-block;
    }

    /* KPI Metric Cards */
    .kpi-container {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1.3rem 1.4rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.2s ease-in-out;
        position: relative;
        overflow: hidden;
        height: 100%;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.06);
        border-color: #CBD5E1;
    }
    .kpi-accent-bar {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
    }
    .kpi-accent-rose    { background: linear-gradient(90deg, #FF385C, #E00B41); }
    .kpi-accent-indigo  { background: linear-gradient(90deg, #6366F1, #4F46E5); }
    .kpi-accent-emerald { background: linear-gradient(90deg, #10B981, #059669); }
    .kpi-accent-amber   { background: linear-gradient(90deg, #F59E0B, #D97706); }
    .kpi-accent-cyan    { background: linear-gradient(90deg, #06B6D4, #0891B2); }
    .kpi-accent-violet  { background: linear-gradient(90deg, #8B5CF6, #7C3AED); }

    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    .kpi-title {
        color: #64748B;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-icon-badge {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }
    .kpi-value {
        color: #0F172A;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin-bottom: 0.35rem;
    }
    .kpi-subtext {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.8rem;
        color: #64748B;
        font-weight: 500;
    }
    .kpi-tag-pos {
        background: #DCFCE7;
        color: #15803D;
        padding: 0.1rem 0.45rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.72rem;
    }

    /* Section Cards */
    .ui-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 1.5rem;
    }
    .ui-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid #F1F5F9;
    }
    .ui-card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .ui-card-desc {
        font-size: 0.85rem;
        color: #64748B;
        margin-top: 0.15rem;
    }

    /* Smart Insights Box */
    .insight-card {
        background: #F8FAFC;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        border-left: 4px solid #FF385C;
        margin-bottom: 0.75rem;
        border: 1px solid #E2E8F0;
        border-left-width: 4px;
        transition: all 0.2s ease;
    }
    .insight-card:hover {
        background: #FFFFFF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .insight-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .insight-body {
        font-size: 0.82rem;
        color: #475569;
        line-height: 1.5;
    }

    /* Banner Alerts */
    .banner-info {
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-radius: 10px;
        padding: 0.85rem 1.1rem;
        color: #0369A1;
        font-size: 0.875rem;
        margin-bottom: 1.2rem;
        line-height: 1.5;
    }
    .banner-success {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 10px;
        padding: 0.85rem 1.1rem;
        color: #166534;
        font-size: 0.875rem;
        margin-bottom: 1.2rem;
        line-height: 1.5;
    }

    /* ------------------------------------------------------------- */
    /* CLEAN SIDEBAR STYLING - NO OVERLAPPING, CLEAN CONTRAST        */
    /* ------------------------------------------------------------- */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* Sidebar Text & Labels */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #E2E8F0 !important;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Sidebar Inputs (Selectbox, Multiselect, Inputs) */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* Multiselect Tags */
    section[data-testid="stSidebar"] span[data-baseweb="tag"] {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border-radius: 6px;
        border: 1px solid #475569;
    }

    /* Radio Group */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        background-color: #1E293B !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label span {
        color: #F1F5F9 !important;
    }

    /* Targeted User Preset Buttons inside Sidebar - CLEAN & ISOLATED */
    .stSidebar [data-testid="stVerticalBlock"] .stButton > button {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        padding: 0.45rem 0.6rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }
    .stSidebar [data-testid="stVerticalBlock"] .stButton > button:hover {
        background: linear-gradient(135deg, #FF385C 0%, #E11D48 100%) !important;
        border-color: #FF385C !important;
        box-shadow: 0 4px 12px rgba(255, 56, 92, 0.35) !important;
        transform: translateY(-1px);
    }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.875rem;
        padding: 0 16px;
        background-color: transparent;
        border: none;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    /* Dataframe Container */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }

    /* Hide standard footer */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
"""

# Replace CSS in app.py
css_pattern = r'<style>.*?</style>'
new_style_block = f"<style>{enterprise_css}\n    </style>"
code = re.sub(css_pattern, new_style_block, code, flags=re.DOTALL)

app_path.write_text(code, encoding="utf-8")
print(">> Successfully polished entire UI and fixed sidebar button isolation!")
