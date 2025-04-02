# src/utils/pdf_exporter.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_portfolio_pdf(recommendations, market_outlook, risk_assessment, advice, user_inputs):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Crypto Investment Report")
    y -= 30

    c.setFont("Helvetica", 10)
    for label, value in user_inputs.items():
        c.drawString(40, y, f"{label}: {value}")
        y -= 15
    y -= 10

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Investment Recommendations:")
    y -= 20

    for i, rec in enumerate(recommendations, 1):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, f"{i}. {rec['coin']} - {rec['allocation_percentage']}% (${rec['allocation_amount']})")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Risk Level: {rec['risk_level']} | Return: {rec['potential_return']} | Hold: {rec['holding_period']}")
        y -= 15
        c.drawString(50, y, f"Rationale: {rec['rationale'][:100]}...")
        y -= 25
        if y < 100:
            c.showPage()
            y = height - 40

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "📊 Market Outlook:")
    y -= 15
    c.setFont("Helvetica", 10)
    c.drawString(50, y, market_outlook[:100])
    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "⚠️ Risk Assessment:")
    y -= 15
    c.setFont("Helvetica", 10)
    c.drawString(50, y, risk_assessment[:100])
    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "💡 Additional Advice:")
    y -= 15
    c.setFont("Helvetica", 10)
    for line in advice.split('. '):
        c.drawString(50, y, f"• {line.strip()}")
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 40

    c.save()
    buffer.seek(0)
    return buffer
