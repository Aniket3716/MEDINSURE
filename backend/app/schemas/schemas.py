from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class SexEnum(str, Enum):
    male = "male"
    female = "female"


class SmokingEnum(str, Enum):
    yes = "yes"
    no = "no"


class RegionEnum(str, Enum):
    northeast = "northeast"
    northwest = "northwest"
    southeast = "southeast"
    southwest = "southwest"


class ModelTypeEnum(str, Enum):
    xgboost = "xgboost"
    random_forest = "random_forest"
    decision_tree = "decision_tree"


class RiskCategory(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    very_high = "very_high"


# ─── Auth Schemas ──────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

    @validator("username")
    def username_alphanumeric(cls, v):
        assert v.replace("_", "").replace("-", "").isalnum(), "Username must be alphanumeric"
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# ─── User Schemas ──────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    total_predictions: Optional[int] = 0

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


# ─── Prediction Schemas ────────────────────────────────────────────────────────

class PredictionInput(BaseModel):
    age: int = Field(..., ge=18, le=100, description="Age in years")
    sex: SexEnum
    bmi: float = Field(..., ge=10.0, le=60.0, description="Body Mass Index")
    children: int = Field(..., ge=0, le=10, description="Number of dependents")
    smoker: SmokingEnum
    region: RegionEnum

    class Config:
        json_schema_extra = {
            "example": {
                "age": 35,
                "sex": "male",
                "bmi": 27.5,
                "children": 2,
                "smoker": "no",
                "region": "northeast",
            }
        }


class ModelPrediction(BaseModel):
    model_name: str
    predicted_premium: float
    confidence_interval: Optional[Dict[str, float]] = None


class SHAPExplanation(BaseModel):
    feature_name: str
    shap_value: float
    feature_value: Any
    impact: str  # "positive" | "negative"


class InsurancePlan(BaseModel):
    plan_id: str
    plan_name: str
    provider: str
    monthly_premium: float
    annual_premium: float
    deductible: float
    coverage_limit: float
    plan_type: str  # HMO, PPO, EPO, HDHP
    features: List[str]
    recommended_for: str
    match_score: float  # 0-100


class PredictionResponse(BaseModel):
    prediction_id: int
    input_data: PredictionInput
    model_predictions: List[ModelPrediction]
    best_model: str
    best_prediction: float
    risk_score: float
    risk_category: RiskCategory
    shap_explanations: List[SHAPExplanation]
    recommended_plans: List[InsurancePlan]
    processing_time_ms: float
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionListItem(BaseModel):
    id: int
    age: int
    bmi: float
    smoker: SmokingEnum
    best_prediction: float
    risk_category: RiskCategory
    best_model: str
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionHistory(BaseModel):
    items: List[PredictionListItem]
    total: int
    page: int
    page_size: int


# ─── ML Model Schemas ──────────────────────────────────────────────────────────

class ModelMetrics(BaseModel):
    model_name: str
    mae: float
    mse: float
    rmse: float
    r2_score: float
    training_samples: int
    feature_names: List[str]
    last_trained: datetime


class ModelComparisonResponse(BaseModel):
    models: List[ModelMetrics]
    best_model: str
    comparison_chart_data: List[Dict[str, Any]]


# ─── Report Schemas ────────────────────────────────────────────────────────────

class ReportResponse(BaseModel):
    report_id: int
    filename: str
    file_size_bytes: int
    created_at: datetime
    download_url: str

    class Config:
        from_attributes = True
