from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.core.security import get_current_active_user
from app.schemas.schemas import (
    PredictionInput, PredictionResponse, PredictionHistory,
    PredictionListItem, ModelPrediction, SHAPExplanation, InsurancePlan,
)
from app.services.prediction_service import PredictionService
from app.models.prediction import Prediction

router = APIRouter()


def _build_response(pred: Prediction, result: dict) -> PredictionResponse:
    model_preds = [
        ModelPrediction(model_name=mp["model_name"], predicted_premium=mp["predicted_premium"])
        for mp in result.get("model_predictions", [])
    ]
    shap_exps = [
        SHAPExplanation(**s) for s in result.get("shap_values", [])
    ]
    plans = [InsurancePlan(**p) for p in result.get("recommended_plans", [])]

    return PredictionResponse(
        prediction_id=pred.id,
        input_data=PredictionInput(
            age=pred.age, sex=pred.sex, bmi=pred.bmi,
            children=pred.children, smoker=pred.smoker, region=pred.region,
        ),
        model_predictions=model_preds,
        best_model=pred.best_model,
        best_prediction=pred.best_prediction,
        risk_score=pred.risk_score,
        risk_category=pred.risk_category,
        shap_explanations=shap_exps,
        recommended_plans=plans,
        processing_time_ms=pred.processing_time_ms or 0,
        created_at=pred.created_at,
    )


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def predict(
    input_data: PredictionInput,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Run insurance premium prediction using all three ML models.

    Returns predictions from XGBoost, Random Forest, and Decision Tree,
    plus SHAP explanations, risk analysis, and plan recommendations.
    """
    pipeline = request.app.state.ml_pipeline
    pred, result = await PredictionService.create_prediction(
        db, current_user.id, input_data, pipeline
    )
    return _build_response(pred, result)


@router.get("/history", response_model=PredictionHistory)
async def get_history(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get paginated prediction history for the current user."""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10

    predictions, total = await PredictionService.get_user_predictions(
        db, current_user.id, page, page_size
    )

    items = [
        PredictionListItem(
            id=p.id,
            age=p.age,
            bmi=p.bmi,
            smoker=p.smoker,
            best_prediction=p.best_prediction or 0,
            risk_category=p.risk_category or "medium",
            best_model=p.best_model or "xgboost",
            created_at=p.created_at,
        )
        for p in predictions
    ]

    return PredictionHistory(items=items, total=total, page=page, page_size=page_size)


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get aggregated prediction statistics for the current user."""
    return await PredictionService.get_stats(db, current_user.id)


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get a single prediction by ID."""
    pred = await PredictionService.get_prediction_by_id(db, prediction_id, current_user.id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    result = {
        "model_predictions": [
            {"model_name": "xgboost", "predicted_premium": pred.predicted_premium_xgboost or 0},
            {"model_name": "random_forest", "predicted_premium": pred.predicted_premium_rf or 0},
            {"model_name": "decision_tree", "predicted_premium": pred.predicted_premium_dt or 0},
        ],
        "shap_values": pred.shap_values or [],
        "recommended_plans": pred.recommended_plans or [],
    }
    return _build_response(pred, result)


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Delete a prediction record."""
    deleted = await PredictionService.delete_prediction(db, prediction_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prediction not found")
