#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# TTS Test Script for TARS Voice

"""
TTS Test Script for GPTars

Simple comparison of original TARS audio vs Piper TTS output.

Usage:
    python -m gptars.tests.tts_comparison
"""

import os
import re
import time
import wave
from io import BytesIO
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
VOICES_PATH = REPO_ROOT / "voices"
UPSTREAM_SAMPLES = REPO_ROOT / "upstream" / "src" / "tts" / "wakewords" / "VoiceClones"

# Test text
TEST_TEXT = "Cooper, we are aligned and ready for docking. My humor setting is currently at 75 percent."


def play_audio(audio_data, sample_rate, label=""):
    """Play audio and wait for completion."""
    if label:
        print(f"  Playing: {label}")
    sd.play(audio_data, sample_rate)
    sd.wait()


def test_original_sample():
    """Play the original TARS voice sample for reference."""
    print("\n" + "=" * 60)
    print("ORIGINAL TARS VOICE SAMPLE (Reference)")
    print("=" * 60)
    
    sample_path = UPSTREAM_SAMPLES / "TARS-Long.wav"
    if not sample_path.exists():
        print(f"❌ Original sample not found at {sample_path}")
        return None, None
    
    audio, sr = sf.read(sample_path)
    duration = len(audio) / sr
    print(f"File: {sample_path.name}")
    print(f"Duration: {duration:.2f}s at {sr}Hz")
    print()
    
    # Play first 10 seconds
    play_audio(audio[:int(sr * 10)], sr, "Original TARS (first 10s)")
    return audio, sr


def test_piper_tts():
    """Test Piper TTS with upstream defaults."""
    print("\n" + "=" * 60)
    print("PIPER TTS (Upstream Defaults)")
    print("=" * 60)
    
    try:
        from piper.voice import PiperVoice
    except ImportError:
        print("❌ piper-tts not installed. Run: pip install piper-tts")
        return None, None
    
    model_path = VOICES_PATH / "TARS.onnx"
    if not model_path.exists():
        print(f"❌ TARS voice model not found at {model_path}")
        return None, None
    
    print(f"Model: {model_path.name}")
    
    voice = PiperVoice.load(str(model_path))
    sr = voice.config.sample_rate
    
    print(f"Sample rate: {sr}Hz")
    print(f"Text: \"{TEST_TEXT}\"")
    print()
    
    start_time = time.time()
    
    # Exact upstream approach: split at sentence boundaries
    chunks = re.split(r'(?<=\.)\s', TEST_TEXT)
    all_audio = []
    
    for chunk in chunks:
        if chunk.strip():
            wav_buffer = BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sr)
                voice.synthesize_wav(chunk.strip(), wav_file)
            
            wav_buffer.seek(0)
            audio_chunk, _ = sf.read(wav_buffer)
            all_audio.append(audio_chunk)
    
    audio = np.concatenate(all_audio)
    elapsed = time.time() - start_time
    
    print(f"Generated in {elapsed:.2f}s")
    print(f"Duration: {len(audio)/sr:.2f}s at {sr}Hz")
    print()
    
    play_audio(audio, sr, "Piper TTS")
    return audio, sr


def main():
    """Run TTS comparison tests."""
    print("\n" + "=" * 60)
    print("GPTars TTS TEST")
    print("=" * 60)
    print()
    print("Compare original TARS voice vs Piper TTS output.")
    print("Note: Piper voice quality depends on the TARS.onnx model training.")
    print()
    
    # 1. Original sample
    input("Press ENTER to play ORIGINAL TARS sample...")
    test_original_sample()
    
    time.sleep(0.5)
    
    # 2. Piper TTS
    input("\nPress ENTER to test PIPER TTS...")
    test_piper_tts()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("The Piper TTS uses the TARS.onnx model from the upstream project.")
    print("Voice quality is limited by how well that model was trained.")
    print()
    print("For better voice cloning, options include:")
    print("  - Retrain TARS.onnx with more/better audio samples")
    print("  - Use a commercial TTS like ElevenLabs (requires API key)")
    print("  - The upstream project also supports Azure TTS")
    print()


if __name__ == "__main__":
    main()
