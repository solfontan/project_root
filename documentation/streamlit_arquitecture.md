# 🧹 DataCleaner – Streamlit Apps

DataCleaner provides **three progressive cleaning plans** designed for
real-world datasets and professional ETL workflows.

The philosophy is simple:

> Clean conservatively,  
> never invent data,  
> always keep traceability.

---

## 🧹 DataCleaner – Basic Plan

The **Basic Plan** cleans datasets in a **safe, automatic, and conservative** way.
It focuses only on corrections that can be made with **high confidence**.

This plan is ideal for:

- Excel users
- Power BI users
- Analysts who want a clean dataset without manual preprocessing

---

## 🚀 What the Basic Plan does

The Basic Plan applies the following steps automatically:

### ✅ Column normalization

- Removes accents
- Converts column names to lowercase
- Replaces spaces and symbols with `_`
- Ensures consistent naming for analysis

### ✅ Text normalization (safe)

- Trims extra spaces
- Normalizes capitalization
- Does **not** modify ambiguous or destructive text values

### ✅ Date parsing (conservative)

- Detects date-like columns automatically
- Converts valid values to datetime
- Leaves invalid or ambiguous values unchanged
- Invalid values may remain as `NaT`

### ✅ Duplicate removal

- Removes exact duplicate rows
- Keeps the first occurrence

---

## ❌ What the Basic Plan does NOT do

To avoid incorrect corrections, the Basic Plan **does not**:

- Modify emails
- Guess or normalize cities
- Normalize countries
- Force numeric conversions when values are ambiguous

When a value cannot be interpreted safely, it is **left unchanged**.

---

## 📊 Output

After processing, the app provides:

- Cleaned dataset preview
- Summary metrics:
  - Final number of rows
  - Number of duplicates removed
  - Number of detected date columns
- Download options:
  - 📘 Excel (`.xlsx`)
  - 📄 CSV (`.csv`)

Dates are exported in a consistent format:

- `YYYY-MM-DD`

---

## 🧠 Philosophy

> *“A good data cleaner is not the one that fixes the most,  
> but the one that makes the fewest mistakes.”*

The Basic Plan prioritizes **data integrity over aggressive cleaning**.

---

## 🔜 When to use the Medium Plan

Use the **Medium Plan** if your dataset contains:

- Invalid numbers (e.g. `"Three"` instead of `3`)
- Broken emails
- Inconsistent cities or regions
- Mixed date formats with errors

---

## 🧹 DataCleaner – Medium Plan

The **Medium Plan** extends the Basic Plan with **deeper automatic cleaning**
while still prioritizing safety and transparency.

It is designed for:

- Messy real-world datasets
- CRM / ERP exports
- Surveys and user-generated data

---

## 🚀 What the Medium Plan adds

In addition to everything in the **Basic Plan**, the Medium Plan includes:

---

### 🔢 Numeric correction

- Detects numeric columns by name and behavior
- Cleans values like:
  - `"1,200"` → `1200`
  - `"12.5 USD"` → `12.5`
- Handles invalid values using:
  - Median imputation (recommended)
  - Or leaving them empty (`NaN`)

Invalid numeric values are logged as issues.

---

### 📧 Email validation

- Detects email-like columns automatically
- Validates basic email structure
- Invalid emails are removed from the clean dataset
- All invalid values are logged for review

---

### 🌍 Geographic normalization (conservative)

#### Countries

- Normalized using a controlled dictionary (e.g. Spanish → English)
- No fuzzy guessing
- Unrecognized values are logged as issues

#### Cities

- Capitalization normalization only
- Conservative fuzzy matching (very strict)
- Ambiguous values are:
  - Logged as issues
  - Removed from the clean dataset

This avoids incorrect geographic assumptions.

---

### ⚠️ Issue tracking (key feature)

The Medium Plan tracks **all values that could not be safely corrected**.

Issues are grouped by type:

- 📅 Date parsing issues
- 🔢 Numeric conversion issues
- 📧 Invalid email formats
- 📝 Non-normalizable text
- 🏙️ City issues
- 🌍 Country issues

Each issue includes:

- Column name
- Row index
- Original value

This enables **targeted manual review**.

---

### 🧹 Duplicate handling

- Detects duplicated rows
- Either:
  - Removes duplicates
  - Or marks them (configurable)

---

## 📊 Output & Dashboard

After processing, the app shows:

### Metrics

- Final number of rows
- Duplicates detected
- Total issues found
- Issue categories

### Interactive issue review

- Expandable sections per issue type
- Preview of problematic values
- Clear explanation of why each value was flagged
- Manual review guide (Excel-friendly)

---

## ⬇️ Downloads

You can export the cleaned dataset as:

- 📘 Excel (`.xlsx`)
- 📄 CSV (`.csv`)

Dates are exported consistently:

- `YYYY-MM-DD`
- or `DD-MM-YYYY`

---

## 🧠 Design philosophy

The Medium Plan follows one strict rule:

> **Never guess silently.**

If a value cannot be corrected with high confidence:

- It is not modified
- It is logged
- The user stays in control

---

## 💎 DataCleaner – Premium Plan (ETL Dashboard)

The **Premium Plan** builds on the Medium Plan and adds
**ETL observability and auditability**.

This plan is designed for:

- Data teams
- Analytics workflows
- Long-term dataset ownership

---

## 🚀 What the Premium Plan adds

### 📊 ETL Quality Dashboard (Excel-based)

- A dedicated **Analysis** sheet generated automatically
- A pre-built **Dashboard** sheet linked to analysis cells
- KPIs such as:
  - Dataset health ratio
  - Issues per 1,000 rows
  - Auto-fix vs manual-review ratio
  - Top issue categories
  - Row loss percentage

The dashboard updates automatically when:

- A new dataset is cleaned
- The Analysis sheet is refreshed

---

### 🔍 Full traceability

- Original vs cleaned row counts
- Issue distribution by type
- Identification of fragile columns
- Clear handoff to another analyst or team

---

### 🧠 Why Premium matters

The Premium Plan answers questions like:

- *Where does this dataset usually break?*
- *Which columns need better collection rules?*
- *How risky is automatic cleaning here?*
- *What should be imputed vs fixed at the source?*

This is **ETL intelligence**, not just cleaning.

---

## 🏁 Summary

| Plan    | Focus                             |
|---------|-----------------------------------|
| Basic   | Safe automatic cleanup            |
| Medium  | Accountable, explainable cleaning |
| Premium | ETL insight & long-term quality   |

DataCleaner is designed to **scale with your data maturity**.

> *Clean first. Understand second. Optimize last.*
