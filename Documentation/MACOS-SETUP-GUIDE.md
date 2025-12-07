# Running TARS-AI on macOS (Intelligence Only - No Robotics)

This guide shows you how to run TARS-AI as a pure AI assistant on your MacBook, skipping all robotics, 3D printing, and hardware components.

---

## Prerequisites

- **macOS** (any recent version)
- **Python 3.8+** (check with `python3 --version`)
- **OpenAI API Key** (or another LLM provider)
- **Internet connection** (for API calls)

---

## Quick Start (5 Minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/James-von-Detroit/tars-ai.git
cd tars-ai/src
```

### 2. Install Python Dependencies
```bash
# Install only the core AI dependencies (skip robotics hardware libs)
pip3 install openai tiktoken sentence-transformers \
    flask-cors flask-socketio eventlet \
    requests python-dotenv hyperdb-python \
    bm25s pystemmer scikit-learn flashrank
```

**Minimal install for AI only:**
```bash
pip3 install openai tiktoken hyperdb-python requests python-dotenv flask flask-cors flask-socketio eventlet
```

### 3. Configure API Keys
```bash
# Copy environment template
cp ../.env.template ../.env

# Edit with your favorite editor
nano ../.env
```

Add your OpenAI API key:
```bash
OPENAI_API_KEY="sk-your-key-here"
```

### 4. Configure for macOS (No Hardware)
```bash
# Copy config template
cp config.ini.template config.ini

# Edit configuration
nano config.ini
```

**Key settings to change:**
```ini
[CONTROLS]
enabled = False
# Disable Bluetooth controller

[STT]
stt_processor = openai
# Use OpenAI Whisper API instead of local (simpler setup)
# OR set to 'external' if you want text-only

[TTS]
ttsoption = openai
# Use OpenAI TTS instead of local
# OR set to 'espeak' for basic macOS TTS (say command)

[VISION]
enabled = False
# Disable unless you want image analysis

[EMOTION]
enabled = False
# Disable unless you want emotion detection

[SERVO]
# Ignore all servo settings

[UI]
UI_enabled = False
# Disable the visual UI (designed for Raspberry Pi display)

[CHATUI]
enabled = True
# Enable web-based chat interface
```

### 5. Run TARS-AI
```bash
python3 app.py
```

---

## Access Methods

### Option 1: Web Chat Interface (Recommended for macOS)
Once running:
1. Open browser to: `http://localhost:5012`
2. Start chatting with TARS!

### Option 2: Text-Only Mode
If you don't want voice/audio:
```ini
[STT]
stt_processor = external  # No microphone input

[TTS]
ttsoption = espeak
voice_only = False  # Show text responses
```

### Option 3: Voice Interaction
For voice on macOS:
```ini
[STT]
stt_processor = openai  # Uses OpenAI Whisper API

[TTS]
ttsoption = openai  # Uses OpenAI TTS API
openai_voice = alloy  # Voice options: alloy, echo, fable, onyx, nova, shimmer
```

---

## Simplified macOS Configuration

Here's a complete minimal `config.ini` for macOS AI-only usage:

```ini
[CONTROLS]
controller_name = None
enabled = False
voicemovement = False

[STT]
language = english
wake_word = hey tars
sensitivity = 8
stt_processor = external  # No voice input, text only
external_url = http://localhost:5678
whisper_model = tiny
vosk_model = vosk-model-small-en-us-0.15
use_indicators = False
vad_method = rms
speechdelay = 20
picovoice_keyword_path = ../stt/hey-tars_en_raspberry-pi_v3_0_0.ppn
wake_word_processor = picovoice

[CHAR]
character_card_path = character/TARS/TARS.json
user_name = YourName
user_details = Species: Human. Gender: Male.
responses = ["Oh! You called?", "Took you long enough. Yes?", "Finally!"]

[LLM]
llm_backend = openai
base_url = https://api.openai.com
openai_model = gpt-4o-mini
override_encoding_model = cl100k_base
contextsize = 4000
max_tokens = 1000
temperature = 0.8
top_p = 0.9
seed = -1
systemprompt = Your task is to respond effectively and creatively within the given scenario. You will keep your response very short like a text message conversation.
instructionprompt = You are {char}. Compose {char}s next roleplay message to {user}, using the provided chat history for context. Keep your response short and in plain text only, no emojis or Ascii.
functioncalling = llm

[VISION]
enabled = False
server_hosted = False
base_url = http://localhost:5678

[EMOTION]
enabled = False
emotion_model = SamLowe/roberta-base-go_emotions

[TTS]
ttsoption = openai
azure_region = eastus
ttsurl = http://localhost:7852
toggle_charvoice = True
tts_voice = en-us-amy-low
voice_id = pBVPSZPo5LPLzGPgkXbH
model_id = eleven_multilingual_v2
voice_only = False
is_talking_override = False
is_talking = False
global_timer_paused = False
openai_voice = alloy

[CHATUI]
enabled = True

[RAG]
strategy = naive
vector_weight = 0.5
top_k = 5

[HOME_ASSISTANT]
enabled = False
url = http://homeassistant.local:8123

[DISCORD]
channel_id = 0
enabled = False

[SERVO]
MOVEMENT_VERSION = V2
portMain = 0
portForarm = 1
portHand = 2
starMain = 3
starForarm = 4
starHand = 5
portMainMin = 50
portForarmMin = 50
portHandMin = 50
portMainMax = 130
portForarmMax = 130
portHandMax = 130
starMainMin = 50
starForarmMin = 50
starHandMin = 50
starMainMax = 130
starForarmMax = 130
starHandMax = 130
upHeight = 130
neutralHeight = 90
downHeight = 50
forwardPort = 50
neutralPort = 90
backPort = 130
perfectPortoffset = 0
forwardStarboard = 130
neutralStarboard = 90
backStarboard = 50
perfectStaroffset = 0

[STABLE_DIFFUSION]
enabled = False
service = a1111
url = http://127.0.0.1:7860
prompt_prefix = 
prompt_postfix = 
seed = -1
sampler_name = DPM++ 2M
denoising_strength = 0.7
steps = 20
cfg_scale = 7
width = 512
height = 512
restore_faces = False
negative_prompt = 

[UI]
UI_enabled = False
UI_template = UI_classic
maximize_console = False
neural_net = False
neural_net_always_visible = False
screen_width = 480
screen_height = 800
rotation = 0
show_mouse = False
use_camera_module = False
background_id = 1
fullscreen = False
font_size = 16
target_fps = 30

[BATTERY]
battery_capacity_mAh = 10000
battery_initial_voltage = 12.6
battery_cutoff_voltage = 10.0
auto_shutdown = False
```

