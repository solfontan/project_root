# cleaner/text_tools.py

"""
Text normalization utilities.

This module provides **safe and conservative text normalization helpers**
designed for data cleaning pipelines where **data integrity matters**.

The functions here:
- normalize formatting (case, accents, spacing, symbols)
- DO NOT guess or infer meaning
- DO NOT perform semantic corrections
- are fully reversible at the audit level

Typical use cases:
- City names (before validation or fuzzy matching)
- Free-text categorical columns
- Column name normalization
"""

import pandas as pd
import unicodedata
import re
from unidecode import unidecode


# ---------------------------------------------------------------------
# Regular expressions used internally
# ---------------------------------------------------------------------

# Matches any symbol that is NOT alphanumeric, space, or common separators
_SYMBOL_PATTERN = re.compile(r"[^A-Za-z0-9\s\.,/-]")

# Matches multiple consecutive whitespace characters
_WHITESPACE_PATTERN = re.compile(r"\s+")


# ---------------------------------------------------------------------
# Text normalization functions
# ---------------------------------------------------------------------

def normalize_text_basic(
    value,
    capitalize: bool = True,
    preserve_case: bool = False,
):
    """
    Normalize a text value in a **safe and conservative** way.

    This function performs **format normalization only**:
    - trims whitespace
    - removes accents and diacritics 
    - normalizes unicode characters
    - removes unsafe symbols
    - normalizes spacing
    - optionally applies casing rules

    ⚠️ This function DOES NOT:
    - correct typos
    - infer meaning
    - map values to canonical entities (cities, countries, etc.)

    Parameters
    ----------
    value : Any
        Input value (string-like). NaN values are returned unchanged.

    capitalize : bool, default=True
        If True, returns the text capitalized (first letter uppercase).
        Only applied when preserve_case=False and value is not numeric.

    preserve_case : bool, default=False
        If True, original casing is preserved.
        If False, text is lowercased before optional capitalization.

    Returns
    -------
    str or original value
        Normalized string, or original value if NaN.
    """
    if pd.isna(value):
        return value

    # Convert to string and trim surrounding whitespace
    text = str(value).strip()

    # Normalize unicode characters (NFKD)
    text = unicodedata.normalize("NFKD", text)

    # Remove diacritics / accents safely
    text = text.encode("ascii", "ignore").decode("utf-8", "ignore")

    # Case handling
    if not preserve_case:
        text = text.lower()

    # Remove unsafe symbols
    text = _SYMBOL_PATTERN.sub("", text)

    # Normalize whitespace
    text = _WHITESPACE_PATTERN.sub(" ", text)

    # Optional capitalization (for non-numeric values)
    if capitalize and not preserve_case and not text.isnumeric():
        return text.capitalize()

    return text


# ---------------------------------------------------------------------
# DataFrame utilities
# ---------------------------------------------------------------------

def normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DataFrame column names to a safe, consistent format.

    This function:
    - removes accents
    - converts to lowercase
    - replaces non-alphanumeric characters with underscores
    - collapses multiple underscores
    - strips leading/trailing underscores

    Example:
    --------
    "City Name (Raw)" → "city_name_raw"

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame whose columns will be normalized.

    Returns
    -------
    pandas.DataFrame
        Same DataFrame with normalized column names.
    """
    normalized_columns = (
        pd.Index(df.columns)
        .map(lambda col: unidecode(str(col)).lower())
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )

    df.columns = normalized_columns
    return df

