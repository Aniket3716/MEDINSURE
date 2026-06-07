"""
Test suite for MedInsure API.
Run with: pytest tests/ -v
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch

from app.main import app
from app.ml.pipeline import MLPipeline


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_pipeline():
    pipeline = MagicMock(spec=MLPipeline)
    pipeline.predict.return_value = {
        "model_predictions": [
            {"model_name": "xgboost", "predicted_premium": 12000.0},
            {"model_name": "random_forest", "predicted_premium": 11500.0},
            {"model_name": "decision_tree", "predicted_premium": 12500.0},
        ],
        "best_model": "random_forest",
        "best_prediction": 11500.0,
        "predicted_premium_xgboost": 12000.0,
        "predicted_premium_rf": 11500.0,
        "predicted_premium_dt": 12500.0,
        "risk_score": 42.5,
        "risk_category": "medium",
        "shap_values": [
            {"feature_name": "smoker", "shap_value": 5000.0, "feature_value": 0, "impact": "positive"},
            {"feature_name": "age", "shap_value": 2000.0, "feature_value": 35, "impact": "positive"},
        ],
        "feature_importance": [],
        "recommended_plans": [
            {
                "plan_id": "SILVER_PPO",
                "plan_name": "SilverChoice PPO",
                "provider": "HealthFirst Corp",
                "monthly_premium": 320.0,
                "annual_premium": 3840.0,
                "deductible": 3000,
                "coverage_limit": 1000000,
                "plan_type": "PPO",
                "features": ["Specialist visits"],
                "recommended_for": "Moderate risk",
                "match_score": 78.0,
            }
        ],
        "model_version": "1.0.0",
        "processing_time_ms": 45.2,
    }
    pipeline.get_model_metrics.return_value = {
        "metrics": {
            "xgboost": {"mae": 1200, "mse": 2500000, "rmse": 1581, "r2_score": 0.89, "training_samples": 5000, "feature_names": ["age", "sex", "bmi", "children", "smoker", "region"]},
            "random_forest": {"mae": 1100, "mse": 2200000, "rmse": 1483, "r2_score": 0.91, "training_samples": 5000, "feature_names": ["age", "sex", "bmi", "children", "smoker", "region"]},
            "decision_tree": {"mae": 1500, "mse": 3500000, "rmse": 1871, "r2_score": 0.83, "training_samples": 5000, "feature_names": ["age", "sex", "bmi", "children", "smoker", "region"]},
        },
        "model_version": "1.0.0",
        "trained_at": "2024-01-15T10:00:00",
        "training_samples": 5000,
        "feature_names": ["age", "sex", "bmi", "children", "smoker", "region"],
    }
    return pipeline


@pytest.fixture
async def client(mock_pipeline):
    app.state.ml_pipeline = mock_pipeline
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ─── Health Check ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["version"] == "1.0.0"


# ─── Auth ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_user(client):
    res = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User",
    })
    assert res.status_code in [201, 400]  # 400 if already exists in test db


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    res = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword",
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_access_protected_route_without_token(client):
    res = await client.get("/api/v1/predictions/history")
    assert res.status_code == 403


# ─── ML Pipeline Unit Tests ────────────────────────────────────────────────────

def test_ml_pipeline_synthetic_data():
    from app.ml.pipeline import generate_synthetic_data
    df = generate_synthetic_data(100)
    assert len(df) == 100
    assert set(df.columns) >= {"age", "sex", "bmi", "children", "smoker", "region", "charges"}
    assert df["age"].between(18, 64).all()
    assert df["bmi"].between(15, 55).all()
    assert df["charges"].gt(0).all()


def test_ml_pipeline_risk_scoring():
    pipeline = MLPipeline()

    # Low risk: young, normal BMI, non-smoker
    score_low = pipeline._calculate_risk_score(
        {"age": 25, "bmi": 22, "smoker": "no", "children": 0}, 5000
    )
    # High risk: old, obese, smoker
    score_high = pipeline._calculate_risk_score(
        {"age": 60, "bmi": 38, "smoker": "yes", "children": 3}, 40000
    )
    assert score_low < score_high
    assert 0 <= score_low <= 100
    assert 0 <= score_high <= 100


def test_ml_pipeline_risk_categorization():
    pipeline = MLPipeline()
    assert pipeline._categorize_risk(10) == "low"
    assert pipeline._categorize_risk(35) == "medium"
    assert pipeline._categorize_risk(60) == "high"
    assert pipeline._categorize_risk(85) == "very_high"


def test_ml_pipeline_plan_recommendations():
    pipeline = MLPipeline()
    plans = pipeline._recommend_plans(40, 15000, {"children": 0})
    assert isinstance(plans, list)
    assert len(plans) <= 3
    for plan in plans:
        assert "plan_id" in plan
        assert "monthly_premium" in plan
        assert "match_score" in plan
        assert plan["match_score"] >= 0


def test_ml_pipeline_train_and_predict():
    """Integration test: train models and run a prediction."""
    pipeline = MLPipeline()
    pipeline.train()

    result = pipeline.predict({
        "age": 35,
        "sex": "male",
        "bmi": 27.5,
        "children": 2,
        "smoker": "no",
        "region": "northeast",
    })

    assert "best_prediction" in result
    assert result["best_prediction"] > 0
    assert "risk_score" in result
    assert "risk_category" in result
    assert result["risk_category"] in ["low", "medium", "high", "very_high"]
    assert len(result["model_predictions"]) == 3
    assert len(result["recommended_plans"]) > 0


def test_ml_pipeline_smoker_premium_higher():
    """Smokers should have significantly higher premiums than non-smokers."""
    pipeline = MLPipeline()
    pipeline.train()

    base_input = {"age": 35, "sex": "male", "bmi": 25, "children": 0, "region": "northeast"}

    non_smoker = pipeline.predict({**base_input, "smoker": "no"})
    smoker = pipeline.predict({**base_input, "smoker": "yes"})

    assert smoker["best_prediction"] > non_smoker["best_prediction"]
