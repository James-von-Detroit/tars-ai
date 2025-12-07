# Operation Guide - gptars v3.0 Alpha

Complete guide to operating and customizing your TARS voice assistant.

---

## 🎤 Voice Interaction Modes

### Mode 1: Push-to-Talk (Interactive)

**Best for:** Controlled interaction, testing, development

```bash
source venv/bin/activate
python3 core/voice_engine.py
```

**How it works:**
1. Press ENTER to start recording
2. Speak for 5 seconds (or until you finish)
3. TARS processes and responds with voice
4. Repeat or press Ctrl+C to exit

**Advantages:**
- Full control over when TARS listens
- No false activations
- Best for noisy environments

### Mode 2: Wake Word (Always Listening)

**Best for:** Hands-free operation, natural interaction

```bash
source venv/bin/activate
python3 << 'EOF'
from core.voice_engine import VoiceEngine
from core.wake_word import TARSWakeWordListener

engine = VoiceEngine(verbose=True)
listener = TARSWakeWordListener(engine, threshold=0.5)
listener.start()
EOF
```

**How it works:**
1. TARS listens continuously in background
2. Say "Hey TARS" (or similar phrase)
3. TARS activates and records for 5 seconds
4. TARS responds with voice
5. Returns to listening mode

**Advantages:**
- Natural, conversational interaction
- No keyboard needed
- True "assistant" experience

**Tip:** Adjust `threshold` parameter (0.0-1.0) to control sensitivity
- Lower (0.3) = more sensitive, more false positives
- Higher (0.7) = less sensitive, may miss activations
- Default (0.5) = balanced

### Mode 3: Continuous Conversation

For extended back-and-forth dialogue:

```python
from core.voice_engine import VoiceEngine
from core.tars_personality import create_tars_personality

# Create TARS with your preferences
tars = create_tars_personality(
    honesty=90,
    humor=75,
    user_name="Cooper"
)

engine = VoiceEngine(tars_personality=tars, verbose=True)

# Continuous loop
while True:
    try:
        input("Press ENTER to speak... ")
        result = engine.process_voice_input(duration=5)
    except KeyboardInterrupt:
        break
```

---

## 👁️ Vision Capabilities

### Interactive Vision Mode

```bash
python3 core/vision_engine.py
```

**Controls:**
- `s` - Capture current frame and analyze
- `p` - Toggle preview window
- `q` - Quit

**Use cases:**
- "TARS, what do you see?"
- "TARS, analyze this document"
- "TARS, identify this object"

### Integrated Voice + Vision

```python
from core.voice_engine import VoiceEngine
from core.vision_engine import VisionEngine
from core.tars_personality import DEFAULT_TARS

voice = VoiceEngine(tars_personality=DEFAULT_TARS)
vision = VisionEngine()

# User says: "TARS, look at this"
frame = vision.capture_frame()
if frame:
    description = vision.analyze_image(frame, "Describe what you see")
    # Convert to speech
    audio = voice.text_to_speech(description)
    voice.play_audio(audio)
```

---

## 🎭 Personality Customization

### Built-in Personalities

#### Movie-Accurate TARS (Default)
```python
from core.tars_personality import DEFAULT_TARS
# Honesty: 90%, Humor: 60%, Discretion: 50%
```

#### Maximum Honesty TARS
```python
from core.tars_personality import create_tars_personality

honest_tars = create_tars_personality(
    honesty=100,
    humor=30,
    discretion=10
)
# Brutally honest, minimal humor, very direct
```

#### Comedy TARS
```python
funny_tars = create_tars_personality(
    honesty=70,
    humor=95,
    discretion=40
)
# Lots of jokes, still helpful
```

#### Professional TARS
```python
pro_tars = create_tars_personality(
    honesty=85,
    humor=20,
    discretion=80
)
# Business-like, diplomatic, serious
```

### Dynamic Adjustment

Adjust personality during conversation:

```python
tars = DEFAULT_TARS

# During conversation
tars.adjust_humor(95)  # Make TARS funnier
tars.adjust_honesty(100)  # Maximum honesty
tars.adjust_discretion(20)  # Very blunt

# Check current settings
print(f"Honesty: {tars.settings.honesty}%")
print(f"Humor: {tars.settings.humor}%")
```

