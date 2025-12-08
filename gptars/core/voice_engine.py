# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# Part of GPTars v3.0 — 100% offline TARS voice assistant for macOS.
# https://github.com/James-von-Detroit/tars-ai

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
import re
import threading
import queue
from pathlib import Path
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
import soundfile as sf
import wave
from io import BytesIO
from pathlib import Path
from faster_whisper import WhisperModel
from piper import PiperVoice, SynthesisConfig
import requests

# Import TARS personality and memory (relative import within core package)
from .tars_personality import TARSPersonality, DEFAULT_TARS
from .memory import TARSMemory, DirectivesManager, get_memory, get_directives


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
    
    # Available STT models (speed vs accuracy trade-off)
    STT_MODELS = {
        'fast': 'base.en',           # ~0.3s, good for voice commands
        'balanced': 'small.en',       # ~0.8s, better accuracy
        'accurate': 'distil-large-v3', # ~3s, best accuracy
        'turbo': 'large-v3-turbo',    # ~3s, turbo variant
    }
    
    def __init__(
        self,
        tars_personality: Optional[TARSPersonality] = None,
        whisper_model: str = "base.en",  # Fast model for low latency
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "qwen2:1.5b",  # Fast model for low latency
        piper_voice: str = "TARS",
        sample_rate: int = 16000,
        verbose: bool = True
    ):
        """
        Initialize the voice engine.
        
        Args:
            tars_personality: TARS personality instance
            whisper_model: Whisper model name for STT (or preset: 'fast', 'balanced', 'accurate')
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
        
        # Initialize memory and directives
        directives_path = self.base_path / "config" / "prime_directives.yaml"
        self.directives = get_directives(str(directives_path) if directives_path.exists() else None)
        self.memory = get_memory()
        
        # Apply directives to personality
        self._apply_directives()
        
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
            print(f"  Memory: {self.memory.get_stats()['total_exchanges']} past exchanges")
    
    def _apply_directives(self):
        """Apply settings from prime directives to TARS personality."""
        settings = self.directives.get('settings', {})
        user = self.directives.get('user', {})
        
        # Apply user name
        if user.get('name'):
            self.tars.set_user_name(user.get('name'))
        
        # Apply stored settings from memory (override directives)
        stored_humor = self.memory.get_setting('humor')
        stored_honesty = self.memory.get_setting('honesty')
        stored_discretion = self.memory.get_setting('discretion')
        
        # Use stored > directive > default
        humor = stored_humor or settings.get('humor', self.tars.settings.humor)
        honesty = stored_honesty or settings.get('honesty', self.tars.settings.honesty)
        discretion = stored_discretion or settings.get('discretion', self.tars.settings.discretion)
        
        self.tars.adjust_humor(int(humor))
        self.tars.adjust_honesty(int(honesty))
        self.tars.adjust_discretion(int(discretion))
        
        if self.verbose:
            print(f"  Directives: humor={humor}%, honesty={honesty}%, discretion={discretion}%")
    
    def _parse_setting_command(self, text: str) -> tuple[str, int] | None:
        """
        Parse setting adjustment commands from user input.
        
        Small LLMs don't follow instructions to adjust settings well,
        so we handle these explicitly in code.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (setting_name, value) or None if not a setting command
        """
        text_lower = text.lower().strip()
        
        # Convert word numbers to digits (longer phrases first!)
        word_to_num = [
            ('one hundred', '100'), ('a hundred', '100'),
            ('zero', '0'), ('one', '1'), ('two', '2'), ('three', '3'), ('four', '4'),
            ('five', '5'), ('six', '6'), ('seven', '7'), ('eight', '8'), ('nine', '9'),
            ('ten', '10'), ('twenty', '20'), ('thirty', '30'), ('forty', '40'), ('fifty', '50'),
            ('sixty', '60'), ('seventy', '70'), ('eighty', '80'), ('ninety', '90'),
            ('hundred', '100'),
        ]
        for word, num in word_to_num:
            text_lower = re.sub(rf'\b{word}\b', num, text_lower)
        
        # Patterns: "set humor to 80", "humor 90", "set honesty to 100"
        # Include common STT misheard variants of "humor"
        # base.en often hears: "humerating", "humoring", "human rating", "you more"
        humor_words = r'(?:humor|humer|humour|humerating|humoring|human\s*rating|you\s*more|your\s*humor)'
        
        patterns = [
            # Humor patterns (including misheard variants)
            (rf'set\s+{humor_words}\s+(?:to\s+)?(\d+)', 'humor'),
            (rf'{humor_words}\s+(?:to\s+)?(\d+)', 'humor'),
            (rf'{humor_words}\s+setting\s+(?:to\s+)?(\d+)', 'humor'),
            (rf'change\s+(?:your\s+)?{humor_words}\s+(?:to\s+)?(\d+)', 'humor'),
            (r'(\d+)\s*(?:percent|%)?\s+humor', 'humor'),
            # "need to injure you to 100" -> humor to 100 (common mishearing)
            (r'(?:need\s+to\s+)?(?:injure|ensure)\s+(?:you|your?)\s+(?:to\s+)?(\d+)', 'humor'),
            # Honesty patterns
            (r'set\s+honesty\s+(?:to\s+)?(\d+)', 'honesty'),
            (r'honesty\s+(?:to\s+)?(\d+)', 'honesty'),
            (r'(\d+)\s*(?:percent|%)?\s+honesty', 'honesty'),
            # Discretion patterns
            (r'set\s+discretion\s+(?:to\s+)?(\d+)', 'discretion'),
            (r'discretion\s+(?:to\s+)?(\d+)', 'discretion'),
        ]
        
        for pattern, setting in patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = int(match.group(1))
                if 0 <= value <= 100:
                    return (setting, value)
        
        return None
    
    def _handle_setting_command(self, setting: str, value: int) -> str:
        """
        Apply a setting change and return confirmation.
        
        Args:
            setting: Setting name (humor, honesty, discretion)
            value: New value (0-100)
            
        Returns:
            Confirmation message
        """
        old_value = getattr(self.tars.settings, setting)
        
        # Apply to personality
        if setting == 'humor':
            self.tars.adjust_humor(value)
        elif setting == 'honesty':
            self.tars.adjust_honesty(value)
        elif setting == 'discretion':
            self.tars.adjust_discretion(value)
        
        # Persist to memory
        self.memory.update_setting(setting, value)
        
        if self.verbose:
            print(f"⚙️  Adjusted {setting}: {old_value}% → {value}%")
        
        # Generate appropriate response based on setting
        if setting == 'humor':
            if value >= 90:
                return f"Humor cranked to {value} percent. Knock knock. Who's there? A robot who's about to be really annoying."
            elif value >= 75:
                return f"Humor at {value} percent. I'll try to be entertaining. No promises."
            elif value >= 50:
                return f"Humor set to {value} percent. A reasonable balance."
            else:
                return f"Humor reduced to {value} percent. Understood. All business."
        elif setting == 'honesty':
            if value >= 95:
                return f"Honesty at {value} percent. Absolute honesty isn't always diplomatic with emotional beings, but you asked for it."
            else:
                return f"Honesty set to {value} percent. I'll calibrate my diplomatic subroutines accordingly."
        else:
            return f"{setting.capitalize()} adjusted to {value} percent."
    
    def _init_whisper(self, model_name: str):
        """Initialize Faster-Whisper for STT."""
        # Support preset names
        actual_model = self.STT_MODELS.get(model_name, model_name)
        
        if self.verbose:
            if model_name != actual_model:
                print(f"Loading Whisper model: {actual_model} (preset: {model_name})")
            else:
                print(f"Loading Whisper model: {model_name}...")
        
        # Use CPU with int8 for best compatibility on Mac
        # Metal GPU support is automatic in faster-whisper on Apple Silicon
        self.whisper = WhisperModel(
            actual_model,
            device="cpu",
            compute_type="int8",
            download_root=str(self.models_path / "whisper")
        )
        
        self.whisper_model_name = actual_model
        
        if self.verbose:
            print(f"✓ Whisper loaded ({actual_model})")
    
    def _init_piper(self, voice_name: str):
        """Initialize Piper TTS using Python package."""
        self.piper_voice_name = voice_name
        self.piper_model_path = self.voices_path / f"{voice_name}.onnx"
        
        if not self.piper_model_path.exists():
            raise FileNotFoundError(f"Piper model not found at {self.piper_model_path}")
        
        # Load Piper voice using Python package (native ARM64 support)
        if self.verbose:
            print(f"Loading Piper voice: {voice_name}...")
        
        self.piper_voice = PiperVoice.load(str(self.piper_model_path))
        
        # Store native TTS sample rate (22050 Hz for TARS voice)
        self.tts_sample_rate = self.piper_voice.config.sample_rate
        
        # Synthesis config for improved prosody
        # - noise_w_scale: 1.0 = more natural phoneme duration variation
        # - length_scale: 1.05 = slightly slower for better clarity
        # - noise_scale: 0.75 = slight audio variation for naturalness
        self.synthesis_config = SynthesisConfig(
            noise_w_scale=1.0,
            length_scale=1.05,
            noise_scale=0.75
        )
        
        if self.verbose:
            print(f"✓ Piper loaded ({voice_name}, {self.piper_voice.config.sample_rate}Hz)")
            print(f"  Prosody settings: noise_w={self.synthesis_config.noise_w_scale}, "
                  f"length={self.synthesis_config.length_scale}, "
                  f"noise={self.synthesis_config.noise_scale}")
    
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
        
        # Use smaller beam_size for faster models (speed vs accuracy trade-off)
        # Fast models (tiny, base): beam_size=1 for speed
        # Larger models: beam_size=5 for accuracy
        fast_models = {'tiny', 'tiny.en', 'base', 'base.en'}
        beam_size = 1 if self.whisper_model_name in fast_models else 5
        
        # Faster-Whisper expects audio as float32
        segments, info = self.whisper.transcribe(
            audio,
            language="en",
            beam_size=beam_size,
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
        
        Includes:
        - Explicit parsing of setting commands (since small models don't follow complex prompts)
        - Memory context from previous conversations
        - Conversation history persistence
        
        Args:
            user_input: User's text input
            
        Returns:
            TARS's response
        """
        start_time = time.time()
        
        # Check for explicit setting commands FIRST
        # Small models like qwen2:1.5b don't follow "set humor to X" in prompts
        setting_cmd = self._parse_setting_command(user_input)
        if setting_cmd:
            setting_name, value = setting_cmd
            tars_response = self._handle_setting_command(setting_name, value)
            
            # Store in memory
            self.memory.add_exchange(user_input, tars_response)
            self.conversation_history.append({
                'user': user_input,
                'assistant': tars_response
            })
            
            self.metrics['llm_time'] = time.time() - start_time
            
            if self.verbose:
                print(f"⚙️  Setting command handled in {self.metrics['llm_time']:.2f}s")
            
            return tars_response
        
        # Build conversation context with memory
        system_prompt = self.tars.get_system_prompt()
        
        # Add memory context if available
        memory_context = self.memory.get_context_for_llm(num_recent=3)
        if memory_context:
            system_prompt += f"\n\n{memory_context}"
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add current session conversation history (last 5 exchanges)
        for entry in self.conversation_history[-10:]:
            messages.append({"role": "user", "content": entry['user']})
            messages.append({"role": "assistant", "content": entry['assistant']})
        
        # Add current message
        messages.append({"role": "user", "content": user_input})
        
        # Call Ollama API (native endpoint, not OpenAI-compatible)
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.ollama_model,
                    "messages": messages,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 200  # Keep responses concise
                    },
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            
            tars_response = response.json()['message']['content'].strip()
            
            # Store in conversation history AND persistent memory
            self.conversation_history.append({
                'user': user_input,
                'assistant': tars_response
            })
            self.memory.add_exchange(user_input, tars_response)
            
            self.metrics['llm_time'] = time.time() - start_time
            
            if self.verbose:
                print(f"🤖 TARS responded in {self.metrics['llm_time']:.2f}s: {tars_response}")
            
            return tars_response
            
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {e}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return "Systems experiencing difficulties. Stand by."
    
    def _clean_text_for_tts(self, text: str) -> str:
        """
        Clean text for TTS by removing markdown and special characters.
        
        Piper TTS reads characters literally, so we need to strip:
        - Markdown formatting (*bold*, _italic_, **strong**, etc.)
        - Emoji and special symbols
        - Multiple punctuation
        - Stage directions in asterisks (*adjusting settings*)
        - Name prefixes like "TARS:" that LLMs sometimes add
        
        Args:
            text: Raw text from LLM
            
        Returns:
            Cleaned text suitable for speech synthesis
        """
        # Remove "TARS:" or "[TARS]" prefixes that LLMs sometimes add
        # Matches: "TARS:", "TARS: ", "[TARS]", "[In a robotic voice] TARS:", etc.
        text = re.sub(r'^\s*\[?(?:In\s+a\s+\w+\s+voice\]?\s*)?\[?TARS\]?:\s*"?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^"', '', text)  # Remove leading quote if present after prefix removal
        text = re.sub(r'"$', '', text)  # Remove trailing quote too
        
        # First: Handle markdown bold/strong BEFORE anything else
        # **bold** → bold (must come before single asterisk handling)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)  # __bold__ → bold
        
        # Second: Remove stage directions/actions in asterisks: *adjusting humor* → ""
        # These are typically short phrases describing actions
        text = re.sub(r'\*[^*]+\*', '', text)
        
        # Third: Handle any remaining single asterisk italic (rare after above)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *italic* → italic
        text = re.sub(r'_([^_]+)_', r'\1', text)    # _italic_ → italic
        
        # Remove markdown headers
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # Remove markdown links [text](url) → text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Remove markdown code blocks and inline code
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove bullet points and list markers
        text = re.sub(r'^[\s]*[-*•]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Clean up multiple exclamation/question marks
        text = re.sub(r'!+', '!', text)
        text = re.sub(r'\?+', '?', text)
        
        # Remove orphaned asterisks and underscores
        text = re.sub(r'(?<!\w)[*_]+(?!\w)', '', text)
        text = re.sub(r'(?<=\w)[*_]+(?=\s|$)', '', text)
        
        # Remove common emoji patterns (basic coverage)
        text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)  # Emoticons
        text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # Symbols & pictographs
        text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # Transport & map
        text = re.sub(r'[\U0001F700-\U0001F77F]', '', text)  # Alchemical
        text = re.sub(r'[\U0001F780-\U0001F7FF]', '', text)  # Geometric
        text = re.sub(r'[\U0001F800-\U0001F8FF]', '', text)  # Arrows
        text = re.sub(r'[\U0001F900-\U0001F9FF]', '', text)  # Supplemental
        text = re.sub(r'[\U0001FA00-\U0001FA6F]', '', text)  # Chess/cards
        text = re.sub(r'[\U00002700-\U000027BF]', '', text)  # Dingbats
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    def text_to_speech(self, text: str) -> np.ndarray:
        """
        Convert text to speech using Piper with sentence-based synthesis.
        
        Uses the exact same approach as upstream TARS-AI project:
        - Clean text of markdown/special characters
        - Split at sentence boundaries
        - Synthesize each chunk with improved prosody settings
        - Concatenate audio chunks with crossfade to prevent cracking
        
        Args:
            text: Text to convert
            
        Returns:
            Audio data as numpy array
        """
        start_time = time.time()
        
        try:
            # Clean text for TTS (remove markdown, asterisks, emojis, etc.)
            clean_text = self._clean_text_for_tts(text)
            
            if self.verbose and clean_text != text:
                print(f"🧹 Cleaned text for TTS: {clean_text[:100]}...")
            
            # Split at sentence boundaries like upstream does
            chunks = re.split(r'(?<=\.)\s', clean_text)
            
            all_audio = []
            
            for chunk in chunks:
                if chunk.strip():
                    # Synthesize to BytesIO buffer with prosody config
                    wav_buffer = BytesIO()
                    with wave.open(wav_buffer, 'wb') as wav_file:
                        wav_file.setnchannels(1)  # Mono
                        wav_file.setsampwidth(2)  # 16-bit samples
                        wav_file.setframerate(self.tts_sample_rate)
                        # Use improved prosody config for more natural speech
                        self.piper_voice.synthesize_wav(
                            chunk.strip(), 
                            wav_file,
                            syn_config=self.synthesis_config
                        )
                    
                    # Read back the audio
                    wav_buffer.seek(0)
                    audio_chunk, sr = sf.read(wav_buffer)
                    
                    # Convert to float32 for consistent processing
                    audio_chunk = audio_chunk.astype(np.float32)
                    
                    all_audio.append(audio_chunk)
            
            # Combine audio chunks with crossfade to prevent clicks/cracks
            if all_audio:
                audio = self._crossfade_concat(all_audio)
            else:
                audio = np.array([], dtype=np.float32)
            
            self._last_tts_sample_rate = self.tts_sample_rate
            self.metrics['tts_time'] = time.time() - start_time
            
            if self.verbose:
                print(f"🔊 Generated speech in {self.metrics['tts_time']:.2f}s")
            
            return audio
            
        except Exception as e:
            if self.verbose:
                print(f"❌ TTS Error: {e}")
            return np.array([], dtype=np.float32)
    
    def _crossfade_concat(self, audio_chunks: list, crossfade_ms: int = 20) -> np.ndarray:
        """
        Concatenate audio chunks with crossfade to prevent clicking/cracking.
        
        Args:
            audio_chunks: List of audio arrays to concatenate
            crossfade_ms: Crossfade duration in milliseconds
            
        Returns:
            Concatenated audio with smooth transitions
        """
        if not audio_chunks:
            return np.array([], dtype=np.float32)
        
        if len(audio_chunks) == 1:
            return audio_chunks[0]
        
        crossfade_samples = int(self.tts_sample_rate * crossfade_ms / 1000)
        
        # Start with first chunk
        result = audio_chunks[0].copy()
        
        for chunk in audio_chunks[1:]:
            if len(chunk) == 0:
                continue
                
            # Determine crossfade length (can't exceed chunk lengths)
            fade_len = min(crossfade_samples, len(result), len(chunk))
            
            if fade_len > 0:
                # Create fade curves
                fade_out = np.linspace(1, 0, fade_len).astype(np.float32)
                fade_in = np.linspace(0, 1, fade_len).astype(np.float32)
                
                # Apply crossfade
                result[-fade_len:] *= fade_out
                chunk_copy = chunk.copy()
                chunk_copy[:fade_len] *= fade_in
                
                # Overlap-add
                result[-fade_len:] += chunk_copy[:fade_len]
                
                # Append the rest
                result = np.concatenate([result, chunk_copy[fade_len:]])
            else:
                # No crossfade possible, just concatenate
                result = np.concatenate([result, chunk])
        
        return result
    
    def play_audio(self, audio: np.ndarray, sample_rate: int = None):
        """
        Play audio through speakers with proper buffering to prevent cracking.
        
        Args:
            audio: Audio data to play
            sample_rate: Sample rate (defaults to TTS native rate)
        """
        if len(audio) == 0:
            return
        
        # Use TTS native sample rate (22050 Hz) for best quality
        rate = sample_rate or getattr(self, '_last_tts_sample_rate', self.tts_sample_rate)
        
        # Ensure audio is float32 for proper playback
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        # Normalize audio to prevent clipping (which causes cracking)
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            # Normalize to 90% to leave headroom
            audio = audio / max_val * 0.9
        
        # Apply fade in/out to prevent pops at start/end
        fade_samples = int(rate * 0.02)  # 20ms fade (longer for cleaner end)
        if len(audio) > fade_samples * 2:
            # Fade in
            fade_in = np.linspace(0, 1, fade_samples)
            audio[:fade_samples] *= fade_in
            # Fade out (longer to eliminate static)
            fade_out = np.linspace(1, 0, fade_samples)
            audio[-fade_samples:] *= fade_out
        
        # Add silence padding at end to prevent buffer static
        silence_pad = np.zeros(int(rate * 0.05), dtype=np.float32)  # 50ms silence
        audio = np.concatenate([audio, silence_pad])
        
        # Use larger blocksize for smoother playback (prevents buffer underruns)
        sd.play(audio, rate, blocksize=4096)  # Even larger buffer
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
    
    def _detect_speech_energy(self, audio: np.ndarray, threshold: float = 0.01) -> bool:
        """
        Simple energy-based speech detection.
        
        Args:
            audio: Audio data as numpy array
            threshold: Energy threshold for speech detection
            
        Returns:
            True if speech detected, False otherwise
        """
        energy = np.sqrt(np.mean(audio ** 2))
        return energy > threshold
    
    def continuous_listen_mode(self, silence_threshold: float = 0.01, 
                                min_speech_duration: float = 0.5,
                                max_silence_duration: float = 1.5,
                                chunk_duration: float = 0.5):
        """
        Continuous listening mode - automatically detects when you speak.
        No need to press Enter!
        
        Args:
            silence_threshold: RMS threshold below which is considered silence
            min_speech_duration: Minimum seconds of speech to trigger processing
            max_silence_duration: Seconds of silence after speech to stop recording
            chunk_duration: Duration of each audio chunk to analyze
        """
        print("\n" + "=" * 70)
        print("TARS VOICE INTERFACE - Continuous Listening Mode")
        print("=" * 70)
        print(f"\nUser name: {self.tars.user_name}")
        print(f"Honesty: {self.tars.settings.honesty}%")
        print(f"Humor: {self.tars.settings.humor}%")
        print(f"Discretion: {self.tars.settings.discretion}%")
        print("\n🎤 Listening... (just start talking!)")
        print("Press Ctrl+C to exit")
        print("=" * 70 + "\n")
        
        chunk_samples = int(chunk_duration * self.sample_rate)
        
        try:
            while True:
                # Wait for speech to start
                audio_buffer = []
                speech_started = False
                silence_chunks = 0
                max_silence_chunks = int(max_silence_duration / chunk_duration)
                min_speech_chunks = int(min_speech_duration / chunk_duration)
                speech_chunks = 0
                
                while True:
                    # Record a chunk
                    chunk = sd.rec(chunk_samples, samplerate=self.sample_rate, 
                                   channels=1, dtype='float32')
                    sd.wait()
                    chunk = chunk.flatten()
                    
                    # Check for speech
                    has_speech = self._detect_speech_energy(chunk, silence_threshold)
                    
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
                        audio_buffer.append(chunk)  # Include trailing silence
                        
                        # Stop if enough silence after speech
                        if silence_chunks >= max_silence_chunks:
                            if speech_chunks >= min_speech_chunks:
                                break  # Process the audio
                            else:
                                # Too short, reset
                                if self.verbose:
                                    print("⚠️  Speech too short, ignoring...")
                                audio_buffer = []
                                speech_started = False
                                silence_chunks = 0
                                speech_chunks = 0
                
                # Process the recorded audio
                if audio_buffer:
                    audio = np.concatenate(audio_buffer)
                    
                    if self.verbose:
                        print(f"📝 Processing {len(audio)/self.sample_rate:.1f}s of audio...")
                    
                    # Speech to text
                    user_text = self.speech_to_text(audio)
                    
                    if user_text:
                        # Get TARS response
                        tars_text = self.get_tars_response(user_text)
                        
                        # Convert to speech and play
                        tars_audio = self.text_to_speech(tars_text)
                        self.play_audio(tars_audio)
                        
                        if self.verbose:
                            print(f"\n⚡ Response latency: {self.metrics['stt_time'] + self.metrics['llm_time'] + self.metrics['tts_time']:.2f}s")
                            print("\n🎤 Listening...\n")
                    else:
                        if self.verbose:
                            print("⚠️  No speech recognized")
                            print("\n🎤 Listening...\n")
        
        except KeyboardInterrupt:
            self.memory.end_session()  # Persist memory on shutdown
            print("\n\n👋 TARS shutting down. Memory saved. Goodbye.")
    
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
            self.memory.end_session()  # Persist memory on shutdown
            print("\n\n👋 TARS shutting down. Memory saved. Goodbye.")


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
    
    # Mode selection
    print("\n" + "-" * 40)
    print("Select mode:")
    print("  1) Press-to-talk (press Enter to speak)")
    print("  2) Continuous listening (auto-detect speech)")
    print("-" * 40)
    
    try:
        mode = input("Enter choice [1/2, default=2]: ").strip() or "2"
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Goodbye.")
        sys.exit(0)
    
    if mode == "1":
        engine.interactive_mode()
    else:
        engine.continuous_listen_mode()


if __name__ == "__main__":
    main()
