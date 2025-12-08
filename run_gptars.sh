#!/usr/bin/env bash
################################################################################
# GPTars v3.3.5 - Quick Launch Script with Pre-Checks
# MIT License — © 2024-2025 James-von-Detroit
################################################################################
#
# This script checks all requirements and launches TARS in your chosen mode.
#
# Usage:
#   ./run_gptars.sh [MODE]
#
# Modes (optional argument):
#   1, talk     - Push-to-Talk (Interactive)
#   2, wake     - Wake Word "Hey TARS" (Always Listening + Conversation)
#   3, listen   - Continuous Listening (Auto-detect speech)
#   4, test     - Run test suite
#
# Examples:
#   ./run_gptars.sh          # Interactive menu
#   ./run_gptars.sh wake     # Direct to wake word mode
#   ./run_gptars.sh 2        # Same as above
################################################################################

set -e

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
GPTARS_DIR="$SCRIPT_DIR/gptars"
VOICES_DIR="$SCRIPT_DIR/voices"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# Banner
# =============================================================================
show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
   _____ ____ _______    ____  _____ 
  / ____|  _ \__   __|/\|  _ \/ ____|
 | |  __| |_) | | |  /  \ |_) | (___  
 | | |_ |  __/  | | / /\ \  _ < \___ \ 
 | |__| | |     | |/ ____ \ |_) |___) |
  \_____|_|     |_/_/    \_\___/_____/ 
                                       
       v3.3.5 - macOS ARM64 Edition
EOF
    echo -e "${NC}"
}

# =============================================================================
# Logging helpers
# =============================================================================
log_info() { echo -e "${BLUE}ℹ${NC}  $1"; }
log_ok() { echo -e "${GREEN}✓${NC}  $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC}  $1"; }
log_error() { echo -e "${RED}✗${NC}  $1"; }
log_section() { echo -e "\n${CYAN}═══ $1 ═══${NC}"; }

# =============================================================================
# Pre-flight Checks
# =============================================================================
check_venv() {
    log_section "Checking Virtual Environment"
    
    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment not found at $VENV_DIR"
        echo ""
        echo "Please run the installer first:"
        echo "  cd $GPTARS_DIR/macos && ./install_macos.sh"
        echo ""
        exit 1
    fi
    
    log_ok "Virtual environment found"
    
    # Activate venv
    source "$VENV_DIR/bin/activate"
    log_ok "Virtual environment activated"
}

check_python_packages() {
    log_section "Checking Python Packages"
    
    local missing_packages=()
    
    # Critical packages
    local packages=(
        "faster_whisper:faster-whisper"
        "piper:piper-tts"
        "openwakeword:openwakeword"
        "sounddevice:sounddevice"
        "soundfile:soundfile"
        "numpy:numpy"
        "requests:requests"
    )
    
    for pkg_info in "${packages[@]}"; do
        local import_name="${pkg_info%%:*}"
        local pip_name="${pkg_info##*:}"
        
        if python3 -c "import $import_name" 2>/dev/null; then
            log_ok "$pip_name installed"
        else
            log_warn "$pip_name not found"
            missing_packages+=("$pip_name")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        log_warn "Missing packages: ${missing_packages[*]}"
        echo ""
        read -p "Install missing packages? [Y/n]: " install_choice
        install_choice="${install_choice:-Y}"
        
        if [[ "$install_choice" =~ ^[Yy]$ ]]; then
            log_info "Installing missing packages..."
            pip install "${missing_packages[@]}"
            log_ok "Packages installed"
        else
            log_error "Cannot continue without required packages"
            exit 1
        fi
    fi
}

check_ollama() {
    log_section "Checking Ollama"
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        log_error "Ollama not found"
        echo ""
        echo "Install Ollama:"
        echo "  brew install ollama"
        echo ""
        exit 1
    fi
    log_ok "Ollama installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_ok "Ollama is running"
        
        # Check for LLM model
        local models=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; print(' '.join([m['name'] for m in json.load(sys.stdin).get('models',[])]))" 2>/dev/null || echo "")
        
        if [[ "$models" == *"llama3"* ]] || [[ "$models" == *"mistral"* ]]; then
            log_ok "LLM model available: $models"
        else
            log_warn "No LLM model found. Available: $models"
            echo ""
            read -p "Pull llama3:8b model? [Y/n]: " pull_choice
            pull_choice="${pull_choice:-Y}"
            
            if [[ "$pull_choice" =~ ^[Yy]$ ]]; then
                log_info "Pulling llama3:8b (this may take a while)..."
                ollama pull llama3:8b-instruct-q4_0
                log_ok "Model pulled"
            fi
        fi
    else
        log_warn "Ollama is not running"
        echo ""
        read -p "Start Ollama? [Y/n]: " start_choice
        start_choice="${start_choice:-Y}"
        
        if [[ "$start_choice" =~ ^[Yy]$ ]]; then
            log_info "Starting Ollama..."
            brew services start ollama 2>/dev/null || ollama serve &
            sleep 3
            
            if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                log_ok "Ollama started"
            else
                log_error "Failed to start Ollama"
                exit 1
            fi
        else
            log_error "Cannot continue without Ollama"
            exit 1
        fi
    fi
}

check_voice_model() {
    log_section "Checking Voice Model"
    
    local tars_model="$VOICES_DIR/TARS.onnx"
    
    if [ -f "$tars_model" ]; then
        log_ok "TARS voice model found"
    else
        log_error "TARS voice model not found at $tars_model"
        echo ""
        echo "Please ensure voices/TARS.onnx exists"
        exit 1
    fi
}

check_wake_word_models() {
    log_section "Checking Wake Word Models"
    
    # Check if models are downloaded
    local model_path="$VENV_DIR/lib/python3.*/site-packages/openwakeword/resources/models"
    
    if ls $model_path/hey_jarvis*.onnx 1>/dev/null 2>&1; then
        log_ok "Wake word models found"
    else
        log_warn "Wake word models not downloaded"
        echo ""
        read -p "Download wake word models? [Y/n]: " download_choice
        download_choice="${download_choice:-Y}"
        
        if [[ "$download_choice" =~ ^[Yy]$ ]]; then
            log_info "Downloading wake word models..."
            python3 -c "from openwakeword.utils import download_models; download_models()"
            log_ok "Models downloaded"
        fi
    fi
}

check_microphone() {
    log_section "Checking Microphone"
    
    # Quick test to see if we can access the microphone
    if python3 -c "
import sounddevice as sd
devices = sd.query_devices()
input_devices = [d for d in devices if d['max_input_channels'] > 0]
if not input_devices:
    exit(1)
" 2>/dev/null; then
        log_ok "Microphone accessible"
    else
        log_warn "No microphone detected or permission denied"
        echo ""
        echo "Please grant microphone permission in:"
        echo "  System Preferences → Privacy & Security → Microphone"
        echo ""
    fi
}

# =============================================================================
# Run Pre-Checks
# =============================================================================
run_prechecks() {
    log_section "Running Pre-Flight Checks"
    echo ""
    
    check_venv
    check_python_packages
    check_ollama
    check_voice_model
    check_wake_word_models
    check_microphone
    
    echo ""
    log_ok "All checks passed!"
    echo ""
}

# =============================================================================
# Mode Selection and Launch
# =============================================================================
show_menu() {
    echo -e "${GREEN}Choose mode:${NC}"
    echo ""
    echo "  1) Push-to-Talk     - Press Enter to speak, Ctrl+C to exit"
    echo "  2) Wake Word        - Say 'Hey TARS' to start a conversation"
    echo "  3) Continuous       - Auto-detect speech (no wake word needed)"
    echo "  4) Conversation     - Extended conversation mode (2-min timeout)"
    echo "  5) Test Suite       - Run pytest tests"
    echo ""
    read -p "Enter choice [1-5, default=2]: " choice
    choice="${choice:-2}"
}

launch_tars() {
    local mode="$1"
    
    cd "$SCRIPT_DIR"
    
    case "$mode" in
        1|talk|push)
            echo ""
            log_info "Starting TARS in Push-to-Talk mode..."
            echo ""
            python3 -c "
import sys
sys.path.insert(0, 'gptars')
from core.voice_engine import VoiceEngine
engine = VoiceEngine(verbose=True)
engine.interactive_mode()
"
            ;;
        2|wake|wakeword|hey)
            echo ""
            log_info "Starting TARS with Wake Word detection..."
            log_info "Say 'Hey TARS' to start a conversation!"
            echo ""
            python3 -c "
import sys
sys.path.insert(0, 'gptars')
from core.voice_engine import VoiceEngine
from core.wake_word import TARSWakeWordListener

engine = VoiceEngine(verbose=True)
listener = TARSWakeWordListener(
    engine, 
    threshold=0.5,
    conversation_timeout=120.0,
    verbose=True
)
listener.start()
"
            ;;
        3|listen|continuous|auto)
            echo ""
            log_info "Starting TARS in Continuous Listening mode..."
            log_info "Just start speaking - no wake word needed!"
            echo ""
            python3 -c "
import sys
sys.path.insert(0, 'gptars')
from core.voice_engine import VoiceEngine
engine = VoiceEngine(verbose=True)
engine.continuous_listen_mode()
"
            ;;
        4|conversation|conv|chat)
            echo ""
            log_info "Starting TARS in Extended Conversation mode..."
            log_info "Say 'Hey TARS' to activate, then enjoy extended conversation!"
            log_info "2-minute timeout after silence, say 'goodbye' to exit"
            echo ""
            python3 -c "
import sys
sys.path.insert(0, 'gptars')
from core.wake_word import WakeWordDetector
detector = WakeWordDetector()
detector.conversation_mode()
"
            ;;
        5|test|tests)
            echo ""
            log_info "Running test suite..."
            echo ""
            cd "$GPTARS_DIR"
            pytest tests/ -v
            ;;
        *)
            log_error "Invalid mode: $mode"
            exit 1
            ;;
    esac
}

# =============================================================================
# Main
# =============================================================================
main() {
    show_banner
    
    # Run pre-checks
    run_prechecks
    
    # Check if mode was provided as argument
    if [ -n "$1" ]; then
        launch_tars "$1"
    else
        show_menu
        launch_tars "$choice"
    fi
}

# Run main with all arguments
main "$@"
