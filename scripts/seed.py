#!/usr/bin/env python3
"""
scripts/seed.py — Seed the database with a demo user and sample predictions.
Run inside the backend container: docker exec medinsure_backend python scripts/seed.py
Or locally: cd backend && python ../scripts/seed.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.prediction import Prediction
from app.core.security import get_password_hash
from app.ml.pipeline import MLPipeline
from sqlalchemy import select


DEMO_USERS = [
    {"email": "demo@medinsure.ai", "username": "demo", "password": "demo1234", "full_name": "Demo User"},
    {"email": "alice@example.com", "username": "alice", "password": "alice1234", "full_name": "Alice Johnson"},
]

SAMPLE_PREDICTIONS = [
    {"age": 28, "sex": "female", "bmi": 22.5, "children": 0, "smoker": "no", "region": "northeast"},
    {"age": 42, "sex": "male", "bmi": 31.2, "children": 2, "smoker": "no", "region": "southeast"},
    {"age": 55, "sex": "male", "bmi": 27.8, "children": 3, "smoker": "yes", "region": "northwest"},
    {"age": 35, "sex": "female", "bmi": 25.0, "children": 1, "smoker": "no", "region": "southwest"},
    {"age": 62, "sex": "male", "bmi": 34.5, "children": 0, "smoker": "yes", "region": "northeast"},
]


async def seed():
    print("🌱 Seeding database...")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Train ML pipeline
    pipeline = MLPipeline()
    print("🤖 Training ML models...")
    pipeline.train()

    async with AsyncSessionLocal() as session:
        for user_data in DEMO_USERS:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    is_active=True,
                    is_verified=True,
                )
                session.add(user)
                await session.flush()
                print(f"  ✅ Created user: {user_data['email']}")

                # Add sample predictions for demo user
                if user_data["username"] == "demo":
                    for pred_input in SAMPLE_PREDICTIONS:
                        result = pipeline.predict(pred_input)
                        pred = Prediction(
                            user_id=user.id,
                            age=pred_input["age"],
                            sex=pred_input["sex"],
                            bmi=pred_input["bmi"],
                            children=pred_input["children"],
                            smoker=pred_input["smoker"],
                            region=pred_input["region"],
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
                        session.add(pred)
                    print(f"  📊 Added {len(SAMPLE_PREDICTIONS)} sample predictions for demo user")
            else:
                print(f"  ⚠️  User already exists: {user_data['email']}")

        await session.commit()

    print()
    print("╔══════════════════════════════════════════╗")
    print("║        ✅  Seed complete!                ║")
    print("╠══════════════════════════════════════════╣")
    print("║  Demo login:                             ║")
    print("║    Email:    demo@medinsure.ai           ║")
    print("║    Password: demo1234                    ║")
    print("╚══════════════════════════════════════════╝")


if __name__ == "__main__":
    asyncio.run(seed())
