#!/usr/bin/env bash
################################################################################
# add_license_headers.sh — Automatically add SPDX license headers to source files
#
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# Usage:
#   ./add_license_headers.sh [--dry-run]
#
# Options:
#   --dry-run    Show what would be changed without modifying files
#
# Safe to run multiple times — skips files that already have headers.
################################################################################

set -uo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# Change to repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Counters
MIT_ADDED=0
CCBYNC_ADDED=0
SKIPPED=0

# =============================================================================
# License Headers
# =============================================================================

MIT_HEADER_PY='# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# Part of GPTars v3.0 — 100% offline TARS voice assistant for macOS.
# https://github.com/James-von-Detroit/tars-ai
'

MIT_HEADER_SH='# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# Part of GPTars v3.0 — 100% offline TARS voice assistant for macOS.
# https://github.com/James-von-Detroit/tars-ai
'

MIT_HEADER_SCPT='(* SPDX-License-Identifier: MIT *)
(* Copyright (c) 2024–2025 James-von-Detroit *)
(* Part of GPTars v3.0 — https://github.com/James-von-Detroit/tars-ai *)
'

CCBYNC_HEADER_PY='# SPDX-License-Identifier: CC-BY-NC-4.0
# Copyright (c) TARS-AI Community
# Licensed under Creative Commons Attribution-NonCommercial 4.0 International
#
# Original source: https://github.com/TARS-AI-Community/TARS-AI
# This file may not be used for commercial purposes.
'

CCBYNC_HEADER_SH='# SPDX-License-Identifier: CC-BY-NC-4.0
# Copyright (c) TARS-AI Community
# Licensed under Creative Commons Attribution-NonCommercial 4.0 International
#
# Original source: https://github.com/TARS-AI-Community/TARS-AI
# This file may not be used for commercial purposes.
'

# =============================================================================
# Functions
# =============================================================================

has_license_header() {
    local file="$1"
    # Check for SPDX identifier or common license patterns
    head -20 "$file" 2>/dev/null | grep -qiE "(SPDX-License-Identifier|MIT License|CC-BY-NC|Copyright \(c\))" && return 0
    return 1
}

add_header_to_file() {
    local file="$1"
    local header="$2"
    local license_type="$3"
    
    if has_license_header "$file"; then
        ((SKIPPED++))
        echo -e "  ${DIM}SKIP${NC} $file ${DIM}(already has header)${NC}"
        return 0
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "  ${CYAN}WOULD ADD${NC} [$license_type] $file"
    else
        # Handle shebang lines
        local first_line
        first_line=$(head -1 "$file")
        
        if [[ "$first_line" == "#!"* ]]; then
            # Keep shebang, add header after
            local rest
            rest=$(tail -n +2 "$file")
            echo "$first_line" > "$file.tmp"
            echo "$header" >> "$file.tmp"
            echo "$rest" >> "$file.tmp"
        else
            # No shebang, prepend header
            echo "$header" > "$file.tmp"
            cat "$file" >> "$file.tmp"
        fi
        
        mv "$file.tmp" "$file"
        echo -e "  ${GREEN}ADDED${NC} [$license_type] $file"
    fi
    
    if [[ "$license_type" == "MIT" ]]; then
        ((MIT_ADDED++))
    else
        ((CCBYNC_ADDED++))
    fi
}

# =============================================================================
# Main
# =============================================================================

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  License Header Tool — GPTars Repository${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}DRY RUN MODE — No files will be modified${NC}"
    echo ""
fi

# ─────────────────────────────────────────────────────────────────────────────
# Process gptars/ directory (MIT)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${GREEN}Processing gptars/ (MIT License)${NC}"

# Python files
while IFS= read -r -d '' file; do
    add_header_to_file "$file" "$MIT_HEADER_PY" "MIT"
done < <(find gptars -name "*.py" -type f -print0 2>/dev/null)

# Shell scripts
while IFS= read -r -d '' file; do
    add_header_to_file "$file" "$MIT_HEADER_SH" "MIT"
done < <(find gptars -name "*.sh" -type f -print0 2>/dev/null)

# AppleScript files
while IFS= read -r -d '' file; do
    add_header_to_file "$file" "$MIT_HEADER_SCPT" "MIT"
done < <(find gptars -name "*.scpt" -type f -print0 2>/dev/null)

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Process upstream/ directory (CC-BY-NC 4.0)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}Processing upstream/ (CC-BY-NC 4.0)${NC}"

# Python files
while IFS= read -r -d '' file; do
    add_header_to_file "$file" "$CCBYNC_HEADER_PY" "CC-BY-NC-4.0"
done < <(find upstream -name "*.py" -type f -print0 2>/dev/null)

# Shell scripts
while IFS= read -r -d '' file; do
    add_header_to_file "$file" "$CCBYNC_HEADER_SH" "CC-BY-NC-4.0"
done < <(find upstream -name "*.sh" -type f -print0 2>/dev/null)

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Process shared/ directory (CC-BY-NC 4.0)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}Processing shared/ (CC-BY-NC 4.0)${NC}"

# Python files (if any)
while IFS= read -r -d '' file; do
    add_header_to_file "$file" "$CCBYNC_HEADER_PY" "CC-BY-NC-4.0"
done < <(find shared -name "*.py" -type f -print0 2>/dev/null)

# Shell scripts (if any)
while IFS= read -r -d '' file; do
    add_header_to_file "$file" "$CCBYNC_HEADER_SH" "CC-BY-NC-4.0"
done < <(find shared -name "*.sh" -type f -print0 2>/dev/null)

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Summary${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}MIT headers added:${NC}        $MIT_ADDED"
echo -e "  ${YELLOW}CC-BY-NC headers added:${NC}  $CCBYNC_ADDED"
echo -e "  ${DIM}Skipped (existing):${NC}      $SKIPPED"
echo ""

if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}This was a dry run. Run without --dry-run to apply changes.${NC}"
else
    echo -e "${GREEN}✓ License headers applied successfully!${NC}"
fi
echo ""
