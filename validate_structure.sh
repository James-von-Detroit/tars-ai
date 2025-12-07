#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# Quick validation script for GPTars v3.0 structure
# Tests that all imports work and structure is correct

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║               GPTars v3.0 Structure Validation                            ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test counter
PASSED=0
FAILED=0

test_check() {
    local name="$1"
    local check="$2"
    
    printf "  %-50s " "$name..."
    if eval "$check" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++)) || true
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++)) || true
        return 0
    fi
}

echo -e "${CYAN}Structure Tests:${NC}"
test_check "gptars/ directory exists" "[ -d gptars ]"
test_check "gptars/core/ directory exists" "[ -d gptars/core ]"
test_check "gptars/macos/ directory exists" "[ -d gptars/macos ]"
test_check "gptars/__init__.py exists" "[ -f gptars/__init__.py ]"
test_check "upstream/ directory exists" "[ -d upstream ]"
test_check "shared/ directory exists" "[ -d shared ]"
test_check "run_tars.sh exists at root" "[ -f run_tars.sh ]"
test_check "run_tars.sh is executable" "[ -x run_tars.sh ]"
test_check "install_macos.sh exists" "[ -f gptars/macos/install_macos.sh ]"
test_check "install_macos.sh is executable" "[ -x gptars/macos/install_macos.sh ]"

echo ""
echo -e "${CYAN}Documentation Tests:${NC}"
test_check "README.md exists" "[ -f README.md ]"
test_check "LICENSE.md exists" "[ -f LICENSE.md ]"
test_check "DEPRECATION.md exists" "[ -f DEPRECATION.md ]"
test_check "FORK-STRATEGY.md exists" "[ -f FORK-STRATEGY.md ]"

echo ""
echo -e "${CYAN}Python Import Tests:${NC}"

# Test gptars package import
test_check "Can import gptars package" \
    "python3 -c 'import sys; sys.path.insert(0, \".\"); import gptars'"

# Test core module imports
test_check "Can import gptars.core" \
    "python3 -c 'import sys; sys.path.insert(0, \".\"); from gptars import core'"

test_check "Can import TARSPersonality" \
    "python3 -c 'import sys; sys.path.insert(0, \".\"); from gptars.core.tars_personality import TARSPersonality'"

test_check "Can import DEFAULT_TARS" \
    "python3 -c 'import sys; sys.path.insert(0, \".\"); from gptars.core.tars_personality import DEFAULT_TARS'"

test_check "Can access gptars.__version__" \
    "python3 -c 'import sys; sys.path.insert(0, \".\"); import gptars; assert gptars.__version__ == \"3.1.0\"'"

echo ""
echo -e "${CYAN}License Header Tests:${NC}"
test_check "gptars files have MIT headers" \
    "grep -q 'SPDX-License-Identifier: MIT' gptars/core/voice_engine.py"

test_check "upstream files have CC-BY-NC headers" \
    "grep -q 'SPDX-License-Identifier: CC-BY-NC-4.0' upstream/src/app.py"

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                           Test Results                                    ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${GREEN}Passed:${NC}  $PASSED"
echo -e "  ${RED}Failed:${NC}  $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All validation tests passed!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "  1. Run installer: ${DIM}./gptars/macos/install_macos.sh${NC}"
    echo -e "  2. Activate venv:  ${DIM}source venv/bin/activate${NC}"
    echo -e "  3. Launch TARS:    ${DIM}./run_tars.sh${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some validation tests failed. See above for details.${NC}"
    echo ""
    exit 1
fi
