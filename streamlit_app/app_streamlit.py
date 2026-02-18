import streamlit as st
import pandas as pd
from io import BytesIO
from cleaner import DataCleaner

ISSUE_LABELS = {
    "date": "📅 Date parsing issue",
    "numeric": "🔢 Numeric conversion issue",
    "email": "📧 Invalid email format",
    "text": "📝 Non-normalizable text",
    "city": "🏙️ Ambiguous city value",
    "country": "🌍 Ambiguous country value",
}

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="DataCleaner – Basic Plan",
    layout="wide"
)

st.title("🧹 DataCleaner – Basic Plan")
st.caption(
    "Upload your file and download a clean, structured dataset. "
    "Cleaning is automatic, conservative and transparent."
)

# --------------------------------------------------
# UPLOAD
# --------------------------------------------------
uploaded = st.file_uploader(
    "📤 Upload a CSV or Excel file (processed locally)",
    type=["csv", "xlsx"]
)

if uploaded:

    # -------- LOAD DATA --------
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.subheader("📄 Preview – Original data")
    st.dataframe(df.head(30), use_container_width=True)

    # --------------------------------------------------
    # INFO
    # --------------------------------------------------
    st.subheader("⚙️ Basic plan behavior")

    st.info(
        "🔹 The Basic Plan applies a **safe and automatic cleaning**:\n\n"
        "✔ Normalizes column names\n"
        "✔ Cleans simple text fields\n"
        "✔ Parses common date formats\n"
        "✔ Removes exact duplicates\n\n"
        "❗ Ambiguous values (emails, cities, countries) are **not modified**.\n"
        "They are only reported for transparency."
    )

    # --------------------------------------------------
    # RUN CLEAN
    # --------------------------------------------------
    if st.button("🚀 Run automatic cleaning", use_container_width=True):

        with st.spinner("🧹 Cleaning data…"):
            cleaner = DataCleaner(df)
            cleaner.run_basic_plan()
            df_clean = cleaner.df

        st.success("✅ Cleaning completed")


        # --------------------------------------------------
        # PREVIEW CLEAN
        # --------------------------------------------------
        st.subheader("✅ Preview – Clean data")

        df_display = df_clean.copy()
        for col in df_display.columns:
            if pd.api.types.is_datetime64_any_dtype(df_display[col]):
                df_display[col] = df_display[col].dt.strftime("%Y-%m-%d")

        st.dataframe(df_display.head(20), use_container_width=True)
        
        
        # --------------------------------------------------
        # SUMMARY
        # --------------------------------------------------
        st.subheader("📊 Cleaning summary")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("📄 Final rows", len(df_clean))
        c2.metric("🧹 Duplicates removed", len(cleaner.duplicates_df))
        c3.metric(
            "📅 Date columns parsed",
            len([
                c for c in df_clean.columns
                if pd.api.types.is_datetime64_any_dtype(df_clean[c])
            ])
        )
        c4.metric(
            "⚠️ Issues detected",
            sum(len(v) for v in cleaner.issues.values())
        )

        # --------------------------------------------------
        # ISSUES (INFO ONLY)
        # --------------------------------------------------
        if cleaner.issues:

            st.subheader("⚠️ Detected issues (informational)")
            st.caption(
                "These values could not be interpreted automatically and were left unchanged. "
                "They are shown here for transparency only."
            )

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "Total issues",
                    sum(len(v) for v in cleaner.issues.values())
                )

            with c2:
                st.metric(
                    "Issue types",
                    len(cleaner.issues)
                )

            with st.expander("🛠️ How to review these issues"):
                st.markdown(
                    """
                    **Recommended workflow:**

                    1. Download the clean file  
                    2. Locate the affected row using the **Row index**  
                    3. Review the original value  
                    4. Correct manually if needed  

                    The Basic Plan never changes ambiguous values automatically.
                    """
                )

            for issue_type, items in cleaner.issues.items():
                if not items:
                    continue

                label = ISSUE_LABELS.get(issue_type, issue_type.capitalize())

                with st.expander(f"{label} ({len(items)})"):
                    issues_df = pd.DataFrame(items)
                    issues_df = issues_df.sort_values(["column", "index"])
                    issues_df.columns = ["Column", "Row index", "Original value"]

                    st.dataframe(
                        issues_df.head(20),
                        use_container_width=True,
                        hide_index=True
                    )

                    if len(items) > 20:
                        st.caption("Showing first 20 cases.")

        # --------------------------------------------------
        # DOWNLOAD
        # --------------------------------------------------
        st.subheader("⬇️ Download clean file")

        excel_buffer = BytesIO()
        df_export = df_clean.copy()

        for col in df_export.columns:
            if pd.api.types.is_datetime64_any_dtype(df_export[col]):
                df_export[col] = df_export[col].dt.strftime("%Y-%m-%d")

        df_export.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        _, center, _ = st.columns([2, 3, 2])
        with center:
            b1, b2 = st.columns(2)

            b1.download_button(
                "📘 Download Excel",
                data=excel_buffer,
                file_name="clean_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

            b2.download_button(
                "📄 Download CSV",
                data=df_export.to_csv(index=False).encode("utf-8"),
                file_name="clean_data.csv",
                mime="text/csv",
                use_container_width=True
            )

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
                padding: 16px 0;
            ">
                “A good data cleaner is not the one that fixes the most,<br>
                but the one that makes the fewest mistakes.”
            </div>
            """,
            unsafe_allow_html=True
        )