### Save/Load Custom Personalities

```python
# Create custom TARS
my_tars = create_tars_personality(
    honesty=95,
    humor=80,
    discretion=30,
    user_name="Your Name"
)

# Save to file
my_tars.save_to_file("my_tars_config.json")

# Load later
from core.tars_personality import TARSPersonality
loaded_tars = TARSPersonality.load_from_file("my_tars_config.json")
```

---

## ⚙️ Advanced Configuration

### Whisper Model Selection

Trade-off between speed and accuracy:

```python
# Fastest (least accurate)
engine = VoiceEngine(whisper_model="tiny")  # ~100ms, okay for simple commands

# Fast (good accuracy)
engine = VoiceEngine(whisper_model="base")  # ~200ms, good for most use

# Balanced (recommended)
engine = VoiceEngine(whisper_model="distil-large-v3")  # ~300ms, high accuracy

# Best (slowest)
engine = VoiceEngine(whisper_model="large-v3")  # ~500ms, maximum accuracy
```

### LLM Model Selection

Different Ollama models for different needs:

```bash
# Install alternatives
ollama pull mistral:7b-instruct  # Good balance
ollama pull phi3:mini  # Very fast, smaller
ollama pull llama3:8b-instruct-q8_0  # Higher quality
```

```python
# Use in voice engine
engine = VoiceEngine(ollama_model="mistral:7b-instruct")
```

### TTS Voice Selection

Available Piper voices:

**Male voices (TARS-like):**
- `en_US-lessac-medium` (default, neutral)
- `en_US-ryan-high` (deeper, more robotic)
- `en_US-danny-low` (casual)

**Female voices:**
- `en_US-amy-medium` (clear, professional)
- `en_US-kathleen-low` (warm)

Download additional voices (see MACOS_INSTALL_GUIDE.md) and use:

```python
engine = VoiceEngine(piper_voice="en_US-ryan-high")
```

### Recording Duration

Adjust how long TARS listens:

```python
# Shorter for quick commands
result = engine.process_voice_input(duration=3)

# Longer for complex questions
result = engine.process_voice_input(duration=10)
```

---

## 📊 Performance Monitoring

### View Latency Metrics

```python
engine = VoiceEngine(verbose=True)
result = engine.process_voice_input(duration=5)

print(f"STT: {result['metrics']['stt_time']:.2f}s")
print(f"LLM: {result['metrics']['llm_time']:.2f}s")
print(f"TTS: {result['metrics']['tts_time']:.2f}s")
print(f"Total: {result['metrics']['total_time']:.2f}s")
```

### Optimize for Speed

```python
# Fastest possible setup
fast_engine = VoiceEngine(
    whisper_model="tiny",  # Fastest STT
    ollama_model="phi3:mini",  # Fastest LLM
    piper_voice="en_US-lessac-low",  # Fastest TTS
    verbose=False  # Skip printing (tiny speedup)
)
```

---

## 🔧 Common Use Cases

### Use Case 1: Voice Journal

```python
import datetime
from core.voice_engine import VoiceEngine

engine = VoiceEngine()

entries = []
while True:
    input("Press ENTER to add journal entry (Ctrl+C to finish)... ")
    result = engine.process_voice_input(duration=10)
    if result:
        entries.append({
            'time': datetime.datetime.now(),
            'text': result['user_text'],
            'tars_response': result['tars_text']
        })

# Save to file
with open('journal.txt', 'w') as f:
    for entry in entries:
        f.write(f"{entry['time']}: {entry['text']}\n")
```

### Use Case 2: Voice Notes with TARS Commentary

```python
tars = create_tars_personality(humor=90)  # Witty TARS
engine = VoiceEngine(tars_personality=tars)

print("Say a note, TARS will respond with commentary")
result = engine.process_voice_input(duration=7)

# TARS adds his opinion to your note
print(f"Your note: {result['user_text']}")
print(f"TARS says: {result['tars_text']}")
```

