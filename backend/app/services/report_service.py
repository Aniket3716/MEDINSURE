"""
PDF Report Generator using ReportLab.
Produces detailed insurance prediction reports with charts and SHAP explanations.
"""
import io
import os
from datetime import datetime
from typing import Dict, List, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF


# ─── Color Palette ────────────────────────────────────────────────────────────

PRIMARY = colors.HexColor("#1E3A5F")
ACCENT = colors.HexColor("#2ECC71")
WARNING = colors.HexColor("#F39C12")
DANGER = colors.HexColor("#E74C3C")
LIGHT_GRAY = colors.HexColor("#F8F9FA")
MEDIUM_GRAY = colors.HexColor("#DEE2E6")
DARK_GRAY = colors.HexColor("#495057")
WHITE = colors.white

RISK_COLORS = {
    "low": colors.HexColor("#2ECC71"),
    "medium": colors.HexColor("#F39C12"),
    "high": colors.HexColor("#E67E22"),
    "very_high": colors.HexColor("#E74C3C"),
}


def generate_prediction_report(
    prediction_data: Dict,
    user_data: Dict,
    input_data: Dict,
) -> bytes:
    """
    Generate a comprehensive PDF report for an insurance prediction.
    Returns PDF as bytes.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Medical Insurance Premium Prediction Report",
        author="MedInsure AI",
    )

    styles = _build_styles()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story += _build_header(styles, user_data)
    story.append(Spacer(1, 0.3 * inch))

    # ── Executive Summary ─────────────────────────────────────────────────────
    story += _build_summary_section(styles, prediction_data, input_data)
    story.append(Spacer(1, 0.25 * inch))

    # ── User Profile ─────────────────────────────────────────────────────────
    story += _build_profile_section(styles, input_data)
    story.append(Spacer(1, 0.25 * inch))

    # ── Model Comparison ──────────────────────────────────────────────────────
    story += _build_model_comparison(styles, prediction_data)
    story.append(Spacer(1, 0.25 * inch))

    # ── Risk Analysis ─────────────────────────────────────────────────────────
    story += _build_risk_section(styles, prediction_data)
    story.append(Spacer(1, 0.25 * inch))

    # ── SHAP Explanations ────────────────────────────────────────────────────
    shap_vals = prediction_data.get("shap_values", [])
    if shap_vals:
        story += _build_shap_section(styles, shap_vals)
        story.append(Spacer(1, 0.25 * inch))

    # ── Recommended Plans ─────────────────────────────────────────────────────
    plans = prediction_data.get("recommended_plans", [])
    if plans:
        story += _build_plans_section(styles, plans)
        story.append(Spacer(1, 0.25 * inch))

    # ── Disclaimer ───────────────────────────────────────────────────────────
    story += _build_disclaimer(styles)

    doc.build(story, onFirstPage=_add_page_decorations, onLaterPages=_add_page_decorations)

    buffer.seek(0)
    return buffer.read()


# ─── Style Builder ────────────────────────────────────────────────────────────

def _build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            fontSize=22,
            fontName="Helvetica-Bold",
            textColor=PRIMARY,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            fontSize=11,
            fontName="Helvetica",
            textColor=DARK_GRAY,
            alignment=TA_LEFT,
        ),
        "section_header": ParagraphStyle(
            "SectionHeader",
            fontSize=13,
            fontName="Helvetica-Bold",
            textColor=PRIMARY,
            spaceBefore=8,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            fontSize=10,
            fontName="Helvetica",
            textColor=DARK_GRAY,
            leading=14,
        ),
        "small": ParagraphStyle(
            "Small",
            fontSize=8,
            fontName="Helvetica",
            textColor=colors.gray,
            leading=11,
        ),
        "metric_value": ParagraphStyle(
            "MetricValue",
            fontSize=18,
            fontName="Helvetica-Bold",
            textColor=PRIMARY,
            alignment=TA_CENTER,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabel",
            fontSize=9,
            fontName="Helvetica",
            textColor=DARK_GRAY,
            alignment=TA_CENTER,
        ),
    }


# ─── Page Decorations ─────────────────────────────────────────────────────────

def _add_page_decorations(canvas, doc):
    canvas.saveState()
    # Top bar
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, letter[1] - 0.35 * inch, letter[0], 0.35 * inch, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(0.75 * inch, letter[1] - 0.22 * inch, "MEDINSURE AI")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(
        letter[0] - 0.75 * inch,
        letter[1] - 0.22 * inch,
        "Medical Insurance Premium Prediction Report",
    )
    # Bottom bar
    canvas.setFillColor(LIGHT_GRAY)
    canvas.rect(0, 0, letter[0], 0.4 * inch, fill=1, stroke=0)
    canvas.setFillColor(DARK_GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        0.75 * inch, 0.15 * inch,
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}"
    )
    canvas.drawRightString(
        letter[0] - 0.75 * inch, 0.15 * inch,
        f"Page {doc.page} | Confidential"
    )
    canvas.restoreState()


# ─── Section Builders ─────────────────────────────────────────────────────────

def _build_header(styles, user_data):
    elements = []
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph("Medical Insurance", styles["title"]))
    elements.append(Paragraph("Premium Prediction Report", styles["title"]))
    elements.append(Spacer(1, 0.05 * inch))
    name = user_data.get("full_name") or user_data.get("username", "User")
    elements.append(Paragraph(
        f"Prepared for: <b>{name}</b> &nbsp;|&nbsp; {datetime.now().strftime('%B %d, %Y')}",
        styles["subtitle"],
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
    return elements


def _build_summary_section(styles, prediction_data, input_data):
    elements = []
    elements.append(Paragraph("Executive Summary", styles["section_header"]))

    best = prediction_data.get("best_prediction", 0)
    risk_cat = prediction_data.get("risk_category", "medium").replace("_", " ").title()
    risk_score = prediction_data.get("risk_score", 0)
    best_model = prediction_data.get("best_model", "XGBoost").replace("_", " ").title()

    risk_color = RISK_COLORS.get(prediction_data.get("risk_category", "medium"), WARNING)

    # Metric cards as table
    data = [
        [
            Paragraph(f"${best:,.0f}/yr", styles["metric_value"]),
            Paragraph(f"{risk_score:.0f}/100", styles["metric_value"]),
            Paragraph(risk_cat, ParagraphStyle("RC", fontSize=16, fontName="Helvetica-Bold",
                                               textColor=risk_color, alignment=TA_CENTER)),
            Paragraph(best_model, styles["metric_value"]),
        ],
        [
            Paragraph("Predicted Annual Premium", styles["metric_label"]),
            Paragraph("Risk Score", styles["metric_label"]),
            Paragraph("Risk Category", styles["metric_label"]),
            Paragraph("Best Model", styles["metric_label"]),
        ],
    ]

    col_w = (letter[0] - 1.5 * inch) / 4
    tbl = Table(data, colWidths=[col_w] * 4, rowHeights=[0.5 * inch, 0.25 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 1, MEDIUM_GRAY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(tbl)
    return elements


def _build_profile_section(styles, input_data):
    elements = []
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph("User Risk Profile", styles["section_header"]))

    bmi = input_data.get("bmi", 0)
    bmi_cat = (
        "Underweight" if bmi < 18.5 else
        "Normal" if bmi < 25 else
        "Overweight" if bmi < 30 else "Obese"
    )

    rows = [
        ["Field", "Value", "Field", "Value"],
        ["Age", f"{input_data.get('age')} years", "Sex", input_data.get("sex", "").title()],
        ["BMI", f"{input_data.get('bmi', 0):.1f} ({bmi_cat})", "Smoker", input_data.get("smoker", "").title()],
        ["Children", str(input_data.get("children", 0)), "Region", input_data.get("region", "").title()],
    ]

    col_w = (letter[0] - 1.5 * inch) / 4
    tbl = Table(rows, colWidths=[col_w * 0.7, col_w * 1.3, col_w * 0.7, col_w * 1.3])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 1), (0, -1), LIGHT_GRAY),
        ("BACKGROUND", (2, 1), (2, -1), LIGHT_GRAY),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 1, MEDIUM_GRAY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(tbl)
    return elements


def _build_model_comparison(styles, prediction_data):
    elements = []
    elements.append(Paragraph("Model Comparison", styles["section_header"]))

    model_preds = prediction_data.get("model_predictions", [])
    best_model = prediction_data.get("best_model", "")

    headers = ["Model", "Predicted Premium", "Status"]
    rows = [headers]
    for mp in model_preds:
        name = mp.get("model_name", "").replace("_", " ").title()
        premium = f"${mp.get('predicted_premium', 0):,.2f}/year"
        is_best = mp.get("model_name") == best_model
        status = "✓ Best Model" if is_best else "—"
        rows.append([name, premium, status])

    col_w = (letter[0] - 1.5 * inch)
    tbl = Table(rows, colWidths=[col_w * 0.4, col_w * 0.35, col_w * 0.25])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 1, MEDIUM_GRAY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (2, 1), (2, -1), ACCENT),
        ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"),
    ]))
    elements.append(tbl)
    return elements


def _build_risk_section(styles, prediction_data):
    elements = []
    elements.append(Paragraph("Risk Assessment", styles["section_header"]))

    risk_score = prediction_data.get("risk_score", 50)
    risk_category = prediction_data.get("risk_category", "medium")
    risk_color = RISK_COLORS.get(risk_category, WARNING)

    descriptions = {
        "low": "Your risk profile is favorable. You are likely to qualify for competitive insurance rates. Maintaining a healthy lifestyle will help keep premiums low.",
        "medium": "Your risk profile indicates moderate health risk factors. Consider lifestyle improvements such as weight management and regular check-ups to potentially reduce premiums.",
        "high": "Your risk profile shows elevated health risk factors. Comprehensive coverage is recommended. Consulting a healthcare provider about risk reduction strategies may help over time.",
        "very_high": "Your risk profile indicates significant health risk factors. Comprehensive insurance coverage is strongly recommended. Work closely with healthcare providers on risk management.",
    }

    elements.append(Paragraph(
        f"Risk Score: <b>{risk_score:.1f}/100</b> — Category: <b>{risk_category.replace('_', ' ').title()}</b>",
        ParagraphStyle("RiskHeader", fontSize=11, fontName="Helvetica-Bold",
                       textColor=risk_color, spaceAfter=6),
    ))
    elements.append(Paragraph(descriptions.get(risk_category, ""), styles["body"]))

    # Visual risk bar
    bar_width = 4 * inch
    filled = bar_width * (risk_score / 100)
    d = Drawing(bar_width + 1, 22)
    d.add(Rect(0, 4, bar_width, 14, fillColor=MEDIUM_GRAY, strokeColor=None))
    d.add(Rect(0, 4, filled, 14, fillColor=risk_color, strokeColor=None))
    elements.append(d)

    return elements


def _build_shap_section(styles, shap_values):
    elements = []
    elements.append(Paragraph("Feature Impact Analysis (SHAP)", styles["section_header"]))
    elements.append(Paragraph(
        "SHAP (SHapley Additive exPlanations) values show how each feature contributes to the predicted premium. Positive values increase the premium; negative values decrease it.",
        styles["body"],
    ))
    elements.append(Spacer(1, 0.1 * inch))

    headers = ["Feature", "Impact Value", "Direction", "Your Value"]
    rows = [headers]

    for item in shap_values[:6]:
        feat = item.get("feature_name", "").replace("_", " ").title()
        shap_val = item.get("shap_value", 0)
        direction = "▲ Increases Premium" if shap_val > 0 else "▼ Decreases Premium"
        feat_val = str(round(item.get("feature_value", 0), 2))
        rows.append([feat, f"${abs(shap_val):,.2f}", direction, feat_val])

    col_w = (letter[0] - 1.5 * inch)
    tbl = Table(rows, colWidths=[col_w * 0.28, col_w * 0.22, col_w * 0.28, col_w * 0.22])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOX", (0, 0), (-1, -1), 1, MEDIUM_GRAY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(tbl)
    return elements


def _build_plans_section(styles, plans):
    elements = []
    elements.append(Paragraph("Recommended Insurance Plans", styles["section_header"]))

    for i, plan in enumerate(plans[:3]):
        elements.append(Spacer(1, 0.08 * inch))
        match = plan.get("match_score", 0)
        header_data = [[
            Paragraph(
                f"#{i+1} {plan.get('plan_name', '')} — {plan.get('plan_type', '')}",
                ParagraphStyle("PlanName", fontSize=11, fontName="Helvetica-Bold", textColor=WHITE),
            ),
            Paragraph(
                f"Match: {match:.0f}%",
                ParagraphStyle("Match", fontSize=10, fontName="Helvetica-Bold",
                               textColor=WHITE, alignment=TA_RIGHT),
            ),
        ]]
        col_w = (letter[0] - 1.5 * inch)
        header_tbl = Table(header_data, colWidths=[col_w * 0.7, col_w * 0.3])
        header_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(header_tbl)

        details = [
            ["Provider", plan.get("provider", ""), "Monthly Premium", f"${plan.get('monthly_premium', 0):,.2f}"],
            ["Annual Premium", f"${plan.get('annual_premium', 0):,.2f}", "Deductible", f"${plan.get('deductible', 0):,.0f}"],
            ["Coverage Limit", f"${plan.get('coverage_limit', 0):,.0f}", "Best For", plan.get("recommended_for", "")],
        ]
        col_w2 = col_w / 4
        details_tbl = Table(details, colWidths=[col_w2 * 0.7, col_w2 * 1.3, col_w2 * 0.7, col_w2 * 1.3])
        details_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
            ("BACKGROUND", (2, 0), (2, -1), LIGHT_GRAY),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOX", (0, 0), (-1, -1), 1, MEDIUM_GRAY),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, MEDIUM_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(details_tbl)

    return elements


def _build_disclaimer(styles):
    elements = []
    elements.append(HRFlowable(width="100%", thickness=1, color=MEDIUM_GRAY))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph("Important Disclaimer", styles["section_header"]))
    elements.append(Paragraph(
        "This report is generated by an AI-powered prediction system and is intended for informational purposes only. "
        "The predicted premiums are estimates based on statistical models and may not reflect actual insurance quotes. "
        "Actual premiums may vary based on additional factors assessed by insurance providers. "
        "This report does not constitute financial or medical advice. Please consult with a licensed insurance professional "
        "before making any insurance-related decisions.",
        styles["small"],
    ))
    return elements
