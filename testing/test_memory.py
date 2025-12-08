"""
Tests for TARS memory and setting command parsing.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gptars.core.memory import TARSMemory, DirectivesManager


class TestTARSMemory:
    """Test suite for TARSMemory class."""
    
    def test_memory_initialization(self):
        """Test that memory initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = TARSMemory(memory_path=tmpdir, max_history=10)
            assert memory.memory_path == Path(tmpdir)
            assert memory.max_history == 10
            assert len(memory.current_session) == 0
    
    def test_add_exchange(self):
        """Test adding conversation exchanges."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = TARSMemory(memory_path=tmpdir)
            memory.add_exchange("Hello TARS", "Hello Cooper.")
            
            assert len(memory.current_session) == 1
            assert len(memory.past_conversations) == 1
            assert memory.past_conversations[0]['user'] == "Hello TARS"
            assert memory.past_conversations[0]['tars'] == "Hello Cooper."
    
    def test_get_context_for_llm(self):
        """Test getting conversation context for LLM."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = TARSMemory(memory_path=tmpdir)
            memory.add_exchange("First message", "First response")
            memory.add_exchange("Second message", "Second response")
            
            context = memory.get_context_for_llm(num_recent=2)
            assert "First message" in context
            assert "Second response" in context
            assert "[Previous Conversation:]" in context
    
    def test_setting_persistence(self):
        """Test that settings persist to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create memory and set a value
            memory1 = TARSMemory(memory_path=tmpdir)
            memory1.update_setting("humor", 95)
            memory1.end_session()
            
            # Create new memory instance from same path
            memory2 = TARSMemory(memory_path=tmpdir)
            assert memory2.get_setting("humor") == 95
    
    def test_conversation_persistence(self):
        """Test that conversations persist to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create memory and add exchange
            memory1 = TARSMemory(memory_path=tmpdir)
            memory1.add_exchange("Test question", "Test answer")
            memory1.end_session()
            
            # Create new memory instance from same path
            memory2 = TARSMemory(memory_path=tmpdir)
            assert len(memory2.past_conversations) == 1
            assert memory2.past_conversations[0]['user'] == "Test question"
    
    def test_max_history_limit(self):
        """Test that history is limited to max_history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = TARSMemory(memory_path=tmpdir, max_history=3)
            
            for i in range(5):
                memory.add_exchange(f"Message {i}", f"Response {i}")
            
            # Should only keep last 3
            assert len(memory.past_conversations) == 3
            assert memory.past_conversations[0]['user'] == "Message 2"
            assert memory.past_conversations[-1]['user'] == "Message 4"


class TestDirectivesManager:
    """Test suite for DirectivesManager class."""
    
    def test_default_directives(self):
        """Test that defaults are used when no file exists."""
        dm = DirectivesManager(directives_path="/nonexistent/path.yaml")
        assert dm.get('identity') is not None
        assert dm.get_setting('humor') == 75
    
    def test_get_system_prompt(self):
        """Test system prompt generation."""
        dm = DirectivesManager()
        prompt = dm.get_system_prompt()
        
        assert "TARS" in prompt
        assert "Humor=" in prompt
        assert "Honesty=" in prompt


class TestSettingCommandParsing:
    """Test setting command parsing patterns."""
    
    def setup_method(self):
        """Set up test fixtures."""
        import re
        self.patterns = [
            (r'set\s+humor\s+(?:to\s+)?(\d+)', 'humor'),
            (r'humor\s+(?:to\s+)?(\d+)', 'humor'),
            (r'humor\s+setting\s+(?:to\s+)?(\d+)', 'humor'),
            (r'set\s+honesty\s+(?:to\s+)?(\d+)', 'honesty'),
            (r'honesty\s+(?:to\s+)?(\d+)', 'honesty'),
            (r'(\d+)\s*(?:percent|%)?\s+humor', 'humor'),
        ]
        self.re = re
    
    def _parse(self, text):
        """Parse a setting command."""
        text_lower = text.lower().strip()
        for pattern, setting in self.patterns:
            match = self.re.search(pattern, text_lower)
            if match:
                value = int(match.group(1))
                if 0 <= value <= 100:
                    return (setting, value)
        return None
    
    def test_set_humor_to_pattern(self):
        """Test 'set humor to X' pattern."""
        result = self._parse("Set humor to 80")
        assert result == ('humor', 80)
    
    def test_humor_number_pattern(self):
        """Test 'humor X' pattern."""
        result = self._parse("humor 75")
        assert result == ('humor', 75)
    
    def test_number_percent_humor(self):
        """Test 'X percent humor' pattern."""
        result = self._parse("100 percent humor")
        assert result == ('humor', 100)
    
    def test_set_honesty_pattern(self):
        """Test 'set honesty to X' pattern."""
        result = self._parse("set honesty to 95")
        assert result == ('honesty', 95)
    
    def test_no_match(self):
        """Test that non-command text returns None."""
        result = self._parse("What's the weather like?")
        assert result is None
    
    def test_invalid_value(self):
        """Test that values over 100 are rejected."""
        result = self._parse("set humor to 150")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
