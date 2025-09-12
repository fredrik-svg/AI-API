#!/usr/bin/env bash
set -e
URL="$1"
if [ -z "$URL" ]; then
  echo "Usage: bash scripts/download_model.sh <GGUF_DIRECT_URL>"
  exit 1
fi
mkdir -p data/models
FNAME="data/models/model.gguf"
curl -L "$URL" -o "$FNAME"
echo "Saved model to $FNAME"
