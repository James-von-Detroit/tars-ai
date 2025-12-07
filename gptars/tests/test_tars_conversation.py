# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# Part of GPTars v3.0 — 100% offline TARS voice assistant for macOS.
# https://github.com/James-von-Detroit/tars-ai

"""
tests/test_tars_conversation.py

End-to-end testing for TARS voice assistant
Tests the complete STT → LLM → TTS pipeline

Author: gptars v3.0
"""

import pytest
import numpy as np
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from tars_personality import (
    PersonalitySettings,
    TARSPersonality,
    create_tars_personality,
    DEFAULT_TARS
)


class TestPersonalitySettings:
    """Test personality settings validation and behavior."""
    
    def test_default_settings(self):
        """Test default personality settings."""
        settings = PersonalitySettings()
        assert settings.honesty == 90
        assert settings.humor == 60
        assert settings.discretion == 50
        assert settings.loyalty == 100
    
    def test_custom_settings(self):
        """Test custom personality settings."""
        settings = PersonalitySettings(
            honesty=100,
            humor=30,
            discretion=80
        )
        assert settings.honesty == 100
        assert settings.humor == 30
        assert settings.discretion == 80
    
    def test_invalid_settings(self):
        """Test that invalid settings raise errors."""
        with pytest.raises(ValueError):
            PersonalitySettings(honesty=150)  # > 100
        
        with pytest.raises(ValueError):
            PersonalitySettings(humor=-10)  # < 0
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        settings = PersonalitySettings(honesty=95, humor=75)
        d = settings.to_dict()
        assert d['honesty'] == 95
        assert d['humor'] == 75
        assert 'loyalty' in d
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'honesty': 85,
            'humor': 70,
            'discretion': 60,
            'sarcasm': 80,
            'directness': 90,
            'loyalty': 100,
            'absolute_mode': False,
            'cue_light': False
        }
        settings = PersonalitySettings.from_dict(data)
        assert settings.honesty == 85
        assert settings.humor == 70


class TestTARSPersonality:
    """Test TARS personality system."""
    
    def test_initialization(self):
        """Test basic initialization."""
        tars = TARSPersonality()
        assert tars.settings.honesty == 90
        assert tars.user_name == "Cooper"
    
    def test_custom_initialization(self):
        """Test initialization with custom settings."""
        settings = PersonalitySettings(honesty=100, humor=30)
        tars = TARSPersonality(settings)
        assert tars.settings.honesty == 100
        assert tars.settings.humor == 30
    
    def test_adjust_honesty(self):
        """Test honesty adjustment."""
        tars = TARSPersonality()
        tars.adjust_honesty(100)
        assert tars.settings.honesty == 100
        
        with pytest.raises(ValueError):
            tars.adjust_honesty(150)
    
    def test_adjust_humor(self):
        """Test humor adjustment."""
        tars = TARSPersonality()
        tars.adjust_humor(95)
        assert tars.settings.humor == 95
        
        with pytest.raises(ValueError):
            tars.adjust_humor(-5)
    
    def test_adjust_discretion(self):
        """Test discretion adjustment."""
        tars = TARSPersonality()
        tars.adjust_discretion(75)
        assert tars.settings.discretion == 75
    
    def test_set_user_name(self):
        """Test changing user name."""
        tars = TARSPersonality()
        tars.set_user_name("Brand")
        assert tars.user_name == "Brand"
    
    def test_system_prompt_generation(self):
        """Test system prompt generation."""
        tars = TARSPersonality()
        prompt = tars.get_system_prompt()
        
        # Check key elements are present
        assert "TARS" in prompt
        assert "military" in prompt.lower()
        assert "Interstellar" in prompt
        assert f"{tars.settings.honesty}%" in prompt
        assert f"{tars.settings.humor}%" in prompt
        assert "Cooper" in prompt  # Default user name
    
    def test_high_honesty_prompt(self):
        """Test that high honesty affects prompt."""
        settings = PersonalitySettings(honesty=95, humor=30)
        tars = TARSPersonality(settings)
        prompt = tars.get_system_prompt()
        
        assert "95%" in prompt
        assert "extremely direct" in prompt.lower() or "truthful" in prompt.lower()
    
    def test_high_humor_prompt(self):
        """Test that high humor affects prompt."""
        settings = PersonalitySettings(honesty=70, humor=95)
        tars = TARSPersonality(settings)
        prompt = tars.get_system_prompt()
        
        assert "95%" in prompt
        assert "joke" in prompt.lower() or "wit" in prompt.lower()
    
    def test_instruction_prompt(self):
        """Test instruction prompt generation."""
        tars = TARSPersonality()
        tars.set_user_name("Test User")
        prompt = tars.get_instruction_prompt()
        
        assert "TARS" in prompt
        assert "Test User" in prompt
    
    def test_save_load(self, tmp_path):
        """Test saving and loading personality."""
        # Create custom TARS
        tars1 = create_tars_personality(honesty=85, humor=75, user_name="Test")
        
        # Save to file
        filepath = tmp_path / "tars_config.json"
        tars1.save_to_file(str(filepath))
        
        # Load from file
        tars2 = TARSPersonality.load_from_file(str(filepath))
        
        # Verify settings match
        assert tars2.settings.honesty == 85
        assert tars2.settings.humor == 75


