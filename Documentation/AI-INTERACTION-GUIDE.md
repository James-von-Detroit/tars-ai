# TARS-AI Quick Reference: AI Interaction Guide

This is a quick reference for understanding and interacting with TARS-AI's intelligence features.

---

## What Can TARS Actually Do?

### Core Intelligence Capabilities

| Capability | Description | Example |
|------------|-------------|---------|
| **Conversational AI** | Natural language understanding and generation | "Tell me about yourself" |
| **Memory Recall** | Remembers past conversations | "What did we talk about yesterday?" |
| **Context Awareness** | Understands conversation flow | Multi-turn dialogues |
| **Character Roleplay** | Stays in character (TARS personality) | Responds with TARS's humor and honesty settings |
| **Image Understanding** | Can describe and analyze images | "What do you see in this image?" |
| **Web Search** | Can search the internet for info | "What's the weather in Detroit?" |
| **Learning** | Improves over time from conversations | Memory builds with each chat |

---

## Understanding the AI Architecture

### Conversation Flow
```
You type/say something
    ↓
TARS searches its memory for relevant context
    ↓
Builds a rich prompt with:
  - Your message
  - Relevant past conversations
  - TARS's personality traits
  - Current date/time
    ↓
Sends to LLM (GPT-4, etc.)
    ↓
LLM generates response
    ↓
TARS saves conversation to memory
    ↓
You receive response
```

### Memory System
TARS has two types of memory:

1. **Short-term Memory**
   - Last few exchanges in conversation
   - Always included in prompts
   - Reset when you restart (unless saved)

2. **Long-term Memory**
   - Stored permanently in HyperDB
   - Searched using semantic similarity
   - Survives restarts
   - Gets richer over time

---

## How to Get the Best Responses

### Tips for Better Conversations

1. **Be Conversational**
   - ✅ "Hey TARS, what do you think about AI ethics?"
   - ❌ "AI ethics information"

2. **Reference Past Conversations**
   - ✅ "Remember when we talked about space travel?"
   - TARS will search its memory and recall the context

3. **Use TARS's Personality**
   - TARS has humor and honesty settings
   - ✅ "Give me your honest opinion on this"
   - TARS will respond according to its character

4. **Ask for Explanations**
   - ✅ "Can you explain quantum computing in simple terms?"
   - TARS is designed to be helpful and educational

5. **Multi-turn Conversations**
   - Have back-and-forth dialogues
   - TARS maintains context across turns

### Example Conversations

**Learning from memory:**
```
You: "I'm working on a Python project"
TARS: "What kind of Python project are you working on?"
[Later that day or next week]
You: "I'm stuck on that project"
TARS: "Is this about the Python project you mentioned? What part are you stuck on?"
```

**Character consistency:**
```
You: "Should I take the safe path or the risky one?"
TARS: "With my honesty setting at 90%, I'd say the safe path is boring but predictable. 
       The risky one could be disaster or glory. Your call, but don't blame me if you pick glory."
```

---

## Configuration for Different Use Cases

### 1. Casual Chat Assistant
```ini
[LLM]
temperature = 0.8  # More creative
max_tokens = 1000  # Longer responses
contextsize = 4000

[RAG]
top_k = 5  # Moderate memory recall
```

### 2. Technical Assistant
```ini
[LLM]
temperature = 0.4  # More focused
max_tokens = 2000  # Detailed explanations
contextsize = 8000  # More context

[RAG]
top_k = 10  # More memory recall
```

### 3. Creative Roleplay
```ini
[LLM]
temperature = 1.0  # Very creative
max_tokens = 500  # Snappy responses
contextsize = 4000

[RAG]
top_k = 3  # Less memory influence
```

---

## Personality Customization

### TARS's Personality Traits
Located in: `/src/character/TARS/persona.ini`

```ini
[PERSONA]
humor = 75       # 0-100, how funny TARS is
honesty = 90     # 0-100, how blunt/honest
loyalty = 95     # 0-100, how dedicated to user
curiosity = 80   # 0-100, how inquisitive
formality = 30   # 0-100, how casual vs formal
```

**What they do:**
- **Humor**: Higher = more jokes and sarcasm
- **Honesty**: Higher = more direct, less sugar-coating
- **Loyalty**: Higher = more protective and supportive
- **Curiosity**: Higher = asks more questions
- **Formality**: Higher = more professional, lower = more casual

### Editing Personality
```bash
nano /src/character/TARS/persona.ini
```

Change values, save, restart TARS. Instant personality change!

---

## LLM Backend Options

### OpenAI (Recommended for Quality)
```ini
[LLM]
llm_backend = openai
base_url = https://api.openai.com
openai_model = gpt-4o-mini  # or gpt-4, gpt-3.5-turbo
```
- **Pros**: Best quality, fast, reliable
- **Cons**: Costs money (~$0.001-0.01 per conversation)

### Local LLM (Free, Private)
```ini
[LLM]
llm_backend = ooba
base_url = http://localhost:5000
```
- **Pros**: Free, private, offline capable
- **Cons**: Slower, needs good hardware, lower quality

### DeepInfra (Cloud, Cheaper)
```ini
[LLM]
llm_backend = deepinfra
base_url = https://api.deepinfra.com
openai_model = meta-llama/Meta-Llama-3-70B-Instruct
```
- **Pros**: Cheaper than OpenAI, many models
- **Cons**: Slightly less reliable

