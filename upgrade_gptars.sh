#!/bin/bash
# ============================================================================
# GPTars Upgrade Script
# Version: 3.3.5
# 
# Upgrades existing GPTars installations to the latest package versions
# Designed for macOS ARM64 (Apple Silicon)
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory (supports symlinks)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/gptars/macos/requirements-macos.txt"
BACKUP_DIR="$SCRIPT_DIR/backups"

# Logging
LOG_FILE="$SCRIPT_DIR/upgrade_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

print_banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}           ${GREEN}GPTars Upgrade Script v3.3.5${NC}                      ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}           ${YELLOW}macOS ARM64 (Apple Silicon)${NC}                      ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_prereqs() {
    log "${BLUE}[1/6]${NC} Checking prerequisites..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log "${RED}ERROR: Python 3 not found${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    log "  ✓ Python $PYTHON_VERSION found"
    
    # Check for virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        log "${RED}ERROR: Virtual environment not found at $VENV_DIR${NC}"
        log "  Please run the setup script first or create a venv manually"
        exit 1
    fi
    log "  ✓ Virtual environment found"
    
    # Check requirements file
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log "${RED}ERROR: Requirements file not found at $REQUIREMENTS_FILE${NC}"
        exit 1
    fi
    log "  ✓ Requirements file found"
    
    # Check for pip
    if ! "$VENV_DIR/bin/pip" --version &> /dev/null; then
        log "${RED}ERROR: pip not found in virtual environment${NC}"
        exit 1
    fi
    log "  ✓ pip available"
    
    echo ""
}

backup_current() {
    log "${BLUE}[2/6]${NC} Creating backup of current packages..."
    
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="$BACKUP_DIR/requirements_backup_$(date +%Y%m%d_%H%M%S).txt"
    
    source "$VENV_DIR/bin/activate"
    pip freeze > "$BACKUP_FILE"
    
    log "  ✓ Backup saved to: $BACKUP_FILE"
    echo ""
}

upgrade_pip() {
    log "${BLUE}[3/6]${NC} Upgrading pip and setuptools..."
    
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel 2>&1 | tee -a "$LOG_FILE"
    
    log "  ✓ pip and setuptools upgraded"
    echo ""
}

upgrade_packages() {
    log "${BLUE}[4/6]${NC} Upgrading packages to latest versions..."
    
    source "$VENV_DIR/bin/activate"
    
    # Core packages that need upgrading (in dependency order)
    PACKAGES=(
        # Numpy first (many packages depend on it)
        "numpy"
        
        # Core audio
        "sounddevice"
        "soundfile"
        "scipy"
        
        # STT/TTS
        "faster-whisper"
        "piper-tts"
        "onnxruntime"
        
        # LLM/API
        "openai"
        "tiktoken"
        "requests"
        
        # Transformers ecosystem
        "transformers"
        "accelerate"
        "sentence-transformers"
        
        # Memory/Search
        "chromadb"
        "scikit-learn"
        "pandas"
        
        # Vision
        "pillow"
        "opencv-python"
        
        # Utilities
        "rich"
        "click"
        "psutil"
        
        # macOS integration
        "pyobjc-core"
        "pyobjc-framework-Cocoa"
        "pyobjc-framework-AVFoundation"
        
        # Development
        "pytest"
        "pytest-asyncio"
        "black"
    )
    
    for pkg in "${PACKAGES[@]}"; do
        log "  Upgrading $pkg..."
        pip install --upgrade "$pkg" 2>&1 | grep -E "(Installing|Successfully|Requirement)" | head -2 | tee -a "$LOG_FILE"
    done
    
    log "  ✓ All packages upgraded"
    echo ""
}

verify_installation() {
    log "${BLUE}[5/6]${NC} Verifying installation..."
    
    source "$VENV_DIR/bin/activate"
    
    # Test critical imports
    log "  Testing imports..."
    
    python3 << 'EOF'
import sys
try:
    # Core packages
    import numpy
    import scipy
    import sounddevice
    import soundfile
    
    # STT/TTS
    import faster_whisper
    from piper import PiperVoice
    import onnxruntime
    
    # LLM
    import openai
    import tiktoken
    
    # ML
    import transformers
    import torch
    
    # Wake word
    import openwakeword
    
    # Utilities
    import rich
    import click
    
    print("  ✓ All critical imports successful")
    
    # Print versions
    print(f"\n  Package Versions:")
    print(f"    numpy: {numpy.__version__}")
    print(f"    faster-whisper: {faster_whisper.__version__}")
    print(f"    onnxruntime: {onnxruntime.__version__}")
    print(f"    transformers: {transformers.__version__}")
    print(f"    torch: {torch.__version__}")
    
except ImportError as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)
EOF
    
    if [ $? -ne 0 ]; then
        log "${RED}ERROR: Verification failed${NC}"
        exit 1
    fi
    
    echo ""
}

check_conflicts() {
    log "${BLUE}[6/6]${NC} Checking for dependency conflicts..."
    
    source "$VENV_DIR/bin/activate"
    
    CONFLICTS=$(pip check 2>&1 || true)
    
    if [ -z "$CONFLICTS" ]; then
        log "  ✓ No dependency conflicts found"
    else
        log "${YELLOW}  Warning: Some dependency conflicts detected:${NC}"
        echo "$CONFLICTS" | head -5 | tee -a "$LOG_FILE"
        log "  (These are usually safe to ignore if imports work)"
    fi
    
    echo ""
}

print_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                ${GREEN}Upgrade Complete!${NC}                            ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    log "Log file: $LOG_FILE"
    echo ""
    log "Next steps:"
    log "  1. Test GPTars: ./run_gptars.sh"
    log "  2. If issues occur, restore backup:"
    log "     pip install -r $BACKUP_DIR/requirements_backup_*.txt"
    echo ""
}

# ============================================================================
# Main
# ============================================================================

print_banner

# Parse arguments
SKIP_BACKUP=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./upgrade_gptars.sh [options]"
            echo ""
            echo "Options:"
            echo "  --no-backup    Skip creating a backup of current packages"
            echo "  --help, -h     Show this help message"
            echo ""
            exit 0
            ;;
        *)
            log "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Run upgrade steps
check_prereqs

if [ "$SKIP_BACKUP" = false ]; then
    backup_current
fi

upgrade_pip
upgrade_packages
verify_installation
check_conflicts
print_summary
