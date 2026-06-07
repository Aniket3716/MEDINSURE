"""
ML Pipeline for Medical Insurance Premium Prediction.
Trains and manages XGBoost, Random Forest, and Decision Tree models.
"""
import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
import pandas as pd
import joblib
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─── Insurance Plans Database ─────────────────────────────────────────────────

INSURANCE_PLANS = [
    {
        "plan_id": "BASIC_HMO",
        "plan_name": "BasicCare HMO",
        "provider": "MedShield Insurance",
        "plan_type": "HMO",
        "base_monthly": 150,
        "deductible": 5000,
        "coverage_limit": 500000,
        "features": ["Primary care coverage", "Preventive care", "Generic prescriptions"],
        "recommended_for": "Healthy individuals with low risk",
        "min_risk": 0,
        "max_risk": 30,
    },
    {
        "plan_id": "SILVER_PPO",
        "plan_name": "SilverChoice PPO",
        "provider": "HealthFirst Corp",
        "plan_type": "PPO",
        "base_monthly": 280,
        "deductible": 3000,
        "coverage_limit": 1000000,
        "features": ["Specialist visits", "Out-of-network coverage", "Mental health", "Dental & Vision"],
        "recommended_for": "Moderate risk individuals needing flexibility",
        "min_risk": 20,
        "max_risk": 55,
    },
    {
        "plan_id": "GOLD_PPO",
        "plan_name": "GoldPlus PPO",
        "provider": "PremiumCare Group",
        "plan_type": "PPO",
        "base_monthly": 420,
        "deductible": 1500,
        "coverage_limit": 2000000,
        "features": ["Comprehensive coverage", "Low deductible", "Specialist access", "Prescription drugs", "Mental health", "Dental & Vision"],
        "recommended_for": "High-use individuals and families",
        "min_risk": 40,
        "max_risk": 75,
    },
    {
        "plan_id": "HDHP_HSA",
        "plan_name": "HealthSaver HDHP + HSA",
        "provider": "TrustHealth Insurance",
        "plan_type": "HDHP",
        "base_monthly": 200,
        "deductible": 4000,
        "coverage_limit": 1500000,
        "features": ["HSA compatible", "Preventive care", "Tax advantages", "Catastrophic coverage"],
        "recommended_for": "Tax-savvy individuals with moderate income",
        "min_risk": 15,
        "max_risk": 60,
    },
    {
        "plan_id": "PREMIUM_EPO",
        "plan_name": "EliteCare EPO",
        "provider": "Apex Health Solutions",
        "plan_type": "EPO",
        "base_monthly": 550,
        "deductible": 500,
        "coverage_limit": 5000000,
        "features": ["Near-zero deductible", "Unlimited specialist visits", "Concierge services", "Global coverage", "Dental & Vision", "Alternative medicine"],
        "recommended_for": "High-risk individuals needing comprehensive coverage",
        "min_risk": 60,
        "max_risk": 100,
    },
    {
        "plan_id": "FAMILY_PPO",
        "plan_name": "FamilyFirst PPO",
        "provider": "United Family Health",
        "plan_type": "PPO",
        "base_monthly": 380,
        "deductible": 2000,
        "coverage_limit": 3000000,
        "features": ["Family coverage", "Pediatric care", "Maternity benefits", "Mental health", "Dental & Vision", "Wellness programs"],
        "recommended_for": "Families with children",
        "min_risk": 25,
        "max_risk": 80,
    },
]


# ─── Synthetic Data Generator ─────────────────────────────────────────────────

def generate_synthetic_data(n_samples: int = 5000) -> pd.DataFrame:
    """
    Generate realistic synthetic insurance data based on the Kaggle
    Medical Cost Personal Dataset distribution.
    """
    np.random.seed(42)

    age = np.random.randint(18, 65, n_samples)
    sex = np.random.choice(["male", "female"], n_samples)
    bmi = np.clip(np.random.normal(30, 6, n_samples), 15, 55)
    children = np.random.choice([0, 1, 2, 3, 4, 5], n_samples, p=[0.4, 0.25, 0.2, 0.1, 0.04, 0.01])
    smoker = np.random.choice(["yes", "no"], n_samples, p=[0.2, 0.8])
    region = np.random.choice(["northeast", "northwest", "southeast", "southwest"], n_samples)

    # Realistic premium calculation formula
    base = 3000
    charges = (
        base
        + age * 250
        + (bmi - 25) ** 2 * 15
        + children * 400
        + (smoker == "yes") * 20000
        + np.where(region == "northeast", 500, 0)
        + np.where(region == "northwest", 300, 0)
        + np.where(sex == "female", 200, 0)
        + np.random.normal(0, 1500, n_samples)  # noise
    )
    charges = np.clip(charges, 1000, 60000)

    return pd.DataFrame({
        "age": age,
        "sex": sex,
        "bmi": bmi,
        "children": children,
        "smoker": smoker,
        "region": region,
        "charges": charges,
    })


