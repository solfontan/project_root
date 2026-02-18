# cleaner/number_tools.py

"""
Numeric normalization utilities.

This module provides **safe and conservative numeric cleaning functions**
for data pipelines where numeric integrity and traceability are required.

The functions here:
- normalize numeric strings
- handle common formatting issues (commas, symbols)
- convert values to numeric types safely
- report problematic values instead of silently fixing them

Typical use cases:
- Financial data imported from Excel
- CSV files with mixed numeric formats
- Columns containing numeric values stored as text
"""

import pandas as pd
import re


# ---------------------------------------------------------------------
# Regular expressions used internally
# ---------------------------------------------------------------------

# Matches any character that is NOT a digit, dot, or minus sign
_NON_NUMERIC_PATTERN = re.compile(r"[^\d\.\-]")


# ---------------------------------------------------------------------
# Numeric cleaning functions
# ---------------------------------------------------------------------

def clean_numeric_series(
    series: pd.Series,
    on_error: str = "nan",
):
    """
    Clean and normalize a pandas Series containing numeric values.

    This function:
    - removes non-numeric symbols
    - normalizes decimal separators
    - safely converts values to numeric
    - tracks values that could not be converted

    ⚠️ This function DOES NOT:
    - guess missing values
    - invent numbers
    - silently overwrite invalid data

    Parameters
    ----------
    series : pandas.Series
        Input Series containing numeric-like values.

    on_error : {"nan", "median"}, default="nan"
        Strategy to apply when conversion fails:
        - "nan": keep invalid values as NaN (recommended)
        - "median": replace invalid values with the median of valid data

    Returns
    -------
    tuple
        (cleaned_series, issues)

        cleaned_series : pandas.Series
            Series converted to numeric dtype.

        issues : list
            Unique original values that could not be converted.
            Useful for auditing and reporting.
    """
    original_series = series.copy()

    # Convert everything to string and normalize formatting
    cleaned_text = (
        series
        .astype(str)
        .str.strip()
        .replace({"": None, "nan": None, "None": None})
        .str.replace(",", ".", regex=False)
        .str.replace(_NON_NUMERIC_PATTERN, "", regex=True)
    )

    # Convert to numeric, forcing invalid values to NaN
    numeric_series = pd.to_numeric(cleaned_text, errors="coerce")

    # Identify problematic values (original was not NaN, but conversion failed)
    issue_mask = numeric_series.isna() & original_series.notna()

    issues = (
        original_series[issue_mask]
        .astype(str)
        .unique()
        .tolist()
    )

    # Optional strategy: fill NaN values with median
    if on_error == "median" and not numeric_series.dropna().empty:
        numeric_series = numeric_series.fillna(numeric_series.median())

    return numeric_series, issues
