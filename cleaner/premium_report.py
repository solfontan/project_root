# cleaner/pdf_report.py

import io
import datetime
import matplotlib.pyplot as plt
import pandas as pd

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER


def generate_premium_pdf(metrics, cleaner, df_clean):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # -----------------------------
    # Custom Styles
    # -----------------------------
    title_style = styles["Title"]
    section_style = styles["Heading2"]

    center_style = ParagraphStyle(
        name="Center",
        parent=styles["Normal"],
        alignment=TA_CENTER
    )

    # =============================
    # COVER
    # =============================
    elements.append(Paragraph("DataCleaner – Premium Intelligence Report", title_style))
    elements.append(Spacer(1, 20))

    today = datetime.date.today().strftime("%B %d, %Y")

    elements.append(Paragraph(f"Generated on: {today}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    health_score = round(metrics["health_ratio"] * 100, 2)

    elements.append(Paragraph(
        f"<b>Dataset Health Score: {health_score}/100</b>",
        center_style
    ))
    elements.append(Spacer(1, 30))

    # =============================
    # EXECUTIVE SUMMARY
    # =============================
    elements.append(Paragraph("Executive Summary", section_style))
    elements.append(Spacer(1, 12))

    summary_text = f"""
    Raw Rows: {metrics["total_rows_raw"]}<br/>
    Clean Rows: {metrics["total_rows_clean"]}<br/>
    Total Issues: {metrics["total_issues"]}<br/>
    Auto-Fix Ratio: {round(metrics["auto_fix_ratio"]*100,2)}%<br/>
    """

    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # =============================
    # KEY METRICS TABLE
    # =============================
    elements.append(Paragraph("Key Metrics Overview", section_style))
    elements.append(Spacer(1, 12))

    data = [
        ["Metric", "Value"],
        ["Rows (raw)", metrics["total_rows_raw"]],
        ["Rows (clean)", metrics["total_rows_clean"]],
        ["Rows removed", metrics["rows_removed"]],
        ["Total columns", metrics["total_columns"]],
        ["Total issues", metrics["total_issues"]],
        ["Issues per 1,000 rows", round(metrics["issues_per_1000_rows"],2)]
    ]

    table = Table(data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#f3f4f6")),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # =============================
    # ISSUE DISTRIBUTION GRAPH
    # =============================
    elements.append(Paragraph("Issue Distribution Analysis", section_style))
    elements.append(Spacer(1, 12))

    issue_df = pd.DataFrame.from_dict(
        metrics["issues_by_type"],
        orient="index",
        columns=["count"]
    ).reset_index()

    issue_df.columns = ["Issue Type", "Count"]

    if not issue_df.empty:

        plt.figure(figsize=(6,4))
        plt.bar(issue_df["Issue Type"], issue_df["Count"], color="#3B82F6")
        plt.title("Issue Distribution")
        plt.xticks(rotation=45)

        img_buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format="png")
        plt.close()

        img_buffer.seek(0)

        elements.append(Image(img_buffer, width=5*inch, height=3*inch))
        elements.append(Spacer(1, 20))

    # =============================
    # SYSTEM INTERPRETATION
    # =============================
    elements.append(Paragraph("System Interpretation", section_style))
    elements.append(Spacer(1, 12))

    if health_score >= 85:
        interpretation = "Dataset is highly reliable and ready for analytics."
    elif health_score >= 60:
        interpretation = "Moderate inconsistencies detected. Recommended targeted validation."
    else:
        interpretation = "High risk dataset. Intervention required before business use."

    elements.append(Paragraph(interpretation, styles["Normal"]))
    elements.append(Spacer(1, 20))

    doc.build(elements)

    buffer.seek(0)
    return buffer

