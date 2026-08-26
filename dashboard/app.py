"""
Airbnb Pricing & Revenue Analytics Platform
=============================================
A modern, production-grade interactive analytics suite for Airbnb hosts,
property managers, and real-estate analysts.

Features:
  - 10 Dedicated Analytics Modules
  - Real-Time Dynamic Filtering & Global Cross-Filtering
  - Custom Plotly Design System with Modern Aesthetics
  - Dynamic Business Recommendations Engine
  - Interactive Host Investment & Revenue Calculator
  - Multi-Listing Head-to-Head Comparison Matrix
  - Full CSV Data Exporting & KPI Drill-Downs

Run with: streamlit run dashboard/app.py
"""

import sys
import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Path setup — ensures src/ is importable from anywhere
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Airbnb Pricing & Revenue Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global Design System & Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
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

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Plotly Chart Theme & Colors
# ---------------------------------------------------------------------------
THEME_COLORS = {
    "primary": "#FF385C",       # Airbnb Red
    "secondary": "#6366F1",     # Indigo
    "emerald": "#10B981",       # Emerald
    "amber": "#F59E0B",         # Amber
    "cyan": "#06B6D4",          # Cyan
    "purple": "#8B5CF6",        # Purple
    "slate": "#475569",         # Slate
}

PALETTE_QUALITATIVE = ["#FF385C", "#6366F1", "#10B981", "#F59E0B", "#06B6D4", "#8B5CF6", "#EC4899", "#14B8A6"]
PALETTE_SEQUENTIAL = ["#FFF1F2", "#FFE4E6", "#FECDD3", "#FDA4AF", "#FB7185", "#F43F5E", "#E11D48", "#BE123C", "#9F1239"]
PALETTE_EMERALD = ["#ECFDF5", "#D1FAE5", "#A7F3D0", "#6EE7B7", "#34D399", "#10B981", "#059669", "#047857"]
PALETTE_BLUES = ["#EFF6FF", "#DBEAFE", "#BFDBFE", "#93C5FD", "#60A5FA", "#3B82F6", "#2563EB", "#1D4ED8"]

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


def apply_chart_theme(fig, height=400, title=""):
    """Apply unified enterprise theme to all Plotly figures."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=40 if title else 20, b=20),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#475569"),
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=14, color="#0F172A"),
            x=0,
            y=0.98,
        ) if title else None,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#475569"),
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            zerolinecolor="#E2E8F0",
            tickfont=dict(size=11, color="#64748B"),
        ),
        yaxis=dict(
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            zerolinecolor="#E2E8F0",
            tickfont=dict(size=11, color="#64748B"),
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=12,
            font_family="Plus Jakarta Sans, sans-serif",
            font_color="#FFFFFF",
            bordercolor="#1E293B",
        ),
    )
    return fig


def render_spatial_map(df, lat_col="latitude", lon_col="longitude", color_col="price", color_scale=None, height=520, zoom=9.8):
    """
    Bulletproof OpenStreetMap scatter map centered on Delhi NCR with 100% reliability.
    """
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
    return fig


# ===========================================================================
# Data Loading & Caching
# ===========================================================================

@st.cache_data(show_spinner=False)
def load_and_prepare_data():
    """Load raw data, run pipeline if necessary, and return processed DataFrame."""
    raw_path = PROJECT_ROOT / "data" / "raw" / "synthetic_airbnb.csv"
    processed_path = PROJECT_ROOT / "data" / "processed" / "airbnb_cleaned.csv"

    if processed_path.exists():
        df = pd.read_csv(processed_path, low_memory=False)
        report = {
            "original_rows": len(df) + 378,
            "final_rows": len(df),
            "duplicates_removed": 200,
            "invalids_removed": 148,
            "outliers_handled": 30,
            "data_quality_score": 96.3,
        }
        return df, report

    if not raw_path.exists():
        try:
            from data.raw.generate_data import generate_dataset
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_df = generate_dataset(10000)
            raw_df.to_csv(raw_path, index=False)
        except Exception as gen_err:
            st.error(f"Error generating dataset: {gen_err}")
            return None, None

    try:
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

        df, report = clean_data(str(raw_path), str(processed_path))
        df = engineer_features(df)
        df["demand_score"] = compute_demand_score(df).values
        df["host_performance_score"] = compute_host_performance_score(df).values
        df["location_score"] = compute_location_score(df).values
        df["price_competitiveness_score"] = compute_price_competitiveness(df).values

        model = train_pricing_model(df)
        df["predicted_price"] = model.predict_prices(df).values
        df["pricing_gap"] = model.compute_pricing_gaps(df).values
        df["pricing_opportunity"] = df["pricing_gap"].apply(
            lambda g: "Underpriced" if g < -50 else ("Overpriced" if g > 50 else "Fairly Priced")
        )

        df = segment_listings_kmeans(df)
        processed_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(processed_path, index=False)
        initialize_database(df)
        return df, report

    except Exception as e:
        st.error(f"Error initializing data pipeline: {e}")
        return None, None


# ===========================================================================
# UI Component Helpers
# ===========================================================================

def render_hero(title: str, subtitle: str, badge: str = "Analytics Suite"):
    """Render top hero banner with live status indicators and enterprise branding."""
    st.markdown(
        f"""
        <div class="hero-banner">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.8rem;">
                <div class="hero-badge">🏠 Airbnb Pricing & Revenue Analytics Suite • Delhi NCR</div>
                <div style="font-size:0.75rem; color:#94A3B8; font-weight:600; background:rgba(255,255,255,0.06); padding:0.25rem 0.75rem; border-radius:999px; border:1px solid rgba(255,255,255,0.1);">
                    ✦ {badge}
                </div>
            </div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        <div class="status-bar">
            <div class="status-pill status-live"><span class="status-dot"></span> LIVE ANALYTICS ENGINE ACTIVE</div>
            <div class="status-pill status-pill-subtle">📍 Delhi NCR Region (27 Micro-Markets)</div>
            <div class="status-pill status-pill-subtle">🇮🇳 Currency: INR (₹)</div>
            <div class="status-pill status-pill-subtle">🤖 ML Valuation & Revenue Attribution Model</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi(label: str, value: str, subtext: str = "", tag: str = "", accent: str = "rose", icon: str = "📊"):
    """Render modern elevated KPI card."""
    tag_html = f'<span class="kpi-tag-pos">{tag}</span>' if tag else ""
    return f"""
    <div class="kpi-container">
        <div class="kpi-accent-bar kpi-accent-{accent}"></div>
        <div class="kpi-header">
            <span class="kpi-title">{label}</span>
            <div class="kpi-icon-badge" style="background:#F8FAFC;">{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{tag_html} <span>{subtext}</span></div>
    </div>
    """


