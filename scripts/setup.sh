#!/bin/bash
# ============================================================
# Project Setup Script
# ============================================================
# Each team member runs this ONCE after cloning the repository.
#
# What it does:
#   1. Installs Python dependencies (uv sync)
#   2. Configures Git hooks (auto-format with ruff on commit)
#   3. Pulls DVC-tracked data and model checkpoints
#   4. Copies .env.example → .env if needed
#
# Usage:
#   ./scripts/setup.sh
# ============================================================

set -e

echo "🚀 Setting up NLP MLOps Project..."
echo ""

# ── 1. Python dependencies ──────────────────────────────────
echo "📦 Installing Python dependencies..."
uv sync --dev
echo "✅ Dependencies installed"
echo ""

# ── 2. Git hooks (auto ruff format on commit) ───────────────
echo "🔧 Configuring Git hooks..."
git config core.hooksPath .githooks
echo "✅ Pre-commit hook activated (auto ruff format + lint)"
echo ""

# ── 3. DVC data pull ────────────────────────────────────────
echo "📥 Pulling DVC-tracked data and checkpoints..."
if uv run dvc pull 2>/dev/null; then
    echo "✅ DVC data pulled successfully"
else
    echo "⚠️  DVC pull failed. You may need to configure credentials:"
    echo "   export AWS_ACCESS_KEY_ID=<your-dagshub-token>"
    echo "   export AWS_SECRET_ACCESS_KEY=<your-dagshub-token>"
    echo "   Then re-run: uv run dvc pull"
fi
echo ""

# ── 4. Environment file ─────────────────────────────────────
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Created .env — please fill in your credentials"
else
    echo "✅ .env already exists"
fi
echo ""

# ── Done ─────────────────────────────────────────────────────
echo "════════════════════════════════════════════════════════"
echo "✅ Setup complete! You're ready to go."
echo ""
echo "Quick start:"
echo "  uv run uvicorn api.main:app --reload    # Start API"
echo "  cd frontend && npm run dev              # Start frontend"
echo "  uv run python -m pytest tests/ -v       # Run tests"
echo "════════════════════════════════════════════════════════"
