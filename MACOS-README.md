# TARS-AI for macOS - Quick Start

## Yes, TARS has Real AI Intelligence! 🧠

TARS-AI uses **actual Large Language Models (LLMs)** like GPT-4 for intelligence. This isn't a simple chatbot - it has:

- ✅ **Real LLM Brain**: GPT-4, GPT-3.5, or **local models (Ollama)**
- ✅ **ARM Mac Support**: Fully optimized for M1/M2/M3 MacBooks
- ✅ **Persistent Memory**: Remembers conversations across sessions
- ✅ **Character Personality**: Stays in character with customizable traits
- ✅ **Context Awareness**: Understands conversation flow and history
- ✅ **Learning Ability**: Gets smarter as you talk to it
- ✅ **Multi-modal**: Can see, speak, and reason

**You can run the AI on your MacBook without any robotics hardware!**

> **🍎 ARM MacBook Pro Users:** TARS works great on Apple Silicon! See [ARM-MAC-LOCAL-LLM-GUIDE.md](Documentation/ARM-MAC-LOCAL-LLM-GUIDE.md) for optimized setup with local LLMs.

---

## 5-Minute Setup (macOS)

### Step 1: Install Dependencies
```bash
# Clone the repo (replace with your fork if applicable)
git clone https://github.com/James-von-Detroit/tars-ai.git
cd tars-ai/src

# Install minimal dependencies (AI only)
pip3 install openai tiktoken hyperdb-python requests python-dotenv flask flask-cors flask-socketio eventlet
```

### Step 2: Configure
```bash
# Copy macOS config
cp config.ini.macos config.ini

# Set up API key
cp ../.env.template ../.env
nano ../.env  # Add your OpenAI API key
```

### Step 3: Run
```bash
python3 app.py
```

### Step 4: Chat
Open your browser to: **http://localhost:5012**

Start chatting with TARS!

---

## What You Can Do

### Basic Conversations
```
You: "Hello TARS, tell me about yourself"
TARS: "I'm TARS, an AI assistant. My humor setting is at 75% and my 
       honesty is at 90%, so expect some sarcasm with your truth."
```

### Memory Recall
```
You: "My favorite color is blue"
TARS: "Got it. Blue it is."

[Later or in a new session]
You: "What's my favorite color?"
TARS: "You mentioned blue is your favorite color."
```

### Character Personality
TARS has adjustable personality traits:
- Humor: 75% (can be sarcastic)
- Honesty: 90% (very direct)
- Loyalty: 95% (protective)
- Curiosity: 80% (asks questions)
- Formality: 30% (casual)

Edit `/src/character/TARS/persona.ini` to customize!

---

## Local LLM Setup (Free & Private) 🆓

### Use Ollama for On-Device AI

Perfect for ARM MacBooks (M1/M2/M3)! Run AI completely offline and free.

```bash
# Install Ollama
brew install ollama

# Download a model
ollama pull llama2          # 7B model (good for M1/M2)
# OR
ollama pull mistral         # 7B model (high quality)
# OR for M2/M3 Pro/Max
ollama pull llama2:13b      # 13B model (better quality)

# Start server (in separate terminal)
ollama serve
```

### Configure TARS for Local LLM

In `config.ini`:
```ini
[LLM]
llm_backend = ooba
base_url = http://localhost:11434/v1
openai_model = llama2  # or mistral, phi, etc.
```

In `.env`:
```bash
OPENAI_API_KEY=not-needed-for-local
```

**Benefits:**
- ✅ **Zero cost** - No API fees
- ✅ **100% private** - Data stays on your Mac
- ✅ **Offline capable** - No internet needed after model download
- ✅ **Optimized for Apple Silicon** - Uses Metal GPU acceleration

**See [ARM-MAC-LOCAL-LLM-GUIDE.md](Documentation/ARM-MAC-LOCAL-LLM-GUIDE.md) for complete setup & testing plan**

---

## Local LLM Setup (Free & Private) 🆓

### Use Ollama for On-Device AI

Perfect for ARM MacBooks (M1/M2/M3)! Run AI completely offline and free.

