from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional, List
from datetime import datetime

from app.models.prediction import Prediction
from app.schemas.schemas import PredictionInput
from app.ml.pipeline import MLPipeline


class PredictionService:

    @staticmethod
    async def create_prediction(
        db: AsyncSession,
        user_id: int,
        input_data: PredictionInput,
        pipeline: MLPipeline,
    ) -> Prediction:
        """Run ML inference and persist result."""
        result = pipeline.predict(input_data.model_dump())

        prediction = Prediction(
            user_id=user_id,
            age=input_data.age,
            sex=input_data.sex.value,
            bmi=input_data.bmi,
            children=input_data.children,
            smoker=input_data.smoker.value,
            region=input_data.region.value,
            predicted_premium_xgboost=result.get("predicted_premium_xgboost"),
            predicted_premium_rf=result.get("predicted_premium_rf"),
            predicted_premium_dt=result.get("predicted_premium_dt"),
            best_model=result.get("best_model"),
            best_prediction=result.get("best_prediction"),
            risk_score=result.get("risk_score"),
            risk_category=result.get("risk_category"),
            shap_values=result.get("shap_values"),
            feature_importance=result.get("feature_importance"),
            recommended_plans=result.get("recommended_plans"),
            model_version=result.get("model_version"),
            processing_time_ms=result.get("processing_time_ms"),
        )

        db.add(prediction)
        await db.flush()
        await db.refresh(prediction)
        return prediction, result

    @staticmethod
    async def get_prediction_by_id(
        db: AsyncSession, prediction_id: int, user_id: int
    ) -> Optional[Prediction]:
        result = await db.execute(
            select(Prediction).where(
                Prediction.id == prediction_id,
                Prediction.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_predictions(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[Prediction], int]:
        offset = (page - 1) * page_size

        total_result = await db.execute(
            select(func.count()).where(Prediction.user_id == user_id)
        )
        total = total_result.scalar() or 0

        result = await db.execute(
            select(Prediction)
            .where(Prediction.user_id == user_id)
            .order_by(desc(Prediction.created_at))
            .offset(offset)
            .limit(page_size)
        )
        predictions = result.scalars().all()

        return list(predictions), total

    @staticmethod
    async def delete_prediction(
        db: AsyncSession, prediction_id: int, user_id: int
    ) -> bool:
        pred = await PredictionService.get_prediction_by_id(db, prediction_id, user_id)
        if not pred:
            return False
        await db.delete(pred)
        return True

    @staticmethod
    async def get_stats(db: AsyncSession, user_id: int) -> dict:
        """Get summary statistics for a user's predictions."""
        result = await db.execute(
            select(
                func.count().label("total"),
                func.avg(Prediction.best_prediction).label("avg_premium"),
                func.min(Prediction.best_prediction).label("min_premium"),
                func.max(Prediction.best_prediction).label("max_premium"),
                func.avg(Prediction.risk_score).label("avg_risk"),
            ).where(Prediction.user_id == user_id)
        )
        row = result.one()
        return {
            "total_predictions": row.total or 0,
            "avg_premium": round(float(row.avg_premium or 0), 2),
            "min_premium": round(float(row.min_premium or 0), 2),
            "max_premium": round(float(row.max_premium or 0), 2),
            "avg_risk_score": round(float(row.avg_risk or 0), 2),
        }
