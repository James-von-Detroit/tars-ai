#!/bin/bash
# SPDX-License-Identifier: CC-BY-NC-4.0
# Copyright (c) TARS-AI Community
# Licensed under Creative Commons Attribution-NonCommercial 4.0 International
#
# Original source: https://github.com/TARS-AI-Community/TARS-AI
# This file may not be used for commercial purposes.


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sleep 1

if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
fi

export DISPLAY=:0

lxterminal --working-directory="$SCRIPT_DIR" --command="bash -c 'python3 App-Start.py; exec bash'" &

echo "TARS-AI launched at $(date)" >> "$SCRIPT_DIR/autostart.log"