```bash
# Install Ollama
brew install ollama

# Download a model
ollama pull llama2          # 7B model (good for M1/M2)
# OR
ollama pull mistral         # 7B model (high quality)
# OR for M2/M3 Pro/Max
ollama pull llama2:13b      # 13B model (better quality)

# Start server (in separate terminal)
ollama serve
```

### Configure TARS for Local LLM

In `config.ini`:
```ini
[LLM]
llm_backend = ooba
base_url = http://localhost:11434/v1
openai_model = llama2  # or mistral, phi, etc.
```

In `.env`:
```bash
OPENAI_API_KEY=not-needed-for-local
```

**Benefits:**
- ✅ **Zero cost** - No API fees
- ✅ **100% private** - Data stays on your Mac
- ✅ **Offline capable** - No internet needed after model download
- ✅ **Optimized for Apple Silicon** - Uses Metal GPU acceleration

**See [ARM-MAC-LOCAL-LLM-GUIDE.md](Documentation/ARM-MAC-LOCAL-LLM-GUIDE.md) for complete setup & testing plan**

---

## Alternative Configurations

### Use GPT-4 (Better Quality)
In `config.ini`:
```ini
[LLM]
llm_backend = openai
openai_model = gpt-4o  # More expensive but smarter
```

### Enable Voice
In `config.ini`:
```ini
[STT]
stt_processor = openai  # Voice input via Whisper API

[TTS]
ttsoption = openai  # Voice output
openai_voice = alloy  # Choose: alloy, echo, fable, onyx, nova, shimmer
```

---

## Documentation

Four comprehensive guides are available in `/Documentation/`:

1. **ARM-MAC-LOCAL-LLM-GUIDE.md** ⭐ NEW!
   - Complete setup for ARM MacBooks (M1/M2/M3)
   - Local LLM with Ollama
   - Performance benchmarks
   - QA testing plan

2. **AI-INTELLIGENCE-ANALYSIS.md**
   - Detailed analysis of AI capabilities
   - Architecture and technical details
   - Comparison to other AI systems

2. **MACOS-SETUP-GUIDE.md**
   - Complete setup instructions for macOS
   - Troubleshooting guide
   - Advanced configuration options

3. **AI-INTERACTION-GUIDE.md**
   - How to get the best responses
   - Memory management
   - Personality customization
   - Tool use and function calling

---

## Cost Considerations

### OpenAI API (Recommended)
- **gpt-4o-mini**: ~$0.001-0.01 per conversation
- **gpt-4**: ~$0.01-0.10 per conversation
- Daily casual use: ~$0.10-1.00/day

### Free Alternatives
- **Local LLMs** (Ollama): Free but slower
- **DeepInfra**: Free tier available
- **Ooba/TabbyAPI**: Self-hosted, free

---

## Key Features

### 1. Advanced Memory System
- Uses HyperDB vector database
- Semantic search for context
- Persists across restarts
- Gets better over time

### 2. Sophisticated Prompts
- Dynamic prompt engineering
- Token-aware context management
- Character personality injection
- Multi-turn conversation handling

### 3. Optional Add-ons
- Vision (image understanding)
- Web search
- Home automation (Home Assistant)
- Discord bot
- Image generation (Stable Diffusion)

---

## Troubleshooting

### "Module not found" errors
```bash
pip3 install [missing-module]
```

### "API key not found"
Check `.env` file has your key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Port 5012 already in use
```bash
lsof -ti:5012 | xargs kill -9
```

### Import errors for hardware modules
These are safe to ignore on macOS - they're for Raspberry Pi hardware.

---

## Next Steps

1. **Explore the documentation** in `/Documentation/`
2. **Customize personality** in `/src/character/TARS/persona.ini`
3. **Try different models** (GPT-4 for better quality)
4. **Enable vision** to analyze images
5. **Add integrations** (Discord, Home Assistant)

---

## Summary

**TARS-AI is a real, intelligent AI assistant that:**
- Uses actual LLMs (GPT-4, etc.)
- Has sophisticated memory and learning
- Maintains character personality
- Can be extended with tools and integrations
- Runs completely in software on macOS

**The robotics are optional - the AI brain is the real star!**

Enjoy your intelligent TARS companion! 🤖✨
