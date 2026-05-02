#!/bin/bash

# =============================================================
#  start.sh — runs the entire project from scratch
#  Usage: bash start.sh
# =============================================================

set -e  # stop if anything fails

BOLD="\033[1m"
BLUE="\033[34m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

echo ""
echo -e "${BOLD}🌏 Asia-Pacific Digital Trade Regulatory Tool${RESET}"
echo -e "   UNESCAP Hackathon 2026 · Open Source"
echo ""

# ── Step 0: check Python ──────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}✗ Python 3 not found. Install it from https://python.org${RESET}"
  exit 1
fi
echo -e "${GREEN}✓${RESET} Python $(python3 --version | cut -d' ' -f2) found"

# ── Step 1: install dependencies ──────────────────────────
echo -e "\n${BLUE}[1/5]${RESET} Installing dependencies..."
pip install -r requirements.txt -q --disable-pip-version-check
echo -e "${GREEN}✓${RESET} Dependencies ready"

# ── Step 2: check .env / API key ─────────────────────────
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo -e "\n${YELLOW}⚠  No .env file found — created one from .env.example${RESET}"
  echo -e "   Open ${BOLD}.env${RESET} and paste your Anthropic API key."
  echo -e "   Get a free key at ${BOLD}https://console.anthropic.com${RESET}\n"
fi

# load .env
set -a
source .env 2>/dev/null || true
set +a

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your-key-here" ]; then
  echo -e "\n${YELLOW}⚠  ANTHROPIC_API_KEY not set.${RESET}"
  echo -e "   Loading built-in sample data instead (no AI extraction)..."
  USE_SAMPLES=true
else
  echo -e "${GREEN}✓${RESET} API key found"
  USE_SAMPLES=false
fi

# make sure data folder exists
mkdir -p data

# ── Step 3: scrape or seed ────────────────────────────────
echo -e "\n${BLUE}[2/5]${RESET} Collecting regulation documents..."

if [ "$USE_SAMPLES" = true ]; then
  python3 scripts/seed_samples.py
  echo -e "${GREEN}✓${RESET} Sample data loaded"
else
  python3 backend/scraper.py
  echo -e "${GREEN}✓${RESET} Scraping complete"

  # ── Step 4: AI extraction ─────────────────────────────
  echo -e "\n${BLUE}[3/5]${RESET} Running AI extraction (Claude is reading the documents)..."
  python3 backend/extractor.py
  echo -e "${GREEN}✓${RESET} Extraction complete"
fi

# ── Step 5: build database ────────────────────────────────
echo -e "\n${BLUE}[4/5]${RESET} Building database..."
python3 backend/database.py
echo -e "${GREEN}✓${RESET} Database ready"

# ── Step 6: launch server ─────────────────────────────────
echo -e "\n${BLUE}[5/5]${RESET} Starting server...\n"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${BOLD}Open your browser:${RESET}  http://localhost:5000"
echo -e "  Press ${BOLD}Ctrl+C${RESET} to stop"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

python3 backend/server.py
