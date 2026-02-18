# ARQUITECTURE GEO_TOOLS.PY

* Cities **y** Countries
* Heurística de detección
* Ejemplos before / after
* Explicación de por qué es seguro
* Alineado con Basic / Medium / Premium

---

````md
# 🌍 `geo_tools` — Geographic Cleaning (Cities & Countries)

The `geo_tools` module provides **safe, conservative and auditable utilities**
for cleaning **city and country names** in tabular datasets.

It is designed for **real ETL pipelines**, not demos.

> ❝ Never invent geographic data.  
> Normalize only when evidence is strong. ❞

This module is primarily used by the **Medium Plan** of `DataCleaner`.

---

## 🎯 What problems does it solve?

Real-world datasets often contain geographic values like:

### Cities
- `SEVILA`
- `Barclona`
- `Maddrd`
- `Se`
- random casing and spacing

### Countries
- `usa`, `U.S.A`, `United states`
- `Arg`, `Brasil`, `espana`
- mixed languages and abbreviations

Blind fuzzy matching usually **corrupts data silently**.  
`geo_tools` avoids that by applying **layered, evidence-based logic**.

---

## 🧠 Core Principles

1. **Exact match > learned match > fuzzy match**
2. **Fuzzy matching is conservative**
3. **Short or ambiguous values are never guessed**
4. **Uncertain values are flagged, not corrected**
5. **Original data is never lost**
6. **All decisions are traceable**

---

## 🧱 Architecture overview

`geo_tools` does **not decide when** to clean a column.

That responsibility belongs to `DataCleaner`, which:
- detects candidate columns by name
- validates them by sample behavior
- applies geo cleaning only when evidence is strong

`geo_tools` only answers:
> *“Given that this column is geographic, how do we clean it safely?”*

---

## 🏙️ City cleaning — Medium Plan

### Entry point

```python
handle_city_medium(cleaner, column, fuzzy_threshold=95)
````

## Internal output columns

* `<column>_clean`
* `<column>_confidence`
* `<column>_source`

Only `<column>_clean` is exposed to the final dataset.
The others are **internal metadata**, reserved for dashboards and audits.

---

### Step-by-step logic (Cities)

#### 1️⃣ Basic normalization

* Trim spaces
* Normalize capitalization

```text
" sevilla " → "Sevilla"
```

---

#### 2️⃣ Exact global match

Matches against a global city database (`geonamescache`).

```text
"Sevilla" → Sevilla
confidence: 100
source: exact
```

✔ High confidence
✔ No fuzzy logic

---

#### 3️⃣ Learned match (dataset memory)

If a city was already resolved **with high confidence** earlier,
reuse it.

```text
Earlier row:
"Sevilla" → Sevilla (exact)

Later row:
"SEVILLA" → Sevilla
confidence: 95
source: learned
```

This:

* improves consistency
* avoids repeated fuzzy searches
* scales efficiently

---

#### 4️⃣ Conservative fuzzy match

Applied **only if all conditions are met**:

* Length ≥ 4
* Global similarity (NOT partial match)
* Score ≥ threshold (default: 95)
* Reasonable length ratio

❌ Rejected (too dangerous):

```text
"Bar" → Barcelona ❌
"Se" → Sevilla ❌
```

✔ Accepted:

```text
"Maddrd" → Madrid
confidence: 89
source: fuzzy
```

---

#### 5️⃣ Unresolved → Issue

If no safe match is found:

* Value is NOT corrected
* It is removed from the clean dataset
* An issue is recorded

```text
"Se" → None
issue_type: city
```

---

## 🌍 Country cleaning — Medium Plan

Countries use a **similar but stricter** strategy
because incorrect country corrections are costly.

### Entry point

```python
handle_country_medium(cleaner, column)
```

---

### Step-by-step logic (Countries)

#### 1️⃣ Alias match (safe list)

Common, explicit aliases only:

```text
"usa" → United States
"uk" → United Kingdom
```

✔ Confidence: 100
✔ Source: alias

---

2️⃣ Exact global match

Uses `pycountry` official country names.

```text
"Spain" → Spain
confidence: 100
source: exact
```

---

3️⃣ Learned match (dataset memory)

Once a country is resolved with high confidence,
future rows reuse it.

```text
"united states" → United States
confidence: 95
source: learned
```

---

4️⃣ Conservative fuzzy (very strict)

Used only when:

* length ≥ 4
* score ≥ 97–98
* strong similarity

```text
"Argentin" → Argentina
confidence: 98
source: fuzzy
```

---

5️⃣ Unresolved → Issue

Ambiguous or unknown values are **not guessed**.

```text
"EU" → None
issue_type: country
```

---

## 📊 Example — Cities (Before / After)

### 🔴 Raw input

| city    |
| ------- |
| Sevilla |
| SEVILA  |
| Bar     |
| Maddrd  |
| None    |

---

### 🟢 Internal cleaned (debug view)

| city    | city_clean | city_confidence | city_source |
| ------- | ---------- | --------------- | ----------- |
| Sevilla | Sevilla    | 100             | exact       |
| SEVILA  | Sevilla    | 95              | learned     |
| Bar     | None       | None            | unresolved  |
| Maddrd  | Madrid     | 89              | fuzzy       |
| None    | None       | None            | missing     |

---

### ✅ Public dataset (exported)

| city    | city_clean |
| ------- | ---------- |
| Sevilla | Sevilla    |
| SEVILA  | Sevilla    |
| Bar     | None       |
| Maddrd  | Madrid     |
| None    | None       |

> `city_confidence` and `city_source` are **intentionally hidden**
> and reserved for Premium dashboards and ETL analysis.

---

## 🧪 Why this approach works

* Prevents **silent data corruption**
* Makes corrections **explainable**
* Enables **ETL quality metrics**, such as:

  * % exact vs fuzzy
  * confidence distributions
  * most problematic cities / countries
* Scales naturally to **Advanced / Premium plans**

---

## 🚫 What `geo_tools` does NOT do

* ❌ Guess short values
* ❌ Force corrections
* ❌ Infer countries from cities
* ❌ Overwrite original data blindly

---
