from fastapi import FastAPI
import app.models
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.db.database import engine, Base
from app.api.routes import auth, predictions, users, reports, models as ml_models
from app.ml.pipeline import MLPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events."""
    logger.info("🚀 Starting MedInsure API...")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables initialized")

    # Load ML models
    pipeline = MLPipeline()
    pipeline.load_or_train()
    app.state.ml_pipeline = pipeline
    logger.info("✅ ML models loaded")

    yield

    logger.info("🛑 Shutting down MedInsure API...")


app = FastAPI(
    title="MedInsure API",
    description="""
    ## Medical Insurance Premium Prediction & Recommendation System

    A production-ready API for predicting medical insurance premiums using Machine Learning.

    ### Features
    - 🔐 JWT Authentication
    - 🤖 Multi-model ML predictions (XGBoost, Random Forest, Decision Tree)
    - 📊 SHAP Explainable AI
    - 📋 Insurance plan recommendations
    - 📄 PDF report generation
    - 📈 Prediction history
    """,
    version="1.0.0",
    contact={"name": "MedInsure Team", "email": "dev@medinsure.ai"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Predictions"])
app.include_router(ml_models.router, prefix="/api/v1/models", tags=["ML Models"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "MedInsure API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "medinsure-api",
        "version": "1.0.0",
    }
