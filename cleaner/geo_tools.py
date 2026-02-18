"""
Geographic validation and normalization utilities.

This module provides conservative, dataset-aware helpers for
cleaning country and city names in ETL pipelines.

Design principles:
- Never invent geographic data
- Learn only from high-confidence values
- Countries: dictionary-based (no fuzzy)
- Cities: conservative fuzzy + dataset learning
"""

import json
from pathlib import Path

import pandas as pd
import unicodedata
from thefuzz import process, fuzz

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def normalize_key(value: str) -> str | None:
    """Lowercase, strip, remove accents."""
    if value is None:
        return None

    s = str(value).strip().lower()
    if not s:
        return None

    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("utf-8")
    return s


def normalize_basic(value):
    """Safe public normalization (capitalization only)."""
    if value is None:
        return None

    s = str(value).strip()
    return s.title() if s else None


# --------------------------------------------------
# COUNTRY MAP (ES → EN)
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "json" / "country_es_en.json"

with open(JSON_PATH, encoding="utf-8") as f:
    COUNTRY_MAP_ES = json.load(f)


# --------------------------------------------------
# CITY DATA
# --------------------------------------------------
try:
    import geonamescache
    HAS_GEONAMES = True
except Exception:
    HAS_GEONAMES = False


def build_city_set():
    if not HAS_GEONAMES:
        return set()

    gc = geonamescache.GeonamesCache()
    return {c["name"].lower() for c in gc.get_cities().values()}


CITIES_SET = build_city_set()
CITIES_LIST = list(CITIES_SET)


# --------------------------------------------------
# SAFE FUZZY MATCH (CITIES ONLY)
# --------------------------------------------------
def safe_fuzzy_match(value, candidates, threshold=95):
    if not value or len(value) < 4:
        return None, 0

    match = process.extractOne(
        value.lower(),
        candidates,
        scorer=fuzz.ratio
    )

    if not match:
        return None, 0

    candidate, score = match

    if score < threshold:
        return None, score

    length_ratio = min(len(value), len(candidate)) / max(len(value), len(candidate))
    if length_ratio < 0.6:
        return None, score

    return candidate.title(), score


# ==================================================
# COUNTRY HANDLER — MEDIUM PLAN
# ==================================================
def handle_country_medium(cleaner, column):
    """
    Country cleaning using ES → EN dictionary only.

    Public output:
    - <column>_clean

    Internal:
    - issues only
    """

    cleaned = []

    for idx in cleaner.df.index:
        raw = cleaner.original_df.loc[idx, column]

        if pd.isna(raw):
            cleaned.append(None)
            continue

        key = normalize_key(raw)

        if key in COUNTRY_MAP_ES:
            cleaned.append(COUNTRY_MAP_ES[key])
        else:
            cleaner._add_issue("country", column, idx, raw)
            cleaned.append(None)

    cleaner.df[f"{column}_clean"] = cleaned
    cleaner._processed_columns.add(column)
    return cleaner


# ==================================================
# CITY HANDLER — MEDIUM PLAN
# ==================================================
def handle_city_medium(cleaner, column, fuzzy_threshold=95):
    """
    Conservative city normalization with dataset learning.
    """

    cleaned = []
    learned = {}

    for idx in cleaner.df.index:
        raw = cleaner.original_df.loc[idx, column]

        if pd.isna(raw):
            cleaned.append(None)
            continue

        value = normalize_basic(raw)
        key = value.lower()

        # Exact match
        if key in CITIES_SET:
            cleaned.append(value)
            learned[key] = value
            continue

        # Learned match
        if key in learned:
            cleaned.append(learned[key])
            continue

        # Fuzzy (cities only)
        match, score = safe_fuzzy_match(
            value,
            CITIES_LIST,
            threshold=fuzzy_threshold
        )

        if match:
            cleaned.append(match)
            if score >= 97:
                learned[key] = match
            continue

        # Unresolved
        cleaner._add_issue("city", column, idx, raw)
        cleaned.append(None)

    cleaner.df[f"{column}_clean"] = cleaned
    cleaner._processed_columns.add(column)
    return cleaner
