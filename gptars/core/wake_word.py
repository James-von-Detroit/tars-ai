# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# Part of GPTars v3.0 — 100% offline TARS voice assistant for macOS.
# https://github.com/James-von-Detroit/tars-ai

"""
core/wake_word.py

Wake Word Detection for gptars v3.1.0

Listens for "Hey TARS" wake word using OpenWakeWord (free, offline).
Optimized for Apple Silicon with low latency detection.

Author: gptars v3.1
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
from openwakeword.model import Model


class WakeWordDetector:
    """
    Wake word detection system for TARS.
    
    Listens continuously for "Hey TARS" (or custom wake phrase)
    and triggers callback when detected.
    """
    
    def __init__(
        self,
        wake_word: str = "hey_jarvis",  # Using hey_jarvis as base, sounds similar to "hey TARS"
        threshold: float = 0.5,
        sample_rate: int = 16000,
        chunk_size: int = 1280,  # 80ms at 16kHz
        verbose: bool = True
    ):
        """
        Initialize wake word detector.
        
        Args:
            wake_word: Wake word model name
            threshold: Detection threshold (0.0-1.0, higher = less sensitive)
            sample_rate: Audio sample rate (16000 Hz recommended)
            chunk_size: Audio chunk size in samples
            verbose: Print status messages
        """
        self.wake_word = wake_word
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.verbose = verbose
        
        # State
        self.running = False
        self.detection_callback = None
        self.audio_stream = None
        
        # Initialize OpenWakeWord model
        self._init_model()
        
        if self.verbose:
            print("✓ Wake Word Detector initialized")
            print(f"  Wake phrase: '{wake_word}' (threshold: {threshold})")
            print(f"  Sample rate: {sample_rate} Hz")
    
    def _init_model(self):
        """Initialize the wake word detection model."""
        if self.verbose:
            print(f"Loading wake word model: {self.wake_word}...")
        
        try:
            # Initialize model with specified wake word
            # OpenWakeWord will download the model if not present
            self.model = Model(
                wakeword_models=[self.wake_word],
                inference_framework='onnx'  # Use ONNX for better cross-platform support
            )
            
            if self.verbose:
                print("✓ Wake word model loaded")
                
        except Exception as e:
            print(f"❌ Error loading wake word model: {e}")
            print("\nTip: The model will be downloaded automatically on first run")
            raise
    
    def set_callback(self, callback: Callable):
        """
        Set callback function to be called when wake word is detected.
        
        Args:
            callback: Function to call (no arguments)
        """
        self.detection_callback = callback
    
    def process_audio(self, audio_chunk: np.ndarray) -> bool:
        """
        Process audio chunk and check for wake word.
        
        Args:
            audio_chunk: Audio data as numpy array (float32, mono, 16kHz)
            
        Returns:
            True if wake word detected
        """
        # Convert to int16 if needed (OpenWakeWord expects int16)
        if audio_chunk.dtype == np.float32:
            audio_chunk = (audio_chunk * 32767).astype(np.int16)
        
        # Get prediction
        prediction = self.model.predict(audio_chunk)
        
        # Check if wake word detected
        for wake_word_name, score in prediction.items():
            if score >= self.threshold:
                if self.verbose:
                    print(f"\n🎯 Wake word detected! (confidence: {score:.2f})")
                return True
        
        return False
    
    def audio_callback(self, indata, frames, time_info, status):
        """
        Callback for audio stream.
        
        Called by sounddevice for each audio chunk.
        """
        if status:
            if self.verbose:
                print(f"⚠️  Audio status: {status}")
        
        # Convert to mono if stereo
        if len(indata.shape) > 1:
            audio = indata[:, 0]
        else:
            audio = indata.flatten()
        
        # Process audio
        detected = self.process_audio(audio)
        
        if detected and self.detection_callback:
            # Call callback in separate thread to avoid blocking audio stream
            threading.Thread(target=self.detection_callback, daemon=True).start()
    
    def start(self):
        """Start listening for wake word."""
        if self.running:
            if self.verbose:
                print("⚠️  Already running")
            return
        
        self.running = True
        
        if self.verbose:
            print("\n👂 Listening for wake word...")
            print(f"   Say: 'Hey TARS' or similar to '{self.wake_word}'")
            print("   Press Ctrl+C to stop\n")
        
        try:
            # Open audio stream
            self.audio_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                blocksize=self.chunk_size,
                callback=self.audio_callback
            )
            
            self.audio_stream.start()
            
            # Keep running until stopped
            while self.running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            if self.verbose:
                print("\n\n👋 Stopping wake word detection...")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop listening for wake word."""
        self.running = False
        
        if self.audio_stream is not None:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
        
        if self.verbose:
            print("✓ Wake word detection stopped")
    
    def test_detection(self, duration: int = 10):
        """
        Test wake word detection for specified duration.
        
        Args:
            duration: Test duration in seconds
        """
        print(f"\n🧪 Testing wake word detection for {duration} seconds...")
        print(f"Say: 'Hey TARS' or similar phrase")
        
        detection_count = 0
        
        def test_callback():
            nonlocal detection_count
            detection_count += 1
            print(f"✓ Detection #{detection_count}")
        
        self.set_callback(test_callback)
        
        # Start detection
        self.running = True
        
        self.audio_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=self.chunk_size,
            callback=self.audio_callback
        )
        
        self.audio_stream.start()
        
        # Run for specified duration
        time.sleep(duration)
        
        # Stop
        self.stop()
        
        print(f"\n✓ Test complete: {detection_count} detections in {duration} seconds")


