#!/bin/bash
# SPDX-License-Identifier: CC-BY-NC-4.0
# Copyright (c) TARS-AI Community
# Licensed under Creative Commons Attribution-NonCommercial 4.0 International
#
# Original source: https://github.com/TARS-AI-Community/TARS-AI
# This file may not be used for commercial purposes.

# Atomikspace
# email: olivierdion1@hotmail.com

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/tars-ai.desktop"
LAUNCHER_SCRIPT="$SCRIPT_DIR/lp.sh"

mkdir -p "$AUTOSTART_DIR"

if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    rm -f "$LAUNCHER_SCRIPT"
    echo " TARS-AI removed from autostart"
    echo " The program will no longer start automatically on boot"
else
    # Create the launcher script
    cat > "$LAUNCHER_SCRIPT" << 'LAUNCHER_EOF'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sleep 8

if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
fi

export DISPLAY=:0

lxterminal --working-directory="$SCRIPT_DIR" --command="bash -c 'python3 App-Start.py; exec bash'" &

echo "TARS-AI launched at $(date)" >> "$SCRIPT_DIR/autostart.log"
LAUNCHER_EOF

    chmod +x "$LAUNCHER_SCRIPT"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=TARS-AI
Comment=Start TARS-AI on boot with proper environment
Exec=$LAUNCHER_SCRIPT
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF
    
    echo " TARS-AI added to autostart"
    echo " The program will start automatically on next boot"
    echo " A terminal window will open showing the TARS-AI interface"
fi
