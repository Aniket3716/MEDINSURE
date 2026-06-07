from fastapi import APIRouter, Depends, Request, HTTPException
from datetime import datetime

from app.core.security import get_current_active_user
from app.schemas.schemas import ModelComparisonResponse, ModelMetrics

router = APIRouter()


@router.get("/metrics", response_model=ModelComparisonResponse)
async def get_model_metrics(
    request: Request,
    current_user=Depends(get_current_active_user),
):
    """Get performance metrics for all trained models."""
    pipeline = request.app.state.ml_pipeline
    data = pipeline.get_model_metrics()

    metrics_list = []
    for name, m in data["metrics"].items():
        metrics_list.append(ModelMetrics(
            model_name=name.replace("_", " ").title(),
            mae=m.get("mae", 0),
            mse=m.get("mse", 0),
            rmse=m.get("rmse", 0),
            r2_score=m.get("r2_score", 0),
            training_samples=m.get("training_samples", 0),
            feature_names=m.get("feature_names", []),
            last_trained=datetime.fromisoformat(data["trained_at"]) if data.get("trained_at") else datetime.utcnow(),
        ))

    # Best model by R²
    best = max(metrics_list, key=lambda m: m.r2_score).model_name if metrics_list else "XGBoost"

    # Chart data for frontend
    chart_data = [
        {
            "model": m.model_name,
            "MAE": m.mae,
            "RMSE": m.rmse,
            "R2": m.r2_score,
        }
        for m in metrics_list
    ]

    return ModelComparisonResponse(
        models=metrics_list,
        best_model=best,
        comparison_chart_data=chart_data,
    )


@router.post("/retrain")
async def retrain_models(
    request: Request,
    current_user=Depends(get_current_active_user),
):
    """Trigger model retraining with fresh synthetic data."""
    pipeline = request.app.state.ml_pipeline
    metrics = pipeline.retrain()

    return {
        "message": "Models retrained successfully",
        "metrics": metrics,
        "retrained_at": datetime.utcnow().isoformat(),
    }


@router.get("/info")
async def get_model_info(
    request: Request,
    current_user=Depends(get_current_active_user),
):
    """Get metadata about the currently deployed models."""
    pipeline = request.app.state.ml_pipeline
    data = pipeline.get_model_metrics()
    return {
        "model_version": data.get("model_version", "1.0.0"),
        "trained_at": data.get("trained_at"),
        "training_samples": data.get("training_samples", 0),
        "feature_names": data.get("feature_names", []),
        "available_models": list(pipeline.models.keys()),
    }