# ─── Main ML Pipeline ─────────────────────────────────────────────────────────

class MLPipeline:
    """
    Manages training, evaluation, and inference for all three ML models.
    """

    FEATURE_COLS = ["age", "sex", "bmi", "children", "smoker", "region"]
    TARGET_COL = "charges"
    MODEL_VERSION = "1.0.0"

    def __init__(self):
        self.models_path = Path(settings.ML_MODELS_PATH)
        self.models_path.mkdir(parents=True, exist_ok=True)

        self.models: Dict[str, Any] = {}
        self.metrics: Dict[str, Dict] = {}
        self.explainers: Dict[str, Any] = {}
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: List[str] = []
        self.trained_at: Optional[datetime] = None
        self.training_samples: int = 0

    # ─── Data Preprocessing ──────────────────────────────────────────────────

    def _preprocess(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """Encode categorical features."""
        df = df.copy()
        categorical_cols = ["sex", "smoker", "region"]

        for col in categorical_cols:
            if fit:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
            else:
                if col in self.label_encoders:
                    le = self.label_encoders[col]
                    df[col] = le.transform(df[col].astype(str))

        return df

    def _get_feature_names(self) -> List[str]:
        return ["age", "sex_encoded", "bmi", "children", "smoker_encoded", "region_encoded"]

    # ─── Training ────────────────────────────────────────────────────────────

    def train(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Dict]:
        """Train all three models and compute metrics."""
        logger.info("🤖 Starting ML pipeline training...")

        if df is None:
            logger.info("Generating synthetic training data...")
            df = generate_synthetic_data(5000)

        self.training_samples = len(df)

        # Preprocess
        df_encoded = self._preprocess(df, fit=True)
        X = df_encoded[self.FEATURE_COLS].rename(columns={
            "sex": "sex_encoded",
            "smoker": "smoker_encoded",
            "region": "region_encoded",
        })
        # Ensure correct column names after encoding
        X = df_encoded[self.FEATURE_COLS]
        y = df_encoded[self.TARGET_COL] if self.TARGET_COL in df_encoded.columns else None

        if y is None:
            raise ValueError("Target column 'charges' not found in data")

        self.feature_names = list(X.columns)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Define models
        model_configs = {
            "xgboost": XGBRegressor(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbosity=0,
            ),
            "random_forest": RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1,
            ),
            "decision_tree": DecisionTreeRegressor(
                max_depth=8,
                min_samples_split=10,
                random_state=42,
            ),
        }

        all_metrics = {}

        for name, model in model_configs.items():
            logger.info(f"Training {name}...")
            start = time.time()
            model.fit(X_train, y_train)
            train_time = time.time() - start

            # Evaluate
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)

            metrics = {
                "mae": round(float(mae), 2),
                "mse": round(float(mse), 2),
                "rmse": round(float(rmse), 2),
                "r2_score": round(float(r2), 4),
                "training_samples": self.training_samples,
                "train_time_seconds": round(train_time, 2),
                "feature_names": self.feature_names,
            }

            self.models[name] = model
            self.metrics[name] = metrics
            all_metrics[name] = metrics

            logger.info(f"  {name}: R²={r2:.4f}, RMSE=${rmse:.2f}, MAE=${mae:.2f}")

        # Build SHAP explainers
        self._build_explainers(X_train)

        self.trained_at = datetime.utcnow()
        self._save_artifacts()

        logger.info("✅ Training complete!")
        return all_metrics

    # ─── SHAP Explainers ─────────────────────────────────────────────────────

    def _build_explainers(self, X_background: pd.DataFrame):
        """Build SHAP explainers for all models."""
        logger.info("Building SHAP explainers...")

        background = shap.sample(X_background, 100, random_state=42)

        for name, model in self.models.items():
            try:
                if name == "xgboost":
                    self.explainers[name] = shap.TreeExplainer(model)
                elif name == "random_forest":
                    self.explainers[name] = shap.TreeExplainer(model)
                elif name == "decision_tree":
                    self.explainers[name] = shap.TreeExplainer(model)
            except Exception as e:
                logger.warning(f"Could not build SHAP explainer for {name}: {e}")

    def _get_shap_values(self, model_name: str, X: pd.DataFrame) -> List[Dict]:
        """Get SHAP feature importance for a single prediction."""
        if model_name not in self.explainers:
            return []

        try:
            explainer = self.explainers[model_name]
            shap_vals = explainer.shap_values(X)

            if isinstance(shap_vals, list):
                shap_vals = shap_vals[0]

            shap_vals_flat = shap_vals[0] if len(shap_vals.shape) > 1 else shap_vals

            result = []
            for i, feat in enumerate(self.feature_names):
                val = float(shap_vals_flat[i])
                result.append({
                    "feature_name": feat,
                    "shap_value": round(val, 2),
                    "feature_value": float(X.iloc[0, i]),
                    "impact": "positive" if val > 0 else "negative",
                })

            return sorted(result, key=lambda x: abs(x["shap_value"]), reverse=True)
        except Exception as e:
            logger.error(f"SHAP computation failed: {e}")
            return []

    # ─── Persistence ─────────────────────────────────────────────────────────

    def _save_artifacts(self):
        """Save all models and metadata to disk."""
        for name, model in self.models.items():
            path = self.models_path / f"{name}.joblib"
            joblib.dump(model, path)

        joblib.dump(self.label_encoders, self.models_path / "label_encoders.joblib")
        joblib.dump(self.explainers, self.models_path / "explainers.joblib")

        metadata = {
            "model_version": self.MODEL_VERSION,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "training_samples": self.training_samples,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
        }
        with open(self.models_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✅ Artifacts saved to {self.models_path}")

    def load_or_train(self):
        """Load models from disk, or train if not found."""
        metadata_path = self.models_path / "metadata.json"

        if metadata_path.exists():
            try:
                self._load_artifacts()
                logger.info("✅ ML models loaded from disk")
                return
            except Exception as e:
                logger.warning(f"Failed to load models: {e}. Retraining...")

        self.train()

    def _load_artifacts(self):
        """Load saved model artifacts."""
        model_names = ["xgboost", "random_forest", "decision_tree"]

        for name in model_names:
            path = self.models_path / f"{name}.joblib"
            if path.exists():
                self.models[name] = joblib.load(path)

        enc_path = self.models_path / "label_encoders.joblib"
        if enc_path.exists():
            self.label_encoders = joblib.load(enc_path)

        exp_path = self.models_path / "explainers.joblib"
        if exp_path.exists():
            self.explainers = joblib.load(exp_path)

        meta_path = self.models_path / "metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                metadata = json.load(f)
            self.metrics = metadata.get("metrics", {})
            self.feature_names = metadata.get("feature_names", self.FEATURE_COLS)
            self.training_samples = metadata.get("training_samples", 0)
            self.trained_at = (
                datetime.fromisoformat(metadata["trained_at"])
                if metadata.get("trained_at")
                else None
            )

    # ─── Inference ───────────────────────────────────────────────────────────

    def predict(self, input_data: Dict) -> Dict:
        """Run prediction with all models and return full results."""
        start_time = time.time()

        if not self.models:
            self.load_or_train()

        # Build input DataFrame
        df = pd.DataFrame([{
            "age": input_data["age"],
            "sex": input_data["sex"],
            "bmi": input_data["bmi"],
            "children": input_data["children"],
            "smoker": input_data["smoker"],
            "region": input_data["region"],
        }])

        df_encoded = self._preprocess(df, fit=False)
        X = df_encoded[self.FEATURE_COLS]

        # Predictions from all models
        predictions = {}
        for name, model in self.models.items():
            pred = float(model.predict(X)[0])
            predictions[name] = max(0, round(pred, 2))

        # Best model by lowest RMSE
        best_model = min(
            self.metrics.keys(),
            key=lambda m: self.metrics[m].get("rmse", float("inf"))
        ) if self.metrics else "xgboost"

        best_prediction = predictions.get(best_model, list(predictions.values())[0])

        # Risk scoring
        risk_score = self._calculate_risk_score(input_data, best_prediction)
        risk_category = self._categorize_risk(risk_score)

        # SHAP explanations for best model
        shap_explanations = self._get_shap_values(best_model, X)

        # Recommended plans
        recommended_plans = self._recommend_plans(risk_score, best_prediction, input_data)

        processing_time_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "model_predictions": [
                {"model_name": name, "predicted_premium": pred}
                for name, pred in predictions.items()
            ],
            "best_model": best_model,
            "best_prediction": best_prediction,
            "predicted_premium_xgboost": predictions.get("xgboost"),
            "predicted_premium_rf": predictions.get("random_forest"),
            "predicted_premium_dt": predictions.get("decision_tree"),
            "risk_score": risk_score,
            "risk_category": risk_category,
            "shap_values": shap_explanations,
            "feature_importance": shap_explanations,
            "recommended_plans": recommended_plans,
            "model_version": self.MODEL_VERSION,
            "processing_time_ms": processing_time_ms,
        }

    def _calculate_risk_score(self, input_data: Dict, predicted_premium: float) -> float:
        """Calculate a 0-100 risk score based on input features and predicted premium."""
        score = 0.0

        # Age factor (max 20 points)
        age = input_data.get("age", 30)
        score += min((age - 18) / 47 * 20, 20)

        # BMI factor (max 20 points)
        bmi = input_data.get("bmi", 25)
        if bmi < 18.5:
            score += 8
        elif bmi < 25:
            score += 2
        elif bmi < 30:
            score += 8
        elif bmi < 35:
            score += 14
        else:
            score += 20

        # Smoking factor (max 35 points)
        if input_data.get("smoker") == "yes":
            score += 35

        # Children factor (max 10 points)
        children = input_data.get("children", 0)
        score += min(children * 2, 10)

        # Premium factor (max 15 points)
        premium_normalized = min(predicted_premium / 60000 * 15, 15)
        score += premium_normalized

        return round(min(score, 100), 2)

    def _categorize_risk(self, risk_score: float) -> str:
        if risk_score < 25:
            return "low"
        elif risk_score < 50:
            return "medium"
        elif risk_score < 75:
            return "high"
        else:
            return "very_high"

    def _recommend_plans(
        self, risk_score: float, predicted_premium: float, input_data: Dict
    ) -> List[Dict]:
        """Recommend insurance plans based on risk profile."""
        recommendations = []

        for plan in INSURANCE_PLANS:
            # Check risk range match
            if plan["min_risk"] <= risk_score <= plan["max_risk"] + 20:
                # Adjust monthly premium based on user's predicted premium
                premium_multiplier = max(0.5, min(predicted_premium / 10000, 3.0))
                monthly = round(plan["base_monthly"] * premium_multiplier, 2)

                # Calculate match score
                risk_overlap = max(0, min(risk_score, plan["max_risk"]) - max(risk_score - 10, plan["min_risk"]))
                risk_range = plan["max_risk"] - plan["min_risk"]
                match_score = round((risk_overlap / risk_range) * 100, 1) if risk_range > 0 else 50

                # Boost for families with children
                if input_data.get("children", 0) > 1 and "family" in plan["plan_id"].lower():
                    match_score = min(match_score + 15, 100)

                recommendations.append({
                    **plan,
                    "monthly_premium": monthly,
                    "annual_premium": round(monthly * 12, 2),
                    "match_score": max(match_score, 30),
                })

        # Sort by match score and return top 3
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations[:3]

    def get_model_metrics(self) -> Dict:
        """Return all model metrics."""
        return {
            "metrics": self.metrics,
            "model_version": self.MODEL_VERSION,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "training_samples": self.training_samples,
            "feature_names": self.feature_names,
        }

    def retrain(self, new_data: Optional[pd.DataFrame] = None) -> Dict:
        """Retrain all models with new data."""
        logger.info("🔄 Retraining models...")
        return self.train(new_data)
