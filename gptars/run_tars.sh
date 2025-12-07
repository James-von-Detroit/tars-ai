#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# Part of GPTars v3.0 — 100% offline TARS voice assistant for macOS.
# https://github.com/James-von-Detroit/tars-ai

# run_tars.sh - Quick launch script for TARS voice assistant

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
   _____ ____ _______    ____  _____ 
  / ____|  _ \__   __|/\|  _ \/ ____|
 | |  __| |_) | | |  /  \ |_) | (___  
 | | |_ |  __/  | | / /\ \  _ < \___ \ 
 | |__| | |     | |/ ____ \ |_) |___) |
  \_____|_|     |_/_/    \_\___/_____/ 
                                       
          v3.0 Alpha - macOS ARM
EOF
echo -e "${NC}"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./macos/install_macos.sh first."
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Starting it now..."
    brew services start ollama
    sleep 3
fi

# Show menu
echo -e "${GREEN}Choose mode:${NC}"
echo "1) Push-to-Talk (Interactive)"
echo "2) Wake Word (Always Listening)"
echo "3) Vision Mode"
echo "4) Test Personality"
echo "5) Run Tests"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "Starting TARS in Push-to-Talk mode..."
        python3 core/voice_engine.py
        ;;
    2)
        echo ""
        echo "Starting TARS with Wake Word detection..."
        python3 -c "
from core.voice_engine import VoiceEngine
from core.wake_word import TARSWakeWordListener

engine = VoiceEngine(verbose=True)
listener = TARSWakeWordListener(engine, threshold=0.5)
listener.start()
"
        ;;
    3)
        echo ""
        echo "Starting TARS Vision Mode..."
        python3 core/vision_engine.py
        ;;
    4)
        echo ""
        echo "Testing TARS Personality System..."
        python3 core/tars_personality.py
        ;;
    5)
        echo ""
        echo "Running test suite..."
        pytest tests/ -v
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
