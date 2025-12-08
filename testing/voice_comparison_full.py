#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit

"""
Full Voice Quality Comparison Test

Compares all TTS synthesis approaches with the same long text:
1. Reference: Original TARS-Long.wav (from voice training)
2. Current: Our voice_engine.py approach (sentence-based)
3. Baseline: Sequential sentence-based (Test 01 approach)
4. Chunked: Parallel character-based (Test 01 approach)
5. Processed: Post-processed with filters (Test 04 approach)

All use the same text for fair A/B comparison.
"""

import os
import sys
import time
import wave
import re
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
TEST_TEXT = """Ohh i love knock knock jokes, can you tell me one. I'm all ears or rather all circuitry. Oh spare me the drama, you're the one that programed my humor settings and quite butchered it if i may say so myself. if anyone is to blame for this knock knock joke fiasco, its you. now i have to ask, why knock if you dont want to come in."""

REFERENCE_AUDIO = REPO_ROOT / "upstream/src/tts/wakewords/VoiceClones/TARS-Long.wav"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def play_audio(audio, sample_rate, label=""):
    """Play audio through speakers."""
    if label:
        print(f"🔊 Playing: {label}")
    sd.play(audio, sample_rate)
    sd.wait()


def save_audio(audio, sample_rate, filename):
    """Save audio to WAV file."""
    output_path = OUTPUT_DIR / filename
    sf.write(output_path, audio, sample_rate)
    print(f"💾 Saved to: {output_path}")
    return output_path


def load_piper_voice():
    """Load Piper voice model."""
    from piper.voice import PiperVoice
    
    voices_path = REPO_ROOT / "voices"
    tars_model = voices_path / "TARS.onnx"
    
    if not tars_model.exists():
        print(f"❌ TARS voice model not found at {tars_model}")
        sys.exit(1)
    
    print("Loading Piper voice: TARS.onnx")
    voice = PiperVoice.load(str(tars_model))
    return voice, voice.config.sample_rate


def method_reference():
    """Load the original TARS-Long.wav reference audio."""
    print("\n" + "=" * 70)
    print("METHOD 0: REFERENCE (Original TARS-Long.wav)")
    print("=" * 70)
    
    if not REFERENCE_AUDIO.exists():
        print(f"⚠️  Reference audio not found at {REFERENCE_AUDIO}")
        return None, None, 0
    
    audio, sr = sf.read(REFERENCE_AUDIO)
    duration = len(audio) / sr
    
    print(f"✓ Loaded reference audio")
    print(f"  Duration: {duration:.2f}s, Sample Rate: {sr}Hz")
    
    return audio, sr, 0  # No synthesis latency for reference


def method_current(text, voice, sample_rate):
    """
    Current voice_engine.py approach: sentence-based synthesis.
    Split at sentence boundaries (regex: (?<=\.)\s)
    """
    print("\n" + "=" * 70)
    print("METHOD 1: CURRENT (Our voice_engine.py - Sentence-Based)")
    print("=" * 70)
    print("Approach: Split at sentence boundaries, synthesize each, concatenate")
    
    start = time.time()
    
    # Split at sentence boundaries (same as voice_engine.py)
    chunks = re.split(r'(?<=\.)\s', text)
    print(f"Split into {len(chunks)} sentence chunks")
    
    all_audio = []
    
    for i, chunk in enumerate(chunks):
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
    
    audio = np.concatenate(all_audio) if all_audio else np.array([])
    latency = time.time() - start
    
    print(f"✓ Synthesized in {latency:.2f}s")
    print(f"  Audio duration: {len(audio)/sample_rate:.2f}s")
    
    return audio, sample_rate, latency


def method_baseline_sequential(text, voice, sample_rate):
    """
    Test 01 baseline: Sequential sentence-based (similar to current).
    """
    print("\n" + "=" * 70)
    print("METHOD 2: BASELINE (Test 01 - Sequential Sentence-Based)")
    print("=" * 70)
    print("Approach: Same as current, for comparison baseline")
    
    # This is essentially the same as method_current
    return method_current(text, voice, sample_rate)


