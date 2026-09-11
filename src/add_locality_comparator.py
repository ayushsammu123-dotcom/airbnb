"""
Add Head-to-Head Locality Comparator to Location Intelligence.
"""
from pathlib import Path
import re

app_path = Path("dashboard/app.py")
code = app_path.read_text(encoding="utf-8")

comparator_snippet = """
    # Head-to-Head Locality Comparison Sandbox
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    render_card_header("⚖️ Locality Head-to-Head Comparison Sandbox", "Compare pricing power, occupancy, and revenue density across any two Delhi NCR micro-markets")
    
    all_micro = sorted(df["neighbourhood"].dropna().unique().tolist()) if "neighbourhood" in df.columns else []
    if len(all_micro) >= 2:
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            loc_a = st.selectbox("📍 Select Benchmark Locality A", all_micro, index=0, key="cmp_loc_a")
        with c_l2:
            loc_b = st.selectbox("📍 Select Comparison Locality B", all_micro, index=min(1, len(all_micro)-1), key="cmp_loc_b")
        
        df_a = df[df["neighbourhood"] == loc_a]
        df_b = df[df["neighbourhood"] == loc_b]
        
        if not df_a.empty and not df_b.empty:
            metric_data = {
                "Metric": ["Average Daily Rate (₹)", "Median Daily Rate (₹)", "Est. Annual Revenue / Listing (₹)", "Average Occupancy Rate (%)", "Active Listings Count", "Superhost Share (%)"],
                f"Locality A: {loc_a}": [
                    f"₹{df_a['price'].mean():,.0f}",
                    f"₹{df_a['price'].median():,.0f}",
                    f"₹{df_a['estimated_annual_revenue'].mean():,.0f}",
                    f"{df_a['estimated_occupancy_rate'].mean()*100:.1f}%",
                    f"{len(df_a):,}",
                    f"{(df_a['host_is_superhost']==True).mean()*100:.1f}%"
                ],
                f"Locality B: {loc_b}": [
                    f"₹{df_b['price'].mean():,.0f}",
                    f"₹{df_b['price'].median():,.0f}",
                    f"₹{df_b['estimated_annual_revenue'].mean():,.0f}",
                    f"{df_b['estimated_occupancy_rate'].mean()*100:.1f}%",
                    f"{len(df_b):,}",
                    f"{(df_b['host_is_superhost']==True).mean()*100:.1f}%"
                ],
            }
            cmp_df = pd.DataFrame(metric_data)
            st.dataframe(cmp_df, use_container_width=True, hide_index=True)
            
            p_diff = ((df_a['price'].mean() / max(1, df_b['price'].mean())) - 1) * 100
            st.markdown(f\"\"\"
            <div class='note-box'>
                <div class='note-box-title'>📊 Analyst Comparative Summary</div>
                <div class='note-box-body'>
                    <b>{loc_a}</b> commands a <b>{abs(p_diff):.1f}% {'higher' if p_diff>=0 else 'lower'}</b> average daily rate compared to <b>{loc_b}</b>. 
                    {'It represents a premium high-yield market for entire home conversions.' if p_diff>=0 else 'It represents an accessible, high-occupancy market with steady booking volume.'}
                </div>
            </div>
            \"\"\", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
"""

code = code.replace("st.markdown(\"</div>\", unsafe_allow_html=True)\n\n\n# ===========================================================================\n# PAGE 5: Host Analytics", "st.markdown(\"</div>\", unsafe_allow_html=True)\n" + comparator_snippet + "\n\n# ===========================================================================\n# PAGE 5: Host Analytics")

app_path.write_text(code, encoding="utf-8")
print(">> Added Locality Head-to-Head Comparison tool!")
