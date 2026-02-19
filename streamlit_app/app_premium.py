import streamlit as st
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")

import plotly.express as px
from io import BytesIO


from cleaner.cleaner_core import DataCleaner
from cleaner.premium_report import generate_premium_pdf



# -----------------------------
# SESSION STATE
# -----------------------------
if "cleaner" not in st.session_state:
    st.session_state.cleaner = None

if "df_clean" not in st.session_state:
    st.session_state.df_clean = None

if "metrics" not in st.session_state:
    st.session_state.metrics = None


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="DataCleaner – Premium",
    layout="wide"
)

st.markdown("""
<style>
.card {
    background-color: #111827;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    text-align: center;
}
.card-title {
    font-size: 16px;
    color: #9ca3af;
}
.card-value {
    font-size: 32px;
    font-weight: 700;
    margin-top: 8px;
}
.card-sub {
    font-size: 14px;
    color: #6b7280;
    margin-top: 6px;
}
.section-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


st.title("🧠 DataCleaner – Premium Intelligence Dashboard")

uploaded = st.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

# -----------------------------
# CLEANING
# -----------------------------
if uploaded:

    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    if st.button("🚀 Run Premium Analysis"):

        cleaner = DataCleaner(df)
        cleaner.run_medium_plan()

        st.session_state.cleaner = cleaner
        st.session_state.df_clean = cleaner.df
        st.session_state.metrics = cleaner.compute_metrics()

        st.success("Premium analysis completed.")

# ==================================================
# OVERVIEW
# ==================================================
def overview_page():

    df_clean = st.session_state.df_clean
    metrics = st.session_state.metrics

    health_score = round(metrics["health_ratio"] * 100, 2)

    st.markdown('<div class="section-title">📊 Executive Overview</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="card">
        <div class="card-title">Raw Rows</div>
        <div class="card-value">{metrics["total_rows_raw"]}</div>
        <div class="card-sub">Original dataset size</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="card">
        <div class="card-title">Clean Rows</div>
        <div class="card-value">{metrics["total_rows_clean"]}</div>
        <div class="card-sub">After automated validation</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="card">
        <div class="card-title">Total Issues</div>
        <div class="card-value">{metrics["total_issues"]}</div>
        <div class="card-sub">Detected inconsistencies</div>
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="card">
        <div class="card-title">Columns</div>
        <div class="card-value">{metrics["total_columns"]}</div>
        <div class="card-sub">Dataset dimensions</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ===============================
    # HEALTH CLASSIFICATION
    # ===============================

    if health_score >= 85:
        health_label = "🟢 Healthy Dataset"
        interpretation = "Your dataset is highly reliable and ready for analytics."
        color = "#22C55E"

    elif health_score >= 60:
        health_label = "🟡 Moderate Risk"
        interpretation = "The dataset is usable but contains structural inconsistencies."
        color = "#FACC15"

    else:
        health_label = "🔴 High Risk"
        interpretation = "Significant data quality problems detected. Review recommended before business use."
        color = "#EF4444"

    st.markdown("### 📈 Overall Quality Indicator")

    st.markdown(f"""
    <div style="
        padding:20px;
        border-radius:12px;
        background:#111827;
        border-left:6px solid {color};
        margin-bottom:20px;
    ">
        <div style="font-size:22px; font-weight:600;">
            {health_label}
        </div>
        <div style="font-size:16px; margin-top:8px;">
            Health Score: <b>{health_score}/100</b>
        </div>
        <div style="margin-top:8px; font-size:14px; opacity:0.8;">
            {interpretation}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===============================
    # AUTOMATED INSIGHTS
    # ===============================

    st.markdown("### 🔎 Automated Intelligence Insights")

    if metrics["total_issues"] > 0:

        worst_issue = max(
            metrics["issues_by_type"],
            key=metrics["issues_by_type"].get
        )

        st.info(f"""
        **Primary Risk Area:** {worst_issue.upper()}  

        • {metrics["issues_by_type"][worst_issue]} records affected  
        • Represents {round(metrics["issues_by_type"][worst_issue] / metrics["total_rows_raw"] * 100, 2)}% of total rows  
        • Targeted correction here would produce the highest quality gain
        """)

    if metrics["rows_removed"] > 0:
        st.warning(f"""
        **Duplicate Risk Detected**

        • {metrics["rows_removed"]} duplicate rows removed  
        • Indicates potential upstream integration or sync issues  
        • Recommend validating data ingestion pipeline
        """)
        
        
    st.markdown("---")
    st.markdown("## ⬇️ Download Clean Dataset")

    df_export = st.session_state.df_clean.copy()

    excel_buffer = BytesIO()
    df_export.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    col1, col2 = st.columns(2)

    col1.download_button(
        "📘 Download Excel (.xlsx)",
        data=excel_buffer,
        file_name="clean_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    col2.download_button(
        "📄 Download CSV (.csv)",
        data=df_export.to_csv(index=False).encode("utf-8"),
        file_name="clean_data.csv",
        mime="text/csv",
        use_container_width=True
    )



# ==================================================
# DATA QUALITY
# ==================================================
def data_quality_page():

    metrics = st.session_state.metrics

    st.markdown('<div class="section-title">🧪 Data Quality Assessment</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div class="card">
        <div class="card-title">Issues per 1,000 rows</div>
        <div class="card-value">{round(metrics["issues_per_1000_rows"], 2)}</div>
        <div class="card-sub">Operational instability indicator</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="card">
        <div class="card-title">Rows Removed</div>
        <div class="card-value">{round(metrics["rows_removed_pct"]*100, 2)}%</div>
        <div class="card-sub">Duplicate risk factor</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="card">
        <div class="card-title">Auto-Fix Ratio</div>
        <div class="card-value">{round(metrics["auto_fix_ratio"]*100, 2)}%</div>
        <div class="card-sub">Automation effectiveness</div>
    </div>
    """, unsafe_allow_html=True)



    # ===============================
    # ISSUE DISTRIBUTION (TOP 5)
    # ===============================

    st.markdown("### 🔍 Top Issue Types")

    issue_df = pd.DataFrame.from_dict(
    metrics["issues_by_type"],
    orient="index",
    columns=["count"]
    ).reset_index()

    issue_df.columns = ["Issue Type", "Count"]

    color_map = {
        "numeric": "#3B82F6",
        "email": "#A855F7",
        "date": "#FACC15",
        "city": "#EF4444",
        "country": "#22C55E",
        "text": "#F97316"
    }

    fig = px.bar(
        issue_df,
        x="Issue Type",
        y="Count",
        color="Issue Type",
        color_discrete_map=color_map
    )

    st.plotly_chart(fig, use_container_width=True)


    st.caption("Only top 5 issue categories are displayed for clarity.")


    # ===============================
    # BUSINESS INTERPRETATION
    # ===============================

    st.markdown("### 🧠 System Interpretation")

    if metrics["health_ratio"] >= 0.85:
        st.success("Dataset quality is high. Minor inconsistencies detected.")
    elif metrics["health_ratio"] >= 0.60:
        st.warning("Dataset shows moderate structural inconsistencies.")
    else:
        st.error("Dataset is high-risk and requires intervention before analytics.")




# ==================================================
# ISSUES BREAKDOWN
# ==================================================
def issues_page():

    cleaner = st.session_state.cleaner
    metrics = st.session_state.metrics
    df_clean = st.session_state.df_clean

    st.markdown('<div class="section-title">⚠️ Issue Intelligence</div>', unsafe_allow_html=True)

    total_issues = metrics["total_issues"]
    issue_types = len(metrics["issues_by_type"])

    # =========================
    # KPI CARDS
    # =========================
    col1, col2 = st.columns(2)

    col1.markdown(f"""
    <div class="card">
        <div class="card-title">Total Issues</div>
        <div class="card-value">{total_issues}</div>
        <div class="card-sub">Detected inconsistencies</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="card">
        <div class="card-title">Issue Categories</div>
        <div class="card-value">{issue_types}</div>
        <div class="card-sub">Distinct error types</div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # ISSUE DISTRIBUTION
    # =========================
    st.markdown("### 📊 Issue Distribution by Type")

    issue_df = pd.DataFrame.from_dict(
        metrics["issues_by_type"],
        orient="index",
        columns=["Count"]
    ).reset_index()

    issue_df.columns = ["Issue Type", "Count"]

    if issue_df.empty:
        st.success("No issues detected in this dataset.")
        return

    # Soft color palette (más profesional)
    color_map = {
        "numeric": "#3B82F6",
        "email": "#8B5CF6",
        "date": "#FACC15",
        "city": "#FB923C",
        "country": "#34D399",
        "text": "#60A5FA"
    }

    fig = px.bar(
        issue_df,
        x="Issue Type",
        y="Count",
        color="Issue Type",
        color_discrete_map=color_map
    )

    fig.update_layout(
        showlegend=False,
        title="Issue Frequency by Category"
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # TOP COLUMNS IMPACT
    # =========================
    st.markdown("### 🎯 Top 5 Columns by Issue Impact")

    column_impact = []

    for col in df_clean.columns:
        issue_count = sum(
            1 for items in cleaner.issues.values()
            for item in items if item["column"] == col
        )

        if issue_count > 0:
            column_impact.append({"Column": col, "Issues": issue_count})

    if column_impact:
        df_col = pd.DataFrame(column_impact)
        df_col = df_col.sort_values("Issues", ascending=False).head(5)

        fig2 = px.bar(
            df_col,
            x="Column",
            y="Issues",
            color="Issues",
            color_continuous_scale="Oranges"
        )

        fig2.update_layout(showlegend=False)

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.success("No column-level issues detected.")

    # =========================
    # DRILL DOWN
    # =========================
    st.markdown("### 🔍 Issue Drill-down")

    selected_issue = st.selectbox(
        "Select issue type to inspect",
        list(metrics["issues_by_type"].keys())
    )

    selected_items = cleaner.issues.get(selected_issue, [])
    df_issue = pd.DataFrame(selected_items)

    if not df_issue.empty:
        st.dataframe(df_issue, use_container_width=True)

        st.info(f"""
        This issue type affects **{len(df_issue)} records**.
        Improving validation rules for **{selected_issue.upper()}**
        would significantly reduce overall data risk.
        """)

# ==================================================
# COLUMN ANALYSIS
# ==================================================
def column_analysis_page():

    df_clean = st.session_state.df_clean
    cleaner = st.session_state.cleaner

    st.markdown('<div class="section-title">🧱 Column Risk Intelligence</div>', unsafe_allow_html=True)

    col_data = []

    for col in df_clean.columns:

        null_pct = df_clean[col].isna().mean()

        issue_count = sum(
            1 for items in cleaner.issues.values()
            for item in items if item["column"] == col
        )

        col_data.append({
            "Column": col,
            "Null %": round(null_pct * 100, 2),
            "Issues": issue_count
        })

    df_col = pd.DataFrame(col_data)

    # =========================
    # TOP 5 RISK COLUMNS
    # =========================
    st.markdown("### 🚨 Top 5 Risk Columns")

    df_top = df_col.sort_values(
        ["Issues", "Null %"],
        ascending=False
    ).head(5)

    fig = px.bar(
        df_top,
        x="Column",
        y="Issues",
        color="Null %",
        color_continuous_scale="Oranges"
    )

    fig.update_layout(showlegend=True)

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # FULL TABLE
    # =========================
    st.markdown("### 📋 Full Column Risk Table")

    st.dataframe(
        df_col.sort_values(["Issues", "Null %"], ascending=False),
        use_container_width=True
    )

    st.info("""
    Columns with higher issue counts or null percentages represent structural risk areas.
    Prioritizing validation rules for these columns improves overall dataset reliability
    and downstream reporting accuracy.
    """)


# ==================================================
# GEOGRAPHIC INSIGHTS
# ==================================================
def geo_page():

    df_clean = st.session_state.df_clean

    geo_cols = [
        col for col in df_clean.columns
        if "city" in col.lower() or "country" in col.lower()
    ]

    if not geo_cols:
        st.markdown('<div class="section-title">🌍 Geographic Intelligence</div>', unsafe_allow_html=True)
        st.info("No geographic columns detected in this dataset.")
        return

    st.markdown('<div class="section-title">🌍 Geographic Intelligence</div>', unsafe_allow_html=True)

    for col in geo_cols:

        st.markdown(f"### 📍 {col.upper()} Distribution")

        series = df_clean[col]

        # 🔒 Seguridad contra errores
        series = series.astype("object")
        series = series.where(series.notna(), "Missing")
        series = series.astype(str)

        value_counts = (
            series.value_counts()
            .head(10)
            .reset_index()
        )

        value_counts.columns = ["Location", "Count"]

        # =========================
        # COLOR LOGIC
        # =========================
        if "_clean" in col:
            fig = px.bar(
                value_counts,
                x="Location",
                y="Count",
                color="Location",
                title=f"Processed Version ({col})"
            )
        else:
            fig = px.bar(
                value_counts,
                x="Location",
                y="Count",
                color_discrete_sequence=["#38BDF8"],  # Celeste RAW
                title=f"Raw Version ({col})"
            )

        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(value_counts, use_container_width=True)

        st.info(f"""
        This chart shows the distribution of geographic values in **{col}**.
        Cleaned versions reduce inconsistencies and improve segmentation accuracy.
        """)



# -----------------------------
# NAVIGATION
# -----------------------------
    
if st.session_state.df_clean is not None:
    # 🔹 Definición de páginas
    pages = [
            st.Page(overview_page, title="📊 Overview"),
            st.Page(data_quality_page, title="🧪 Data Quality"),
            st.Page(issues_page, title="⚠️ Issues Breakdown"),
            st.Page(column_analysis_page, title="🧱 Column Analysis"),
            st.Page(geo_page, title="🌍 Geographic Insights")
        ]
    

    # 🔹 Renderiza navegación (queda debajo del título)
    pg = st.navigation(pages)

    # 🔹 Empuja el export al fondo
    st.sidebar.markdown("<br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📄 Export")

    st.sidebar.button(
        "📄 Executive PDF Report (Coming Soon)",
        disabled=True
    )

    
    # st.sidebar.markdown("---")
    
    # if st.sidebar.button("Download PDF Report"):

    #     pdf = generate_premium_pdf(
    #         st.session_state.metrics,
    #         st.session_state.cleaner,
    #         st.session_state.df_clean
    #     )

    #     st.sidebar.download_button(
    #         label="Download PDF",
    #         data=pdf,
    #         file_name="data_cleaner_premium_report.pdf",
    #         mime="application/pdf"
    #     )
    pg.run()
    
# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    """
    <div style="
        text-align: center;
        font-style: italic;
        color: #aaa;
        font-size: 16px;
        padding: 12px 0;
    ">
        “A good data cleaner is not the one that fixes the most,<br>
        but the one that makes the fewest mistakes.”
    </div>
    """,
    unsafe_allow_html=True
)