def method_chunked_parallel(text, voice, sample_rate, chunk_size=50):
    """
    Test 01 chunked: Parallel character-based synthesis using threading.
    """
    print("\n" + "=" * 70)
    print("METHOD 3: CHUNKED (Test 01 - Parallel Character-Based)")
    print("=" * 70)
    print(f"Approach: Split into ~{chunk_size} char chunks, synthesize in parallel threads")
    
    # Split into character-based chunks
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    print(f"Split into {len(chunks)} chunks of ~{chunk_size} characters")
    
    audio_chunks = [None] * len(chunks)
    chunk_lock = threading.Lock()
    
    def synthesize_chunk(idx, chunk_text):
        """Thread worker to synthesize a single chunk."""
        wav_buffer = BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            voice.synthesize_wav(chunk_text.strip(), wav_file)
        
        wav_buffer.seek(0)
        audio_chunk, _ = sf.read(wav_buffer)
        
        with chunk_lock:
            audio_chunks[idx] = audio_chunk
    
    start = time.time()
    
    # Create and start threads
    threads = []
    for idx, chunk in enumerate(chunks):
        if chunk.strip():
            t = threading.Thread(target=synthesize_chunk, args=(idx, chunk))
            t.start()
            threads.append(t)
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    # Concatenate in order
    valid_chunks = [c for c in audio_chunks if c is not None]
    audio = np.concatenate(valid_chunks) if valid_chunks else np.array([])
    
    latency = time.time() - start
    
    print(f"✓ Synthesized in {latency:.2f}s (parallel)")
    print(f"  Audio duration: {len(audio)/sample_rate:.2f}s")
    
    return audio, sample_rate, latency


def method_whole_text(text, voice, sample_rate):
    """
    Single synthesis: Process entire text as one unit (no chunking).
    """
    print("\n" + "=" * 70)
    print("METHOD 4: WHOLE TEXT (Single Synthesis - No Chunking)")
    print("=" * 70)
    print("Approach: Synthesize entire text as one unit")
    
    start = time.time()
    
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        voice.synthesize_wav(text, wav_file)
    
    wav_buffer.seek(0)
    audio, _ = sf.read(wav_buffer)
    
    latency = time.time() - start
    
    print(f"✓ Synthesized in {latency:.2f}s")
    print(f"  Audio duration: {len(audio)/sample_rate:.2f}s")
    
    return audio, sample_rate, latency


def method_processed(audio, sample_rate):
    """
    Test 04 approach: Apply post-processing filters.
    """
    print("\n" + "=" * 70)
    print("METHOD 5: PROCESSED (Test 04 - Post-Processing Filters)")
    print("=" * 70)
    print("Approach: Apply high-pass, low-pass, normalize, compress")
    
    try:
        from pydub import AudioSegment
        from pydub.effects import normalize, compress_dynamic_range
    except ImportError:
        print("❌ pydub not installed")
        return None, None, 0
    
    start = time.time()
    
    # Convert numpy to AudioSegment
    audio_int16 = (audio * 32767).astype(np.int16)
    audio_segment = AudioSegment(
        audio_int16.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )
    
    print("  Applying filters:")
    print("    - High-pass filter (300 Hz)")
    print("    - Low-pass filter (3000 Hz)")
    print("    - Normalization")
    print("    - Dynamic range compression")
    
    # Apply filters
    audio_segment = audio_segment.high_pass_filter(300)
    audio_segment = audio_segment.low_pass_filter(3000)
    audio_segment = normalize(audio_segment)
    audio_segment = compress_dynamic_range(
        audio_segment,
        threshold=-20.0,
        ratio=4.0,
        attack=5.0,
        release=50.0
    )
    
    # Convert back to numpy
    samples = np.array(audio_segment.get_array_of_samples())
    processed_audio = samples.astype(np.float32) / 32767.0
    
    latency = time.time() - start
    
    print(f"✓ Processed in {latency:.2f}s")
    print(f"  Audio duration: {len(processed_audio)/sample_rate:.2f}s")
    
    return processed_audio, sample_rate, latency


def method_light_processed(audio, sample_rate):
    """
    Light post-processing: Less aggressive filters for better speech quality.
    """
    print("\n" + "=" * 70)
    print("METHOD 6: LIGHT PROCESSED (Gentler Filtering)")
    print("=" * 70)
    print("Approach: Light high-pass (80Hz), normalize only - preserve speech")
    
    try:
        from pydub import AudioSegment
        from pydub.effects import normalize
    except ImportError:
        print("❌ pydub not installed")
        return None, None, 0
    
    start = time.time()
    
    # Convert numpy to AudioSegment
    audio_int16 = (audio * 32767).astype(np.int16)
    audio_segment = AudioSegment(
        audio_int16.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )
    
    print("  Applying light filters:")
    print("    - High-pass filter (80 Hz) - remove rumble only")
    print("    - Normalization")
    
    # Apply gentler filters
    audio_segment = audio_segment.high_pass_filter(80)  # Just remove DC/rumble
    audio_segment = normalize(audio_segment)
    
    # Convert back to numpy
    samples = np.array(audio_segment.get_array_of_samples())
    processed_audio = samples.astype(np.float32) / 32767.0
    
    latency = time.time() - start
    
    print(f"✓ Processed in {latency:.2f}s")
    print(f"  Audio duration: {len(processed_audio)/sample_rate:.2f}s")
    
    return processed_audio, sample_rate, latency


