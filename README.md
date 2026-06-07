# 🏥 MedInsure AI — Medical Insurance Premium Prediction System

> A production-ready, full-stack AI application that predicts medical insurance premiums using Machine Learning, explains predictions with SHAP, and recommends insurance plans.

[![CI/CD](https://github.com/your-org/medinsure/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/your-org/medinsure/actions)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Live Demo

| Service   | URL                                          |
|-----------|----------------------------------------------|
| Frontend  | https://medinsure.vercel.app                 |
| API       | https://medinsure-api.onrender.com           |
| API Docs  | https://medinsure-api.onrender.com/docs      |

**Demo credentials:** `demo@medinsure.ai` / `demo1234`

---

## ✨ Features

| Feature                  | Details                                             |
|--------------------------|-----------------------------------------------------|
| 🤖 Multi-Model ML        | XGBoost, Random Forest, Decision Tree               |
| 📊 Explainable AI        | SHAP feature importance per prediction              |
| 🎯 Risk Profiling        | 0–100 risk score with 4-tier categorization         |
| 🛡️ Plan Recommendations  | 6 curated plans matched to risk profile             |
| 📄 PDF Reports           | Professional downloadable reports via ReportLab     |
| 🔐 JWT Auth              | Access + refresh token authentication               |
| 📈 Prediction History    | Paginated history with full detail view             |
| 🐳 Fully Containerized   | Docker + Docker Compose for all services            |
| 🚀 Cloud Ready           | One-click deploy to Vercel + Render                 |
| 🧪 Tested                | Unit + integration tests for ML pipeline & API      |

---

## 📁 Project Structure

```
medinsure/
├── backend/                        # FastAPI application
│   ├── app/
│   │   ├── api/routes/             # Route handlers
│   │   │   ├── auth.py             # Register, login, refresh, /me
│   │   │   ├── predictions.py      # Predict, history, stats, detail
│   │   │   ├── models.py           # ML metrics, retrain
│   │   │   ├── reports.py          # PDF download
│   │   │   └── users.py            # Profile management
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic settings
│   │   │   └── security.py         # JWT + bcrypt
│   │   ├── db/
│   │   │   └── database.py         # Async SQLAlchemy engine
│   │   ├── models/                 # ORM models
│   │   │   ├── user.py
│   │   │   ├── prediction.py
│   │   │   └── report.py
│   │   ├── schemas/
│   │   │   └── schemas.py          # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── user_service.py     # User CRUD
│   │   │   ├── prediction_service.py  # ML orchestration + DB
│   │   │   └── report_service.py   # PDF generation
│   │   └── ml/
│   │       ├── pipeline.py         # MLPipeline (train + infer + SHAP)
│   │       └── models/             # Saved .joblib artifacts
│   ├── tests/
│   │   └── test_main.py            # Unit + integration tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                       # React + Vite application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── DashboardPage.jsx   # Stats + recent predictions
│   │   │   ├── PredictionPage.jsx  # Form + live results
│   │   │   ├── HistoryPage.jsx     # Paginated table
│   │   │   ├── PredictionDetailPage.jsx
│   │   │   └── ModelsPage.jsx      # Model comparison charts
│   │   ├── components/
│   │   │   └── shared/Layout.jsx   # Sidebar navigation
│   │   ├── services/
│   │   │   ├── api.js              # Axios + interceptors
│   │   │   └── predictionService.js
│   │   └── store/
│   │       └── authStore.js        # Zustand + persist
│   ├── nginx.conf
│   ├── vercel.json
│   └── Dockerfile
│
├── docker/
│   └── init.sql                    # DB initialization
├── scripts/
│   ├── setup.sh                    # One-command local setup
│   └── seed.py                     # Demo data seeder
├── .github/workflows/ci-cd.yml     # GitHub Actions CI/CD
├── docker-compose.yml              # Production compose
├── docker-compose.dev.yml          # Dev override (hot reload)
└── render.yaml                     # Render deployment config
```

---

## 🛠️ Tech Stack

### Backend
| Technology       | Version  | Purpose                          |
|-----------------|----------|----------------------------------|
| FastAPI          | 0.111    | Async REST API framework         |
| SQLAlchemy       | 2.0      | Async ORM                        |
| PostgreSQL       | 16       | Primary database                 |
| Pydantic         | 2.7      | Data validation & settings       |
| Python-JOSE      | 3.3      | JWT token handling               |
| Passlib + bcrypt | 1.7/4.0  | Password hashing                 |

### Machine Learning
| Library      | Version | Purpose                              |
|-------------|---------|--------------------------------------|
| XGBoost      | 2.0.3   | Gradient boosted trees               |
| Scikit-Learn | 1.4.2   | Random Forest, Decision Tree, metrics|
| SHAP         | 0.45.1  | Explainable AI / feature importance  |
| Pandas       | 2.2.2   | Data manipulation                    |
| NumPy        | 1.26.4  | Numerical computing                  |
| Joblib       | 1.4.0   | Model serialization                  |
| ReportLab    | 4.1.0   | PDF generation                       |

### Frontend
| Technology      | Version | Purpose                        |
|----------------|---------|--------------------------------|
| React           | 18.3    | UI framework                   |
| React Router    | 6.23    | Client-side routing            |
| Axios           | 1.7     | HTTP client with interceptors  |
| React Hook Form | 7.51    | Form management & validation   |
| Recharts        | 2.12    | Data visualization charts      |
| Zustand         | 4.5     | Global state management        |
| Tailwind CSS    | 3.4     | Utility-first styling          |
| Lucide React    | 0.383   | Icon library                   |
| React Hot Toast | 2.4     | Notification toasts            |

---

## 🏃 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/medinsure.git
cd medinsure

# One-command setup (handles .env, build, and start)
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Services start at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs

### Option 2: Manual (Development)

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Edit DATABASE_URL and SECRET_KEY

# Start with hot reload
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm ci --legacy-peer-deps
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev                       # http://localhost:3000
```

**Database**
```bash
# Using Docker for just the DB:
docker run -d \
  --name medinsure_db \
  -e POSTGRES_USER=medinsure \
  -e POSTGRES_PASSWORD=medinsure_password \
  -e POSTGRES_DB=medinsure_db \
  -p 5432:5432 \
  postgres:16-alpine
```

### Seed Demo Data
```bash
cd backend
python ../scripts/seed.py
# Creates: demo@medinsure.ai / demo1234 with 5 sample predictions
```

---

## 🧠 Machine Learning Architecture

### Models

| Model           | Algorithm            | Hyperparameters                                     |
|----------------|----------------------|-----------------------------------------------------|
| XGBoost         | Gradient Boosting    | n_estimators=300, max_depth=6, lr=0.05, subsample=0.8 |
| Random Forest   | Bagging Ensemble     | n_estimators=200, max_depth=10, min_samples_split=5   |
| Decision Tree   | CART                 | max_depth=8, min_samples_split=10                   |

### Feature Engineering

| Input Feature | Type        | Encoding       | Impact                    |
|--------------|-------------|----------------|---------------------------|
| age          | Continuous  | Raw            | Strong positive            |
| sex          | Categorical | LabelEncoder   | Moderate                  |
| bmi          | Continuous  | Raw            | Non-linear (quadratic)    |
| children     | Discrete    | Raw            | Moderate positive          |
| smoker       | Binary      | LabelEncoder   | **Strongest** factor (~20k uplift) |
| region       | Categorical | LabelEncoder   | Weak regional variation    |

### Training Pipeline

```
Raw Data (5,000 synthetic samples)
    │
    ├── Preprocessing: LabelEncoder for categorical
    │
    ├── Train/Test Split: 80/20
    │
    ├── Parallel Model Training:
    │   ├── XGBoost  ──── R²≈0.94, RMSE≈$2,084
    │   ├── Random Forest ─ R²≈0.97, RMSE≈$1,587  ← Best
    │   └── Decision Tree ─ R²≈0.96, RMSE≈$1,720
    │
    ├── SHAP TreeExplainer (per model)
    │
    └── Joblib serialization → app/ml/models/
```

### SHAP Explanation
Each prediction includes ordered feature contributions:
```json
[
  {"feature_name": "smoker", "shap_value": 18523.40, "impact": "positive"},
  {"feature_name": "bmi",    "shap_value":  2341.10, "impact": "positive"},
  {"feature_name": "age",    "shap_value":  1876.30, "impact": "positive"},
  {"feature_name": "region", "shap_value":   312.50, "impact": "positive"},
  {"feature_name": "sex",    "shap_value":  -145.20, "impact": "negative"},
  {"feature_name": "children","shap_value":   87.40, "impact": "positive"}
]
```

### Risk Scoring Algorithm
```
Risk Score (0–100) =
  Age factor        (0–20 pts) — linear scaling from 18–65
  BMI factor        (0–20 pts) — penalizes underweight and obesity
  Smoking factor    (0–35 pts) — biggest single factor
  Children factor   (0–10 pts) — 2 pts per child, max 10
  Premium factor    (0–15 pts) — normalized predicted premium

Risk Categories:
  0–24    → Low
  25–49   → Medium
  50–74   → High
  75–100  → Very High
```

---

## 🔌 API Reference

### Authentication

| Method | Endpoint               | Description              |
|--------|------------------------|--------------------------|
| POST   | /api/v1/auth/register  | Create new account       |
| POST   | /api/v1/auth/login     | Login, receive tokens    |
| POST   | /api/v1/auth/refresh   | Refresh access token     |
| GET    | /api/v1/auth/me        | Get current user profile |

### Predictions

| Method | Endpoint                              | Description                  |
|--------|---------------------------------------|------------------------------|
| POST   | /api/v1/predictions/predict           | Run ML prediction            |
| GET    | /api/v1/predictions/history           | Paginated history            |
| GET    | /api/v1/predictions/stats             | Aggregated statistics        |
| GET    | /api/v1/predictions/{id}              | Single prediction detail     |
| DELETE | /api/v1/predictions/{id}              | Delete prediction            |

### ML Models

| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | /api/v1/models/metrics    | All model performance    |
| POST   | /api/v1/models/retrain    | Trigger retraining       |
| GET    | /api/v1/models/info       | Model metadata           |

### Reports

| Method | Endpoint                       | Description          |
|--------|--------------------------------|----------------------|
| GET    | /api/v1/reports/{id}/pdf       | Download PDF report  |

### Sample Request/Response

**POST /api/v1/predictions/predict**
```json
// Request
{
  "age": 35,
  "sex": "male",
  "bmi": 27.5,
  "children": 2,
  "smoker": "no",
  "region": "northeast"
}

// Response
{
  "prediction_id": 42,
  "best_prediction": 12795.40,
  "best_model": "random_forest",
  "risk_score": 22.4,
  "risk_category": "low",
  "model_predictions": [
    {"model_name": "xgboost", "predicted_premium": 13120.50},
    {"model_name": "random_forest", "predicted_premium": 12795.40},
    {"model_name": "decision_tree", "predicted_premium": 13450.10}
  ],
  "shap_explanations": [
    {"feature_name": "age", "shap_value": 1876.30, "impact": "positive"},
    ...
  ],
  "recommended_plans": [...],
  "processing_time_ms": 12.4,
  "created_at": "2024-06-05T10:30:00Z"
}
```

---

## 🗄️ Database Schema

```sql
-- users
CREATE TABLE users (
  id              SERIAL PRIMARY KEY,
  email           VARCHAR(255) UNIQUE NOT NULL,
  username        VARCHAR(100) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  full_name       VARCHAR(200),
  is_active       BOOLEAN DEFAULT TRUE,
  is_verified     BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ
);

-- predictions
CREATE TABLE predictions (
  id                          SERIAL PRIMARY KEY,
  user_id                     INTEGER REFERENCES users(id) ON DELETE CASCADE,
  -- Input features
  age                         INTEGER NOT NULL,
  sex                         VARCHAR(10) NOT NULL,
  bmi                         FLOAT NOT NULL,
  children                    INTEGER NOT NULL,
  smoker                      VARCHAR(5) NOT NULL,
  region                      VARCHAR(20) NOT NULL,
  -- Model outputs
  predicted_premium_xgboost   FLOAT,
  predicted_premium_rf        FLOAT,
  predicted_premium_dt        FLOAT,
  best_model                  VARCHAR(50),
  best_prediction             FLOAT,
  -- Risk
  risk_score                  FLOAT,
  risk_category               VARCHAR(20),
  -- SHAP + Plans (JSONB)
  shap_values                 JSONB,
  feature_importance          JSONB,
  recommended_plans           JSONB,
  -- Meta
  model_version               VARCHAR(50),
  processing_time_ms          FLOAT,
  created_at                  TIMESTAMPTZ DEFAULT NOW()
);

-- reports
CREATE TABLE reports (
  id              SERIAL PRIMARY KEY,
  user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE,
  prediction_id   INTEGER REFERENCES predictions(id) ON DELETE CASCADE,
  filename        VARCHAR(255) NOT NULL,
  file_path       VARCHAR(500),
  file_size_bytes INTEGER,
  report_type     VARCHAR(50) DEFAULT 'prediction_report',
  status          VARCHAR(50) DEFAULT 'generated',
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  downloaded_at   TIMESTAMPTZ
);
```

---

## 🚢 Deployment

### Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

cd frontend

# Set environment variable
# VITE_API_URL=https://medinsure-api.onrender.com/api/v1

vercel --prod
```

Or connect your GitHub repo to Vercel — it reads `vercel.json` automatically.

### Render (Backend)

1. Push to GitHub
2. In Render Dashboard → New → Blueprint
3. Select your repo — Render reads `render.yaml`
4. Set `SECRET_KEY` environment variable manually
5. Deploy!

Render will:
- Provision a PostgreSQL database
- Build the Docker image
- Run the FastAPI server
- Attach a persistent disk for ML model artifacts

### Environment Variables

**Backend (Render)**
```env
DATABASE_URL=postgresql+asyncpg://...  # auto-set from Render DB
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=["https://medinsure.vercel.app"]
ENVIRONMENT=production
```

**Frontend (Vercel)**
```env
VITE_API_URL=https://medinsure-api.onrender.com/api/v1
```

---

## 🧪 Running Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test categories
pytest tests/ -v -k "test_ml"      # ML pipeline tests only
pytest tests/ -v -k "test_auth"    # Auth tests only
```

---

## 🔒 Security Considerations

- **JWT Tokens:** Short-lived access tokens (30 min) + refresh tokens (7 days)
- **Passwords:** bcrypt hashing with cost factor 12
- **SQL Injection:** SQLAlchemy parameterized queries (no raw SQL)
- **CORS:** Explicit allowlist — no wildcard in production
- **Input Validation:** Pydantic enforces strict types and ranges
- **Rate Limiting:** Add `slowapi` middleware for production
- **HTTPS:** Enforced by Vercel and Render in production

---

## 📈 Performance Notes

- ML inference: ~10–50ms per prediction
- SHAP computation: ~5–15ms (TreeExplainer is fast)
- PDF generation: ~200–400ms
- Database queries: async, non-blocking
- Frontend bundle: ~350KB gzipped (vendor-split chunks)
- Docker image: ~1.2GB backend (Python + ML libs), ~25MB frontend (nginx)

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'feat: add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ using FastAPI, React, XGBoost, and SHAP.*
