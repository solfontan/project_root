# cleaner/core.py
import pandas as pd

from cleaner import text_tools as tt
from cleaner import date_tools as dt
from cleaner import email_tools as et
from cleaner import geo_tools as gt
from cleaner import number_tools as nt
from cleaner import validator as val
from .settings import FUZZY_THRESHOLD


class DataCleaner:
    """
    Main orchestration class.

    Coordinates specialized cleaning modules and registers issues
    without destroying original data.
    """

    def __init__(self, source):
        if isinstance(source, pd.DataFrame):
            self.df = source.copy()
        elif isinstance(source, str):
            self.df = (
                pd.read_csv(source)
                if source.endswith(".csv")
                else pd.read_excel(source)
            )
        else:
            raise ValueError("source must be a DataFrame or file path")

        self.original_df = None
        self.duplicates_df = pd.DataFrame()
        self.issues = {}

        self._processed_columns = set()
        self._internal_columns = set()

    # --------------------------------------------------
    # INTERNAL ISSUE REGISTRATION
    # --------------------------------------------------
    def _add_issue(self, issue_type, column, index, value):
        self.issues.setdefault(issue_type, []).append({
            "column": column,
            "index": int(index),
            "value": value
        })

    # --------------------------------------------------
    # COLUMN NORMALIZATION
    # --------------------------------------------------
    def normalize_columns(self):
        original_cols = self.df.columns.tolist()
        self.df = tt.normalize_dataframe_columns(self.df)
        self.column_map = dict(zip(original_cols, self.df.columns))
        return self

    # --------------------------------------------------
    # TEXT HANDLING
    # --------------------------------------------------
    def handle_texts(self, mode="basic"):
        excluded = {"city", "ciudad", "country", "pais", "email", "correo"}

        text_cols = [
            c for c in self.df.select_dtypes(include="object").columns
            if c.lower() not in excluded
        ]

        for col in text_cols:
            cleaned = []

            for idx, value in self.df[col].items():
                if pd.isna(value):
                    cleaned.append(None)
                    continue

                normalized = tt.normalize_text_basic(value)

                if not normalized:
                    self._add_issue("text", col, idx, value)
                    cleaned.append(value)
                else:
                    cleaned.append(normalized)

            self.df[col] = cleaned

        return self

    # --------------------------------------------------
    # DATE HANDLING
    # --------------------------------------------------
    def handle_dates(self, mode="convert"):
        """
        Medium plan date handling:
        - Detects date columns by name
        - Attempts parsing on all values
        - Invalid values become None
        - Issues are always recorded
        """

        DATE_HINTS = {"date", "fecha", "created", "updated", "birth"}

        for col in self.df.columns:

            if col in self._processed_columns:
                continue

            col_l = col.lower()

            # Heuristic by column name (NOT by content)
            if not any(hint in col_l for hint in DATE_HINTS):
                continue

            original = self.original_df[col]
            parsed = []

            for idx, value in original.items():

                if pd.isna(value):
                    parsed.append(None)
                    continue

                parsed_value = dt.parse_date_safe(value)

                if pd.isna(parsed_value):
                    self._add_issue("date", col, idx, value)
                    parsed.append(None)
                else:
                    parsed.append(parsed_value)

            self.df[col] = parsed
            self._processed_columns.add(col)

        return self

    # --------------------------------------------------
    # NUMERIC HANDLING
    # --------------------------------------------------
    def handle_numeric_columns(self, on_error="nan"):
        EXPECTED_NUMERIC = {
            "age", "edad", "price", "precio",
            "quantity", "qty", "cantidad",
            "units", "count", "total", "amount"
        }

        for col in self.df.columns:
            if col in self._processed_columns:
                continue

            if not any(k in col.lower() for k in EXPECTED_NUMERIC):
                continue

            original = self.original_df[col]
            converted, issues = nt.clean_numeric_series(
                self.df[col],
                on_error=on_error
            )

            for idx in original[original.notna() & converted.isna()].index:
                self._add_issue("numeric", col, idx, original.loc[idx])

            self.df[col] = converted
            self._processed_columns.add(col)

        return self

    # --------------------------------------------------
    # EMAIL HANDLING
    # --------------------------------------------------
    def handle_emails(self):
        
        EMAIL_HINTS = {"email", "e-mail", "mail", "correo", "gmail"}

        for col in self.df.columns:
            col_l = col.lower()

            if not any(hint in col_l for hint in EMAIL_HINTS):
                continue


            cleaned = []

            for idx, value in self.original_df[col].items():
                if pd.isna(value):
                    cleaned.append(None)
                    continue

                value = str(value).strip().lower()

                if not et.validate_email_medium(value):
                    self._add_issue("email", col, idx, value)
                    cleaned.append(None)
                else:
                    cleaned.append(value)

            self.df[col] = cleaned
            self._processed_columns.add(col)

        return self

    # --------------------------------------------------
    # COUNTRY HANDLING
    # --------------------------------------------------
    def validate_country_column(self, col):
        self.df[f"{col}_country_valid"] = (
            self.df[col].apply(gt.normalize_country_name)
        )
        return self

    # --------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------
    def handle_duplicates(self, subset=None, mode="remove"):
        self.duplicates_df = val.detect_duplicates(
            self.df,
            subset=subset
        )

        if mode == "remove":
            self.df = val.remove_duplicates(self.df, subset=subset)
        elif mode == "mark":
            self.df["is_duplicate"] = self.df.duplicated(
                subset=subset,
                keep=False
            )

        return self


    # --------------------------------------------------
    # BASIC PLAN
    # --------------------------------------------------
    def run_basic_plan(self):
        self.normalize_columns()
        self.original_df = self.df.copy(deep=True)
        self._processed_columns.clear()
        self.issues.clear()

        self.handle_texts()
        self.handle_dates()
        self.handle_numeric_columns()
        self.handle_emails()
        self.handle_duplicates()

        return self

    # --------------------------------------------------
    # MEDIUM PLAN
    # --------------------------------------------------
    def run_medium_plan(
        self,
        date_mode="convert",
        duplicate_subset=None,
        duplicate_mode="remove",
        numeric_error_mode="nan",
        email_mode="conservative",
        text_mode="basic"
    ):
        """
        Medium cleaning plan.

        Characteristics:
        - Conservative but intelligent corrections
        - Dataset-aware geographic normalization
        - Issues are recorded instead of inventing data
        - Internal diagnostics are kept separate from public output
        """

        # --------------------------------------------------
        # SETUP
        # --------------------------------------------------
        self.normalize_columns()
        self.original_df = self.df.copy(deep=True)
        self._processed_columns.clear()
        self.issues.clear()

        # --------------------------------------------------
        # CORE CLEANING
        # --------------------------------------------------
        self.handle_texts(mode=text_mode)
        self.handle_dates(mode=date_mode)
        self.handle_numeric_columns(on_error=numeric_error_mode)
        self.handle_emails()

        # --------------------------------------------------
        # DUPLICATES
        # --------------------------------------------------
        if duplicate_subset:
            duplicate_subset = [
                self.column_map.get(c, c)
                for c in duplicate_subset
            ]

        self.handle_duplicates(
            subset=duplicate_subset,
            mode=duplicate_mode
        )

        # --------------------------------------------------
        # GEO: COUNTRIES (NAME-BASED, SAFE)
        # --------------------------------------------------
        COUNTRY_NAMES = {
            "country", "pais", "país",
            "nation", "nationality", "region"
        }

        for col in self.df.columns:

            if col in self._processed_columns:
                continue

            if col.lower() not in COUNTRY_NAMES:
                continue

            gt.handle_country_medium(self, col)

        # --------------------------------------------------
        # GEO: CITIES (CONSERVATIVE, DATASET-AWARE)
        # --------------------------------------------------
        CITY_NAMES = {"city", "ciudad"}

        for col in self.df.columns:

            if col in self._processed_columns:
                continue

            if col.lower() not in CITY_NAMES:
                continue

            gt.handle_city_medium(
                self,
                col,
                fuzzy_threshold=FUZZY_THRESHOLD
            )

        return self


    #---------------------------------------------------
    # TABLA DE MÉTRICAS
    #---------------------------------------------------
    def compute_metrics(self):
        """
        Compute ETL quality metrics based on original vs cleaned dataset
        and detected issues.
        """

        # -----------------------------
        # BASIC COUNTS
        # -----------------------------
        total_rows_raw = len(self.original_df)
        total_rows_clean = len(self.df)
        total_columns = len(self.original_df.columns)

        rows_removed = total_rows_raw - total_rows_clean
        rows_removed_pct = (
            rows_removed / total_rows_raw
            if total_rows_raw > 0 else 0
        )

        total_cells = total_rows_raw * total_columns

        # -----------------------------
        # ISSUE COUNTS
        # -----------------------------
        total_issues = sum(len(v) for v in self.issues.values())

        issues_by_type = {
            issue_type: len(items)
            for issue_type, items in self.issues.items()
        }

        # Safe getters
        city_issues = issues_by_type.get("city", 0)
        country_issues = issues_by_type.get("country", 0)
        numeric_issues = issues_by_type.get("numeric", 0)
        date_issues = issues_by_type.get("date", 0)
        email_issues = issues_by_type.get("email", 0)
        text_issues = issues_by_type.get("text", 0)

        # -----------------------------
        # NORMALIZED METRICS
        # -----------------------------
        issues_per_1000_rows = (
            (total_issues / total_rows_raw) * 1000
            if total_rows_raw > 0 else 0
        )

        issue_ratio = (
            total_issues / total_cells
            if total_cells > 0 else 0
        )

        health_ratio = 1 - issue_ratio

        # -----------------------------
        # AUTO-FIX METRICS (KEY FOR PREMIUM)
        # -----------------------------
        auto_fixed_issues = (
            total_issues
            - city_issues
            - country_issues
        )

        auto_fix_ratio = (
            auto_fixed_issues / total_issues
            if total_issues > 0 else 0
        )

        # -----------------------------
        # FINAL METRICS DICT
        # -----------------------------
        metrics = {
            # Header KPIs
            "total_rows_raw": total_rows_raw,
            "total_rows_clean": total_rows_clean,
            "rows_removed": rows_removed,
            "rows_removed_pct": rows_removed_pct,

            # Volume
            "total_columns": total_columns,
            "total_cells": total_cells,

            # Issues
            "total_issues": total_issues,
            "issues_per_1000_rows": issues_per_1000_rows,
            "issues_by_type": issues_by_type,

            # Specific issues (easy Excel mapping)
            "city_issues": city_issues,
            "country_issues": country_issues,
            "numeric_issues": numeric_issues,
            "date_issues": date_issues,
            "email_issues": email_issues,
            "text_issues": text_issues,

            # Quality ratios
            "health_ratio": health_ratio,
            "auto_fix_ratio": auto_fix_ratio,
        }

        return metrics