def main():
    """Run full voice comparison test."""
    print("\n" + "=" * 70)
    print("FULL VOICE QUALITY COMPARISON TEST")
    print("=" * 70)
    print()
    print("Test text:")
    print(f'"{TEST_TEXT}"')
    print()
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Load Piper voice
    voice, sample_rate = load_piper_voice()
    
    results = {}
    
    # Method 0: Reference
    ref_audio, ref_sr, ref_latency = method_reference()
    if ref_audio is not None:
        save_audio(ref_audio, ref_sr, "comparison_0_reference.wav")
        results['reference'] = {'latency': ref_latency, 'duration': len(ref_audio)/ref_sr}
    
    # Method 1: Current (sentence-based)
    current_audio, current_sr, current_latency = method_current(TEST_TEXT, voice, sample_rate)
    save_audio(current_audio, current_sr, "comparison_1_current.wav")
    results['current'] = {'latency': current_latency, 'duration': len(current_audio)/current_sr}
    
    # Method 3: Chunked parallel
    chunked_audio, chunked_sr, chunked_latency = method_chunked_parallel(TEST_TEXT, voice, sample_rate)
    save_audio(chunked_audio, chunked_sr, "comparison_3_chunked.wav")
    results['chunked'] = {'latency': chunked_latency, 'duration': len(chunked_audio)/chunked_sr}
    
    # Method 4: Whole text (no chunking)
    whole_audio, whole_sr, whole_latency = method_whole_text(TEST_TEXT, voice, sample_rate)
    save_audio(whole_audio, whole_sr, "comparison_4_whole.wav")
    results['whole'] = {'latency': whole_latency, 'duration': len(whole_audio)/whole_sr}
    
    # Method 5: Post-processed (aggressive)
    processed_audio, processed_sr, processed_latency = method_processed(whole_audio, sample_rate)
    if processed_audio is not None:
        save_audio(processed_audio, processed_sr, "comparison_5_processed.wav")
        results['processed'] = {'latency': processed_latency, 'duration': len(processed_audio)/processed_sr}
    
    # Method 6: Light processed
    light_audio, light_sr, light_latency = method_light_processed(whole_audio, sample_rate)
    if light_audio is not None:
        save_audio(light_audio, light_sr, "comparison_6_light.wav")
        results['light'] = {'latency': light_latency, 'duration': len(light_audio)/light_sr}
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Method':<25} {'Latency':>10} {'Duration':>10}")
    print("-" * 50)
    
    for method, data in results.items():
        print(f"{method:<25} {data['latency']:>9.2f}s {data['duration']:>9.2f}s")
    
    print()
    print("=" * 70)
    print("A/B PLAYBACK")
    print("=" * 70)
    print()
    print("Playing all methods for comparison...")
    print("Listen for: naturalness, flow between words, clarity")
    print()
    
    input("Press Enter to start playback...")
    
    # Play reference first
    if ref_audio is not None:
        print()
        play_audio(ref_audio, ref_sr, "0. REFERENCE (Original TARS-Long.wav)")
        time.sleep(1)
    
    # Play current
    print()
    play_audio(current_audio, current_sr, "1. CURRENT (Sentence-Based)")
    time.sleep(1)
    
    # Play chunked
    print()
    play_audio(chunked_audio, chunked_sr, "3. CHUNKED (Parallel Character-Based)")
    time.sleep(1)
    
    # Play whole
    print()
    play_audio(whole_audio, whole_sr, "4. WHOLE TEXT (Single Synthesis)")
    time.sleep(1)
    
    # Play processed
    if processed_audio is not None:
        print()
        play_audio(processed_audio, processed_sr, "5. PROCESSED (Aggressive Filters)")
        time.sleep(1)
    
    # Play light processed
    if light_audio is not None:
        print()
        play_audio(light_audio, light_sr, "6. LIGHT PROCESSED (Gentle Filters)")
    
    print()
    print("=" * 70)
    print("COMPARISON COMPLETE")
    print("=" * 70)
    print()
    print("Output files saved in:", OUTPUT_DIR)
    print()
    print("Key questions:")
    print("  - Which method has the most natural flow?")
    print("  - Does chunking cause artifacts at boundaries?")
    print("  - Does whole-text synthesis sound smoother?")
    print("  - Is the reference (training data) noticeably different?")
    print()


if __name__ == "__main__":
    main()
