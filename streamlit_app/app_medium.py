import streamlit as st
import pandas as pd
from io import BytesIO

from cleaner.cleaner_core import DataCleaner

ISSUE_LABELS = {
    "date": "📅 Date parsing issue",
    "numeric": "🔢 Numeric conversion issue",
    "email": "📧 Invalid email format",
    "text": "📝 Non-normalizable text",
    "city": "🏙️ Ambiguous city value",
}

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="DataCleaner – Medium Plan",
    layout="wide"
)

st.title("🧹 DataCleaner – Medium Plan")
st.caption(
    "Upload your file and download a clean, structured dataset. "
    "This plan applies deeper but still safe automatic cleaning."
)

# --------------------------------------------------
# UPLOAD
# --------------------------------------------------
uploaded = st.file_uploader(
    "📤 Upload a CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded:

    # -------- LOAD FILE --------
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.subheader("📄 Original data preview")
    st.dataframe(df.head(20), use_container_width=True)

    # ==================================================
    # CLEANING MODE
    # ==================================================
    st.subheader("⚡ Cleaning mode")

    use_recommended = st.checkbox(
        "✅ Use recommended mode",
        value=True,
        help="Applies safe automatic corrections without data loss."
    )

    if use_recommended:
        date_format = "y-m-d"
        numeric_error_mode = "median"
        remove_duplicates = True
    else:
        with st.expander("⚙️ Advanced options"):
            date_format = st.radio(
                "Original date format",
                ["y-m-d", "d-m-y"]
            )

            numeric_error_mode = st.radio(
                "How to handle invalid numeric values",
                [
                    ("median", "Auto-fix using median"),
                    ("nan", "Leave as empty")
                ],
                format_func=lambda x: x[1]
            )[0]

            remove_duplicates = st.checkbox(
                "Remove duplicated rows",
                value=True
            )

    # ==================================================
    # RUN CLEAN
    # ==================================================
    if st.button("🚀 Run data cleaning"):

        with st.spinner("🧹 Cleaning data…"):
            cleaner = DataCleaner(df)

            cleaner.run_medium_plan(
                date_mode="convert",
                duplicate_subset=None,
                duplicate_mode="remove" if remove_duplicates else "mark",
                numeric_error_mode=numeric_error_mode,
                text_mode="basic"
            )

            df_clean = cleaner.df

        st.success("✅ Cleaning completed")

        # ==================================================
        # PREVIEW
        # ==================================================
        st.subheader("✅ Clean data preview")

        df_display = cleaner.df.drop(
            columns=cleaner._internal_columns,
            errors="ignore"
        ).copy()

        for col in df_display.columns:
            if pd.api.types.is_datetime64_any_dtype(df_display[col]):
                df_display[col] = df_display[col].dt.strftime(
                    "%d-%m-%Y" if date_format == "d-m-y" else "%Y-%m-%d"
                )

        
        st.dataframe(df_display.head(20), use_container_width=True)


        # --------------------------------------------------
        # CITY INFO (CORRECTED)
        # --------------------------------------------------
        st.info(
            "ℹ️ City values are handled conservatively in the Medium Plan.\n\n"
            "Only capitalization is normalized. Ambiguous values are flagged "
            "as issues and removed from the clean dataset to avoid incorrect assumptions."
        )

        # ==================================================
        # SUMMARY
        # ==================================================
        st.subheader("📊 Cleaning summary")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("📄 Final rows", len(df_clean))
        c2.metric("🧹 Duplicates detected", len(cleaner.duplicates_df))
        c3.metric("⚠️ Issues detected", sum(len(v) for v in cleaner.issues.values()))
        c4.metric("🧩 Issue types", len(cleaner.issues))

        # ==================================================
        # ISSUES
        # ==================================================
        if cleaner.issues:
            st.subheader("⚠️ Values requiring review")
            st.caption(
                "These values could not be corrected automatically and may require manual review. "
                "Some values are shown in English because geographic normalization relies on "
                "standardized reference libraries."
            )

            with st.expander("🛠️ Manual review guide (recommended)"):
                st.markdown(
                    """
                    Some values were **not corrected automatically** to avoid incorrect assumptions.

                    ### Recommended workflow (Excel or similar tools):

                    1. Download the cleaned file  
                    2. Locate the affected row using the **Row index** shown above  
                    3. Review the original value  
                    4. Apply the correction if you are confident  
                    5. Save your final dataset  

                    This manual step ensures **maximum data accuracy** while keeping
                    the automated cleaning process transparent and reproducible.
                    """
                )

                st.caption(
                    "Automatic cleaning should assist decisions — not replace them."
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
                        



        # ==================================================
        # DOWNLOAD
        # ==================================================
        st.subheader("⬇️ Download clean file")

        df_export = df_display.copy()
        excel_buffer = BytesIO()
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
        padding: 12px 0;
    ">
        “A good data cleaner is not the one that fixes the most,<br>
        but the one that makes the fewest mistakes.”
    </div>
    """,
    unsafe_allow_html=True
)


