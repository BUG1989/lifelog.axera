#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env.local ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env.local
  set +a
fi

export LIFELOG_HOME="${LIFELOG_HOME:-$ROOT/data/lifelog-demo}"
PHOTOS="${PHOTOS:-$LIFELOG_HOME/photos}"
DOCS="${DOCS:-$LIFELOG_HOME/docs}"

mkdir -p "$LIFELOG_HOME"

echo "== ingest photos =="
.venv/bin/python -m lifelog.cli ingest "$PHOTOS"

if [[ -d "$DOCS" ]]; then
  echo "== ingest documents =="
  .venv/bin/python -m lifelog.cli ingest "$DOCS"
fi

echo "== bulk caption (Qwen3.5-2B, single concurrency) =="
.venv/bin/python -m lifelog.cli caption --model qwen3.5-2b --concurrency 1

if [[ -d "$DOCS" ]]; then
  echo "== OCR documents =="
  .venv/bin/python -m lifelog.cli ocr --model minicpm-ocr-1.0 --since "${OCR_SINCE:-2024-02-01}"
fi

echo "== aggregate =="
.venv/bin/python -m lifelog.cli aggregate --model qwen3.5-2b

echo "== profile (35B-A3B) =="
.venv/bin/python -m lifelog.cli profile \
  --model minicpm-v-4.7-35b-a3b --describe-model qwen3.5-2b

echo "== stories (35B-A3B) =="
.venv/bin/python -m lifelog.cli story \
  --model minicpm-v-4.7-35b-a3b --all-voices
