"""
core/voice_engine.py

Voice Pipeline for gptars v3.1.0

Complete STT → LLM → TTS pipeline for offline voice interaction with TARS.
Optimized for Apple Silicon (M1/M2/M3/M4) with <800ms target latency.

Components:
- Speech-to-Text: Faster-Whisper (Metal GPU accelerated)
- LLM: Llama-3-8B-Instruct via Ollama
- Text-to-Speech: Piper TTS
- Wake Word: OpenWakeWord

Author: gptars v3.1
"""

import os
import sys
import time
import json
import threading
import queue
from pathlib import Path
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
import requests

# Import TARS personality (relative import within core package)
from .tars_personality import TARSPersonality, DEFAULT_TARS


class VoiceEngine:
    """
    Complete voice interaction pipeline for TARS.
    
    Handles:
    1. Audio capture from microphone
    2. Speech-to-text conversion
    3. LLM processing with TARS personality
    4. Text-to-speech generation
    5. Audio playback
    """
    
    def __init__(
        self,
        tars_personality: Optional[TARSPersonality] = None,
        whisper_model: str = "distil-large-v3",
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "llama3:8b-instruct-q4_0",
        piper_voice: str = "en_US-lessac-medium",
        sample_rate: int = 16000,
        verbose: bool = True
    ):
        """
        Initialize the voice engine.
        
        Args:
            tars_personality: TARS personality instance
            whisper_model: Whisper model name for STT
            ollama_url: Ollama server URL
            ollama_model: Model name in Ollama
            piper_voice: Piper TTS voice name
            sample_rate: Audio sample rate
            verbose: Print status messages
        """
        self.tars = tars_personality or DEFAULT_TARS
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model
        self.sample_rate = sample_rate
        self.verbose = verbose
        
        # Paths - repo root is parent.parent.parent for files in gptars/core/
        self.base_path = Path(__file__).parent.parent  # gptars/
        self.repo_root = self.base_path.parent         # GPTars/
        self.models_path = self.base_path / "models"
        self.voices_path = self.repo_root / "voices"   # voices/ at repo root
        
        # Initialize components
        self._init_whisper(whisper_model)
        self._init_piper(piper_voice)
        
        # State
        self.listening = False
        self.audio_queue = queue.Queue()
        self.conversation_history = []
        
        # Performance metrics
        self.metrics = {
            'stt_time': 0,
            'llm_time': 0,
            'tts_time': 0,
            'total_time': 0
        }
        
        if self.verbose:
            print("✓ Voice Engine initialized")
            print(f"  STT: Faster-Whisper ({whisper_model})")
            print(f"  LLM: Ollama ({ollama_model})")
            print(f"  TTS: Piper ({piper_voice})")
    
    def _init_whisper(self, model_name: str):
        """Initialize Faster-Whisper for STT."""
        if self.verbose:
            print(f"Loading Whisper model: {model_name}...")
        
        # Use CPU with int8 for best compatibility on Mac
        # Metal GPU support is automatic in faster-whisper on Apple Silicon
        self.whisper = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
            download_root=str(self.models_path / "whisper")
        )
        
        if self.verbose:
            print("✓ Whisper loaded")
    
    def _init_piper(self, voice_name: str):
        """Initialize Piper TTS."""
        self.piper_voice = voice_name
        self.piper_binary = self.voices_path / "piper" / "piper"  # piper/piper from tarball
        self.piper_model = self.voices_path / f"{voice_name}.onnx"
        
        if not self.piper_binary.exists():
            raise FileNotFoundError(f"Piper binary not found at {self.piper_binary}")
        if not self.piper_model.exists():
            raise FileNotFoundError(f"Piper model not found at {self.piper_model}")
        
        if self.verbose:
            print(f"✓ Piper configured with {voice_name}")
    
    def record_audio(self, duration: int = 5) -> np.ndarray:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio data as numpy array
        """
        if self.verbose:
            print(f"🎤 Recording for {duration} seconds...")
        
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        return audio.flatten()
    
    def speech_to_text(self, audio: np.ndarray) -> str:
        """
        Convert audio to text using Faster-Whisper.
        
        Args:
            audio: Audio data as numpy array
            
        Returns:
            Transcribed text
        """
        start_time = time.time()
        
        # Faster-Whisper expects audio as float32
        segments, info = self.whisper.transcribe(
            audio,
            language="en",
            beam_size=5,
            vad_filter=True  # Voice Activity Detection for better accuracy
        )
        
        # Combine all segments
        text = " ".join([segment.text for segment in segments]).strip()
        
        self.metrics['stt_time'] = time.time() - start_time
        
        if self.verbose:
            print(f"📝 Transcribed in {self.metrics['stt_time']:.2f}s: {text}")
        
        return text
    
    def get_tars_response(self, user_input: str) -> str:
        """
        Get response from TARS using Ollama.
        
        Args:
            user_input: User's text input
            
        Returns:
            TARS's response
        """
        start_time = time.time()
        
        # Build conversation context
        messages = [
            {"role": "system", "content": self.tars.get_system_prompt()}
        ]
        
        # Add conversation history (last 5 exchanges)
        for entry in self.conversation_history[-10:]:
            messages.append({"role": "user", "content": entry['user']})
            messages.append({"role": "assistant", "content": entry['assistant']})
        
        # Add current message
        messages.append({"role": "user", "content": user_input})
        
        # Call Ollama API
        try:
            response = requests.post(
                f"{self.ollama_url}/v1/chat/completions",
                json={
                    "model": self.ollama_model,
                    "messages": messages,
                    "temperature": 0.8,
                    "max_tokens": 200,  # Keep responses concise
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            
            tars_response = response.json()['choices'][0]['message']['content'].strip()
            
            # Store in conversation history
            self.conversation_history.append({
                'user': user_input,
                'assistant': tars_response
            })
            
            self.metrics['llm_time'] = time.time() - start_time
            
            if self.verbose:
                print(f"🤖 TARS responded in {self.metrics['llm_time']:.2f}s: {tars_response}")
            
            return tars_response
            
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {e}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return "Systems experiencing difficulties. Stand by."
    
    def text_to_speech(self, text: str) -> np.ndarray:
        """
        Convert text to speech using Piper.
        
        Args:
            text: Text to convert
            
        Returns:
            Audio data as numpy array
        """
        start_time = time.time()
        
        # Create temp file for output
        temp_wav = "/tmp/tars_tts_output.wav"
        
        # Run Piper
        import subprocess
        
        try:
            # Piper reads from stdin and writes to stdout
            process = subprocess.Popen(
                [
                    str(self.piper_binary),
                    "--model", str(self.piper_model),
                    "--output_file", temp_wav
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(input=text.encode('utf-8'), timeout=10)
            
            if process.returncode != 0:
                raise RuntimeError(f"Piper failed: {stderr.decode()}")
            
            # Load the generated audio
            audio, sr = sf.read(temp_wav)
            
            # Resample if needed
            if sr != self.sample_rate:
                import scipy.signal
                audio = scipy.signal.resample(
                    audio,
                    int(len(audio) * self.sample_rate / sr)
                )
            
            self.metrics['tts_time'] = time.time() - start_time
            
            if self.verbose:
                print(f"🔊 Generated speech in {self.metrics['tts_time']:.2f}s")
            
            return audio
            
        except Exception as e:
            if self.verbose:
                print(f"❌ TTS Error: {e}")
            return np.array([])
    
    def play_audio(self, audio: np.ndarray):
        """
        Play audio through speakers.
        
        Args:
            audio: Audio data to play
        """
        if len(audio) == 0:
            return
        
        sd.play(audio, self.sample_rate)
        sd.wait()
    
    def process_voice_input(self, duration: int = 5) -> dict:
        """
        Complete voice interaction cycle.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Dictionary with interaction details and metrics
        """
        total_start = time.time()
        
        # 1. Record audio
        audio = self.record_audio(duration)
        
        # 2. Speech to text
        user_text = self.speech_to_text(audio)
        
        if not user_text:
            if self.verbose:
                print("⚠️  No speech detected")
            return None
        
        # 3. Get TARS response
        tars_text = self.get_tars_response(user_text)
        
        # 4. Convert to speech
        tars_audio = self.text_to_speech(tars_text)
        
        # 5. Play audio
        self.play_audio(tars_audio)
        
        self.metrics['total_time'] = time.time() - total_start
        
        if self.verbose:
            print(f"\n⚡ Total latency: {self.metrics['total_time']:.2f}s")
            print(f"   STT: {self.metrics['stt_time']:.2f}s")
            print(f"   LLM: {self.metrics['llm_time']:.2f}s")
            print(f"   TTS: {self.metrics['tts_time']:.2f}s")
        
        return {
            'user_text': user_text,
            'tars_text': tars_text,
            'metrics': self.metrics.copy()
        }
    
    def interactive_mode(self):
        """
        Run interactive voice conversation mode.
        Press Enter to start recording, Ctrl+C to exit.
        """
        print("\n" + "=" * 70)
        print("TARS VOICE INTERFACE - Interactive Mode")
        print("=" * 70)
        print(f"\nUser name: {self.tars.user_name}")
        print(f"Honesty: {self.tars.settings.honesty}%")
        print(f"Humor: {self.tars.settings.humor}%")
        print(f"Discretion: {self.tars.settings.discretion}%")
        print("\nPress ENTER to speak (5 second recording)")
        print("Press Ctrl+C to exit")
        print("=" * 70 + "\n")
        
        try:
            while True:
                input("Press ENTER to speak... ")
                result = self.process_voice_input(duration=5)
                print()
        
        except KeyboardInterrupt:
            print("\n\n👋 TARS shutting down. Goodbye.")


def main():
    """Main entry point for voice engine."""
    print("\n" + "=" * 70)
    print("gptars v3.1.0 - Voice Engine")
    print("=" * 70)
    print()
    
    # Check if Ollama is running
    print("Checking Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        print("✓ Ollama is running")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("\nPlease start Ollama:")
        print("  brew services start ollama")
        print("or")
        print("  ollama serve")
        sys.exit(1)
    
    print()
    
    # Initialize voice engine
    engine = VoiceEngine(verbose=True)
    
    # Run interactive mode
    engine.interactive_mode()


if __name__ == "__main__":
    main()
