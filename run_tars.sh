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

# Find repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
VENV_DIR="$REPO_ROOT/venv"
GPTARS_DIR="$REPO_ROOT/gptars"

# Banner
echo -e "${CYAN}"
cat << "BANNER"
   _____ ____ _______    ____  _____ 
  / ____|  _ \__   __|/\|  _ \/ ____|
 | |  __| |_) | | |  /  \ |_) \___  \
 | | |_ |  __/  | | / /\ \  _ < ___) |
 | |__| | |     | |/ ____ \ |_) |__) |
  \_____|_|     |_/_/    \_\___/____/
                                     
         v3.1.0 – TARS Voice Assistant
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
echo "  1) Voice Assistant     - Full voice pipeline (STT → LLM → TTS)"
echo "  2) Vision Mode         - Camera + LLaVA image analysis"
echo "  3) Chat Only           - Text-only conversation"
echo "  4) Wake Word Test      - Test \"Hey TARS\" detection"
echo "  5) TTS Test            - Test text-to-speech"
echo "  6) Exit"
echo ""
read -p "Enter choice [1-6, default=1]: " choice
choice="${choice:-1}"

cd "$GPTARS_DIR"
export PYTHONPATH="$GPTARS_DIR:$PYTHONPATH"

case $choice in
    1)
        echo -e "\n${GREEN}Starting Voice Assistant...${NC}"
        echo -e "${DIM}Say \"Hey TARS\" to wake, then speak your question.${NC}\n"
        python3 -m core.voice_engine
        ;;
    2)
        echo -e "\n${GREEN}Starting Vision Mode...${NC}"
        python3 -m core.vision_engine
        ;;
    3)
        echo -e "\n${GREEN}Starting Chat Mode...${NC}"
        python3 -c "
from core.tars_personality import TARSPersonality, DEFAULT_TARS
tars = DEFAULT_TARS
print('TARS Chat Mode. Type \"quit\" to exit.\n')
while True:
    try:
        user = input('You: ')
        if user.lower() in ['quit', 'exit', 'q']:
            print('\nTARS: Goodbye.')
            break
        response = tars.generate_response(user)
        print(f'TARS: {response}\n')
    except (KeyboardInterrupt, EOFError):
        print('\nTARS: Goodbye.')
        break
"
        ;;
    4)
        echo -e "\n${GREEN}Testing Wake Word Detection...${NC}"
        python3 -m core.wake_word
        ;;
    5)
        echo -e "\n${GREEN}Testing Text-to-Speech...${NC}"
        echo "What a piece of work is a man." | "$REPO_ROOT/voices/piper/piper" \
            --model "$REPO_ROOT/voices/en_US-lessac-medium.onnx" \
            --output_file /tmp/tars_test.wav && \
        afplay /tmp/tars_test.wav && \
        echo -e "${GREEN}✓ TTS working!${NC}"
        ;;
    6|*)
        echo -e "\n${DIM}Goodbye.${NC}"
        exit 0
        ;;
esac
