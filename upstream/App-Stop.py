# SPDX-License-Identifier: CC-BY-NC-4.0
# Copyright (c) TARS-AI Community
# Licensed under Creative Commons Attribution-NonCommercial 4.0 International
#
# Original source: https://github.com/TARS-AI-Community/TARS-AI
# This file may not be used for commercial purposes.

import os
import subprocess

def stop_tars_ai():
    # Ensure DISPLAY is set for GUI applications
    display = os.getenv("DISPLAY", ":0")
    
    command = (
        f"killall xterm"
    )
    
    subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    stop_tars_ai()