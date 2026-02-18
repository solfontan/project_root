# cleaner/settings.py

"""
Global configuration settings.

This module defines adjustable constants used across the data cleaning
pipeline. Centralizing configuration values allows consistent behavior
and easier customization without modifying core logic.

These settings are intentionally conservative by default.
"""

# ---------------------------------------------------------------------
# Date handling
# ---------------------------------------------------------------------

# Default date format used for exports and parsing behavior.
# Options:
# - "y-m-d" → yyyy-mm-dd
# - "d-m-y" → dd-mm-yyyy
# DEFAULT_DATE_FORMAT = "y-m-d"


# ---------------------------------------------------------------------
# Fuzzy matching
# ---------------------------------------------------------------------

# Minimum similarity score (0–100) required to consider a fuzzy match valid.
# Used for conservative matching logic (e.g., city name suggestions).
FUZZY_THRESHOLD = 85


# ---------------------------------------------------------------------
# Duplicate handling (future use)
# ---------------------------------------------------------------------

# Whether duplicates should be kept by default.
# Recommended: False (detect first, remove explicitly).
# KEEP_DUPLICATES = False


# ---------------------------------------------------------------------
# Deployment / platform-related settings (future use)
# ---------------------------------------------------------------------

# Time (in seconds) after which temporary files may be removed
# in cloud or SaaS deployments.
# REMOVE_TEMP_FILES_AFTER_SECONDS = 3600