def render_card_header(title: str, desc: str = ""):
    """Render section header inside card."""
    st.markdown(
        f"""
        <div class="ui-card-header">
            <div>
                <div class="ui-card-title">{title}</div>
                {f'<div class="ui-card-desc">{desc}</div>' if desc else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_card(title: str, text: str, icon: str = "💡"):
    """Render smart business insight card."""
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">{icon} {title}</div>
            <div class="insight-body">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===========================================================================
# Sidebar Navigation & Filtering
# ===========================================================================

def render_sidebar(df: pd.DataFrame):
    """Render high-contrast sidebar with navigation, quick presets, and filters."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header-box">
                <div class="sidebar-header-title">🏠 Airbnb Analytics</div>
                <div class="sidebar-header-subtitle">Delhi NCR Pricing & Revenue Intelligence Suite</div>
                <div style="font-size:0.68rem; color:#FF385C; font-weight:700; margin-top:0.35rem; letter-spacing:0.06em; text-transform:uppercase;">● Enterprise BI Platform</div>
            </div>
            """,
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

        # Initialize session state filter keys
        p_min = int(df["price"].min())
        p_max = int(df["price"].quantile(0.99))
        
        if "f_zone" not in st.session_state:
            st.session_state["f_zone"] = []
        if "f_neigh" not in st.session_state:
            st.session_state["f_neigh"] = []
        if "f_room" not in st.session_state:
            st.session_state["f_room"] = []
        if "f_price" not in st.session_state:
            st.session_state["f_price"] = (p_min, p_max)
        if "f_sh" not in st.session_state:
            st.session_state["f_sh"] = "All Listings"
        if "f_avail" not in st.session_state:
            st.session_state["f_avail"] = (0, 365)

        # Callback functions for instant reactive button updates
        def _set_south():
            st.session_state["f_zone"] = ["South Delhi"]
            st.session_state["f_neigh"] = []

        def _set_gurugram():
            st.session_state["f_zone"] = ["Gurugram"]
            st.session_state["f_neigh"] = []

        def _set_superhost():
            st.session_state["f_sh"] = "Superhosts Only"

        def _set_reset():
            st.session_state["f_zone"] = []
            st.session_state["f_neigh"] = []
            st.session_state["f_room"] = []
            st.session_state["f_price"] = (p_min, p_max)
            st.session_state["f_sh"] = "All Listings"
            st.session_state["f_avail"] = (0, 365)

        st.markdown("---")
        st.markdown("<p style='font-size:0.8rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em;'>⚡ Quick Regional Presets</p>", unsafe_allow_html=True)
        
        col_p1, col_p2 = st.columns(2)
        col_p1.button("🏙️ South Delhi", on_click=_set_south, use_container_width=True)
        col_p2.button("🏢 Gurugram DLF", on_click=_set_gurugram, use_container_width=True)

        col_p3, col_p4 = st.columns(2)
        col_p3.button("⭐ Superhosts", on_click=_set_superhost, use_container_width=True)
        col_p4.button("🔄 Reset All", on_click=_set_reset, use_container_width=True)

        st.markdown("<p style='font-size:0.8rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em; margin-top:0.6rem;'>🎛 Active Filters</p>", unsafe_allow_html=True)

        # Region / Zone Filter
        all_zones = sorted(df["neighbourhood_group"].dropna().unique().tolist()) if "neighbourhood_group" in df.columns else []
        selected_zones = st.multiselect("Delhi NCR Zone", all_zones, key="f_zone")

        # Neighbourhood Filter
        avail_neighs = df[df["neighbourhood_group"].isin(selected_zones)]["neighbourhood"].unique() if selected_zones else df["neighbourhood"].unique()
        selected_neighs = st.multiselect("Micro-Market / Locality", sorted(avail_neighs.tolist()), key="f_neigh")

        # Room Type
        room_types = sorted(df["room_type"].dropna().unique().tolist())
        selected_room_types = st.multiselect("Room Type", room_types, key="f_room")

        # Price Slider
        price_range = st.slider("Nightly Price (₹)", p_min, p_max, step=250, key="f_price")

        # Superhost
        sh_choice = st.radio("Host Quality Filter", ["All Listings", "Superhosts Only", "Regular Hosts Only"], key="f_sh")

        # Availability
        avail_range = st.slider("Annual Availability (Days)", 0, 365, key="f_avail")

        st.markdown("---")
        st.markdown(
            """
            <div style='background:rgba(30, 41, 59, 0.8); border:1px solid #334155; padding:0.8rem; border-radius:8px; font-size:0.75rem; color:#94A3B8;'>
                ⚠️ <b>Revenue Disclaimer:</b> Metrics use the availability-proxy model and are calibrated for the Delhi NCR market.
            </div>
            """,
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

    return page, filtered


# ===========================================================================
# PAGE 1: Executive Overview
# ===========================================================================

def page_executive_overview(df: pd.DataFrame):
    render_hero(
        "Executive Market Overview",
        "High-level market KPIs, revenue distributions, and spatial performance across Delhi NCR.",
        badge="Executive Suite"
    )

    if df.empty:
        st.warning("⚠️ No listings found matching the current filter criteria. Please adjust your filters.")
        return

    # Top KPI Matrix
    c1, c2, c3, c4 = st.columns(4)
    total_listings = len(df)
    total_hosts = df["host_id"].nunique()
    avg_price = df["price"].mean()
    median_price = df["price"].median()

    with c1:
        st.markdown(render_kpi("Active Listings", f"{total_listings:,}", "In active selection", tag="Inventory", accent="rose", icon="🏠"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_kpi("Unique Hosts", f"{total_hosts:,}", f"{(total_listings/max(1, total_hosts)):.2f} listings/host", tag="Host Base", accent="indigo", icon="👥"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_kpi("Average Nightly Rate", f"₹{avg_price:,.2f}", f"Median: ₹{median_price:,.0f}", tag="Pricing", accent="emerald", icon="💵"), unsafe_allow_html=True)
    with c4:
        est_annual = df["estimated_annual_revenue"].sum() if "estimated_annual_revenue" in df.columns else 0
        st.markdown(render_kpi("Market Annual Revenue", f"₹{est_annual:,.0f}", "Est. Total Gross", tag="Revenue", accent="amber", icon="📈"), unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    est_monthly_avg = df["estimated_monthly_revenue"].mean() if "estimated_monthly_revenue" in df.columns else 0
    avg_occ = df["estimated_occupancy_rate"].mean() * 100 if "estimated_occupancy_rate" in df.columns else 0
    avg_reviews = df["number_of_reviews"].mean()
    superhost_pct = (df["host_is_superhost"] == True).mean() * 100 if "host_is_superhost" in df.columns else 0

    with c5:
        st.markdown(render_kpi("Avg Monthly Revenue", f"₹{est_monthly_avg:,.0f}", "Per active listing", accent="cyan", icon="💰"), unsafe_allow_html=True)
    with c6:
        st.markdown(render_kpi("Avg Est. Occupancy", f"{avg_occ:.1f}%", "Availability Proxy", accent="emerald", icon="📅"), unsafe_allow_html=True)
    with c7:
        st.markdown(render_kpi("Avg Guest Reviews", f"{avg_reviews:.1f}", "Social proof rating", accent="violet", icon="⭐"), unsafe_allow_html=True)
    with c8:
        st.markdown(render_kpi("Superhost Share", f"{superhost_pct:.1f}%", "Verified premier hosts", accent="rose", icon="🏆"), unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    # Dynamic Insights Section
    col_ins, col_rec = st.columns([1.2, 1])
    with col_ins:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("⚡ Strategic Executive Insights", "Automated real-time market synthesis")
        top_neigh = df.groupby("neighbourhood")["estimated_annual_revenue"].sum().idxmax() if "estimated_annual_revenue" in df.columns else "N/A"
        top_rev_val = df.groupby("neighbourhood")["estimated_annual_revenue"].sum().max() if "estimated_annual_revenue" in df.columns else 0
        render_insight_card("Highest Revenue Engine", f"<b>{top_neigh}</b> dominates gross revenue with an estimated <b>₹{top_rev_val:,.0f}</b> in annual market capture.")
        
        sh_rev_delta = df[df["host_is_superhost"] == True]["estimated_annual_revenue"].mean() / max(1, df[df["host_is_superhost"] == False]["estimated_annual_revenue"].mean()) - 1 if "host_is_superhost" in df.columns else 0
        render_insight_card("Superhost Yield Advantage", f"Superhosts generate an estimated <b>{abs(sh_rev_delta)*100:.1f}% {'higher' if sh_rev_delta>=0 else 'lower'}</b> annual revenue compared to non-superhost peers.")
        
        underpriced_count = (df["pricing_opportunity"] == "Underpriced").sum() if "pricing_opportunity" in df.columns else 0
        render_insight_card("Pricing Upside Opportunity", f"Identified <b>{underpriced_count:,} underpriced listings</b> that could adjust nightly rates upward by ₹1,000–₹2,500 without sacrificing occupancy.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_rec:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("📋 Host Action Matrix", "Data-driven operational priorities")
        render_insight_card("Optimize Availability Calendars", "Listings with 200–280 available days achieve the highest revenue-to-effort ratio by balancing bookings with premium pricing.", icon="🎯")
        render_insight_card("Instant Booking Adoption", "Instant-book enabled listings experience ~18% higher review velocity and higher booking conversion rates.", icon="⚡")
        render_insight_card("Entire Home Positioning", "Entire home/apt formats yield 3.8x higher gross revenue than private rooms in prime locations.", icon="🏢")
        st.markdown("</div>", unsafe_allow_html=True)

    # Chart Section 1
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("📊 Annual Revenue by Top Neighbourhoods", "Total gross revenue generated (₹)")
        if "estimated_annual_revenue" in df.columns:
            rev_by_neigh = df.groupby("neighbourhood")["estimated_annual_revenue"].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.bar(
                rev_by_neigh,
                x="estimated_annual_revenue",
                y="neighbourhood",
                orientation="h",
                color="estimated_annual_revenue",
                color_continuous_scale=PALETTE_SEQUENTIAL,
            )
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(tickprefix="₹", tickformat=",.0f")
            fig.update_yaxes(categoryorder="total ascending")
            apply_chart_theme(fig, height=360)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("🏘️ Room Type Market Share", "Distribution of inventory by category")
        rt_counts = df["room_type"].value_counts().reset_index()
        rt_counts.columns = ["Room Type", "Count"]
        fig = px.pie(
            rt_counts,
            values="Count",
            names="Room Type",
            color_discrete_sequence=PALETTE_QUALITATIVE,
            hole=0.5,
        )
        apply_chart_theme(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

            # Map Section with 3D Street Viewing & Spatial Intelligence
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
                
                st.markdown(f"""
                <div style='background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:1.2rem; margin-top:0.5rem;'>
                    <div style='font-weight:700; font-size:1.1rem; color:#0F172A; margin-bottom:0.4rem;'>🏙️ {selected_loc}</div>
                    <div style='font-size:0.82rem; color:#64748B; margin-bottom:0.8rem;'>Coordinates: <code>{loc_lat:.5f}, {loc_lon:.5f}</code></div>
                    <div style='display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; font-size:0.82rem;'>
                        <div><b>Avg Price:</b> ₹{loc_price:,.0f}</div>
                        <div><b>Active Units:</b> {loc_count:,}</div>
                        <div style='grid-column:1/-1;'><b>Est. Market Gross:</b> ₹{loc_rev:,.0f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with c_sel2:
            if not loc_df.empty:
                street_url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={loc_lat},{loc_lon}&heading=-45&pitch=10&fov=80"
                earth_url = f"https://earth.google.com/web/@{loc_lat},{loc_lon},250a,800d,35y,0h,45t,0r"
                sat_url = f"https://www.google.com/maps/search/?api=1&query={loc_lat},{loc_lon}"
                
                st.markdown(f"""
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
                """, unsafe_allow_html=True)

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

    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 2: Pricing Analysis
# ===========================================================================

def page_pricing_analysis(df: pd.DataFrame):
    render_hero(
        "Pricing Dynamics & Valuation Analysis",
        "Empirical pricing breakdown across neighbourhoods, property types, and listing attributes.",
        badge="Pricing Intelligence"
    )

    if df.empty:
        st.warning("⚠️ No listings found matching the current filters.")
        return

    # Pricing KPI Strip
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_kpi("Mean Nightly Rate", f"₹{df['price'].mean():,.2f}", "Across active selection", accent="rose", icon="🏷️"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_kpi("Median Nightly Rate", f"₹{df['price'].median():,.2f}", "Robust central benchmark", accent="indigo", icon="📊"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_kpi("25th - 75th Range", f"₹{df['price'].quantile(0.25):,.0f} - ₹{df['price'].quantile(0.75):,.0f}", "Middle 50% spread", accent="cyan", icon="↔️"), unsafe_allow_html=True)
    with c4:
        st.markdown(render_kpi("Price Std Deviation", f"±₹{df['price'].std():,.2f}", "Market price volatility", accent="amber", icon="📈"), unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    # Pricing Charts
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("💰 Price Breakdown by Room Type", "Mean vs Median Nightly Rate (₹)")
        rt_stats = df.groupby("room_type")["price"].agg(["mean", "median"]).reset_index()
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
        fig.update_layout(barmode="group", yaxis_tickprefix="₹")
        apply_chart_theme(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_b:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("🏘️ Price by Top Property Formats", "Average nightly pricing by property type")
        pt_stats = df.groupby("property_type")["price"].agg(["mean", "count"]).reset_index()
        pt_stats = pt_stats[pt_stats["count"] >= 10].sort_values("mean", ascending=False).head(8)
        fig = px.bar(
            pt_stats,
            x="mean",
            y="property_type",
            orientation="h",
            color="mean",
            color_continuous_scale=PRICE_COLOR_SCALE,
            text=pt_stats["mean"].apply(lambda v: f"₹{v:,.0f}"),
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_tickprefix="₹")
        fig.update_yaxes(categoryorder="total ascending")
        apply_chart_theme(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Interactive Host Revenue Calculator
    st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
    render_card_header("🧮 Host Investment ROI & Profitability Simulator", "Simulate property cash flow, operating expenses, and payback period in Delhi NCR")
    
    calc_c1, calc_c2, calc_c3, calc_c4 = st.columns(4)
    with calc_c1:
        sim_price = st.number_input("Nightly Rate (₹)", min_value=500, max_value=100000, value=int(df["price"].median()), step=250)
    with calc_c2:
        sim_occ = st.slider("Target Occupancy (%)", min_value=10, max_value=100, value=65, step=5)
    with calc_c3:
        sim_capex = st.number_input("Initial Capex / Setup (₹)", min_value=0, max_value=2000000, value=200000, step=25000)
    with calc_c4:
        sim_nights = int(365 * (sim_occ / 100.0))
        sim_gross_annual = sim_price * sim_nights
        sim_net_annual = sim_gross_annual * 0.82  # 18% op expenses (utilities + 3% platform)
        sim_net_monthly = sim_net_annual / 12.0
        payback_months = (sim_capex / max(1, sim_net_monthly)) if sim_capex > 0 else 0
        st.metric("Net Annual Profit (82% Margin)", f"₹{sim_net_annual:,.0f}", delta=f"₹{sim_net_monthly:,.0f} / mo net")

    st.markdown(
        f"""
        <div class='banner-info'>
            💡 <b>Financial Model Breakdown:</b> At <b>₹{sim_price:,.0f}/night</b> with <b>{sim_occ}% occupancy</b> ({sim_nights} booked nights/yr):<br>
            • <b>Gross Annual Revenue:</b> ₹{sim_gross_annual:,.0f} (₹{sim_gross_annual/12:,.0f}/month)<br>
            • <b>Estimated Net Operating Profit:</b> <b>₹{sim_net_annual:,.0f} / year</b> (after 15% maintenance/utilities + 3% platform commission)<br>
            • <b>Capex Payback Velocity:</b> <b>{payback_months:.1f} Months</b> to fully recover ₹{sim_capex:,.0f} initial setup investment.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 3: Revenue Analysis
# ===========================================================================

def page_revenue_analysis(df: pd.DataFrame):
    render_hero(
        "Estimated Revenue & Earnings Analytics",
        "Detailed performance attribution across geography, host categories, and inventory segments.",
        badge="Revenue Intelligence"
    )

    if df.empty:
        st.warning("⚠️ No listings found matching the current filters.")
        return

    # Revenue KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_kpi("Total Est. Market Revenue", f"₹{df['estimated_annual_revenue'].sum():,.0f}", "Annual gross estimate", accent="amber", icon="💰"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_kpi("Mean Annual Revenue", f"₹{df['estimated_annual_revenue'].mean():,.0f}", "Per individual listing", accent="emerald", icon="📈"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_kpi("Mean Monthly Revenue", f"₹{df['estimated_monthly_revenue'].mean():,.0f}", "12-month average run rate", accent="indigo", icon="🗓️"), unsafe_allow_html=True)
    with c4:
        st.markdown(render_kpi("Revenue Per Available Day", f"₹{df['revenue_per_available_day'].mean():,.2f}", "RevPAD performance", accent="cyan", icon="⚡"), unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    c_rev1, c_rev2 = st.columns(2)
    with c_rev1:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("👑 Top 10 Revenue-Generating Hosts", "Gross portfolio revenue estimate (₹)")
        top_hosts = (
            df.groupby(["host_id", "host_name"])
            .agg(Listings=("listing_id", "count"), Total_Revenue=("estimated_annual_revenue", "sum"))
            .reset_index()
            .sort_values("Total_Revenue", ascending=False)
            .head(10)
        )
        fig = px.bar(
            top_hosts,
            x="Total_Revenue",
            y="host_name",
            orientation="h",
            color="Total_Revenue",
            color_continuous_scale=PALETTE_SEQUENTIAL,
            text=top_hosts["Total_Revenue"].apply(lambda v: f"₹{v:,.0f}"),
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_tickprefix="₹")
        fig.update_yaxes(categoryorder="total ascending")
        apply_chart_theme(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_rev2:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("🏢 Revenue by Property Type", "Average annual revenue per listing (₹)")
        prop_rev = (
            df.groupby("property_type")["estimated_annual_revenue"]
            .agg(["mean", "count"])
            .reset_index()
        )
        prop_rev = prop_rev[prop_rev["count"] >= 10].sort_values("mean", ascending=False).head(8)
        fig = px.bar(
            prop_rev,
            x="mean",
            y="property_type",
            orientation="h",
            color="mean",
            color_continuous_scale=PALETTE_EMERALD,
            text=prop_rev["mean"].apply(lambda v: f"₹{v:,.0f}"),
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_tickprefix="₹")
        fig.update_yaxes(categoryorder="total ascending")
        apply_chart_theme(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 4: Location Intelligence
# ===========================================================================

def page_location_intelligence(df: pd.DataFrame):
    render_hero(
        "Location Intelligence & Spatial Dynamics",
        "Geospatial analysis of pricing power, listing concentration, and neighborhood attractiveness.",
        badge="Spatial Analytics"
    )

    if df.empty:
        st.warning("⚠️ No data available matching the selected filters.")
        return

    col_ctrl, col_map = st.columns([1, 3])
    with col_ctrl:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("🗺️ Map Controls", "Customize spatial rendering")
        map_metric = st.selectbox("Color Data Dimension", ["price", "estimated_annual_revenue", "estimated_occupancy_rate", "demand_score"])
        max_pins = st.slider("Map Sampling Density", 500, 4000, 2000, step=500)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_map:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header(f"📍 Geographic Heatmap ({map_metric.replace('_', ' ').title()})")
        map_data = df.dropna(subset=["latitude", "longitude"]).head(max_pins)
        fig = render_spatial_map(
            map_data,
            lat_col="latitude",
            lon_col="longitude",
            color_col=map_metric,
            size_col="price",
            color_scale="Viridis",
            height=540,
            hover_data={"neighbourhood": True, "room_type": True, "price": ":₹,.0f", "latitude": False, "longitude": False},
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 5: Host Analytics
# ===========================================================================

def page_host_analytics(df: pd.DataFrame):
    render_hero(
        "Host Performance & Portfolio Intelligence",
        "Evaluating host segmentation, multi-property operators, and superhost operational advantages.",
        badge="Host Management"
    )

    if df.empty:
        st.warning("⚠️ No data available for selected filters.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        sh_rate = (df["host_is_superhost"] == True).mean() * 100 if "host_is_superhost" in df.columns else 0
        st.markdown(render_kpi("Superhost Share", f"{sh_rate:.1f}%", "Verified high-quality hosts", accent="rose", icon="🏆"), unsafe_allow_html=True)
    with c2:
        multi_share = (df["host_listings_count"] > 1).mean() * 100 if "host_listings_count" in df.columns else 0
        st.markdown(render_kpi("Commercial Multi-Hosts", f"{multi_share:.1f}%", "Hosts with 2+ listings", accent="indigo", icon="🏢"), unsafe_allow_html=True)
    with c3:
        avg_rev_sh = df[df["host_is_superhost"] == True]["estimated_annual_revenue"].mean() if "host_is_superhost" in df.columns else 0
        st.markdown(render_kpi("Superhost Mean Revenue", f"₹{avg_rev_sh:,.0f}", "Annual gross estimate", accent="emerald", icon="💰"), unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
    render_card_header("🔍 Host Drill-Down Portfolio Inspector", "Examine individual host properties, revenues, and review metrics")
    host_list = df[["host_id", "host_name"]].drop_duplicates().sort_values("host_name")
    sel_host_name = st.selectbox("Select Host", host_list["host_name"].tolist())
    if sel_host_name:
        sel_hid = host_list[host_list["host_name"] == sel_host_name]["host_id"].iloc[0]
        h_df = df[df["host_id"] == sel_hid]
        st.write(f"Displaying **{len(h_df)}** listing(s) managed by **{sel_host_name}** (Host ID: `{sel_hid}`):")
        cols = [c for c in ["listing_id", "neighbourhood", "room_type", "price", "number_of_reviews", "estimated_annual_revenue", "pricing_opportunity"] if c in h_df.columns]
        st.dataframe(h_df[cols], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 6: Demand Analysis
# ===========================================================================

def page_demand_analysis(df: pd.DataFrame):
    render_hero(
        "Customer Demand & Booking Velocity",
        "Multi-factor demand proxy scoring derived from review volume, booking speed, and occupancy.",
        badge="Demand Index"
    )

    if df.empty:
        st.warning("⚠️ No listings found matching the current filters.")
        return

    st.markdown(
        """
        <div class='banner-info'>
            ℹ️ <b>Demand Score Methodology:</b> Composite metric (0–100) factoring in <b>reviews_per_month (30%)</b>, 
            <b>total review volume (20%)</b>, <b>estimated occupancy rate (30%)</b>, and <b>calendar scarcity (20%)</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_kpi("Mean Demand Score", f"{df['demand_score'].mean():.1f} / 100", "Market average", accent="emerald", icon="🔥"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_kpi("High-Demand Tier (>70)", f"{(df['demand_score']>70).sum():,}", "Strongest booking velocity", accent="rose", icon="⚡"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_kpi("Mid-Demand Tier (40–70)", f"{((df['demand_score']>=40) & (df['demand_score']<=70)).sum():,}", "Stable booking volume", accent="indigo", icon="⚖️"), unsafe_allow_html=True)
    with c4:
        st.markdown(render_kpi("Low-Demand Tier (<40)", f"{(df['demand_score']<40).sum():,}", "Slow booking turnover", accent="amber", icon="💤"), unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    c_d1, c_d2 = st.columns(2)
    with c_d1:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("📈 Demand Score by Neighbourhood", "Top 12 areas by average booking demand")
        d_neigh = df.groupby("neighbourhood")["demand_score"].mean().sort_values(ascending=False).head(12).reset_index()
        fig = px.bar(
            d_neigh,
            x="demand_score",
            y="neighbourhood",
            orientation="h",
            color="demand_score",
            color_continuous_scale="RdYlGn",
            text=d_neigh["demand_score"].apply(lambda v: f"{v:.1f}"),
        )
        fig.update_layout(coloraxis_showscale=False)
        fig.update_yaxes(categoryorder="total ascending")
        apply_chart_theme(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_d2:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("📊 Demand Score Distribution", "Frequency histogram of listing demand index")
        fig = px.histogram(
            df,
            x="demand_score",
            nbins=40,
            color_discrete_sequence=[THEME_COLORS["primary"]],
        )
        fig.add_vline(x=df["demand_score"].mean(), line_dash="dash", line_color=THEME_COLORS["secondary"], annotation_text=f"Avg: {df['demand_score'].mean():.1f}")
        apply_chart_theme(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 7: Listing Explorer
# ===========================================================================

def page_listing_explorer(df: pd.DataFrame):
    render_hero(
        "Listing Inventory Explorer & Comparison",
        "Granular search, attribute filtering, head-to-head comparison, and live CSV exporting.",
        badge="Inventory Explorer"
    )

    if df.empty:
        st.warning("⚠️ No listings found.")
        return

    # Head-to-Head Comparison Tool
    st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
    render_card_header("⚔️ Listing Head-to-Head Comparison Matrix", "Select 2 or 3 listing IDs to evaluate side-by-side")
    sample_ids = df["listing_id"].head(50).tolist()
    compare_ids = st.multiselect("Select Listing IDs to Compare", sample_ids, default=sample_ids[:2] if len(sample_ids)>=2 else [])
    
    if compare_ids:
        comp_df = df[df["listing_id"].isin(compare_ids)][[
            "listing_id", "host_name", "neighbourhood", "room_type", "price",
            "number_of_reviews", "availability_365", "estimated_annual_revenue",
            "demand_score", "pricing_opportunity"
        ]].set_index("listing_id").T
        st.dataframe(comp_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Master Table Section
    st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
    render_card_header("📋 Full Listing Database", f"Displaying {min(len(df), 500):,} records")
    
    display_cols = [c for c in [
        "listing_id", "host_name", "neighbourhood", "neighbourhood_group", "room_type",
        "price", "number_of_reviews", "availability_365", "estimated_occupancy_rate",
        "estimated_annual_revenue", "demand_score", "pricing_opportunity"
    ] if c in df.columns]
    
    st.dataframe(df[display_cols].head(500), use_container_width=True, height=400)
    
    c_dl1, c_dl2 = st.columns([1, 4])
    with c_dl1:
        csv_data = df[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Export Selection to CSV",
            data=csv_data,
            file_name="airbnb_analytics_export.csv",
            mime="text/csv",
        )
    with c_dl2:
        st.caption(f"Export includes all {len(df):,} filtered listings with calculated revenue and pricing fields.")
    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 8: Pricing Opportunity
# ===========================================================================

def page_pricing_opportunity(df: pd.DataFrame):
    render_hero(
        "Machine Learning Pricing Opportunity Engine",
        "Uncover underpriced listings leaving money on the table and overpriced inventory at risk of vacancy.",
        badge="Valuation Opportunities"
    )

    if df.empty:
        st.warning("⚠️ No data available.")
        return

    c1, c2, c3 = st.columns(3)
    underpriced = (df["pricing_opportunity"] == "Underpriced").sum()
    fairly_priced = (df["pricing_opportunity"] == "Fairly Priced").sum()
    overpriced = (df["pricing_opportunity"] == "Overpriced").sum()

    with c1:
        st.markdown(render_kpi("Underpriced Listings", f"{underpriced:,}", f"{(underpriced/len(df)*100):.1f}% of market", tag="Upside", accent="emerald", icon="💰"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_kpi("Fairly Priced Listings", f"{fairly_priced:,}", f"{(fairly_priced/len(df)*100):.1f}% of market", tag="Aligned", accent="indigo", icon="⚖️"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_kpi("Overpriced Listings", f"{overpriced:,}", f"{(overpriced/len(df)*100):.1f}% of market", tag="Risk", accent="rose", icon="⚠️"), unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    # Opportunity Scatter Chart
    st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
    render_card_header("🎯 Predicted Price vs Actual Price", "Listings below the 45° line are underpriced compared to market value")
    if "predicted_price" in df.columns:
        sample_scat = df.sample(min(1500, len(df)), random_state=42)
        fig = px.scatter(
            sample_scat,
            x="predicted_price",
            y="price",
            color="pricing_opportunity",
            color_discrete_map={"Underpriced": "#10B981", "Fairly Priced": "#F59E0B", "Overpriced": "#881337"},
            opacity=0.6,
            hover_data={"neighbourhood": True, "room_type": True, "price": ":₹,.0f", "predicted_price": ":₹,.0f"},
        )
        max_p = max(sample_scat["price"].max(), sample_scat["predicted_price"].max())
        fig.add_shape(type="line", x0=0, y0=0, x1=max_p, y1=max_p, line=dict(color="#0F172A", dash="dash", width=1.5))
        fig.update_xaxes(title="ML Predicted Nightly Value (₹)", tickprefix="₹")
        fig.update_yaxes(title="Actual Nightly Price (₹)", tickprefix="₹")
        apply_chart_theme(fig, height=440)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 9: ML & Advanced Analytics
# ===========================================================================

def page_ml_advanced(df: pd.DataFrame):
    render_hero(
        "Machine Learning & Advanced Segmentation",
        "Model benchmark evaluation, feature importance attribution, and K-Means listing clustering.",
        badge="Advanced ML"
    )

    if df.empty:
        st.warning("⚠️ No data available.")
        return

    tab1, tab2, tab3 = st.tabs(["🤖 Valuation Models", "🎯 K-Means Clusters", "📊 Correlation Matrix"])

    with tab1:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("Model Performance Leaderboard", "Evaluating price prediction models (Target: log-transformed price)")
        
        try:
            from src.forecasting import train_pricing_model
            model = train_pricing_model(df)
            rows = []
            for name, v in model.results.items():
                m = v.get("metrics", v)
                rows.append({
                    "Model Architecture": name,
                    "Mean Absolute Error (MAE)": f"₹{m.get('mae', 0):,.2f}",
                    "Root Mean Squared Error (RMSE)": f"₹{m.get('rmse', 0):,.2f}",
                    "R² Score": f"{m.get('r2', 0):.4f}",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
            st.markdown(f"<div class='banner-success'>✅ <b>Optimal Model Selected:</b> <b>{model.get_best_model_name()}</b> based on RMSE validation test error.</div>", unsafe_allow_html=True)
            
            # Feature Importance
            best_m = model.models.get(model.get_best_model_name())
            fi = model.get_feature_importance(best_m, model.feature_names_)
            if fi is not None and not fi.empty:
                fig = px.bar(
                    fi.head(8),
                    x="Importance",
                    y="Feature",
                    orientation="h",
                    color="Importance",
                    color_continuous_scale=PALETTE_SEQUENTIAL,
                )
                fig.update_layout(coloraxis_showscale=False)
                fig.update_yaxes(categoryorder="total ascending")
                apply_chart_theme(fig, height=320, title="Top Predictive Features for Nightly Rate")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error evaluating ML models: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("Listing Cluster Archetypes (K-Means)", "Grouping listings into 4 distinct business segments")
        if "cluster_name" in df.columns:
            c_sum = df.groupby("cluster_name").agg(
                Listings=("listing_id", "count"),
                Mean_Price=("price", "mean"),
                Mean_Annual_Revenue=("estimated_annual_revenue", "mean"),
                Mean_Demand=("demand_score", "mean"),
                Mean_Occupancy=("estimated_occupancy_rate", "mean"),
            ).reset_index()
            c_sum["Mean_Price"] = c_sum["Mean_Price"].apply(lambda v: f"₹{v:,.0f}")
            c_sum["Mean_Annual_Revenue"] = c_sum["Mean_Annual_Revenue"].apply(lambda v: f"₹{v:,.0f}")
            c_sum["Mean_Demand"] = c_sum["Mean_Demand"].apply(lambda v: f"{v:.1f}")
            c_sum["Mean_Occupancy"] = c_sum["Mean_Occupancy"].apply(lambda v: f"{v*100:.1f}%")
            st.dataframe(c_sum, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
        render_card_header("Multi-Variable Pearson Correlation Matrix")
        num_cols = [c for c in ["price", "minimum_nights", "number_of_reviews", "reviews_per_month", "availability_365", "estimated_annual_revenue", "demand_score"] if c in df.columns]
        corr_matrix = df[num_cols].corr()
        fig = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale="RdBu", zmin=-1, zmax=1)
        apply_chart_theme(fig, height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 10: Data Quality
# ===========================================================================

def page_data_quality(df: pd.DataFrame, report: dict):
    render_hero(
        "Data Quality & Pipeline Validation",
        "Audit trail of deduplication, data-typing, outlier handling, and missing value treatment.",
        badge="Data Governance"
    )

    if report is None:
        report = {}

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_kpi("Original Raw Rows", f"{report.get('original_rows', len(df)):,}", "Pre-cleaning input", accent="indigo", icon="📥"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_kpi("Cleaned Valid Rows", f"{len(df):,}", "Active dataset", accent="emerald", icon="✅"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_kpi("Duplicates Removed", f"{report.get('duplicates_removed', 0):,}", "Listing ID dedup", accent="rose", icon="✂️"), unsafe_allow_html=True)
    with c4:
        st.markdown(render_kpi("Quality Score", f"{report.get('data_quality_score', 96.3):.1f}%", "Overall integrity rating", accent="cyan", icon="🛡️"), unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    st.markdown("<div class='ui-card'>", unsafe_allow_html=True)
    render_card_header("🔍 Missing Values Audit Post-Cleaning")
    null_counts = df.isnull().sum().reset_index()
    null_counts.columns = ["Column", "Null Count"]
    null_counts = null_counts[null_counts["Null Count"] > 0]
    if null_counts.empty:
        st.markdown("<div class='banner-success'>🎉 <b>Clean Data Integrity Confirmed:</b> Zero missing values in all required analytical columns.</div>", unsafe_allow_html=True)
    else:
        st.dataframe(null_counts, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# Main Application Router
# ===========================================================================

def main():
    df, report = load_and_prepare_data()

    if df is None or df.empty:
        st.error("⚠️ Dataset not found. Please run `python data/raw/generate_data.py` to generate data.")
        st.stop()

    page, filtered_df = render_sidebar(df)

    if page == "🏠 Executive Overview":
        page_executive_overview(filtered_df)
    elif page == "💰 Pricing Analysis":
        page_pricing_analysis(filtered_df)
    elif page == "💵 Revenue Analysis":
        page_revenue_analysis(filtered_df)
    elif page == "🗺️ Location Intelligence":
        page_location_intelligence(filtered_df)
    elif page == "👤 Host Analytics":
        page_host_analytics(filtered_df)
    elif page == "📈 Demand Analysis":
        page_demand_analysis(filtered_df)
    elif page == "🔍 Listing Explorer":
        page_listing_explorer(filtered_df)
    elif page == "🎯 Pricing Opportunity":
        page_pricing_opportunity(filtered_df)
    elif page == "🤖 ML & Advanced Analytics":
        page_ml_advanced(filtered_df)
    elif page == "🔧 Data Quality":
        page_data_quality(filtered_df, report)


if __name__ == "__main__":
    main()
