#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit

"""
Test 03: VAD/Interruption Handling for Responsive Dialogue

Rationale: Voice feels "off" if the AI interrupts or misses pauses, especially 
in noisy robot environments. Bi-directional streaming (inspired by Moshi/Kyutai) 
or VAD tweaks in voice forks prevent this by delaying response triggers.

This test demonstrates Voice Activity Detection (VAD) for proper pause detection.

Usage:
    cd /home/runner/work/tars-ai/tars-ai
    python3 testing/test_03_voice_adjustment.py

Requirements:
    - pyaudio or sounddevice
    - webrtcvad
    - gptars package installed
"""

import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Test configuration
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_FILE = OUTPUT_DIR / "test_03_log.txt"


def test_simple_vad(duration=30, silence_threshold=0.01, pause_duration=1.5):
    """
    Simple energy-based VAD test (no webrtcvad required).
    
    Args:
        duration: Test duration in seconds
        silence_threshold: RMS threshold for silence detection
        pause_duration: Seconds of silence to trigger response
    """
    import sounddevice as sd
    import numpy as np
    
    print("=" * 70)
    print("SIMPLE VAD TEST (Energy-Based)")
    print("=" * 70)
    print()
    print(f"Configuration:")
    print(f"  Silence threshold: {silence_threshold}")
    print(f"  Pause duration: {pause_duration}s")
    print(f"  Test duration: {duration}s")
    print()
    print("Instructions:")
    print("  1. Start speaking after 'Listening...' appears")
    print("  2. Pause for more than 1.5 seconds to trigger response")
    print("  3. Test will log all detected speech/silence events")
    print()
    print("🎤 Listening...")
    print()
    
    sample_rate = 16000
    chunk_duration = 0.5
    chunk_samples = int(chunk_duration * sample_rate)
    
    log_entries = []
    
    def detect_speech_energy(audio, threshold):
        """Simple energy-based speech detection."""
        energy = np.sqrt(np.mean(audio ** 2))
        return energy > threshold
    
    def log_event(event_type, message):
        """Log event with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = f"[{timestamp}] {event_type}: {message}"
        print(entry)
        log_entries.append(entry)
    
    speech_started = False
    silence_start = None
    speech_start = None
    response_count = 0
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            # Record a chunk
            chunk = sd.rec(chunk_samples, samplerate=sample_rate, 
                          channels=1, dtype='float32')
            sd.wait()
            chunk = chunk.flatten()
            
            # Check for speech
            has_speech = detect_speech_energy(chunk, silence_threshold)
            
            if has_speech:
                if not speech_started:
                    speech_start = time.time()
                    log_event("SPEECH_START", "Speech detected, recording...")
                    speech_started = True
                silence_start = None
            elif speech_started:
                if silence_start is None:
                    silence_start = time.time()
                    log_event("SILENCE_START", f"Silence detected after {time.time() - speech_start:.1f}s of speech")
                
                # Check if silence duration exceeds threshold
                silence_duration = time.time() - silence_start
                if silence_duration >= pause_duration:
                    speech_duration = silence_start - speech_start
                    response_count += 1
                    log_event("TRIGGER", f"User pause detected - would trigger TTS response #{response_count}")
                    log_event("INFO", f"Speech duration: {speech_duration:.1f}s, Silence duration: {silence_duration:.1f}s")
                    
                    # Reset
                    speech_started = False
                    silence_start = None
                    speech_start = None
                    
                    print()
                    log_event("STATUS", "Ready for next utterance...")
                    print()
    
    except KeyboardInterrupt:
        print("\n")
        log_event("INFO", "Test interrupted by user")
    
    # Save log
    with open(LOG_FILE, 'w') as f:
        f.write(f"Test 03: VAD/Interruption Handling Test\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Configuration: silence_threshold={silence_threshold}, pause_duration={pause_duration}s\n")
        f.write("\n")
        f.write("\n".join(log_entries))
        f.write("\n")
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total responses triggered: {response_count}")
    print(f"Log saved to: {LOG_FILE}")
    print()


def test_webrtc_vad(duration=30, vad_mode=2, pause_duration=1.5):
    """
    WebRTC VAD test (more accurate, requires webrtcvad).
    
    Args:
        duration: Test duration in seconds
        vad_mode: WebRTC VAD aggressiveness (0-3, higher = more aggressive)
        pause_duration: Seconds of silence to trigger response
    """
    try:
        import webrtcvad
    except ImportError:
        print("⚠️  webrtcvad not installed. Skipping WebRTC VAD test.")
        print("   To install: pip install webrtcvad")
        return
    
    try:
        import pyaudio
    except ImportError:
        print("⚠️  pyaudio not installed. Skipping WebRTC VAD test.")
        print("   To install: brew install portaudio && pip install pyaudio")
        return
    
    print("=" * 70)
    print("WEBRTC VAD TEST (Advanced)")
    print("=" * 70)
    print()
    print(f"Configuration:")
    print(f"  VAD mode: {vad_mode} (0=least aggressive, 3=most aggressive)")
    print(f"  Pause duration: {pause_duration}s")
    print(f"  Test duration: {duration}s")
    print()
    print("Instructions:")
    print("  1. Start speaking after 'Listening...' appears")
    print("  2. Pause for more than 1.5 seconds to trigger response")
    print("  3. Test will log all detected speech/silence events")
    print()
    print("🎤 Listening...")
    print()
    
    vad = webrtcvad.Vad(vad_mode)
    
    sample_rate = 16000
    frame_duration = 30  # ms (10, 20, or 30)
    frame_size = int(sample_rate * frame_duration / 1000)
    
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frame_size
    )
    
    log_entries = []
    
    def log_event(event_type, message):
        """Log event with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = f"[{timestamp}] {event_type}: {message}"
        print(entry)
        log_entries.append(entry)
    
    speech_started = False
    silence_start = None
    speech_start = None
    response_count = 0
    interruption_count = 0
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            # Read frame
            frame = stream.read(frame_size, exception_on_overflow=False)
            
            # VAD detection
            is_speech = vad.is_speech(frame, sample_rate)
            
            if is_speech:
                if not speech_started:
                    if silence_start is not None:
                        # User interrupted during silence
                        interruption_count += 1
                        log_event("INTERRUPT", f"User spoke during silence (interruption #{interruption_count})")
                    
                    speech_start = time.time()
                    log_event("SPEECH_START", "Speech detected, recording...")
                    speech_started = True
                silence_start = None
            elif speech_started:
                if silence_start is None:
                    silence_start = time.time()
                    log_event("SILENCE_START", f"Silence detected after {time.time() - speech_start:.1f}s of speech")
                
                # Check if silence duration exceeds threshold
                silence_duration = time.time() - silence_start
                if silence_duration >= pause_duration:
                    speech_duration = silence_start - speech_start
                    response_count += 1
                    log_event("TRIGGER", f"User pause detected - would trigger TTS response #{response_count}")
                    log_event("INFO", f"Speech duration: {speech_duration:.1f}s, Silence duration: {silence_duration:.1f}s")
                    
                    # Reset
                    speech_started = False
                    silence_start = None
                    speech_start = None
                    
                    print()
                    log_event("STATUS", "Ready for next utterance...")
                    print()
    
    except KeyboardInterrupt:
        print("\n")
        log_event("INFO", "Test interrupted by user")
    
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
    
    # Save log
    with open(LOG_FILE, 'a') as f:
        f.write(f"\n\n")
        f.write(f"WebRTC VAD Test\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Configuration: vad_mode={vad_mode}, pause_duration={pause_duration}s\n")
        f.write("\n")
        f.write("\n".join(log_entries))
        f.write("\n")
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total responses triggered: {response_count}")
    print(f"Total interruptions detected: {interruption_count}")
    print(f"Log saved to: {LOG_FILE}")
    print()


