# cleaner/validator.py

"""
Data validation utilities.

This module provides helpers for detecting and handling duplicate records
in pandas DataFrames.

The functions here:
- identify duplicated rows with full traceability
- optionally remove duplicates in a controlled way

No assumptions are made about which duplicate is "correct".
"""

import pandas as pd


# ---------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------

def detect_duplicates(
    df: pd.DataFrame,
    subset: list | None = None,
) -> pd.DataFrame:
    """
    Detect duplicated rows in a DataFrame.

    This function:
    - identifies all duplicated rows (including originals)
    - preserves original row indices for traceability
    - does NOT modify the original DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame.

    subset : list or None, default=None
        Columns to consider for duplicate detection.
        If None, all columns are used.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing duplicated rows with an added
        `original_index` column.
    """
    duplicates = df[df.duplicated(subset=subset, keep=False)]

    duplicates = duplicates.assign(
        original_index=duplicates.index
    )

    ordered_columns = (
        ["original_index"]
        + [col for col in duplicates.columns if col != "original_index"]
    )

    return duplicates[ordered_columns]


# ---------------------------------------------------------------------
# Duplicate removal
# ---------------------------------------------------------------------

def remove_duplicates(
    df: pd.DataFrame,
    subset: list | None = None,
) -> pd.DataFrame:
    """
    Remove duplicated rows from a DataFrame.

    This function:
    - keeps the first occurrence of each duplicate
    - returns a new DataFrame
    - does NOT log or report removed rows

    ⚠️ Recommended usage:
    - Call `detect_duplicates` first
    - Review duplicates
    - Then call this function if removal is desired

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame.

    subset : list or None, default=None
        Columns to consider for duplicate detection.
        If None, all columns are used.

    Returns
    -------
    pandas.DataFrame
        DataFrame with duplicates removed.
    """
    return df.drop_duplicates(subset=subset)
