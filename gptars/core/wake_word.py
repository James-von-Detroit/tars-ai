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
    Supports conversation sessions that stay active until timeout.
    """
    
    def __init__(
        self,
        voice_engine,
        wake_word: str = "hey_jarvis",
        threshold: float = 0.5,
        conversation_timeout: float = 120.0,  # 2 minutes default
        verbose: bool = True
    ):
        """
        Initialize TARS wake word listener.
        
        Args:
            voice_engine: VoiceEngine instance to activate on detection
            wake_word: Wake word model name
            threshold: Detection threshold
            conversation_timeout: Seconds of silence before ending conversation
            verbose: Print status messages
        """
        self.voice_engine = voice_engine
        self.verbose = verbose
        self.conversation_timeout = conversation_timeout
        
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
        self.in_conversation = False
        self.last_interaction_time = 0
    
    def on_wake_word_detected(self):
        """Handle wake word detection - start a conversation session."""
        if self.processing:
            if self.verbose:
                print("⚠️  Already processing, ignoring detection")
            return
        
        self.processing = True
        self.in_conversation = True
        self.last_interaction_time = time.time()
        
        try:
            if self.verbose:
                print("\n" + "=" * 50)
                print("🤖 TARS ACTIVATED - Conversation Started")
                print(f"   (Will timeout after {self.conversation_timeout}s of silence)")
                print("=" * 50)
            
            # Start conversation loop
            self._conversation_loop()
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Error in conversation: {e}")
        
        finally:
            self.processing = False
            self.in_conversation = False
            if self.verbose:
                print("\n👂 Conversation ended. Say 'Hey TARS' to start again...\n")
    
    def _conversation_loop(self):
        """
        Run a continuous conversation until timeout.
        
        Listens for speech, processes it, responds, and keeps listening
        until conversation_timeout seconds of silence.
        """
        import numpy as np
        import sounddevice as sd
        
        sample_rate = self.voice_engine.sample_rate
        chunk_duration = 0.5  # 500ms chunks
        chunk_samples = int(chunk_duration * sample_rate)
        silence_threshold = 0.01
        min_speech_duration = 0.5
        max_silence_duration = 2.0  # Stop recording after 2s silence
        
        while self.in_conversation:
            # Check for conversation timeout
            if time.time() - self.last_interaction_time > self.conversation_timeout:
                if self.verbose:
                    print(f"\n⏱️  Conversation timeout ({self.conversation_timeout}s)")
                break
            
            if self.verbose:
                remaining = int(self.conversation_timeout - (time.time() - self.last_interaction_time))
                print(f"\n🎤 Listening... (conversation active, {remaining}s until timeout)")
            
            # Listen for speech
            audio_buffer = []
            speech_started = False
            silence_chunks = 0
            speech_chunks = 0
            max_silence_chunks = int(max_silence_duration / chunk_duration)
            min_speech_chunks = int(min_speech_duration / chunk_duration)
            
            # Give user time to start speaking (up to timeout)
            initial_silence_start = time.time()
            
            while self.in_conversation:
                # Check conversation timeout during listening
                if time.time() - self.last_interaction_time > self.conversation_timeout:
                    if not speech_started:
                        return  # Timeout, end conversation
                
                # Record a chunk
                chunk = sd.rec(chunk_samples, samplerate=sample_rate, 
                               channels=1, dtype='float32')
                sd.wait()
                chunk = chunk.flatten()
                
                # Check for speech
                has_speech = self.voice_engine._detect_speech_energy(chunk, silence_threshold)
                
                if has_speech:
                    if not speech_started:
                        if self.verbose:
                            print("🎙️  Speech detected, recording...")
                        speech_started = True
                    speech_chunks += 1
                    silence_chunks = 0
                    audio_buffer.append(chunk)
                elif speech_started:
                    silence_chunks += 1
                    audio_buffer.append(chunk)
                    
                    if silence_chunks >= max_silence_chunks:
                        if speech_chunks >= min_speech_chunks:
                            break  # Process the audio
                        else:
                            # Too short, reset
                            audio_buffer = []
                            speech_started = False
                            silence_chunks = 0
                            speech_chunks = 0
            
            # Process if we have audio
            if audio_buffer and self.in_conversation:
                audio = np.concatenate(audio_buffer)
                
                if self.verbose:
                    print(f"📝 Processing {len(audio)/sample_rate:.1f}s of audio...")
                
                # Speech to text
                user_text = self.voice_engine.speech_to_text(audio)
                
                if user_text:
                    # Update last interaction time
                    self.last_interaction_time = time.time()
                    
                    # Check for exit phrases
                    exit_phrases = ['goodbye', 'bye', 'stop', 'exit', 'quit', 'shut down', 'end conversation']
                    if any(phrase in user_text.lower() for phrase in exit_phrases):
                        if self.verbose:
                            print("👋 Exit phrase detected")
                        # Say goodbye
                        goodbye_text = self.voice_engine.get_tars_response("User said goodbye, give a brief farewell.")
                        goodbye_audio = self.voice_engine.text_to_speech(goodbye_text)
                        self.voice_engine.play_audio(goodbye_audio)
                        break
                    
                    # Get TARS response
                    tars_text = self.voice_engine.get_tars_response(user_text)
                    
                    # Convert to speech and play
                    tars_audio = self.voice_engine.text_to_speech(tars_text)
                    self.voice_engine.play_audio(tars_audio)
                    
                    # Update interaction time after response
                    self.last_interaction_time = time.time()
                    
                    if self.verbose:
                        latency = (self.voice_engine.metrics['stt_time'] + 
                                   self.voice_engine.metrics['llm_time'] + 
                                   self.voice_engine.metrics['tts_time'])
                        print(f"⚡ Response latency: {latency:.2f}s")
                else:
                    if self.verbose:
                        print("⚠️  No speech recognized")
    
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
        print("📢 Say 'Hey TARS' to start a conversation")
        print(f"   Conversation stays active for {int(self.conversation_timeout)}s after last speech")
        print("   Say 'goodbye' or 'stop' to end conversation early")
        print()
        print("Press Ctrl+C to exit")
        print("=" * 70)
        
        self.detector.start()


def main():
    """Main entry point for wake word detection testing."""
    print("\n" + "=" * 70)
    print("gptars v3.1.0 - Wake Word Detection")
    print("=" * 70)
    print()
    print("Select mode:")
    print("  1) Test wake word detection only (30 seconds)")
    print("  2) Full TARS with wake word + conversation mode")
    print()
    
    try:
        choice = input("Enter choice [1/2, default=2]: ").strip() or "2"
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Goodbye.")
        return
    
    if choice == "1":
        # Test detection only
        detector = WakeWordDetector(verbose=True)
        detector.test_detection(duration=30)
    else:
        # Full TARS with wake word
        from .voice_engine import VoiceEngine
        
        print("\nInitializing TARS...")
        engine = VoiceEngine(verbose=True)
        
        # Create listener with 2-minute conversation timeout
        listener = TARSWakeWordListener(
            engine, 
            threshold=0.5,
            conversation_timeout=120.0,  # 2 minutes
            verbose=True
        )
        
        listener.start()


if __name__ == "__main__":
    main()
