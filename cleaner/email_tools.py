# cleaner/email_tools.py

"""
Email validation and normalization utilities.

This module provides **safe and flexible email validation tools**
designed for data cleaning pipelines.

Key principles:
- Never invent emails
- Normalize only when validation succeeds
- Support environments with or without external dependencies
- Allow both column-level auditing and strict value cleaning

Typical use cases:
- CRM data cleaning
- User databases
- Marketing datasets
"""

import pandas as pd
import re

# ---------------------------------------------------------------------
# Optional dependency handling
# ---------------------------------------------------------------------

try:
    from email_validator import validate_email
    HAS_EMAIL_VALIDATOR = True
except Exception:
    HAS_EMAIL_VALIDATOR = False


# ---------------------------------------------------------------------
# Fallback regex (simple validation)
# ---------------------------------------------------------------------

_SIMPLE_EMAIL_PATTERN = re.compile(
    r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$",
    flags=re.IGNORECASE
)


# ---------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------

def validate_email_simple(email) -> bool:
    """
    Perform a simple regex-based email validation.

    This is a **fallback method** used when the `email-validator`
    package is not available.

    Parameters
    ----------
    email : Any
        Email-like value to validate.

    Returns
    -------
    bool
        True if the email matches a basic pattern, False otherwise.
    """
    if email is None or (isinstance(email, float) and pd.isna(email)):
        return False

    return bool(_SIMPLE_EMAIL_PATTERN.match(str(email).strip()))


def validate_email_safe(email):
    """
    Validate an email address and return a normalized version if valid.

    This function:
    - Uses `email-validator` when available
    - Falls back to regex-based validation otherwise
    - Never raises exceptions

    Parameters
    ----------
    email : Any
        Email-like value to validate.

    Returns
    -------
    tuple
        (is_valid, normalized_email)

        is_valid : bool
            Whether the email is considered valid.

        normalized_email : str or None
            Normalized email if valid, otherwise None.
    """
    if not HAS_EMAIL_VALIDATOR: # si esta instalado el email_validator
        is_valid = validate_email_simple(email)
        return is_valid, email if is_valid else None

    try:
        validation = validate_email(
            str(email).strip(),
            check_deliverability=False # no chequea dominio
        )
        return True, validation.email
    except Exception:
        return False, None


# ---------------------------------------------------------------------
# DataFrame-level utilities
# ---------------------------------------------------------------------

def validate_email_column(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:
    """
    Validate and normalize an email column in a DataFrame.

    This function:
    - Validates each email value
    - Adds two new columns:
        - `<column>_email_valid`
        - `<column>_email_normalized`

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame.

    column : str
        Name of the column containing email addresses.

    Returns
    -------
    pandas.DataFrame
        DataFrame with validation and normalization columns added.
    """
    results = df[column].apply(validate_email_safe)

    is_valid, normalized = zip(*results)

    df[f"{column}_email_valid"] = is_valid
    df[f"{column}_email_normalized"] = normalized

    return df


# ---------------------------------------------------------------------
# Strict cleaning utility
# ---------------------------------------------------------------------

def clean_email_strict(email):
    """
    Strictly clean and normalize a single email value.

    This function:
    - Lowercases the email
    - Validates it
    - Returns None if validation fails

    ⚠️ This is intended for pipelines where invalid emails
    must be removed or nullified.

    Parameters
    ----------
    email : Any
        Email-like value.

    Returns
    -------
    str or None
        Normalized email if valid, otherwise None.
    """
    if email is None or (isinstance(email, float) and pd.isna(email)):
        return None

    email_str = str(email).strip().lower()

    if not HAS_EMAIL_VALIDATOR:
        return email_str if validate_email_simple(email_str) else None

    try:
        validation = validate_email(
            email_str,
            check_deliverability=False
        )
        return validation.email
    except Exception:
        return None

def validate_email_medium(email: str) -> bool:
    if not email:
        return False

    email = email.strip().lower()

    if "@" not in email:
        return False

    local, _, domain = email.partition("@")

    if not local or "." not in domain:
        return False

    if len(domain.split(".")[-1]) < 2:
        return False

    return True
