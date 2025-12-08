"""
TARS Conversation Memory Module

Provides persistent memory for TARS across sessions.
Stores conversations, user preferences, and conversation summaries.
"""

import json
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import deque


class TARSMemory:
    """Manages persistent conversation memory for TARS."""
    
    def __init__(self, memory_path: Optional[str] = None, max_history: int = 100):
        """
        Initialize TARS memory system.
        
        Args:
            memory_path: Path to store memory files (default: ~/.tars/memory/)
            max_history: Maximum conversation turns to keep in memory
        """
        self.memory_path = Path(memory_path or os.path.expanduser("~/.tars/memory/"))
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        self.max_history = max_history
        self.conversation_file = self.memory_path / "conversations.json"
        self.settings_file = self.memory_path / "settings.json"
        self.summaries_file = self.memory_path / "summaries.json"
        
        # In-memory state
        self.current_session: list[dict] = []
        self.past_conversations: deque = deque(maxlen=max_history)
        self.user_settings: dict = {}
        self.summaries: list[str] = []
        
        # Load existing data
        self._load_memory()
        
    def _load_memory(self):
        """Load persisted memory from disk."""
        # Load conversation history
        if self.conversation_file.exists():
            try:
                with open(self.conversation_file, 'r') as f:
                    data = json.load(f)
                    self.past_conversations = deque(data.get('conversations', []), maxlen=self.max_history)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[MEMORY] Warning: Could not load conversations: {e}")
                
        # Load user settings
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    self.user_settings = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[MEMORY] Warning: Could not load settings: {e}")
                
        # Load summaries
        if self.summaries_file.exists():
            try:
                with open(self.summaries_file, 'r') as f:
                    data = json.load(f)
                    self.summaries = data.get('summaries', [])
            except (json.JSONDecodeError, IOError) as e:
                print(f"[MEMORY] Warning: Could not load summaries: {e}")
                
    def _save_memory(self):
        """Persist memory to disk."""
        try:
            # Save conversations
            with open(self.conversation_file, 'w') as f:
                json.dump({'conversations': list(self.past_conversations)}, f, indent=2)
                
            # Save settings
            with open(self.settings_file, 'w') as f:
                json.dump(self.user_settings, f, indent=2)
                
            # Save summaries
            with open(self.summaries_file, 'w') as f:
                json.dump({'summaries': self.summaries}, f, indent=2)
                
        except IOError as e:
            print(f"[MEMORY] Error saving memory: {e}")
            
    def add_exchange(self, user_input: str, tars_response: str):
        """
        Add a conversation exchange to memory.
        
        Args:
            user_input: What the user said
            tars_response: TARS's response
        """
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'tars': tars_response
        }
        self.current_session.append(exchange)
        self.past_conversations.append(exchange)
        
        # Auto-save periodically
        if len(self.current_session) % 5 == 0:
            self._save_memory()
            
    def get_context_for_llm(self, num_recent: int = 5) -> str:
        """
        Get recent conversation context formatted for LLM prompt.
        
        Args:
            num_recent: Number of recent exchanges to include
            
        Returns:
            Formatted string with conversation history
        """
        if not self.past_conversations:
            return ""
            
        recent = list(self.past_conversations)[-num_recent:]
        
        context_lines = ["[Previous Conversation:]"]
        for ex in recent:
            context_lines.append(f"User: {ex['user']}")
            context_lines.append(f"TARS: {ex['tars']}")
        context_lines.append("[End of Previous Conversation]\n")
        
        return "\n".join(context_lines)
        
    def update_setting(self, key: str, value):
        """
        Update a user setting and persist it.
        
        Args:
            key: Setting name (e.g., 'humor', 'honesty')
            value: New value
        """
        self.user_settings[key] = value
        self.user_settings['last_updated'] = datetime.now().isoformat()
        self._save_memory()
        
    def get_setting(self, key: str, default=None):
        """
        Get a persisted setting.
        
        Args:
            key: Setting name
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        return self.user_settings.get(key, default)
        
    def get_all_settings(self) -> dict:
        """Get all persisted settings."""
        return self.user_settings.copy()
        
    def add_summary(self, summary: str):
        """Add a conversation summary (for long-term memory compression)."""
        self.summaries.append({
            'timestamp': datetime.now().isoformat(),
            'summary': summary
        })
        self._save_memory()
        
    def end_session(self):
        """End current session and persist all data."""
        self._save_memory()
        self.current_session = []
        
    def clear_history(self):
        """Clear all conversation history (keeps settings)."""
        self.past_conversations.clear()
        self.current_session = []
        self.summaries = []
        self._save_memory()
        
    def get_stats(self) -> dict:
        """Get memory statistics."""
        return {
            'total_exchanges': len(self.past_conversations),
            'current_session': len(self.current_session),
            'summaries': len(self.summaries),
            'settings_count': len(self.user_settings),
            'memory_path': str(self.memory_path)
        }


class DirectivesManager:
    """Loads and manages TARS prime directives from YAML config."""
    
    def __init__(self, directives_path: Optional[str] = None):
        """
        Initialize directives manager.
        
        Args:
            directives_path: Path to prime_directives.yaml
        """
        self.directives_path = Path(directives_path) if directives_path else None
        self.directives: dict = {}
        
        # Default directives if file not found
        self.defaults = {
            'identity': {'name': 'TARS'},
            'user': {'name': 'Cooper'},
            'settings': {'humor': 75, 'honesty': 90, 'discretion': 80},
            'prime_directives': [
                "Always identify as TARS from Interstellar",
                "Respond with dry wit proportional to humor setting",
                "Keep responses concise"
            ],
            'response_style': {'max_sentences': 3, 'prefer_short': True}
        }
        
        self._load_directives()
        
    def _load_directives(self):
        """Load directives from YAML file."""
        if self.directives_path and self.directives_path.exists():
            try:
                with open(self.directives_path, 'r') as f:
                    self.directives = yaml.safe_load(f)
                print(f"[DIRECTIVES] Loaded from {self.directives_path}")
            except (yaml.YAMLError, IOError) as e:
                print(f"[DIRECTIVES] Error loading: {e}, using defaults")
                self.directives = self.defaults
        else:
            print("[DIRECTIVES] No directives file found, using defaults")
            self.directives = self.defaults
            
    def get(self, key: str, default=None):
        """Get a directive value by key."""
        return self.directives.get(key, default)
        
    def get_setting(self, setting_name: str) -> int:
        """Get a specific setting value (humor, honesty, etc)."""
        settings = self.directives.get('settings', {})
        return settings.get(setting_name, 75)
        
    def get_system_prompt(self) -> str:
        """
        Generate a system prompt from directives.
        
        Returns:
            Formatted system prompt string for LLM
        """
        identity = self.directives.get('identity', {})
        user = self.directives.get('user', {})
        settings = self.directives.get('settings', {})
        primes = self.directives.get('prime_directives', [])
        style = self.directives.get('response_style', {})
        
        name = identity.get('name', 'TARS')
        user_name = user.get('name', 'the user')
        humor = settings.get('humor', 75)
        honesty = settings.get('honesty', 90)
        
        prompt_parts = [
            f"You are {name}, a former Marine Corps tactical robot from the movie Interstellar.",
            f"You are speaking with {user_name}.",
            f"Your current settings: Humor={humor}%, Honesty={honesty}%.",
            "",
            "Prime Directives:"
        ]
        
        for i, directive in enumerate(primes, 1):
            prompt_parts.append(f"  {i}. {directive}")
            
        prompt_parts.extend([
            "",
            "Response Guidelines:",
            f"  - Maximum {style.get('max_sentences', 3)} sentences unless asked for detail",
            f"  - Prefer {'short' if style.get('prefer_short', True) else 'detailed'} responses",
            "  - Use dry wit and sarcasm appropriate to humor setting",
            "  - Always comply with settings adjustment requests"
        ])
        
        return "\n".join(prompt_parts)
        
    def reload(self):
        """Reload directives from file."""
        self._load_directives()


# Global instances for easy import
_memory_instance: Optional[TARSMemory] = None
_directives_instance: Optional[DirectivesManager] = None


def get_memory() -> TARSMemory:
    """Get or create the global memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = TARSMemory()
    return _memory_instance


def get_directives(directives_path: Optional[str] = None) -> DirectivesManager:
    """Get or create the global directives instance."""
    global _directives_instance
    if _directives_instance is None:
        _directives_instance = DirectivesManager(directives_path)
    return _directives_instance