class TARSWakeWordListener:
    """
    Complete wake word listening system for TARS voice interface.
    
    Combines wake word detection with voice engine activation.
    """
    
    def __init__(
        self,
        voice_engine,
        wake_word: str = "hey_jarvis",
        threshold: float = 0.5,
        verbose: bool = True
    ):
        """
        Initialize TARS wake word listener.
        
        Args:
            voice_engine: VoiceEngine instance to activate on detection
            wake_word: Wake word model name
            threshold: Detection threshold
            verbose: Print status messages
        """
        self.voice_engine = voice_engine
        self.verbose = verbose
        
        # Initialize detector
        self.detector = WakeWordDetector(
            wake_word=wake_word,
            threshold=threshold,
            verbose=verbose
        )
        
        # Set callback
        self.detector.set_callback(self.on_wake_word_detected)
        
        # State
        self.processing = False
    
    def on_wake_word_detected(self):
        """Handle wake word detection."""
        if self.processing:
            if self.verbose:
                print("⚠️  Already processing, ignoring detection")
            return
        
        self.processing = True
        
        try:
            if self.verbose:
                print("\n" + "=" * 50)
                print("TARS ACTIVATED")
                print("=" * 50)
            
            # Process voice input
            self.voice_engine.process_voice_input(duration=5)
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Error processing voice: {e}")
        
        finally:
            self.processing = False
            if self.verbose:
                print("\n👂 Listening for wake word...\n")
    
    def start(self):
        """Start listening for wake word."""
        print("\n" + "=" * 70)
        print("TARS VOICE ASSISTANT - Always Listening Mode")
        print("=" * 70)
        print()
        print(f"User name: {self.voice_engine.tars.user_name}")
        print(f"Honesty: {self.voice_engine.tars.settings.honesty}%")
        print(f"Humor: {self.voice_engine.tars.settings.humor}%")
        print()
        print("Say 'Hey TARS' to activate")
        print("Press Ctrl+C to exit")
        print("=" * 70)
        
        self.detector.start()


def main():
    """Main entry point for wake word detection testing."""
    print("\n" + "=" * 70)
    print("gptars v3.1.0 - Wake Word Detection Test")
    print("=" * 70)
    print()
    
    # Initialize detector
    detector = WakeWordDetector(verbose=True)
    
    # Test for 30 seconds
    detector.test_detection(duration=30)


if __name__ == "__main__":
    main()
