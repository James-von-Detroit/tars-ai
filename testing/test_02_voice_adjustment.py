#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit

"""
Test 02: Prosody Correction for Natural Intonation

Rationale: AI voices often sound "weird" or detached due to flat prosody 
(pacing, emphasis). Adjustments in tools like Podcastle or Eleven Labs add 
emotional tuning, reported in voice AI forks to mimic Interstellar's dry humor.

This test demonstrates prosody adjustment using ElevenLabs VoiceSettings.
For Piper TTS (local), prosody is fixed by the model, but we can demonstrate
comparative A/B testing.

Usage:
    cd /home/runner/work/tars-ai/tars-ai
    python3 testing/test_02_voice_adjustment.py

Requirements:
    - gptars package installed
    - Piper TTS voice model (TARS.onnx)
    - Optional: elevenlabs package for cloud TTS comparison
"""

import os
import sys
import time
from pathlib import Path

import numpy as np
import sounddevice as sd

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Test configuration
TEST_TEXTS = [
    "Cooper, you son of a bitch. I knew you'd come back.",
    "My humor setting is currently at 75 percent. Would you like me to adjust it?",
    "Affirmative. Initiating docking sequence now.",
    "That's impossible. Or, as you humans would say, totally doable with the right attitude.",
]
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def prosody_adjusted_tts_elevenlabs(text, stability=0.5, clarity=0.8, 
                                     exaggeration=0.7, api_key=None):
    """
    Prosody-adjusted TTS using ElevenLabs VoiceSettings.
    
    Args:
        text: Text to synthesize
        stability: Lower = more emotional variation (0.0-1.0)
        clarity: Higher = clearer enunciation (0.0-1.0)
        exaggeration: Adds pitch/volume shifts (0.0-1.0)
        api_key: ElevenLabs API key
        
    Returns:
        tuple: (audio_bytes, sample_rate, metrics)
    """
    try:
        from elevenlabs import generate, VoiceSettings
    except ImportError:
        print("⚠️  elevenlabs not installed. Skipping ElevenLabs test.")
        print("   To install: pip install elevenlabs")
        return None, None, None
    
    api_key = api_key or os.getenv("ELEVEN_API_KEY")
    if not api_key:
        print("⚠️  No ElevenLabs API key found. Skipping ElevenLabs test.")
        print("   Set ELEVEN_API_KEY environment variable to test.")
        return None, None, None
    
    voice_settings = VoiceSettings(
        stability=stability,
        similarity_boost=clarity,
        style=exaggeration,
        use_speaker_boost=True
    )
    
    start = time.time()
    
    try:
        audio_bytes = generate(
            text=text,
            voice="Adam",  # Or custom TARS-trained voice
            model="eleven_turbo_v2",  # Faster model
            voice_settings=voice_settings,
            api_key=api_key
        )
        
        latency = time.time() - start
        
        metrics = {
            'latency': latency,
            'stability': stability,
            'clarity': clarity,
            'exaggeration': exaggeration
        }
        
        return audio_bytes, 22050, metrics
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None, None


def test_piper_baseline(text, voice_model_path):
    """
    Test Piper TTS (no prosody control, model-determined).
    
    Args:
        text: Text to synthesize
        voice_model_path: Path to Piper .onnx model
        
    Returns:
        tuple: (audio_data, sample_rate, metrics)
    """
    try:
        from piper.voice import PiperVoice
        import soundfile as sf
        import wave
        from io import BytesIO
    except ImportError:
        print("❌ Required packages not installed.")
        print("   Run: pip install piper-tts soundfile")
        return None, None, None
    
    if not voice_model_path.exists():
        print(f"❌ Voice model not found at {voice_model_path}")
        return None, None, None
    
    voice = PiperVoice.load(str(voice_model_path))
    sample_rate = voice.config.sample_rate
    
    start = time.time()
    
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        voice.synthesize_wav(text, wav_file)
    
    wav_buffer.seek(0)
    audio_data, _ = sf.read(wav_buffer)
    
    latency = time.time() - start
    
    metrics = {
        'latency': latency,
        'model': voice_model_path.name,
        'note': 'Piper prosody fixed by model training'
    }
    
    return audio_data, sample_rate, metrics


def play_audio_bytes(audio_bytes, label=""):
    """Play audio from bytes (MP3 format)."""
    if label:
        print(f"🔊 Playing: {label}")
    
    try:
        from pydub import AudioSegment
        from pydub.playback import play
        from io import BytesIO
        
        audio = AudioSegment.from_mp3(BytesIO(audio_bytes))
        play(audio)
    except ImportError:
        print("⚠️  pydub not installed for MP3 playback")
        print("   Audio saved to file for manual playback")
    except Exception as e:
        print(f"⚠️  Playback error: {e}")


def play_audio(audio, sample_rate, label=""):
    """Play audio from numpy array."""
    if label:
        print(f"🔊 Playing: {label}")
    sd.play(audio, sample_rate)
    sd.wait()


def score_naturalness(label):
    """Prompt user to score naturalness."""
    print(f"\nRate the naturalness of '{label}' (1-5):")
    print("  1 = Very robotic/unnatural")
    print("  2 = Somewhat robotic")
    print("  3 = Neutral/acceptable")
    print("  4 = Good/natural")
    print("  5 = Excellent/very natural")
    
    try:
        score = int(input("Score: ").strip())
        return max(1, min(5, score))  # Clamp to 1-5
    except (ValueError, EOFError):
        print("Using default score: 3")
        return 3


