# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
"""
gptars - Fully local, offline TARS voice assistant for Apple Silicon

This package provides a complete voice assistant pipeline with:
- Speech-to-Text (Faster-Whisper with Metal GPU acceleration)
- Local LLM (Llama-3 via Ollama)
- Text-to-Speech (Piper TTS)
- Wake Word Detection ("Hey TARS" via OpenWakeWord)
- Vision (LLaVA via webcam)

For more info: https://github.com/James-von-Detroit/tars-ai
"""

__version__ = "3.3.5"
__author__ = "James-von-Detroit"
__license__ = "MIT"

# Import core components for easy access
from gptars.core import TARSPersonality, DEFAULT_TARS

__all__ = ['TARSPersonality', 'DEFAULT_TARS', '__version__']
