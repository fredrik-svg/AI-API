#!/usr/bin/env bash
set -e
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp -n .env.example .env || true
echo "✅ Environment ready. Edit .env then run: bash scripts/run.sh"
