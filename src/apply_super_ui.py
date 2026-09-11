"""
UI/UX Elevation script for Airbnb Analytics Platform (Delhi NCR).
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

# 1. Update Sidebar labeling from 'Borough' to 'Delhi NCR Zone'
code = code.replace('selected_boroughs = st.multiselect("Borough",', 'selected_boroughs = st.multiselect("Delhi NCR Zone",')

# 2. Add Live Status Bar helper in CSS and component
css_upgrade = """
    /* Live Status Bar */
    .status-bar {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding: 0.6rem 1rem;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.7rem;
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
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* Comparison Card */
    .compare-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .compare-header {
        font-size: 1rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.6rem;
    }
"""

if ".status-bar" not in code:
    code = code.replace("/* Hide Streamlit Header / Footer Branding */", css_upgrade + "\n    /* Hide Streamlit Header / Footer Branding */")

# Add Live Status Bar to render_hero
render_hero_new = """def render_hero(title: str, subtitle: str, badge: str = "Analytics Suite"):
    \"\"\"Render top hero banner with live status indicators.\"\"\"
    st.markdown(
        f\"\"\"
        <div class="hero-banner">
            <div class="hero-badge">✦ {badge}</div>
            <h1>🏠 {title}</h1>
            <p>{subtitle}</p>
        </div>
        <div class="status-bar">
            <div class="status-pill status-live"><span class="status-dot"></span> LIVE ENGINE ACTIVE</div>
            <div class="status-pill status-pill-subtle">📍 27 Delhi NCR Micro-Markets</div>
            <div class="status-pill status-pill-subtle">🇮🇳 Currency: INR (₹)</div>
            <div class="status-pill status-pill-subtle">⚡ Real-time ML Pricing Model</div>
        </div>
        \"\"\",
        unsafe_allow_html=True,
    )"""

code = re.sub(r'def render_hero\(title: str, subtitle: str, badge: str = "Analytics Suite"\):.*?unsafe_allow_html=True,\s*\)', render_hero_new, code, flags=re.DOTALL)

app_path.write_text(code, encoding="utf-8")
print(">> Successfully applied UI elevation upgrades!")
