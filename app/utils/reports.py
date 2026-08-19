"""PDF report generation via ReportLab."""
import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def table_pdf(title, headers, rows):
    """Build a simple titled table PDF. rows: list of lists. Returns bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(title, styles["Title"]),
        Paragraph(f"Generated {date.today().isoformat()}", styles["Normal"]),
        Spacer(1, 12),
    ]

    data = [headers] + [[str(c) if c is not None else "" for c in row] for row in rows]
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f9")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    return buf.getvalue()


def certificate_pdf(title, lines):
    """A simple certificate-style PDF (e.g. baby dedication). Returns bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Spacer(1, 80), Paragraph(title, styles["Title"]), Spacer(1, 40)]
    for line in lines:
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 16))
    doc.build(elements)
    return buf.getvalue()