def test_integrated_vad(duration=30):
    """
    Test VAD integration with gptars voice engine.
    
    Args:
        duration: Test duration in seconds
    """
    try:
        from gptars.core.voice_engine import VoiceEngine
    except ImportError:
        print("⚠️  gptars not installed. Skipping integrated test.")
        return
    
    print("=" * 70)
    print("INTEGRATED VAD TEST (with gptars)")
    print("=" * 70)
    print()
    print("This test uses the gptars VoiceEngine's built-in VAD")
    print("for continuous listening mode.")
    print()
    print(f"Test duration: {duration}s")
    print()
    print("The engine will automatically detect speech and respond.")
    print("Press Ctrl+C to stop.")
    print()
    
    # Initialize voice engine
    engine = VoiceEngine(verbose=True)
    
    # Use threading to limit duration
    def stop_after_duration():
        time.sleep(duration)
        print("\n⏱️  Test duration reached")
        # Send interrupt signal
        import signal
        import os
        os.kill(os.getpid(), signal.SIGINT)
    
    timer_thread = threading.Thread(target=stop_after_duration, daemon=True)
    timer_thread.start()
    
    try:
        # Run continuous listening mode
        engine.continuous_listen_mode(
            silence_threshold=0.01,
            min_speech_duration=0.5,
            max_silence_duration=1.5,
            chunk_duration=0.5
        )
    except KeyboardInterrupt:
        print("\n✓ Test complete")


def main():
    """Run VAD/interruption handling tests."""
    print("\n" + "=" * 70)
    print("TEST 03: VAD/INTERRUPTION HANDLING FOR RESPONSIVE DIALOGUE")
    print("=" * 70)
    print()
    print("This test validates Voice Activity Detection (VAD) for proper")
    print("pause detection and interruption handling.")
    print()
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Mode selection
    print("Select test mode:")
    print("  1) Simple VAD (energy-based, no dependencies)")
    print("  2) WebRTC VAD (advanced, requires webrtcvad + pyaudio)")
    print("  3) Integrated VAD (with gptars voice engine)")
    print("  4) Run all tests")
    print()
    
    try:
        choice = input("Enter choice [1-4, default=1]: ").strip() or "1"
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Goodbye.")
        sys.exit(0)
    
    print()
    
    if choice == "1":
        test_simple_vad(duration=30)
    elif choice == "2":
        test_webrtc_vad(duration=30)
    elif choice == "3":
        test_integrated_vad(duration=30)
    elif choice == "4":
        test_simple_vad(duration=20)
        print("\n")
        test_webrtc_vad(duration=20)
        print("\n")
        print("Skipping integrated test (requires Ollama + full setup)")
    else:
        print("Invalid choice")
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()
    print("Based on VAD testing:")
    print("  - Use silence_threshold=0.01 for typical environments")
    print("  - Use pause_duration=1.5s for natural conversation flow")
    print("  - Adjust thresholds for noisy environments:")
    print("    * Higher silence_threshold (0.02-0.03) for noisy rooms")
    print("    * Lower pause_duration (1.0s) for faster response")
    print("  - WebRTC VAD mode 2-3 works best for robot environments")
    print()
    print("Interruption handling:")
    print("  - System should stop TTS playback if user interrupts")
    print("  - Implement voice activity monitoring during TTS playback")
    print("  - Target: 0 interruptions during user pauses")
    print()


if __name__ == "__main__":
    main()
