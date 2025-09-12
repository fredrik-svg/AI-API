#!/usr/bin/env bash
set -e
URL="$1"
if [ -z "$URL" ]; then
  echo "Usage: bash scripts/ingest.sh <URL>"
  exit 1
fi
source .venv/bin/activate
curl -s -X POST "http://127.0.0.1:8000/ingest/url" -H "Content-Type: application/json" -d "{"url":"$URL"}"
