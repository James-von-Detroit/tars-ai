# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit

"""
Voice Adjustment Test Suite for TARS-AI

This package contains four test scripts designed to diagnose and improve
voice quality issues in the TARS-AI fork.

Tests:
- test_01_voice_adjustment.py: Latency reduction via chunked TTS
- test_02_voice_adjustment.py: Prosody correction for natural intonation
- test_03_voice_adjustment.py: VAD/interruption handling
- test_04_voice_adjustment.py: Distortion/noise reduction

See README.md for detailed documentation.
"""

__version__ = "1.0.0"
__all__ = [
    "test_01_voice_adjustment",
    "test_02_voice_adjustment",
    "test_03_voice_adjustment",
    "test_04_voice_adjustment",
]
