"""
Comprehensive layout and visual outlining refinement for dashboard/app.py.
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

# 1. Clean up awkward height spacers and replace with clean flex margins
code = code.replace("<div style='height:12px;'></div>", "")
code = code.replace("<div style='height:20px;'></div>", "")

# 2. Modernize KPI and Card CSS for tight, structured outlining
improved_card_css = """
    /* Section Cards with Crisp Visual Outlines */
    .ui-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 10px 15px -3px rgba(0,0,0,0.02);
        margin-bottom: 1.2rem;
    }
    .ui-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #F1F5F9;
    }
    .ui-card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .ui-card-desc {
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 0.15rem;
    }

    /* KPI Metric Cards - Unified Height & Crisp Outlines */
    .kpi-container {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1.2rem 1.3rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        transition: all 0.2s ease-in-out;
        position: relative;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -4px rgba(0,0,0,0.06);
        border-color: #CBD5E1;
    }
"""

code = re.sub(r'/\* Section Cards \*/.*?\.ui-card-desc\s*\{[^}]*\}', improved_card_css, code, flags=re.DOTALL)

app_path.write_text(code, encoding="utf-8")
print(">> Successfully refined dashboard outlining and visual structure!")