---

## Testing Your Setup

### 1. Start TARS
```bash
cd tars-ai/src
python3 app.py
```

### 2. Check for Errors
You should see:
```
LOAD: Script running from: /path/to/tars-ai/src
LOAD: Found existing memory: TARS.pickle.gz
LOAD: Memory loaded successfully
LOAD: ChatUI starting on port 5012...
LOAD: TARS-AI v4.0 running.
```

### 3. Open Web Interface
```bash
open http://localhost:5012
```

### 4. Send a Test Message
Type: "Hello TARS, can you hear me?"

Expected response: TARS should respond in character!

---

## Troubleshooting

### Import Errors
```bash
# Install missing dependencies
pip3 install [missing-package]
```

### Port Already in Use
```bash
# Kill process on port 5012
lsof -ti:5012 | xargs kill -9
```

### API Key Errors
- Check `.env` file has correct API key
- Verify key is active at https://platform.openai.com/api-keys
- Check you have credits/billing set up

### Module Import Errors for Hardware
If you see errors about `adafruit`, `evdev`, or `lgpio`:

**Option 1: Remove hardware imports**
Edit `app.py` and comment out hardware imports:
```python
# from modules.module_btcontroller import *
```

**Option 2: Mock installations**
```bash
# These won't work but will prevent import errors
pip3 install adafruit-circuitpython-pca9685 || true
```

---

## Development Tips

### Use Local LLM (No API Costs)
1. Install Ollama: `brew install ollama`
2. Download a model: `ollama pull llama2`
3. Start Ollama: `ollama serve`
4. Update `config.ini`:
```ini
[LLM]
llm_backend = ooba
base_url = http://localhost:11434/v1
openai_model = llama2
```

### Customize Character
Edit `/src/character/TARS/TARS.json` to change personality!

### Enable Memory Persistence
Memory is automatically saved to `/memory/TARS.pickle.gz`
- Survives restarts
- Gets smarter over time
- Can be cleared by deleting the file

### Monitor API Usage
```bash
# Watch your OpenAI usage
tail -f logs/app.log  # if logging enabled
```

---

## Cost Considerations

### OpenAI API (Recommended for macOS)
- **GPT-4o-mini**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **Typical conversation**: ~$0.001-0.01 per exchange
- **Daily casual use**: ~$0.10-1.00

### Free Alternatives
1. **Local LLM** (Ollama): Free but slower on macOS
2. **DeepInfra**: Free tier available
3. **Ooba/TabbyAPI**: Self-hosted, free

---

## Advanced Features

### Enable Vision
```bash
pip3 install transformers torch pillow
```
```ini
[VISION]
enabled = True
server_hosted = False
```
Now TARS can analyze images you show it!

### Enable Web Search
```bash
pip3 install selenium
```
TARS can search the web for information!

### Discord Bot
```ini
[DISCORD]
enabled = True
channel_id = your-channel-id
```
Add your Discord token to `.env` and TARS joins your server!

---

## Running as Background Service

### Using Screen
```bash
screen -S tars
cd tars-ai/src
python3 app.py
# Press Ctrl+A then D to detach
# screen -r tars to reattach
```

### Using tmux
```bash
brew install tmux
tmux new -s tars
cd tars-ai/src
python3 app.py
# Press Ctrl+B then D to detach
# tmux attach -t tars to reattach
```

---

## Next Steps

1. **Customize the personality** - Edit character files
2. **Train with conversations** - Chat more to build memory
3. **Explore different models** - Try GPT-4 for better responses
4. **Add integrations** - Connect to Home Assistant, Discord, etc.
5. **Develop features** - The codebase is clean and modular

---

## Summary

You now have a fully functional AI assistant running on your MacBook:
- ✅ Real LLM intelligence (GPT-4/3.5)
- ✅ Persistent memory
- ✅ Web chat interface
- ✅ Character personality
- ✅ Optional voice interaction
- ✅ No robotics hardware needed

**Enjoy your intelligent TARS AI companion!**
