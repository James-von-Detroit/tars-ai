#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit

"""
Test 01: Latency Reduction via Chunked TTS Synthesis

Rationale: High latency (e.g., 500ms+ delays in web-called TTS) makes voice feel 
"off" or unresponsive, common in robot AIs like TARS. Forks of similar projects 
(e.g., voice-enabled LLMs) fix this by pre-buffering or parallelizing synthesis.

This test demonstrates chunked synthesis with threading to reduce perceived latency.

Usage:
    cd /home/runner/work/tars-ai/tars-ai
    python3 testing/test_01_voice_adjustment.py

Requirements:
    - gptars package installed
    - Piper TTS voice model (TARS.onnx)
    - Optional: elevenlabs package for cloud TTS comparison
"""

import os
import sys
import time
import re
import wave
import threading
from io import BytesIO
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Test configuration
TEST_TEXT = "This is TARS reporting. Mission status nominal. All systems are functioning within acceptable parameters."
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def chunked_tts_piper(text, voice_model_path, chunk_size=50):
    """
    Chunked TTS synthesis using Piper (local, offline).
    
    Args:
        text: Text to synthesize
        voice_model_path: Path to Piper .onnx voice model
        chunk_size: Number of characters per chunk
        
    Returns:
        tuple: (audio_data, sample_rate, latency)
    """
    try:
        from piper.voice import PiperVoice
    except ImportError:
        print("❌ piper-tts not installed. Run: pip install piper-tts")
        return None, None, None
    
    if not voice_model_path.exists():
        print(f"❌ Voice model not found at {voice_model_path}")
        return None, None, None
    
    print(f"Loading Piper voice: {voice_model_path.name}")
    voice = PiperVoice.load(str(voice_model_path))
    sample_rate = voice.config.sample_rate
    
    # Split text into chunks
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    print(f"Split text into {len(chunks)} chunks of ~{chunk_size} characters")
    
    audio_chunks = []
    audio_lock = threading.Lock()
    
    def synthesize_chunk(idx, chunk):
        """Thread worker to synthesize a single chunk."""
        wav_buffer = BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            voice.synthesize_wav(chunk.strip(), wav_file)
        
        wav_buffer.seek(0)
        audio_chunk, _ = sf.read(wav_buffer)
        
        with audio_lock:
            audio_chunks.append((idx, audio_chunk))
    
    # Start timer
    start = time.time()
    
    # Create threads for parallel synthesis
    threads = []
    for idx, chunk in enumerate(chunks):
        t = threading.Thread(target=synthesize_chunk, args=(idx, chunk))
        t.start()
        threads.append(t)
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Sort chunks by original order and concatenate
    audio_chunks.sort(key=lambda x: x[0])
    full_audio = np.concatenate([chunk for _, chunk in audio_chunks])
    
    latency = time.time() - start
    
    print(f"✓ Synthesized in {latency:.2f}s (parallel chunked)")
    print(f"  Audio duration: {len(full_audio)/sample_rate:.2f}s")
    
    return full_audio, sample_rate, latency


def baseline_tts_piper(text, voice_model_path):
    """
    Baseline TTS synthesis using Piper (sentence-based, like gptars voice_engine).
    
    Args:
        text: Text to synthesize
        voice_model_path: Path to Piper .onnx voice model
        
    Returns:
        tuple: (audio_data, sample_rate, latency)
    """
    try:
        from piper.voice import PiperVoice
    except ImportError:
        print("❌ piper-tts not installed. Run: pip install piper-tts")
        return None, None, None
    
    if not voice_model_path.exists():
        print(f"❌ Voice model not found at {voice_model_path}")
        return None, None, None
    
    print(f"Loading Piper voice: {voice_model_path.name}")
    voice = PiperVoice.load(str(voice_model_path))
    sample_rate = voice.config.sample_rate
    
    # Start timer
    start = time.time()
    
    # Split at sentence boundaries (upstream approach)
    chunks = re.split(r'(?<=\.)\s', text)
    all_audio = []
    
    for chunk in chunks:
        if chunk.strip():
            wav_buffer = BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                voice.synthesize_wav(chunk.strip(), wav_file)
            
            wav_buffer.seek(0)
            audio_chunk, _ = sf.read(wav_buffer)
            all_audio.append(audio_chunk)
    
    audio = np.concatenate(all_audio)
    latency = time.time() - start
    
    print(f"✓ Synthesized in {latency:.2f}s (baseline sequential)")
    print(f"  Audio duration: {len(audio)/sample_rate:.2f}s")
    
    return audio, sample_rate, latency