### Use Case 3: Camera Description for Accessibility

```python
from core.vision_engine import VisionEngine

vision = VisionEngine()

while True:
    input("Press ENTER to describe current view... ")
    description = vision.tars_see(
        prompt="Describe this scene in detail for someone who can't see it."
    )
    print(description)
```

### Use Case 4: Smart Home Control (Future)

```python
# Example of what's coming in v3.1
def handle_smart_home_command(text):
    if "turn on lights" in text.lower():
        # Send HomeKit command
        pass
    elif "temperature" in text.lower():
        # Get thermostat status
        pass

result = engine.process_voice_input(duration=5)
handle_smart_home_command(result['user_text'])
```

---

## 🎯 Tips for Best Results

### Speech Recognition Tips
1. **Speak clearly** but naturally
2. **Avoid background noise** when possible
3. **Use a good microphone** (MacBook built-in is okay)
4. **Don't shout** - normal volume works best
5. **Pause briefly** between wake word and command

### Getting Better Responses
1. **Be specific** in your questions
2. **Provide context** for complex topics
3. **Use TARS's name** for clarity ("TARS, what should I do?")
4. **Adjust personality** for the task (serious for important, funny for casual)

### Wake Word Optimization
1. **Say clearly:** "Hey TARS" with emphasis on both words
2. **Consistent volume:** Not too loud, not too quiet
3. **Wait for activation:** Look for console message before speaking
4. **Quiet environment:** Reduces false positives

---

## 🔍 Conversation Context

TARS remembers recent conversation:

```python
# Conversation history is automatic
>>> "My name is Cooper"
TARS: "Noted. Good to meet you, Cooper."

>>> "What's my name?"
TARS: "You're Cooper."

>>> "What did we just talk about?"
TARS: "Your introduction. You told me your name."
```

History is kept for last 10 exchanges and resets on restart.

For persistent memory across sessions (coming in future versions).

---

## 🎨 Customizing Responses

### System Prompt Customization

For advanced users, modify the personality system prompt:

```python
tars = DEFAULT_TARS

# Get current prompt
prompt = tars.get_system_prompt()

# Or create completely custom
custom_prompt = """
You are TARS, but with an emphasis on technical accuracy.
Always provide detailed technical explanations.
Use metric units. Be extremely precise with numbers.
"""

# Then use in LLM calls (requires modifying voice_engine.py)
```

---

## 📈 Performance Tuning by Mac Model

### M1 (8GB)
```python
engine = VoiceEngine(
    whisper_model="distil-small-v3",
    ollama_model="llama3:8b-instruct-q4_0"
)
# Expected: 3-4 second total latency
```

### M2 Pro (16GB)
```python
engine = VoiceEngine(
    whisper_model="distil-large-v3",
    ollama_model="llama3:8b-instruct-q4_0"
)
# Expected: 2-3 second total latency
```

### M3 Pro/Max (32GB)
```python
engine = VoiceEngine(
    whisper_model="large-v3",
    ollama_model="llama3:8b-instruct-q8_0"
)
# Expected: 1-2 second total latency
# Can also run vision simultaneously
```

### M4 Max (64GB+)
```python
# Can run largest models
engine = VoiceEngine(
    whisper_model="large-v3",
    ollama_model="llama3:70b-instruct-q4_0"  # Much better quality
)
# Expected: Sub-second for 8B, 3-4s for 70B
```

---

## 🛡️ Privacy & Security

### Data Storage
- **Audio:** Not stored (processed in memory)
- **Transcripts:** Not logged (unless you explicitly save them)
- **Conversation history:** RAM only, cleared on exit
- **Models:** Local files, never uploaded

### Network Usage
- **After installation:** Zero (100% offline)
- **During installation:** Only for downloading models
- **No telemetry:** No data sent to any servers

---

## 🎓 Learning More

- Experiment with personality settings
- Try different models and voices
- Read the code in `core/` directory
- Join the community Discord
- Check example scripts in `examples/` (coming soon)

---

## 🆘 Need Help?

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

---

Enjoy your TARS assistant! 🤖
