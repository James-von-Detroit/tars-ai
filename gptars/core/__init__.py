# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
"""
gptars.core - Core modules for TARS voice assistant

Modules:
    voice_engine: Complete STT → LLM → TTS voice pipeline
    vision_engine: Camera-based vision with LLaVA
    wake_word: "Hey TARS" wake word detection
    tars_personality: TARS personality and response generation
"""

from .tars_personality import TARSPersonality, DEFAULT_TARS

__all__ = ['TARSPersonality', 'DEFAULT_TARS']