---

## Memory Management

### Viewing Memory
Memory stored in: `/memory/TARS.pickle.gz`

### Clearing Memory (Fresh Start)
```bash
rm /memory/TARS.pickle.gz
```
TARS will create new memory on next start.

### Injecting Initial Memories
Create `/memory/initial_memory.json`:
```json
[
  {
    "time": "2024-01-01 12:00:00",
    "userinput": "My name is John and I love coding",
    "botresponse": "Nice to meet you John! I'll remember that you're passionate about coding."
  },
  {
    "time": "2024-01-01 12:01:00",
    "userinput": "I work at OpenAI",
    "botresponse": "OpenAI! That's where I get my intelligence from. Small world!"
  }
]
```

On next startup, TARS will inject these memories.

### Memory Retrieval Strategy

**Naive Strategy** (default):
```ini
[RAG]
strategy = naive
top_k = 5
```
- Simple vector similarity search
- Fast and straightforward

**Hybrid Strategy** (advanced):
```ini
[RAG]
strategy = hybrid
vector_weight = 0.5  # 0.0 = all keyword, 1.0 = all vector
top_k = 5
```
- Combines vector search with keyword matching
- More accurate but slightly slower

---

## Function Calling / Tool Use

TARS can use tools during conversations!

### Available Tools:
1. **Web Search** - Search the internet
2. **Vision** - Analyze images
3. **Image Generation** - Create images with Stable Diffusion
4. **Home Assistant** - Control smart home devices
5. **Discord** - Interact on Discord

### Configuring Function Calling
```ini
[LLM]
functioncalling = llm  # Let LLM decide when to use tools
# OR
functioncalling = NB   # Use Naive Bayes (faster but less accurate)
```

### Example Tool Use
```
You: "What's the current weather in Detroit?"
TARS: [Searches web] "According to current data, it's 45°F and cloudy in Detroit."

You: "Show me an image of a robot"
TARS: [Generates image with Stable Diffusion] "Here's an image I created for you."
```

---

## API Usage and Costs

### Token Management
```ini
[LLM]
contextsize = 4000      # Total tokens available
max_tokens = 1000       # Max tokens in response
```

**Token Usage Breakdown:**
- System prompt: ~100 tokens
- Character info: ~200 tokens
- Long-term memory: ~500 tokens
- Short-term memory: ~1000 tokens
- Your input: ~50-200 tokens
- Response: ~100-1000 tokens

### Optimizing Costs
1. Use `gpt-4o-mini` instead of `gpt-4` (10x cheaper)
2. Lower `contextsize` (less context = cheaper)
3. Lower `max_tokens` (shorter responses)
4. Disable vision/emotion if not needed
5. Use local LLM for practice/development

---

## Monitoring and Debugging

### Logs Location
Check: `src/logs/` (if logging enabled)

### Verbose Mode
Add to prompt building:
```python
# In module_prompt.py, line 57
debug=True  # Prints full prompts
```

### Testing Configuration
```bash
# Test basic setup (verify config loads correctly)
cd /path/to/tars-ai/src
python3 -c "from modules.module_config import load_config; config = load_config(); print('LLM Backend:', config['LLM']['llm_backend'])"

# Note: Full LLM testing requires proper initialization through app.py
# The get_completion function needs manager initialization first
```

---

## Common Issues and Solutions

### TARS Doesn't Remember Past Conversations
- Check that memory file exists: `ls -l /memory/TARS.pickle.gz`
- Verify RAG is enabled in config
- Try: `top_k = 10` for more memory recall

### Responses Are Too Generic
- Increase `temperature` for more creativity
- Lower `temperature` for more focused responses
- Adjust personality traits in `persona.ini`

### Responses Are Too Long
```ini
[LLM]
max_tokens = 200  # Limit response length
```

### API Errors
- Check API key in `.env`
- Verify billing is set up on OpenAI
- Check internet connection
- Try: `base_url = https://api.openai.com` (not /v1)

---

## Advanced: Creating Custom Characters

### 1. Copy TARS Character
```bash
cp -r /src/character/TARS /src/character/MYCHAR
```

### 2. Edit Character JSON
Edit `/src/character/MYCHAR/MYCHAR.json`:
```json
{
  "char_name": "MYCHAR",
  "char_persona": "Your custom personality description",
  "char_greeting": "Hello! I'm MYCHAR.",
  "example_dialogue": "User: Hi\nMYCHAR: Hey there!",
  "world_scenario": "Your character's background"
}
```

### 3. Edit Personality
Edit `/src/character/MYCHAR/persona.ini`:
```ini
[PERSONA]
humor = 50
honesty = 80
loyalty = 70
curiosity = 90
formality = 40
```

### 4. Activate Character
```ini
[CHAR]
character_card_path = character/MYCHAR/MYCHAR.json
```

---

## Summary: Getting Started

1. **Install dependencies**: `pip3 install openai tiktoken hyperdb-python`
2. **Set API key**: Add to `.env`
3. **Configure for macOS**: Edit `config.ini` (disable hardware)
4. **Run**: `python3 app.py`
5. **Chat**: Open `http://localhost:5012`
6. **Customize**: Edit personality in `persona.ini`
7. **Experiment**: Try different models and settings

**The AI intelligence is real - it's powered by GPT-4 with sophisticated memory and character systems!**
