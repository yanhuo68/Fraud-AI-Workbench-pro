# agents/pdf_exporter.py

"""
PDF report builder for:
- SQL
- SQL result
- Trend chart
- Reconciliation summary
- Hybrid synthesis
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import altair as alt
import pandas as pd


def save_altair_chart_as_png(chart: alt.Chart):
    """
    Save an altair chart as PNG by rendering to a temporary file.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    png_path = tmp.name
    chart.save(png_path)
    return png_path


def generate_pdf(
    sql,
    df: pd.DataFrame,
    trend_chart,
    reconciliation_text,
    synthesis_text,
    output_path="analysis_report.pdf",
):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []

    # SQL
    story.append(Paragraph("<b>SQL Query</b>", styles["Heading2"]))
    story.append(Paragraph(f"<pre>{sql}</pre>", styles["Code"]))
    story.append(Spacer(1, 16))

    # Dataframe
    if df is not None and len(df):
        story.append(Paragraph("<b>SQL Result (Head)</b>", styles["Heading2"]))
        story.append(Paragraph(df.head().to_markdown(index=False), styles["BodyText"]))
        story.append(Spacer(1, 16))

    # Trend chart
    if trend_chart:
        png_path = save_altair_chart_as_png(trend_chart)
        story.append(Paragraph("<b>Trend Chart</b>", styles["Heading2"]))
        story.append(Image(png_path, width=500, height=300))
        story.append(Spacer(1, 16))

    # Reconciliation
    story.append(Paragraph("<b>SQL Reconciliation Summary</b>", styles["Heading2"]))
    story.append(Paragraph(reconciliation_text.replace("\n", "<br/>"), styles["BodyText"]))
    story.append(Spacer(1, 16))

    # Synthesis
    story.append(Paragraph("<b>Hybrid SQL + RAG Synthesis Report</b>", styles["Heading2"]))
    story.append(Paragraph(synthesis_text.replace("\n", "<br/>"), styles["BodyText"]))

    doc.build(story)
    return output_path