def chunked_tts_elevenlabs(text, voice_id="21m00Tcm4TlvDq8ikWAM", api_key=None):
    """
    Chunked TTS synthesis using ElevenLabs (cloud API, requires key).
    
    Args:
        text: Text to synthesize
        voice_id: ElevenLabs voice ID
        api_key: ElevenLabs API key (or set ELEVEN_API_KEY env var)
        
    Returns:
        tuple: (audio_data, sample_rate, latency)
    """
    try:
        from elevenlabs import generate, Voice
    except ImportError:
        print("⚠️  elevenlabs not installed. Skipping ElevenLabs test.")
        print("   To install: pip install elevenlabs")
        return None, None, None
    
    api_key = api_key or os.getenv("ELEVEN_API_KEY")
    if not api_key:
        print("⚠️  No ElevenLabs API key found. Skipping ElevenLabs test.")
        print("   Set ELEVEN_API_KEY environment variable to test.")
        return None, None, None
    
    print(f"Using ElevenLabs voice: {voice_id}")
    
    # Split into short chunks
    chunks = [text[i:i+50] for i in range(0, len(text), 50)]
    print(f"Split text into {len(chunks)} chunks of ~50 characters")
    
    audio_bytes_list = []
    audio_lock = threading.Lock()
    
    def synthesize_chunk(idx, chunk):
        """Thread worker to synthesize a single chunk."""
        try:
            audio_bytes = generate(
                text=chunk,
                voice=voice_id,
                model="eleven_multilingual_v2",
                api_key=api_key
            )
            with audio_lock:
                audio_bytes_list.append((idx, audio_bytes))
        except Exception as e:
            print(f"❌ Error synthesizing chunk {idx}: {e}")
    
    # Start timer
    start = time.time()
    
    # Create threads for parallel synthesis
    threads = []
    for idx, chunk in enumerate(chunks):
        t = threading.Thread(target=synthesize_chunk, args=(idx, chunk))
        t.start()
        threads.append(t)
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    if not audio_bytes_list:
        print("❌ No audio generated")
        return None, None, None
    
    # Sort chunks by original order and concatenate
    audio_bytes_list.sort(key=lambda x: x[0])
    full_audio_bytes = b"".join([chunk for _, chunk in audio_bytes_list])
    
    latency = time.time() - start
    
    # Convert to numpy array (ElevenLabs returns MP3)
    # For simplicity, we'll just return the bytes and latency
    print(f"✓ Synthesized in {latency:.2f}s (ElevenLabs parallel chunked)")
    
    return full_audio_bytes, 22050, latency  # ElevenLabs default is 22050 Hz


def save_audio(audio, sample_rate, filename):
    """Save audio to WAV file."""
    output_path = OUTPUT_DIR / filename
    sf.write(output_path, audio, sample_rate)
    print(f"💾 Saved to: {output_path}")
    return output_path


def play_audio(audio, sample_rate, label=""):
    """Play audio through speakers."""
    if label:
        print(f"🔊 Playing: {label}")
    sd.play(audio, sample_rate)
    sd.wait()


def main():
    """Run latency reduction tests."""
    print("\n" + "=" * 70)
    print("TEST 01: LATENCY REDUCTION VIA CHUNKED TTS SYNTHESIS")
    print("=" * 70)
    print()
    print(f"Test text: \"{TEST_TEXT}\"")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Find Piper voice model
    voices_path = REPO_ROOT / "voices"
    tars_model = voices_path / "TARS.onnx"
    
    if not tars_model.exists():
        print(f"❌ TARS voice model not found at {tars_model}")
        print("   Please ensure the voices/ directory contains TARS.onnx")
        sys.exit(1)
    
    # Test 1: Baseline (sequential sentence-based)
    print("-" * 70)
    print("TEST 1A: BASELINE (Sequential Sentence-Based)")
    print("-" * 70)
    baseline_audio, baseline_sr, baseline_latency = baseline_tts_piper(
        TEST_TEXT, tars_model
    )
    
    if baseline_audio is not None:
        save_audio(baseline_audio, baseline_sr, "test_01_baseline.wav")
        print()
        play_audio(baseline_audio, baseline_sr, "Baseline")
    
    print("\n")
    
    # Test 2: Chunked (parallel character-based)
    print("-" * 70)
    print("TEST 1B: CHUNKED (Parallel Character-Based)")
    print("-" * 70)
    chunked_audio, chunked_sr, chunked_latency = chunked_tts_piper(
        TEST_TEXT, tars_model, chunk_size=50
    )
    
    if chunked_audio is not None:
        save_audio(chunked_audio, chunked_sr, "test_01_chunked.wav")
        print()
        play_audio(chunked_audio, chunked_sr, "Chunked")
    
    print("\n")
    
    # Test 3: ElevenLabs (optional, if API key available)
    print("-" * 70)
    print("TEST 1C: ELEVENLABS (Cloud API, Optional)")
    print("-" * 70)
    elevenlabs_audio, elevenlabs_sr, elevenlabs_latency = chunked_tts_elevenlabs(
        TEST_TEXT
    )
    
    if elevenlabs_audio is not None and isinstance(elevenlabs_audio, np.ndarray):
        save_audio(elevenlabs_audio, elevenlabs_sr, "test_01_elevenlabs.wav")
        print()
        play_audio(elevenlabs_audio, elevenlabs_sr, "ElevenLabs")
    elif elevenlabs_audio is not None:
        # Save bytes directly
        output_path = OUTPUT_DIR / "test_01_elevenlabs.mp3"
        with open(output_path, 'wb') as f:
            f.write(elevenlabs_audio)
        print(f"💾 Saved to: {output_path}")
    
    print("\n")
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if baseline_latency and chunked_latency:
        improvement = baseline_latency - chunked_latency
        improvement_pct = (improvement / baseline_latency) * 100
        
        print(f"Baseline latency:  {baseline_latency:.2f}s")
        print(f"Chunked latency:   {chunked_latency:.2f}s")
        
        if improvement > 0:
            print(f"Improvement:       {improvement:.2f}s ({improvement_pct:.1f}% faster)")
        else:
            print(f"Note: Chunked was {abs(improvement):.2f}s slower (threading overhead)")
            print("      Parallel synthesis works best for longer texts or slower models")
        
        if elevenlabs_latency:
            print(f"ElevenLabs latency: {elevenlabs_latency:.2f}s")
    
    print()
    print("Target: <1s end-to-end synthesis for conversational response")
    print()
    print("Output files saved in:", OUTPUT_DIR)
    print()


if __name__ == "__main__":
    main()
