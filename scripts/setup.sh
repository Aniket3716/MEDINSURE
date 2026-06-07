#!/usr/bin/env bash
# scripts/setup.sh — One-command local setup
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     MedInsure AI — Local Setup Script    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Check prerequisites ────────────────────────────────────────────────────────
check_cmd() {
  if ! command -v "$1" &> /dev/null; then
    echo "❌ $1 is required but not installed."
    exit 1
  fi
}
check_cmd docker
check_cmd docker-compose
check_cmd node
check_cmd python3

echo "✅ Prerequisites checked"

# ── Backend .env ───────────────────────────────────────────────────────────────
if [ ! -f backend/.env ]; then
  echo "📝 Creating backend .env from example..."
  cp backend/.env.example backend/.env
  # Generate a random secret key
  SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
  sed -i "s/your-super-secret-key-change-in-production/$SECRET/" backend/.env
  echo "✅ backend/.env created (secret key auto-generated)"
fi

# ── Frontend .env ──────────────────────────────────────────────────────────────
if [ ! -f frontend/.env.local ]; then
  echo "📝 Creating frontend .env.local..."
  echo "VITE_API_URL=http://localhost:8000/api/v1" > frontend/.env.local
  echo "✅ frontend/.env.local created"
fi

# ── Build & Start ──────────────────────────────────────────────────────────────
echo ""
echo "🐳 Building Docker containers (first run may take a few minutes)..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# ── Health check ───────────────────────────────────────────────────────────────
MAX_TRIES=30
COUNT=0
until curl -sf http://localhost:8000/health > /dev/null; do
  COUNT=$((COUNT+1))
  if [ $COUNT -ge $MAX_TRIES ]; then
    echo "❌ Backend did not become healthy. Check: docker-compose logs backend"
    exit 1
  fi
  echo "   Waiting for backend... ($COUNT/$MAX_TRIES)"
  sleep 5
done

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║           ✅  MedInsure is running!          ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  Frontend:  http://localhost:3000            ║"
echo "║  Backend:   http://localhost:8000            ║"
echo "║  API Docs:  http://localhost:8000/docs       ║"
echo "║  pgAdmin:   docker-compose --profile dev up  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
