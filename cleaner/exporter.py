# cleaner/exporter.py

"""
Data export utilities.

This module provides helpers for exporting pandas DataFrames
to user-friendly formats, with special care for Excel compatibility.

The functions here:
- export multiple DataFrames to a single Excel file (in-memory)
- preserve datetime formatting in Excel
- support common export formats (xlsx, csv, parquet)

Typical use cases:
- Streamlit downloads
- Reporting pipelines
- Data cleaning tools with Excel-first users
"""

import pandas as pd
import io


# ---------------------------------------------------------------------
# Excel export utilities
# ---------------------------------------------------------------------

def dataframes_to_excel_bytes(
    dataframes: dict,
    date_format: str = "y-m-d",
) -> bytes:
    """
    Export multiple DataFrames to a single Excel file (in memory).

    This function:
    - writes each DataFrame to a separate sheet
    - enforces consistent datetime formatting
    - returns the Excel file as bytes (ideal for downloads)

    Parameters
    ----------
    dataframes : dict
        Dictionary of {sheet_name: DataFrame} pairs.

    date_format : {"y-m-d", "d-m-y"}, default="y-m-d"
        Date format to apply in Excel:
        - "y-m-d" → yyyy-mm-dd
        - "d-m-y" → dd-mm-yyyy

    Returns
    -------
    bytes
        Excel file content as bytes.
    """
    output_buffer = io.BytesIO()

    excel_date_format = (
        "yyyy-mm-dd"
        if date_format == "y-m-d"
        else "dd-mm-yyyy"
    )

    with pd.ExcelWriter(
        output_buffer,
        engine="xlsxwriter",
        datetime_format=excel_date_format,
    ) as writer:
        workbook = writer.book
        date_cell_format = workbook.add_format(
            {"num_format": excel_date_format}
        )

        for sheet_name, df in dataframes.items():
            safe_name = sheet_name[:31]  # Excel sheet name limit
            df.to_excel(writer, sheet_name=safe_name, index=False)

            worksheet = writer.sheets[safe_name]

            # Force full-column datetime formatting
            for col_idx, column in enumerate(df.columns):
                if pd.api.types.is_datetime64_any_dtype(df[column]):
                    worksheet.set_column(
                        col_idx,
                        col_idx,
                        15,
                        date_cell_format,
                    )

    output_buffer.seek(0)
    return output_buffer.read()


# ---------------------------------------------------------------------
# Generic export utilities
# ---------------------------------------------------------------------

def export_dataframe(
    df: pd.DataFrame,
    path: str,
    file_type: str = "xlsx",
):
    """
    Export a DataFrame to disk in a supported format.

    Supported formats:
    - xlsx
    - csv
    - parquet

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to export.

    path : str
        Destination file path.

    file_type : {"xlsx", "csv", "parquet"}, default="xlsx"
        Output file format.

    Raises
    ------
    ValueError
        If the file_type is not supported.
    """
    if file_type == "xlsx":
        df.to_excel(path, index=False)
    elif file_type == "csv":
        df.to_csv(path, index=False)
    elif file_type == "parquet":
        df.to_parquet(path, index=False)
    else:
        raise ValueError(
            f"Unsupported export format: {file_type}"
        )
