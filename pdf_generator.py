from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
import io


def generate_invoice_pdf(invoice) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=25*mm,
        bottomMargin=25*mm,
        leftMargin=25*mm,
        rightMargin=25*mm
    )

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontSize=22, spaceAfter=2
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"], fontSize=9, textColor=colors.grey
    )
    normal_style = styles["Normal"]
    right_style = ParagraphStyle(
        "Right", parent=styles["Normal"], alignment=TA_RIGHT
    )

    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Paragraph(invoice.invoice_number, label_style))
    elements.append(Spacer(1, 12*mm))

    info_table_data = [
        [
            Paragraph("<b>Billed To</b>", normal_style),
            Paragraph("<b>Invoice Details</b>", normal_style)
        ],
        [
            Paragraph(
                f"{invoice.client.name}<br/>{invoice.client.email}<br/>"
                f"{invoice.client.phone or ''}<br/>{invoice.client.address or ''}",
                normal_style
            ),
            Paragraph(
                f"Issue Date: {invoice.issue_date}<br/>"
                f"Due Date: {invoice.due_date}<br/>"
                f"Status: {invoice.status.upper()}",
                normal_style
            )
        ]
    ]
    info_table = Table(info_table_data, colWidths=[85*mm, 85*mm])
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10*mm))

    table_data = [["Description", "Qty", "Rate (Rs.)", "Amount (Rs.)"]]
    for item in invoice.line_items:
        amount = float(item.quantity) * float(item.rate)
        table_data.append([
            item.description,
            str(item.quantity),
            f"{float(item.rate):,.2f}",
            f"{amount:,.2f}"
        ])

    items_table = Table(table_data, colWidths=[80*mm, 25*mm, 35*mm, 30*mm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 8*mm))

    totals_data = [
        ["Subtotal", f"Rs. {invoice.subtotal:,.2f}"],
        [f"Tax ({invoice.tax_percent}%)", f"Rs. {invoice.tax_amount:,.2f}"],
        ["Total", f"Rs. {invoice.total:,.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[140*mm, 30*mm])
    totals_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("FONTSIZE", (0, 2), (-1, 2), 13),
        ("LINEABOVE", (0, 2), (-1, 2), 0.5, colors.HexColor("#111111")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 15*mm))

    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey
    )
    elements.append(Paragraph("Thank you for your business!", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer