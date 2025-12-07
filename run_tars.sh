#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# GPTars v3.1 — Quick Launch Script
# https://github.com/James-von-Detroit/tars-ai
################################################################################

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Auto-cd to repo root no matter where script is called from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# If this script is at repo root, SCRIPT_DIR is repo root
# Check for gptars/ directory to confirm
if [[ ! -d "$SCRIPT_DIR/gptars" ]]; then
    echo -e "${RED}Error:${NC} Cannot find gptars/ directory"
    echo "This script must be run from the tars-ai repository root"
    exit 1
fi
REPO_ROOT="$SCRIPT_DIR"
VENV_DIR="$REPO_ROOT/venv"
GPTARS_DIR="$REPO_ROOT/gptars"

# Change to repo root
cd "$REPO_ROOT"

# Banner
echo -e "${CYAN}"
cat << "BANNER"
   _____ ____ _______    ____  _____ 
  / ____|  _ \__   __|/\|  _ \/ ____|
 | |  __| |_) | | |  /  \ |_) \___  \
 | | |_ |  __/  | | / /\ \  _ < ___) |
 | |__| | |     | |/ ____ \ |_) |__) |
  \_____|_|     |_/_/    \_\___/____/
                                     
         v3.0.2 – TARS Voice Assistant
BANNER
echo -e "${NC}"

# Check venv
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Error:${NC} Virtual environment not found at $VENV_DIR"
    echo -e "Run the installer first: ${CYAN}./gptars/macos/install_macos.sh${NC}"
    exit 1
fi

# Activate venv
echo -e "${DIM}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Check Ollama
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo -e "${YELLOW}⚠ Ollama not running. Starting...${NC}"
    brew services start ollama 2>/dev/null || ollama serve &>/dev/null &
    sleep 2
fi

# Menu
echo ""
echo -e "${BOLD}Select mode:${NC}"
echo ""
echo "  1) Push-to-talk        - Hold Enter to speak, release to process"
echo "  2) Wake Word           - Say \"Hey TARS\" to activate"
echo "  3) Vision Mode         - Camera + LLaVA image analysis"
echo "  4) Vision Test         - Test camera and vision pipeline"
echo "  5) Run Tests           - Execute test suite"
echo "  6) Exit"
echo ""
read -p "Enter choice [1-6, default=1]: " choice
choice="${choice:-1}"

# Set PYTHONPATH to repo root so 'from gptars.core import ...' works
export PYTHONPATH="$REPO_ROOT:$PYTHONPATH"

case $choice in
    1)
        echo -e "\n${GREEN}Starting Push-to-Talk Voice Assistant...${NC}"
        echo -e "${DIM}Press and hold Enter to speak, release when done.${NC}\n"
        python3 -m gptars.core.voice_engine
        ;;
    2)
        echo -e "\n${GREEN}Starting Wake Word Voice Assistant...${NC}"
        echo -e "${DIM}Say \"Hey TARS\" to wake, then speak your question.${NC}\n"
        python3 -m gptars.core.wake_word
        ;;
    3)
        echo -e "\n${GREEN}Starting Vision Mode...${NC}"
        python3 -m gptars.core.vision_engine
        ;;
    4)
        echo -e "\n${GREEN}Testing Vision Pipeline...${NC}"
        python3 -c "
from gptars.core.vision_engine import VisionEngine
import sys

print('Testing camera access...')
try:
    engine = VisionEngine()
    print('✓ Vision engine initialized')
    frame = engine.capture_frame()
    if frame is not None:
        print('✓ Camera capture successful')
    else:
        print('✗ Camera capture failed')
    sys.exit(0)
except Exception as e:
    print(f'✗ Vision test failed: {e}')
    sys.exit(1)
"
        ;;
    5)
        echo -e "\n${GREEN}Running Test Suite...${NC}"
        cd "$REPO_ROOT"
        python3 -m pytest gptars/tests/ -v
        ;;
    6|*)
        echo -e "\n${DIM}Goodbye.${NC}"
        exit 0
        ;;
esac
