# cleaner/date_tools.py

"""
Date parsing and detection utilities.

This module provides **robust and conservative helpers** for working with
date-like data in pandas DataFrames.

The functions here:
- safely parse individual date values
- detect date-like columns even when stored as object
- tolerate mixed formats and invalid entries
- never raise exceptions during parsing

Typical use cases:
- CSV / Excel imports with inconsistent date formats
- Legacy datasets with mixed datetime representations
- Automatic date column detection in EDA pipelines
"""

import pandas as pd
from dateutil import parser


# ---------------------------------------------------------------------
# Value-level utilities
# ---------------------------------------------------------------------

def parse_date_safe(value):
    """
    Safely parse a single value into a datetime.

    This function:
    - returns NaT for missing or invalid values
    - preserves existing pandas Timestamp values
    - supports mixed date formats
    - never raises exceptions

    Parameters
    ----------
    value : Any
        Date-like value (string, datetime, etc.).

    Returns
    -------
    pandas.Timestamp or pandas.NaT
        Parsed datetime value, or NaT if parsing fails.
    """
    if pd.isna(value):
        return pd.NaT

    # Preserve already-parsed datetime values
    if isinstance(value, pd.Timestamp):
        return value

    text = str(value).strip()

    if text == "" or text.lower() in {"nan", "none"}:
        return pd.NaT

    try:
        return parser.parse(text, dayfirst=True, fuzzy=True)
    except Exception:
        return pd.NaT


# ---------------------------------------------------------------------
# Series-level utilities
# ---------------------------------------------------------------------

def parse_date_series(series: pd.Series) -> pd.Series:
    """
    Parse an entire pandas Series into datetime values safely.

    Parameters
    ----------
    series : pandas.Series
        Input Series containing date-like values.

    Returns
    -------
    pandas.Series
        Series with parsed datetime values (NaT where parsing fails).
    """
    return series.apply(parse_date_safe)


def is_date_like_series(
    series: pd.Series,
    sample_size: int = 10,
    threshold: float = 0.5,
) -> bool:
    """
    Determine whether a Series is likely to represent dates.

    The decision is based on parsing a sample of non-null values
    and checking the ratio of successful parses.

    Parameters
    ----------
    series : pandas.Series
        Input Series to evaluate.

    sample_size : int, default=10
        Number of non-null values to sample.

    threshold : float, default=0.5
        Minimum ratio of successful parses required.

    Returns
    -------
    bool
        True if the Series is considered date-like, False otherwise.
    """
    sample = (
        series
        .dropna()
        .astype(str)
        .head(sample_size)
    )

    if sample.empty:
        return False

    parsed = pd.to_datetime(
        sample,
        errors="coerce",
        infer_datetime_format=True
    )

    success_ratio = parsed.notna().mean()
    return success_ratio >= threshold


# ---------------------------------------------------------------------
# DataFrame-level utilities
# ---------------------------------------------------------------------

def detect_date_columns(
    df: pd.DataFrame,
    sample_size: int = 10,
    threshold: float = 0.4,
) -> list:
    """
    Detect columns in a DataFrame that are likely to contain dates.

    This function:
    - detects datetime dtypes directly
    - evaluates object columns using date parsing heuristics
    - tolerates mixed valid/invalid values

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame.

    sample_size : int, default=10
        Number of non-null values to sample per column.

    threshold : float, default=0.4
        Minimum ratio of successful parses required.

    Returns
    -------
    list
        List of column names likely to represent dates.
    """
    date_columns = []

    for column in df.columns:
        series = df[column]

        # Already datetime dtype
        if pd.api.types.is_datetime64_any_dtype(series):
            date_columns.append(column)
            continue

        parsed_count = 0
        checked_count = 0

        for value in series.dropna().head(sample_size):
            checked_count += 1

            if isinstance(value, pd.Timestamp):
                parsed_count += 1
                continue

            try:
                parser.parse(str(value), fuzzy=True)
                parsed_count += 1
            except Exception:
                pass

        if checked_count > 0 and parsed_count / checked_count >= threshold:
            date_columns.append(column)

    return date_columns
