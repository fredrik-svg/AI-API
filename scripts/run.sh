#!/usr/bin/env bash
set -e
source .venv/bin/activate
HOST=$(grep -E '^HOST=' .env | cut -d= -f2)
PORT=$(grep -E '^PORT=' .env | cut -d= -f2)
python -m uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