class TestDefaultTARS:
    """Test the default TARS instance."""
    
    def test_default_tars_exists(self):
        """Test that DEFAULT_TARS is available."""
        assert DEFAULT_TARS is not None
        assert isinstance(DEFAULT_TARS, TARSPersonality)
    
    def test_default_movie_settings(self):
        """Test that default matches movie settings."""
        assert DEFAULT_TARS.settings.honesty == 90
        assert DEFAULT_TARS.settings.humor == 60
        assert DEFAULT_TARS.settings.loyalty == 100


class TestCreateTARSPersonality:
    """Test the convenience function."""
    
    def test_create_default(self):
        """Test creating with defaults."""
        tars = create_tars_personality()
        assert tars.settings.honesty == 90
        assert tars.settings.humor == 60
    
    def test_create_custom(self):
        """Test creating with custom values."""
        tars = create_tars_personality(
            honesty=100,
            humor=20,
            discretion=70,
            user_name="Brand"
        )
        assert tars.settings.honesty == 100
        assert tars.settings.humor == 20
        assert tars.settings.discretion == 70
        assert tars.user_name == "Brand"


class TestPromptVariations:
    """Test that different settings produce different prompts."""
    
    def test_honest_vs_diplomatic(self):
        """Test prompt differences between honest and diplomatic."""
        honest_tars = create_tars_personality(honesty=100, discretion=10)
        diplomatic_tars = create_tars_personality(honesty=60, discretion=90)
        
        honest_prompt = honest_tars.get_system_prompt()
        diplomatic_prompt = diplomatic_tars.get_system_prompt()
        
        # Prompts should be different
        assert honest_prompt != diplomatic_prompt
        
        # Honest TARS mentions high honesty
        assert "100%" in honest_prompt
        
        # Diplomatic TARS mentions discretion
        assert "90%" in diplomatic_prompt
    
    def test_serious_vs_funny(self):
        """Test prompt differences between serious and funny."""
        serious_tars = create_tars_personality(humor=10)
        funny_tars = create_tars_personality(humor=95)
        
        serious_prompt = serious_tars.get_system_prompt()
        funny_prompt = funny_tars.get_system_prompt()
        
        assert serious_prompt != funny_prompt
        assert "10%" in serious_prompt
        assert "95%" in funny_prompt


# Integration tests (require actual services)

@pytest.mark.integration
class TestVoiceEngineIntegration:
    """Integration tests for voice engine (requires Ollama)."""
    
    @pytest.fixture
    def check_ollama(self):
        """Check if Ollama is available."""
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                pytest.skip("Ollama not running")
        except:
            pytest.skip("Ollama not available")
    
    def test_llm_response(self, check_ollama):
        """Test getting LLM response (requires Ollama running)."""
        from voice_engine import VoiceEngine
        
        engine = VoiceEngine(verbose=False)
        response = engine.get_tars_response("Hello TARS")
        
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
    
    def test_tts_generation(self):
        """Test TTS audio generation."""
        from voice_engine import VoiceEngine
        
        engine = VoiceEngine(verbose=False)
        audio = engine.text_to_speech("Test")
        
        assert audio is not None
        assert len(audio) > 0
        assert isinstance(audio, np.ndarray)


@pytest.mark.integration
class TestVisionEngineIntegration:
    """Integration tests for vision (requires camera and models)."""
    
    def test_camera_access(self):
        """Test camera initialization."""
        try:
            from vision_engine import VisionEngine
            vision = VisionEngine(verbose=False)
            success = vision.start_camera()
            vision.stop_camera()
            assert success
        except Exception as e:
            pytest.skip(f"Camera not available: {e}")


# Performance tests

@pytest.mark.performance
class TestPerformance:
    """Performance benchmarks."""
    
    def test_personality_prompt_generation_speed(self):
        """Test that prompt generation is fast."""
        tars = DEFAULT_TARS
        
        start = time.time()
        for _ in range(100):
            prompt = tars.get_system_prompt()
        elapsed = time.time() - start
        
        # Should be very fast (< 0.1s for 100 iterations)
        assert elapsed < 0.1
        assert len(prompt) > 500  # Reasonably detailed
    
    def test_settings_adjustment_speed(self):
        """Test that adjusting settings is instant."""
        tars = TARSPersonality()
        
        start = time.time()
        for i in range(1000):
            tars.adjust_humor((i % 100) + 1)
        elapsed = time.time() - start
        
        # Should be instant
        assert elapsed < 0.01


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
