# 🧹 DataCleaner – Functional Overview

This document describes **what each module and function does** in the
DataCleaner project.

The philosophy of the project is:

> Clean data conservatively  
> never invent values  
> always keep traceability  

DataCleaner is not a “smart fixer”.
It is a **decision engine** that explains what was fixed, what was not,
and why.

---

## core.py

### class `DataCleaner`

Main orchestration class.

It coordinates all specialized cleaning modules and centralizes:

- the cleaned dataset
- the immutable original dataset
- all detected issues
- quality metrics for ETL analysis

---

### `__init__(source)`

- Loads data from:
  - a `pandas.DataFrame`
  - a CSV file
  - an Excel file
- Initializes internal state:
  - `df`: working DataFrame (mutable)
  - `original_df`: immutable snapshot of original data
  - `issues`: dictionary of detected issues
  - `duplicates_df`: duplicate rows for reporting
  - `_processed_columns`: avoids double-processing
  - `_internal_columns`: reserved for future premium diagnostics

---

### `_add_issue(issue_type, column, index, value)`

Internal helper to register issues.

Each issue stores:

- type (city, country, numeric, date, email, text)
- column name
- original row index
- original value

All modules report problems through this function.
This guarantees **full traceability**.

---

### `normalize_columns()`

- Normalizes column names:
  - lowercase
  - remove accents
  - replace symbols with `_`
- Creates `column_map`:
  - original name → normalized name

Used at the beginning of every plan.

Uses:

- `text_tools.normalize_dataframe_columns`

---

### `handle_texts(mode="basic")`

- Cleans **generic free-text columns**
- Explicitly excludes:
  - city
  - country
  - email
- Applies safe normalization
- Registers an issue if text becomes empty or invalid
- Keeps original value when unsafe to modify

Uses:

- `text_tools.normalize_text_basic`

---

### `handle_dates(mode="convert")`

Two-phase logic:

1. **Detection**
   - Samples values
   - Converts only if a high ratio can be parsed as dates

2. **Conversion**
   - Applies safe parsing
   - Registers issues for values that fail conversion

Uses:

- `date_tools.parse_date_safe`

---

### `handle_numeric_columns(on_error="nan")`

- Detects numeric columns using name heuristics
- Cleans numeric strings
- Converts safely to numeric dtype
- Registers issues when conversion fails

Uses:

- `number_tools.clean_numeric_series`

---

### `handle_emails()`

- Dynamically detects email columns
- Validates email format
- Invalid emails:
  - are removed (`None`)
  - generate an issue
- No guessing or correction beyond normalization

Uses:

- `email_tools.validate_email_simple`

---

### `handle_duplicates(subset=None, mode="remove")`

- Detects duplicated rows
- Stores all duplicates in `duplicates_df` for reporting
- Two modes:
  - `remove`: keep first occurrence
  - `mark`: adds `is_duplicate` flag

Uses:

- `validator.detect_duplicates`
- `validator.remove_duplicates`

---

### `run_basic_plan()`

Basic conservative cleaning pipeline:

1. Normalize columns
2. Snapshot original data
3. Clean texts
4. Detect & convert dates
5. Clean numeric columns
6. Validate emails
7. Remove duplicates

No geographic normalization is applied here.

---

### `run_medium_plan(...)`

Extended, intelligent cleaning pipeline.

Includes everything from the basic plan plus:

#### Countries

- Name-based detection (`country`, `pais`, `país`, `nation`, `region`)
- Dictionary-based normalization (ES → EN)
- No fuzzy matching
- Unrecognized values become issues

Uses:

- `geo_tools.handle_country_medium`

#### Cities

- Conservative fuzzy matching
- Dataset-aware learning
- Blocks short, ambiguous or dangerous matches
- Unresolved values become issues

Uses:

- `geo_tools.handle_city_medium`

---

### `compute_metrics()`

Computes **ETL quality metrics** comparing original vs cleaned data.

Metrics include:

- Row counts (raw / clean / removed)
- Total cells processed
- Total issues detected
- Issues per 1,000 rows
- Issue distribution by type
- Health ratio (dataset cleanliness)
- Auto-fix ratio (how much was fixed automatically)

This method is the foundation of the **Premium ETL Dashboard**.

---

## text_tools.py

### `normalize_text_basic(value)`

- Normalizes text safely:
  - removes accents
  - removes unsafe symbols
  - normalizes whitespace
- Preserves meaning
- Never invents content

---

### `normalize_dataframe_columns(df)`

- Normalizes DataFrame column names
- Ensures compatibility with pipelines and exports

---

## number_tools.py

### `clean_numeric_series(series, on_error)`

- Cleans numeric strings
- Converts to numeric dtype
- Returns:
  - cleaned Series
  - list of invalid original values

Uses `errors="coerce"` to avoid crashes.

---

## email_tools.py

### `validate_email_simple(email)`

- Regex-based email validation
- Dependency-free
- Used as the production default

---

## date_tools.py

### `parse_date_safe(value)`

- Safely parses a single date value
- Returns `NaT` on failure
- Never raises exceptions

---

### `is_date_like_series(series)`

- Heuristically determines if a Series represents dates
- Based on successful parse ratio

---

### `detect_date_columns(df)`

- Detects date-like columns even when dtype is `object`
- Tolerates mixed valid / invalid values

---

## geo_tools.py

### Design principles

- Countries: **dictionary-based only**
- Cities: **conservative fuzzy + dataset learning**
- Never invent geographic data

---

### `handle_country_medium(cleaner, column)`

- Normalizes country names using ES → EN mapping
- No fuzzy logic
- Unrecognized values generate issues
- Produces `<column>_clean`

---

### `handle_city_medium(cleaner, column, fuzzy_threshold)`

- Normalizes city names conservatively
- Uses:
  - exact matches
  - learned matches from the dataset
  - safe fuzzy matching
- Short or ambiguous values are rejected
- Produces `<column>_clean`

---

## validator.py

### `detect_duplicates(df, subset)`

- Detects duplicated rows
- Preserves original row indices
- Used for reporting and auditing

---

### `remove_duplicates(df, subset)`

- Removes duplicated rows
- Keeps first occurrence

---

## exporter.py

### `df_to_excel_bytes(dataframes)`

- Exports multiple DataFrames to Excel
- Preserves datetime formatting
- Returns file as bytes (Streamlit-ready)

---

### `export_df(df, path, file_type)`

Exports DataFrame to:

- Excel (`.xlsx`)
- CSV (`.csv`)
- Parquet (`.parquet`)

---

## settings.py

Global configuration:

- `FUZZY_THRESHOLD`
- Future deployment and platform settings

---

## Design Summary

- Conservative by design
- No silent corrections
- Full traceability
- Dataset-aware logic
- Modular architecture
- Ready for:
  - Streamlit apps
  - CLI tools
  - Premium ETL dashboards