def main():
    """Run prosody correction tests."""
    print("\n" + "=" * 70)
    print("TEST 02: PROSODY CORRECTION FOR NATURAL INTONATION")
    print("=" * 70)
    print()
    print("This test compares different prosody settings to find the most")
    print("natural-sounding voice output for TARS.")
    print()
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Find Piper voice model
    voices_path = REPO_ROOT / "voices"
    tars_model = voices_path / "TARS.onnx"
    
    scores = {}
    
    # Test each phrase
    for i, text in enumerate(TEST_TEXTS, 1):
        print("-" * 70)
        print(f"TEST PHRASE {i}/{len(TEST_TEXTS)}")
        print("-" * 70)
        print(f'Text: "{text}"')
        print()
        
        # Test A: Piper baseline
        print("A) Piper TTS (Baseline - Model Defaults)")
        print()
        
        if tars_model.exists():
            audio, sr, metrics = test_piper_baseline(text, tars_model)
            if audio is not None:
                print(f"   Latency: {metrics['latency']:.2f}s")
                print(f"   Note: {metrics['note']}")
                play_audio(audio, sr, "Piper Baseline")
                scores[f"phrase{i}_piper"] = score_naturalness("Piper Baseline")
        else:
            print(f"   ⚠️  TARS model not found at {tars_model}")
        
        print()
        
        # Test B: ElevenLabs with default settings
        print("B) ElevenLabs (Default Settings)")
        print("   stability=0.5, clarity=0.8, exaggeration=0.7")
        print()
        
        audio_bytes, sr, metrics = prosody_adjusted_tts_elevenlabs(
            text, stability=0.5, clarity=0.8, exaggeration=0.7
        )
        
        if audio_bytes is not None:
            print(f"   Latency: {metrics['latency']:.2f}s")
            output_path = OUTPUT_DIR / f"test_02_phrase{i}_default.mp3"
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            print(f"   💾 Saved to: {output_path}")
            play_audio_bytes(audio_bytes, "ElevenLabs Default")
            scores[f"phrase{i}_eleven_default"] = score_naturalness("ElevenLabs Default")
        
        print()
        
        # Test C: ElevenLabs with TARS personality (more robotic wit)
        print("C) ElevenLabs (TARS Personality - Dry Humor)")
        print("   stability=0.3, clarity=0.9, exaggeration=0.5")
        print()
        
        audio_bytes, sr, metrics = prosody_adjusted_tts_elevenlabs(
            text, stability=0.3, clarity=0.9, exaggeration=0.5
        )
        
        if audio_bytes is not None:
            print(f"   Latency: {metrics['latency']:.2f}s")
            output_path = OUTPUT_DIR / f"test_02_phrase{i}_tars.mp3"
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            print(f"   💾 Saved to: {output_path}")
            play_audio_bytes(audio_bytes, "ElevenLabs TARS")
            scores[f"phrase{i}_eleven_tars"] = score_naturalness("ElevenLabs TARS")
        
        print()
        
        # Test D: ElevenLabs with high emotional variation
        print("D) ElevenLabs (High Emotional Variation)")
        print("   stability=0.2, clarity=0.7, exaggeration=0.9")
        print()
        
        audio_bytes, sr, metrics = prosody_adjusted_tts_elevenlabs(
            text, stability=0.2, clarity=0.7, exaggeration=0.9
        )
        
        if audio_bytes is not None:
            print(f"   Latency: {metrics['latency']:.2f}s")
            output_path = OUTPUT_DIR / f"test_02_phrase{i}_emotional.mp3"
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            print(f"   💾 Saved to: {output_path}")
            play_audio_bytes(audio_bytes, "ElevenLabs Emotional")
            scores[f"phrase{i}_eleven_emotional"] = score_naturalness("ElevenLabs Emotional")
        
        print("\n")
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    if scores:
        print("Naturalness Scores (1-5):")
        print()
        
        # Average by method
        piper_scores = [s for k, s in scores.items() if 'piper' in k]
        eleven_default_scores = [s for k, s in scores.items() if 'default' in k]
        eleven_tars_scores = [s for k, s in scores.items() if 'tars' in k]
        eleven_emotional_scores = [s for k, s in scores.items() if 'emotional' in k]
        
        if piper_scores:
            avg = sum(piper_scores) / len(piper_scores)
            print(f"  Piper Baseline:          {avg:.1f}/5.0")
        
        if eleven_default_scores:
            avg = sum(eleven_default_scores) / len(eleven_default_scores)
            print(f"  ElevenLabs Default:      {avg:.1f}/5.0")
        
        if eleven_tars_scores:
            avg = sum(eleven_tars_scores) / len(eleven_tars_scores)
            print(f"  ElevenLabs TARS:         {avg:.1f}/5.0")
        
        if eleven_emotional_scores:
            avg = sum(eleven_emotional_scores) / len(eleven_emotional_scores)
            print(f"  ElevenLabs Emotional:    {avg:.1f}/5.0")
        
        print()
    
    print("Recommendations:")
    print("  - For Piper: Prosody is determined by model training")
    print("    Consider retraining TARS.onnx with better prosody samples")
    print("  - For ElevenLabs: Adjust stability/clarity/exaggeration iteratively")
    print("    TARS personality works well with: stability=0.3, clarity=0.9")
    print()
    print("Output files saved in:", OUTPUT_DIR)
    print()


if __name__ == "__main__":
    main()
