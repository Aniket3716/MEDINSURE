from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.db.database import get_db
from app.core.security import get_current_active_user
from app.services.prediction_service import PredictionService
from app.services.report_service import generate_prediction_report

router = APIRouter()


@router.get("/{prediction_id}/pdf")
async def download_report(
    prediction_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Generate and download a PDF report for a prediction.
    Returns a streaming PDF response.
    """
    pred = await PredictionService.get_prediction_by_id(db, prediction_id, current_user.id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    prediction_data = {
        "model_predictions": [
            {"model_name": "xgboost", "predicted_premium": pred.predicted_premium_xgboost or 0},
            {"model_name": "random_forest", "predicted_premium": pred.predicted_premium_rf or 0},
            {"model_name": "decision_tree", "predicted_premium": pred.predicted_premium_dt or 0},
        ],
        "best_model": pred.best_model or "xgboost",
        "best_prediction": pred.best_prediction or 0,
        "risk_score": pred.risk_score or 0,
        "risk_category": pred.risk_category or "medium",
        "shap_values": pred.shap_values or [],
        "recommended_plans": pred.recommended_plans or [],
    }

    input_data = {
        "age": pred.age,
        "sex": pred.sex.value if hasattr(pred.sex, "value") else pred.sex,
        "bmi": pred.bmi,
        "children": pred.children,
        "smoker": pred.smoker.value if hasattr(pred.smoker, "value") else pred.smoker,
        "region": pred.region.value if hasattr(pred.region, "value") else pred.region,
        "annual_salary": pred.annual_salary or 0,
        "income_label": pred.income_label or "—",
    }

    user_data = {
        "full_name": current_user.full_name,
        "username": current_user.username,
        "email": current_user.email,
    }

    pdf_bytes = generate_prediction_report(prediction_data, user_data, input_data)

    filename = f"medinsure_report_{prediction_id}_{pred.created_at.strftime('%Y%m%d')}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )