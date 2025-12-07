#!/usr/bin/env bash
################################################################################
# gptars v3.0 – macOS ARM One-Click Installer
# MIT License — © 2024-2025 James-von-Detroit
################################################################################
#
# The first fully local, offline TARS voice assistant for Apple Silicon.
# Complete STT → LLM → TTS pipeline with vision, wake word, and movie-accurate
# personality — 100% offline, zero API costs, sub-2s latency, privacy-first.
#
# Features:
#   - Full logging to ~/tars-install-YYYYMMDD-HHMMSS.log
#   - Error collection and summary report
#   - Ctrl+C handling with partial completion report
#   - Post-install verification with smoke test
#   - Interactive model selection
#   - Auto-detect repo root vs gptars/macos/ execution
#
# Usage:
#   ./install_macos.sh [OPTIONS]
#
# Options:
#   --help, -h       Show this help message
#   --minimal        Skip large model downloads (Whisper, LLM)
#   --skip-models    Same as --minimal
#   --no-smoke-test  Skip the wake-word smoke test
#
# Repository: https://github.com/James-von-Detroit/tars-ai
################################################################################

set -o pipefail  # Catch pipe failures

# =============================================================================
# Version Info
# =============================================================================
INSTALLER_VERSION="3.0.2"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# =============================================================================
# Help Function
# =============================================================================
show_help() {
    cat << 'HELPTEXT'
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   GPTars v3.0 – macOS ARM Installer                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

USAGE:
    ./install_macos.sh [OPTIONS]

OPTIONS:
    --help, -h       Show this help message and exit
    --minimal        Skip large model downloads (Whisper, LLM)
    --skip-models    Same as --minimal
    --no-smoke-test  Skip the wake-word smoke test at the end

DESCRIPTION:
    One-click installer for GPTars - the first fully local, offline TARS voice
    assistant for Apple Silicon Macs (M1/M2/M3/M4).

    This script will install:
      • Homebrew (if not present)
      • Python 3.11 and system dependencies
      • Ollama (local LLM server)
      • Llama-3 or Mistral model (your choice)
      • Faster-Whisper for speech-to-text
      • Piper TTS for text-to-speech
      • OpenWakeWord for "Hey TARS" detection

EXAMPLES:
    # Full installation (recommended):
    ./install_macos.sh

    # Quick install without large models:
    ./install_macos.sh --minimal

    # Run from repo root or gptars/macos/ - script auto-detects!
    cd /path/to/tars-ai && ./gptars/macos/install_macos.sh
    cd /path/to/tars-ai/gptars/macos && ./install_macos.sh

REQUIREMENTS:
    • macOS 13+ (Ventura or later)
    • Apple Silicon (M1/M2/M3/M4)
    • 16GB+ RAM recommended (8GB minimum)
    • ~15GB free disk space

MORE INFO:
    Repository: https://github.com/James-von-Detroit/tars-ai
    Discord:    https://discord.gg/AmE2Gv9EUt

HELPTEXT
    exit 0
}

# =============================================================================
# Path Resolution - Auto-detect repo root
# =============================================================================
resolve_paths() {
    local script_location
    script_location="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Detect where we're being run from and find repo root
    if [[ -d "$script_location/../../upstream" && -d "$script_location/../../gptars" ]]; then
        # Running from gptars/macos/ - go up two levels
        REPO_ROOT="$(cd "$script_location/../.." && pwd)"
    elif [[ -d "$script_location/../upstream" && -d "$script_location/../gptars" ]]; then
        # Running from gptars/ - go up one level  
        REPO_ROOT="$(cd "$script_location/.." && pwd)"
    elif [[ -d "$script_location/gptars" && -d "$script_location/upstream" ]]; then
        # Running from repo root
        REPO_ROOT="$script_location"
    elif [[ -f "$script_location/install_macos.sh" ]]; then
        # Running from gptars/macos/, standard structure
        REPO_ROOT="$(cd "$script_location/../.." && pwd)"
    else
        # Fallback: assume we're in gptars/macos
        REPO_ROOT="$(cd "$script_location/../.." && pwd)"
    fi
    
    # Define all paths relative to repo root
    GPTARS_DIR="$REPO_ROOT/gptars"
    MACOS_DIR="$GPTARS_DIR/macos"
    VENV_DIR="$REPO_ROOT/venv"
    VOICES_DIR="$REPO_ROOT/voices"
    MODELS_DIR="$REPO_ROOT/models"
    REQUIREMENTS_FILE="$MACOS_DIR/requirements-macos.txt"
    RUN_SCRIPT="$REPO_ROOT/run_tars.sh"
    
    # Verify we found the right place
    if [[ ! -d "$GPTARS_DIR" ]]; then
        echo "ERROR: Could not locate gptars/ directory."
        echo "Expected at: $GPTARS_DIR"
        echo "Please run this script from the tars-ai repository."
        exit 1
    fi
}

# =============================================================================
# Configuration
# =============================================================================
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
LOG_FILE="$HOME/tars-install-${TIMESTAMP}.log"
INSTALL_MODE="full"
SMOKE_TEST=true
START_TIME=$(date +%s)

# Tracking arrays
declare -a SUCCESSES=()
declare -a WARNINGS=()
declare -a ERRORS=()
declare -a SKIPPED=()

# Step tracking
CURRENT_STEP=0
TOTAL_STEPS=12

# =============================================================================
# Colors
# =============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# =============================================================================
# Logging Functions
# =============================================================================
log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

log_cmd() {
    local cmd="$1"
    echo "[CMD] $cmd" >> "$LOG_FILE"
}

print_status() {
    local msg="$1"
    echo -e "${BLUE}[INFO]${NC} $msg"
    log "INFO" "$msg"
}

print_success() {
    local msg="$1"
    echo -e "${GREEN}[✓]${NC} $msg"
    log "SUCCESS" "$msg"
    SUCCESSES+=("$msg")
}

print_warning() {
    local msg="$1"
    echo -e "${YELLOW}[⚠]${NC} $msg"
    log "WARNING" "$msg"
    WARNINGS+=("$msg")
}

print_error() {
    local msg="$1"
    echo -e "${RED}[✗]${NC} $msg"
    log "ERROR" "$msg"
    ERRORS+=("$msg")
}

print_step() {
    ((CURRENT_STEP++))
    local msg="$1"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  Step ${CURRENT_STEP}/${TOTAL_STEPS}: ${msg}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "STEP" "[$CURRENT_STEP/$TOTAL_STEPS] $msg"
}

# =============================================================================
# Utility Functions
# =============================================================================
run_cmd() {
    local description="$1"
    local command="$2"
    local allow_failure="${3:-false}"
    
    print_status "$description..."
    log_cmd "$command"
    
    local output
    local exit_code
    
    output=$(eval "$command" 2>&1)
    exit_code=$?
    
    echo "$output" >> "$LOG_FILE"
    
    if [ $exit_code -eq 0 ]; then
        print_success "$description"
        return 0
    else
        if [ "$allow_failure" = "true" ]; then
            print_warning "$description (non-critical, continuing)"
            SKIPPED+=("$description")
            return 0
        else
            print_error "$description failed (exit code: $exit_code)"
            return 1
        fi
    fi
}

check_command() {
    command -v "$1" &> /dev/null
}

format_duration() {
    local seconds=$1
    local minutes=$((seconds / 60))
    local remaining=$((seconds % 60))
    if [ $minutes -gt 0 ]; then
        echo "${minutes}m ${remaining}s"
    else
        echo "${remaining}s"
    fi
}

# =============================================================================
# Report Generation
# =============================================================================
generate_report() {
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    local formatted_duration
    formatted_duration=$(format_duration $duration)
    local exit_status="${1:-completed}"
    
    echo "" | tee -a "$LOG_FILE"
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}║                        INSTALLATION REPORT                                 ║${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    echo -e "${BOLD}Status:${NC}       $exit_status" | tee -a "$LOG_FILE"
    echo -e "${BOLD}Duration:${NC}     $formatted_duration" | tee -a "$LOG_FILE"
    echo -e "${BOLD}Log file:${NC}     $LOG_FILE" | tee -a "$LOG_FILE"
    echo -e "${BOLD}Steps:${NC}        $CURRENT_STEP / $TOTAL_STEPS" | tee -a "$LOG_FILE"
    echo -e "${BOLD}Repo root:${NC}    $REPO_ROOT" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # Successes
    if [ ${#SUCCESSES[@]} -gt 0 ]; then
        echo -e "${GREEN}${BOLD}✓ Completed (${#SUCCESSES[@]}):${NC}" | tee -a "$LOG_FILE"
        for item in "${SUCCESSES[@]}"; do
            echo -e "  ${GREEN}•${NC} $item" | tee -a "$LOG_FILE"
        done
        echo "" | tee -a "$LOG_FILE"
    fi
    
    # Warnings
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo -e "${YELLOW}${BOLD}⚠ Warnings (${#WARNINGS[@]}):${NC}" | tee -a "$LOG_FILE"
        for item in "${WARNINGS[@]}"; do
            echo -e "  ${YELLOW}•${NC} $item" | tee -a "$LOG_FILE"
        done
        echo "" | tee -a "$LOG_FILE"
    fi
    
    # Skipped
    if [ ${#SKIPPED[@]} -gt 0 ]; then
        echo -e "${MAGENTA}${BOLD}○ Skipped (${#SKIPPED[@]}):${NC}" | tee -a "$LOG_FILE"
        for item in "${SKIPPED[@]}"; do
            echo -e "  ${MAGENTA}•${NC} $item" | tee -a "$LOG_FILE"
        done
        echo "" | tee -a "$LOG_FILE"
    fi
    
    # Errors
    if [ ${#ERRORS[@]} -gt 0 ]; then
        echo -e "${RED}${BOLD}✗ Errors (${#ERRORS[@]}):${NC}" | tee -a "$LOG_FILE"
        for item in "${ERRORS[@]}"; do
            echo -e "  ${RED}•${NC} $item" | tee -a "$LOG_FILE"
        done
        echo "" | tee -a "$LOG_FILE"
    fi
    
    # Final status
    if [ ${#ERRORS[@]} -eq 0 ]; then
        echo -e "${GREEN}════════════════════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}${BOLD}  ✓ INSTALLATION SUCCESSFUL${NC}"
        echo -e "${GREEN}════════════════════════════════════════════════════════════════════════════${NC}"
        
        echo ""
        echo -e "${BOLD}🚀 Quick Start Commands:${NC}"
        echo ""
        echo -e "  ${DIM}# Navigate to repo and activate environment:${NC}"
        echo -e "  ${CYAN}cd $REPO_ROOT${NC}"
        echo -e "  ${CYAN}source venv/bin/activate${NC}"
        echo ""
        echo -e "  ${DIM}# Start TARS (interactive launcher):${NC}"
        echo -e "  ${CYAN}./run_tars.sh${NC}"
        echo ""
        echo -e "  ${DIM}# Or test voice pipeline directly:${NC}"
        echo -e "  ${CYAN}cd gptars && python3 core/voice_engine.py${NC}"
        echo ""
        echo -e "  ${DIM}# Say \"Hey TARS\" and start talking!${NC}"
        echo ""
        
        # TARS quote
        echo -e "${DIM}────────────────────────────────────────────────────────────────────────────${NC}"
        echo ""
        echo -e "  ${CYAN}\"Everybody good? Plenty of slaves for my robot colony?\"${NC}"
        echo -e "  ${DIM}    — TARS, Interstellar (2014)${NC}"
        echo ""
        echo -e "  ${GREEN}Thanks for installing GPTars. Welcome to the future of offline AI.${NC}"
        echo ""
    else
        echo -e "${RED}════════════════════════════════════════════════════════════════════════════${NC}"
        echo -e "${RED}${BOLD}  ✗ INSTALLATION COMPLETED WITH ERRORS${NC}"
        echo -e "${RED}════════════════════════════════════════════════════════════════════════════${NC}"
        echo ""
        echo "  Please check the log file for details:"
        echo -e "  ${CYAN}cat $LOG_FILE${NC}"
        echo ""
        echo "  Common fixes:"
        echo "    • Retry the installation: ./gptars/macos/install_macos.sh"
        echo "    • Check disk space: df -h"
        echo "    • Check network: ping -c 3 google.com"
        echo ""
    fi
}

# =============================================================================
# Signal Handlers
# =============================================================================
handle_interrupt() {
    echo ""
    print_error "Installation interrupted by user (Ctrl+C)"
    generate_report "INTERRUPTED"
    exit 130
}

handle_error() {
    local line_no=$1
    print_error "Error on line $line_no"
    generate_report "FAILED"
    exit 1
}

trap handle_interrupt INT TERM
trap 'handle_error $LINENO' ERR

# =============================================================================
# Banner
# =============================================================================
show_banner() {
    echo -e "${BLUE}"
    cat << "BANNER"
   _____ ____ _______    ____  _____   ______ 
  / ____|  _ \__   __|/\|  _ \/ ____| |___  / 
 | |  __| |_) | | |  /  \ |_) \___ \     / /  
 | | |_ |  __/  | | / /\ \  _ < ___) |   / /   
 | |__| | |     | |/ ____ \ |_) |__) |  / /___ 
  \_____|_|     |_/_/    \_\___/____/  /_____|
                                              
          v3.0.2 – macOS ARM Installer
    100% Offline TARS Voice Assistant for M1+
BANNER
    echo -e "${NC}"
    echo ""
    echo -e "${BOLD}Installer:${NC}    v${INSTALLER_VERSION}"
    echo -e "${BOLD}Log file:${NC}     $LOG_FILE"
    echo -e "${BOLD}Mode:${NC}         $INSTALL_MODE"
    echo -e "${BOLD}Repo root:${NC}    $REPO_ROOT"
    echo ""
}

# =============================================================================
# System Checks
# =============================================================================
check_system() {
    print_step "System Diagnostics"
    
    # Log system info
    log "SYSTEM" "=== SYSTEM INFORMATION ==="
    log "SYSTEM" "OS: $(sw_vers -productName) $(sw_vers -productVersion)"
    log "SYSTEM" "Architecture: $(uname -m)"
    log "SYSTEM" "Hostname: $(hostname)"
    log "SYSTEM" "User: $(whoami)"
    log "SYSTEM" "Repo Root: $REPO_ROOT"
    log "SYSTEM" "GPTars Dir: $GPTARS_DIR"
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│ SYSTEM DIAGNOSTIC                                                    │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│ %-22s %-46s │\n" "OS:" "$(sw_vers -productName) $(sw_vers -productVersion)"
    printf "│ %-22s %-46s │\n" "Architecture:" "$(uname -m)"
    printf "│ %-22s %-46s │\n" "Chip:" "$(sysctl -n machdep.cpu.brand_string 2>/dev/null | cut -c1-46 || echo 'Unknown')"
    printf "│ %-22s %-46s │\n" "Memory:" "$(sysctl -n hw.memsize | awk '{printf "%.0f GB", $1/1024/1024/1024}')"
    printf "│ %-22s %-46s │\n" "Disk Free:" "$(df -h "$HOME" | tail -1 | awk '{print $4}')"
    printf "│ %-22s %-46s │\n" "Repo Root:" "$(echo "$REPO_ROOT" | tail -c 47)"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    
    # Check macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script is for macOS only!"
        return 1
    fi
    print_success "macOS detected"
    
    # Check architecture
    local arch
    arch=$(uname -m)
    if [[ "$arch" != "arm64" ]]; then
        print_warning "Detected architecture: $arch (not Apple Silicon)"
        print_warning "This script is optimized for M1/M2/M3/M4 Macs"
    else
        print_success "Apple Silicon ($arch) detected"
    fi
    
    # Check disk space
    local available_gb
    available_gb=$(df -g "$HOME" | tail -1 | awk '{print $4}')
    if [ "$available_gb" -lt 15 ]; then
        print_warning "Low disk space: ${available_gb}GB (15GB+ recommended)"
    else
        print_success "Disk space: ${available_gb}GB available"
    fi
    
    # Verify gptars directory exists
    if [[ ! -d "$GPTARS_DIR" ]]; then
        print_error "gptars directory not found at: $GPTARS_DIR"
        return 1
    fi
    print_success "GPTars directory found"
    
    return 0
}

# =============================================================================
# Installation Steps
# =============================================================================

install_homebrew() {
    print_step "Homebrew Installation"
    
    if check_command brew; then
        print_success "Homebrew already installed: $(brew --version | head -1)"
        return 0
    fi
    
    print_status "Installing Homebrew (this may take a few minutes)..."
    
    if /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" >> "$LOG_FILE" 2>&1; then
        # Add Homebrew to PATH for Apple Silicon
        if [[ "$(uname -m)" == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        print_success "Homebrew installed"
    else
        print_error "Homebrew installation failed"
        return 1
    fi
}

install_system_deps() {
    print_step "System Dependencies"
    
    run_cmd "Updating Homebrew" "brew update" true
    
    local deps=("python@3.11" "portaudio" "ffmpeg" "cmake" "wget")
    for dep in "${deps[@]}"; do
        if brew list "$dep" &>/dev/null; then
            print_success "$dep already installed"
        else
            run_cmd "Installing $dep" "brew install $dep" false || return 1
        fi
    done
    
    return 0
}

install_ollama() {
    print_step "Ollama (Local LLM Server)"
    
    if check_command ollama; then
        print_success "Ollama already installed"
    else
        run_cmd "Installing Ollama" "brew install ollama" false || return 1
    fi
    
    print_status "Starting Ollama service..."
    brew services start ollama >> "$LOG_FILE" 2>&1 || true
    sleep 3
    
    # Verify Ollama is responding
    if curl -s http://localhost:11434/api/tags &>/dev/null; then
        print_success "Ollama service running"
    else
        print_warning "Ollama service may not be fully started yet"
    fi
    
    return 0
}

download_llm_model() {
    print_step "LLM Model Download"
    
    if [[ "$INSTALL_MODE" == "minimal" ]]; then
        print_warning "Skipping LLM model download (minimal mode)"
        SKIPPED+=("LLM model download")
        return 0
    fi
    
    echo ""
    echo -e "${YELLOW}Select LLM model to download:${NC}"
    echo ""
    echo "  1) llama3.2:3b            - Small & fast (~2GB, good for 8GB Macs)"
    echo "  2) llama3:8b-instruct-q4_0 - ⭐ Recommended for TARS (~4.7GB, instruction-tuned)"
    echo "  3) llama3:8b              - Base model (~4.7GB)"
    echo "  4) mistral                - Alternative high quality (~4GB)"
    echo "  5) phi3:mini              - Tiny & fast (~2GB, Microsoft)"
    echo "  6) Skip for now"
    echo ""
    read -t 120 -p "Enter choice [1-6, default=2]: " model_choice || model_choice="2"
    model_choice="${model_choice:-2}"
    
    case $model_choice in
        1)
            run_cmd "Downloading llama3.2:3b" "ollama pull llama3.2:3b" true
            ;;
        2)
            run_cmd "Downloading llama3:8b-instruct-q4_0" "ollama pull llama3:8b-instruct-q4_0" true
            ;;
        3)
            run_cmd "Downloading llama3:8b" "ollama pull llama3:8b" true
            ;;
        4)
            run_cmd "Downloading mistral" "ollama pull mistral" true
            ;;
        5)
            run_cmd "Downloading phi3:mini" "ollama pull phi3:mini" true
            ;;
        *)
            print_warning "Skipping LLM model download"
            SKIPPED+=("LLM model download (user choice)")
            ;;
    esac
    
    return 0
}

setup_python_env() {
    print_step "Python Environment"
    
    cd "$REPO_ROOT" || return 1
    
    if [ ! -d "$VENV_DIR" ]; then
        run_cmd "Creating virtual environment at repo root" "python3.11 -m venv venv" false || return 1
    else
        print_success "Virtual environment already exists"
    fi
    
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    log "INFO" "Activated venv: $(which python)"
    
    run_cmd "Upgrading pip" "pip install --upgrade pip setuptools wheel" false || return 1
    
    return 0
}

install_python_deps() {
    print_step "Python Dependencies"
    
    cd "$REPO_ROOT" || return 1
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    
    if [ -f "$REQUIREMENTS_FILE" ]; then
        run_cmd "Installing Python packages from requirements" "pip install -r $REQUIREMENTS_FILE" false || return 1
    else
        print_warning "requirements-macos.txt not found at $REQUIREMENTS_FILE"
        print_status "Installing core packages manually..."
        run_cmd "Installing core packages" "pip install openai tiktoken requests python-dotenv flask sounddevice numpy scipy" false || return 1
    fi
    
    return 0
}

install_whisper() {
    print_step "Faster-Whisper (Speech-to-Text)"
    
    cd "$REPO_ROOT" || return 1
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    
    run_cmd "Installing faster-whisper" "pip install faster-whisper" false || return 1
    run_cmd "Installing coremltools" "pip install coremltools" true
    
    if [[ "$INSTALL_MODE" == "minimal" ]]; then
        print_warning "Skipping Whisper model download (minimal mode)"
        SKIPPED+=("Whisper model download")
        return 0
    fi
    
    print_status "Downloading Whisper model (distil-large-v3)..."
    mkdir -p "$MODELS_DIR/whisper"
    
    python3 << PYTHON_SCRIPT >> "$LOG_FILE" 2>&1
import os
import sys
try:
    from faster_whisper import WhisperModel
    models_dir = "$MODELS_DIR/whisper"
    os.makedirs(models_dir, exist_ok=True)
    print("Downloading distil-large-v3 model...", file=sys.stderr)
    model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8", download_root=models_dir)
    print("Whisper model downloaded successfully", file=sys.stderr)
except Exception as e:
    print(f"Warning: Could not download Whisper model: {e}", file=sys.stderr)
PYTHON_SCRIPT
    
    print_success "Faster-Whisper installed"
    return 0
}

install_piper_tts() {
    print_step "Piper TTS (Text-to-Speech)"
    
    cd "$REPO_ROOT" || return 1
    mkdir -p "$VOICES_DIR"
    
    PIPER_VERSION="2023.11.14-2"
    # NOTE: macOS ARM64 uses 'aarch64' not 'arm64' in the filename
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/piper_macos_aarch64.tar.gz"
    
    # Piper extracts to piper/ subdirectory, binary is at piper/piper
    if [ ! -f "$VOICES_DIR/piper/piper" ]; then
        print_status "Downloading Piper TTS binary..."
        cd "$VOICES_DIR"
        if curl -L "${PIPER_URL}" -o piper.tar.gz >> "$LOG_FILE" 2>&1; then
            tar -xzf piper.tar.gz >> "$LOG_FILE" 2>&1
            rm -f piper.tar.gz
            chmod +x piper/piper 2>/dev/null || true
            cd "$REPO_ROOT"
            print_success "Piper TTS binary installed"
        else
            cd "$REPO_ROOT"
            print_warning "Could not download Piper TTS binary"
            SKIPPED+=("Piper TTS binary")
        fi
    else
        print_success "Piper TTS binary already installed"
    fi
    
    # Download voice model
    cd "$VOICES_DIR"
    if [ ! -f "en_US-lessac-medium.onnx" ]; then
        print_status "Downloading TTS voice model..."
        wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx >> "$LOG_FILE" 2>&1 || true
        wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json >> "$LOG_FILE" 2>&1 || true
        if [ -f "en_US-lessac-medium.onnx" ]; then
            print_success "TTS voice model downloaded"
        else
            print_warning "Could not download TTS voice model"
            SKIPPED+=("TTS voice model")
        fi
    else
        print_success "TTS voice model already exists"
    fi
    
    cd "$REPO_ROOT"
    return 0
}

install_wake_word() {
    print_step "Wake Word Detection"
    
    cd "$REPO_ROOT" || return 1
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    
    run_cmd "Installing openwakeword" "pip install openwakeword" true
    
    if [[ "$INSTALL_MODE" == "minimal" ]]; then
        print_warning "Skipping wake word model download (minimal mode)"
        SKIPPED+=("Wake word model download")
        return 0
    fi
    
    print_status "Downloading wake word models..."
    mkdir -p "$MODELS_DIR/wakeword"
    
    python3 << PYTHON_SCRIPT >> "$LOG_FILE" 2>&1
import os
import sys
try:
    from openwakeword.model import Model
    models_dir = "$MODELS_DIR/wakeword"
    os.makedirs(models_dir, exist_ok=True)
    print("Downloading wake word models...", file=sys.stderr)
    model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
    print("Wake word models downloaded", file=sys.stderr)
except Exception as e:
    print(f"Warning: Could not download wake word models: {e}", file=sys.stderr)
PYTHON_SCRIPT
    
    print_success "Wake word detection installed"
    return 0
}

request_permissions() {
    print_step "System Permissions"
    
    cd "$REPO_ROOT" || return 1
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    
    print_status "Testing microphone access (this triggers macOS permission dialog)..."
    
    # This Python script actually accesses the microphone, triggering the real permission dialog
    local mic_result
    mic_result=$(python3 << 'PYTHON_MIC_TEST' 2>&1
import sys
try:
    import sounddevice as sd
    import numpy as np
    
    print("Requesting microphone access...", file=sys.stderr)
    # Record 0.5 seconds - this triggers the macOS permission dialog
    duration = 0.5
    sample_rate = 16000
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    # Check if we got actual audio data
    if recording is not None and len(recording) > 0:
        print("MICROPHONE_OK", file=sys.stdout)
    else:
        print("MICROPHONE_EMPTY", file=sys.stdout)
except PermissionError:
    print("MICROPHONE_DENIED", file=sys.stdout)
except Exception as e:
    print(f"MICROPHONE_ERROR: {e}", file=sys.stdout)
PYTHON_MIC_TEST
)
    
    if [[ "$mic_result" == *"MICROPHONE_OK"* ]]; then
        print_success "Microphone access granted"
    elif [[ "$mic_result" == *"MICROPHONE_DENIED"* ]]; then
        print_warning "Microphone permission denied - please grant in System Settings"
    else
        print_warning "Microphone test inconclusive - you may need to grant permission manually"
    fi
    
    echo ""
    echo -e "${YELLOW}If you didn't see a permission dialog:${NC}"
    echo -e "  1. Open ${BOLD}System Settings${NC} > ${BOLD}Privacy & Security${NC} > ${BOLD}Microphone${NC}"
    echo -e "  2. Find ${BOLD}Terminal${NC} (or your terminal app) and enable it"
    echo -e "  3. For camera: ${BOLD}Privacy & Security${NC} > ${BOLD}Camera${NC}"
    echo ""
    
    return 0
}

# =============================================================================
# Verification
# =============================================================================
verify_installation() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  Verification${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    cd "$REPO_ROOT" || return 1
    
    local checks_passed=0
    local checks_total=0
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│ VERIFICATION RESULTS                                                 │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    
    # Check Python
    ((checks_total++))
    if check_command python3; then
        printf "│  ${GREEN}✓${NC} %-65s │\n" "Python3: $(python3 --version 2>&1 | head -1)"
        ((checks_passed++))
    else
        printf "│  ${RED}✗${NC} %-65s │\n" "Python3: NOT FOUND"
    fi
    
    # Check venv
    ((checks_total++))
    if [ -d "$VENV_DIR" ]; then
        printf "│  ${GREEN}✓${NC} %-65s │\n" "Virtual environment: $VENV_DIR"
        ((checks_passed++))
    else
        printf "│  ${RED}✗${NC} %-65s │\n" "Virtual environment: MISSING"
    fi
    
    # Check Ollama
    ((checks_total++))
    if check_command ollama; then
        local models
        models=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
        printf "│  ${GREEN}✓${NC} %-65s │\n" "Ollama: Installed ($models models)"
        ((checks_passed++))
    else
        printf "│  ${YELLOW}○${NC} %-65s │\n" "Ollama: Not installed"
    fi
    
    # Check Piper
    ((checks_total++))
    if [ -f "$VOICES_DIR/piper/piper" ]; then
        printf "│  ${GREEN}✓${NC} %-65s │\n" "Piper TTS: Installed"
        ((checks_passed++))
    else
        printf "│  ${YELLOW}○${NC} %-65s │\n" "Piper TTS: Not installed"
    fi
    
    # Check voice model
    ((checks_total++))
    if [ -f "$VOICES_DIR/en_US-lessac-medium.onnx" ]; then
        printf "│  ${GREEN}✓${NC} %-65s │\n" "TTS Voice model: Downloaded"
        ((checks_passed++))
    else
        printf "│  ${YELLOW}○${NC} %-65s │\n" "TTS Voice model: Not downloaded"
    fi
    
    # Check run_tars.sh
    ((checks_total++))
    if [ -f "$RUN_SCRIPT" ]; then
        printf "│  ${GREEN}✓${NC} %-65s │\n" "run_tars.sh: Found at repo root"
        ((checks_passed++))
    else
        printf "│  ${YELLOW}○${NC} %-65s │\n" "run_tars.sh: Not found"
    fi
    
    # Check gptars/core
    ((checks_total++))
    if [ -d "$GPTARS_DIR/core" ]; then
        printf "│  ${GREEN}✓${NC} %-65s │\n" "gptars/core: Found"
        ((checks_passed++))
    else
        printf "│  ${RED}✗${NC} %-65s │\n" "gptars/core: MISSING"
    fi
    
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  Checks passed: %-3d / %-3d                                           │\n" "$checks_passed" "$checks_total"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    
    log "VERIFY" "Checks passed: $checks_passed / $checks_total"
}

# =============================================================================
# Smoke Test
# =============================================================================
run_smoke_test() {
    if [[ "$SMOKE_TEST" != true ]]; then
        return 0
    fi
    
    print_step "Smoke Test"
    
    cd "$REPO_ROOT" || return 1
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    
    print_status "Testing Python imports and core components..."
    
    local smoke_result
    smoke_result=$(python3 << 'PYTHON_SMOKE' 2>&1
import sys
import os

# Set PYTHONPATH to repo root
sys.path.insert(0, os.getcwd())

try:
    # Test 1: Can we import gptars package?
    try:
        import gptars
        print("✓ gptars package imported")
    except ImportError as e:
        print(f"✗ gptars package import failed: {e}")
        sys.exit(1)
    
    # Test 2: Can we import core modules?
    try:
        from gptars.core.tars_personality import TARSPersonality, DEFAULT_TARS
        print("✓ gptars.core.tars_personality imported")
        
        # Test personality creation
        tars = DEFAULT_TARS
        response = tars.generate_response("Hello TARS", use_ollama=False)
        if response:
            print("✓ TARS personality working")
    except ImportError as e:
        print(f"✗ gptars.core.tars_personality import failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"○ TARS personality test warning: {e}")
    
    # Test 3: Can we import openwakeword?
    try:
        from openwakeword.model import Model
        print("✓ openwakeword imported")
    except ImportError:
        print("○ openwakeword not installed (optional)")
    
    # Test 4: Can we import faster_whisper?
    try:
        from faster_whisper import WhisperModel
        print("✓ faster_whisper imported")
    except ImportError:
        print("○ faster_whisper not installed (optional)")
    
    # Test 5: Can we check Ollama?
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as response:
            print("✓ Ollama responding")
    except:
        print("○ Ollama not responding (start with: brew services start ollama)")
    
    print("")
    print("Smoke test PASSED - core components loaded!")
    sys.exit(0)
except Exception as e:
    print(f"Smoke test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SMOKE
)
    
    echo "$smoke_result"
    log "SMOKE" "$smoke_result"
    
    if echo "$smoke_result" | grep -q "Smoke test PASSED"; then
        print_success "Smoke test completed successfully"
        return 0
    else
        print_warning "Smoke test completed with warnings (see above)"
        return 0
    fi
}

# =============================================================================
# Argument Parsing
# =============================================================================
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                ;;
            --minimal|--skip-models)
                INSTALL_MODE="minimal"
                shift
                ;;
            --no-smoke-test)
                SMOKE_TEST=false
                shift
                ;;
            *)
                print_warning "Unknown option: $1"
                shift
                ;;
        esac
    done
}

# =============================================================================
# Main
# =============================================================================
main() {
    # Parse command line arguments
    parse_args "$@"
    
    # Resolve paths first (before logging starts)
    resolve_paths
    
    # Initialize log
    {
        echo "GPTars v3.0 Installation Log"
        echo "Installer version: $INSTALLER_VERSION"
        echo "Started: $(date)"
        echo "Mode: $INSTALL_MODE"
        echo "Repo root: $REPO_ROOT"
        echo "GPTars dir: $GPTARS_DIR"
        echo "========================================"
    } > "$LOG_FILE"
    
    show_banner
    
    # Show mode info
    if [[ "$INSTALL_MODE" == "minimal" ]]; then
        print_status "Running in minimal mode (skipping large model downloads)"
    fi
    
    # Run installation steps
    check_system || { generate_report "FAILED"; exit 1; }
    install_homebrew || { generate_report "FAILED"; exit 1; }
    install_system_deps || { generate_report "FAILED"; exit 1; }
    install_ollama || { generate_report "FAILED"; exit 1; }
    download_llm_model || { generate_report "FAILED"; exit 1; }
    setup_python_env || { generate_report "FAILED"; exit 1; }
    install_python_deps || { generate_report "FAILED"; exit 1; }
    install_whisper || { generate_report "FAILED"; exit 1; }
    install_piper_tts || { generate_report "FAILED"; exit 1; }
    install_wake_word || { generate_report "FAILED"; exit 1; }
    request_permissions
    
    # Verify and smoke test
    verify_installation
    run_smoke_test
    
    # Generate final report
    generate_report "COMPLETED"
    
    # Exit with appropriate code
    if [ ${#ERRORS[@]} -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main with all arguments
main "$@"
