from sqlalchemy import (
    Column, Integer, Float, String, Boolean,
    DateTime, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class SexEnum(str, enum.Enum):
    male = "male"
    female = "female"


class SmokingEnum(str, enum.Enum):
    yes = "yes"
    no = "no"


class RegionEnum(str, enum.Enum):
    northeast = "northeast"
    northwest = "northwest"
    southeast = "southeast"
    southwest = "southwest"


class ModelTypeEnum(str, enum.Enum):
    xgboost = "xgboost"
    random_forest = "random_forest"
    decision_tree = "decision_tree"


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Input features
    age = Column(Integer, nullable=False)
    sex = Column(Enum(SexEnum), nullable=False)
    bmi = Column(Float, nullable=False)
    children = Column(Integer, nullable=False)
    smoker = Column(Enum(SmokingEnum), nullable=False)
    region = Column(Enum(RegionEnum), nullable=False)

    # Prediction results (all 3 models)
    predicted_premium_xgboost = Column(Float, nullable=True)
    predicted_premium_rf = Column(Float, nullable=True)
    predicted_premium_dt = Column(Float, nullable=True)
    best_model = Column(Enum(ModelTypeEnum), nullable=True)
    best_prediction = Column(Float, nullable=True)

    # Risk categorization
    risk_score = Column(Float, nullable=True)
    risk_category = Column(String(50), nullable=True)  # low, medium, high, very_high

    # SHAP values (stored as JSON)
    shap_values = Column(JSON, nullable=True)
    feature_importance = Column(JSON, nullable=True)

    # Recommended plans (stored as JSON list)
    recommended_plans = Column(JSON, nullable=True)

    # Metadata
    model_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="predictions")
    reports = relationship("Report", back_populates="prediction")
