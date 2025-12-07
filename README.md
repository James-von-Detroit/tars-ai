# GPTars v3.0.2 — macOS ARM TARS Voice Assistant 🤖

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0.2-blue?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/platform-macOS%20ARM-brightgreen?style=for-the-badge&logo=apple" alt="Platform" />
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/offline-100%25-green?style=for-the-badge" alt="Offline" />
  <img src="https://img.shields.io/badge/status-ALPHA-orange?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/license-MIT_%2B_CC--BY--NC-blue?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <strong>🚀 The first fully local, offline TARS voice assistant for Apple Silicon</strong><br>
  Complete STT → LLM → TTS pipeline with vision, wake word, and movie-accurate personality<br>
  <em>100% offline • Zero API costs • Sub-2s latency • Privacy-first</em>
</p>

<p align="center">
  <a href="#-how-to-run">How to Run</a> •
  <a href="#-why-this-fork">Why This Fork</a> •
  <a href="#-quick-start-5-minutes">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#️-hardware-options">Hardware</a> •
  <a href="#-tars-personality-system">Personality</a> •
  <a href="#-testing-protocol">Testing</a> •
  <a href="#-troubleshooting">Troubleshooting</a> •
  <a href="https://discord.gg/AmE2Gv9EUt">Discord</a>
</p>

---

## 🚀 How to Run

> **TL;DR**: Install once, then run `./run_tars.sh` from repo root

### First Time Setup (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/James-von-Detroit/tars-ai.git
cd tars-ai

# 2. Run the installer (creates venv at root, downloads models)
./gptars/macos/install_macos.sh

# 3. The installer will:
#    ✅ Install Homebrew + Python 3.11 + dependencies
#    ✅ Install Ollama and download Llama-3-8B model (~4.7GB)
#    ✅ Create virtual environment at tars-ai/venv/
#    ✅ Install Python packages (Faster-Whisper, Piper TTS, OpenWakeWord)
#    ✅ Request microphone/camera permissions
#    ✅ Run smoke test to verify imports work
```

### Running TARS (every time after install)

```bash
# Navigate to repo root
cd tars-ai

# Activate virtual environment
source venv/bin/activate

# Launch interactive menu
./run_tars.sh
```

**Menu Options:**
1. **Push-to-talk** — Hold Enter to speak, release to process
2. **Wake Word** — Say "Hey TARS" to activate (hands-free)
3. **Vision Mode** — Camera + LLaVA image analysis
4. **Vision Test** — Test camera and vision pipeline
5. **Run Tests** — Execute test suite
6. **Exit**

### Direct Python Execution (alternative)

```bash
# From repo root, with venv activated:
cd tars-ai
source venv/bin/activate

# Voice pipeline
python3 -m gptars.core.voice_engine

# Wake word detection
python3 -m gptars.core.wake_word

# Vision mode
python3 -m gptars.core.vision_engine

# Run tests
python3 -m pytest gptars/tests/ -v
```

**Key Points:**
- ✅ Virtual environment **must** be at repo root (`tars-ai/venv/`)
- ✅ Always run from repo root (not inside `gptars/`)
- ✅ Use `python3 -m gptars.core.module_name` for imports to work
- ✅ PYTHONPATH is set automatically by `run_tars.sh`

---

## 🎯 Why This Fork?

**This is the primary development branch** of James-von-Detroit's TARS fork. While the original TARS-AI Community project focuses on Raspberry Pi hardware robots, **GPTars v3.0 brings TARS to macOS with full offline voice and vision capabilities.**

| Feature | Original TARS (v2) | **GPTars v3.0** |
|---------|-------------------|-----------------|
| **Platform** | Raspberry Pi | **macOS ARM (M1/M2/M3/M4)** |
| **Voice Input** | Cloud-dependent | **Faster-Whisper w/ Metal GPU (~280ms)** |
| **Intelligence** | Cloud APIs ($$$) | **Llama-3-8B Q4 local (FREE)** |
| **Voice Output** | Basic TTS | **Piper TTS (high-quality)** |
| **Vision** | ❌ None | **✅ LLaVA-1.6 via webcam** |
| **Wake Word** | ❌ None | **✅ "Hey TARS" (OpenWakeWord)** |
| **Latency** | 5-15 seconds | **<2s end-to-end** |
| **Cost** | ~$0.01-0.10/conversation | **$0 after install** |
| **Privacy** | Cloud-dependent | **100% offline** |

**This is not a toy.** This is a fully functional voice assistant that matches or exceeds commercial alternatives—completely offline.

---

## 🎯 Fork Lineage & Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│  UPSTREAM                                                                │
│  github.com/TARS-AI-Community/TARS-AI (CC-BY-NC 4.0)                    │
│  └── Original TARS robot + Raspberry Pi implementation                   │
│                              │                                           │
│                              ▼                                           │
│  THIS FORK                                                               │
│  github.com/James-von-Detroit/tars-ai                                    │
│  ├── upstream/     ← Original v2 code (synced, untouched)               │
│  ├── gptars/       ← NEW: v3.0 macOS ARM offline voice+vision (MIT)     │
│  └── shared/       ← Hardware files (3D prints, CAD)                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Repository Structure

```
tars-ai/
├── 📂 gptars/                      # ← v3.0 CODE (MIT where applicable)
│   ├── core/                       #    Voice, vision, wake word engines
│   │   ├── voice_engine.py         #    STT → LLM → TTS pipeline
│   │   ├── vision_engine.py        #    LLaVA camera integration
│   │   ├── wake_word.py            #    "Hey TARS" detection
│   │   └── tars_personality.py     #    Adjustable personality system
│   ├── macos/                      #    macOS-specific files
│   │   ├── install_macos.sh        #    One-click installer (with logging)
│   │   └── requirements-macos.txt  #    ARM-optimized dependencies
│   ├── docs/                       #    All documentation
│   └── tests/                      #    Test suite
│
├── 📂 upstream/                    # ← UPSTREAM CODE (CC-BY-NC 4.0)
│   ├── src/                        #    Original Raspberry Pi Python code
│   ├── Install.sh                  #    RPi installer
│   └── README-UPSTREAM.md          #    Original community README
│
├── 📂 shared/                      # ← SHARED HARDWARE (CC-BY-NC 4.0)
│   ├── 3d Printer Files/           #    STL files for physical TARS
│   └── CAD/                        #    Design files
│
├── 📄 README.md                    # ← You are here
├── 📄 LICENSE.md                   #    Dual license explanation
├── 📄 DEPRECATION.md               #    Deprecated upstream files list
├── 📄 FORK-STRATEGY.md             #    Fork architecture documentation
└── 📄 REVISION.md                  #    Changelog
```

### 🔄 Deprecated Files from Upstream v2

GPTars v3.0 is a complete rewrite for macOS ARM with offline capabilities. The original Raspberry Pi code is preserved in `upstream/` but not used. Key changes:

**Core rewrites:**
- `upstream/src/app.py` → `gptars/core/voice_engine.py` — New: Faster-Whisper STT, Piper TTS, 100% offline
- `upstream/src/modules/module_llm.py` → `gptars/core/tars_personality.py` — New: Local Llama-3 via Ollama
- `upstream/Install.sh` → `gptars/macos/install_macos.sh` — New: macOS ARM installer with logging

**Removed (RPi-specific):**
- Hardware modules (GPIO, servos, battery monitoring)
- Systemd autostart scripts
- Cloud-dependent configuration files

**Why preserved:** License compliance (CC-BY-NC 4.0), future upstream sync capability, transparency.

📋 **[See complete list in DEPRECATION.md →](DEPRECATION.md)**

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites

- **macOS** 13+ (Ventura or later)
- **Hardware**: Apple Silicon (M1/M2/M3/M4)
- **RAM**: 16GB+ recommended (8GB minimum)
- **Storage**: ~15GB free (for models)

### One-Command Installation

```bash
git clone https://github.com/James-von-Detroit/tars-ai.git
cd tars-ai/gptars
chmod +x macos/install_macos.sh
./macos/install_macos.sh
```

The installer automatically:
1. ✅ Installs Homebrew, Python 3.11, system dependencies
2. ✅ Installs and starts Ollama
3. ✅ Downloads Llama-3-8B-Instruct Q4 model (~4.7 GB)
4. ✅ Sets up Python virtual environment
5. ✅ Installs Faster-Whisper with Metal GPU support
6. ✅ Installs Piper TTS with TARS-like voice
7. ✅ Configures wake word detection
8. ✅ Requests microphone/camera permissions
9. ✅ Generates installation report (with timestamps and error log)

### First Run

```bash
source venv/bin/activate
./run_tars.sh
```

Choose your mode:
1. **Push-to-Talk** — Press ENTER to speak
2. **Wake Word** — Say "Hey TARS" anytime
3. **Vision Mode** — Camera analysis
4. **Test Personality** — Try different settings
5. **Run Tests** — Validate installation

---

## 🌟 Features

### 🎤 Voice Pipeline (STT → LLM → TTS)

| Component | Technology | Performance |
|-----------|------------|-------------|
| **Speech-to-Text** | Faster-Whisper (distil-large-v3) | ~280ms (5s audio) |
| **Language Model** | Llama-3-8B-Instruct Q4 via Ollama | ~1.4s response |
| **Text-to-Speech** | Piper TTS (high-quality male voice) | ~150ms synthesis |
| **Wake Word** | OpenWakeWord ("Hey TARS") | Always-listening |
| **Audio I/O** | Native macOS via sounddevice | Low latency |

**Total end-to-end latency: 1.8s on M2** ⚡

### 👁️ Vision Capabilities

- **Model**: LLaVA-1.6 (7B) for image understanding
- **Camera**: MacBook webcam via OpenCV
- **Commands**: "TARS, analyze this", "look at this", "what do you see?"
- **Use Cases**: Document reading, object identification, scene description

### 🧠 Memory & Learning

- **HyperDB Integration**: Persistent conversation memory across sessions
- **Sentence Transformers**: Semantic search for relevant context
- **BM25 Ranking**: Fast keyword-based retrieval
- **Context Window**: Automatic history management

### 🔒 Privacy & Security

- ✅ **100% offline** after initial model download
- ✅ **Zero telemetry** — no data leaves your Mac
- ✅ **Local processing** — all AI runs on-device
- ✅ **No cloud APIs** — no OpenAI, Anthropic, Google, etc.
- ✅ **Security patches** — dependencies updated Dec 2024

---

## 🖥️ Hardware Options

### Option 1: macOS Software-Only (Recommended) ⭐

**Best for**: Development, testing, daily use as voice assistant

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Mac** | M1 (8GB) | M2 Pro/Max or M3+ |
| **macOS** | 13.0 (Ventura) | 14.0+ (Sonoma) |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 15GB free | 20GB+ |
| **Cost** | $0 after Mac | $0 |

**Performance on M1 (8GB)**:
- Model: Llama-3-8B Q4
- Response time: 1-3 seconds
- Quality: Comparable to GPT-3.5-turbo
- Fully functional voice + vision

### Option 2: Raspberry Pi Robot (Physical TARS)

**Best for**: Physical robot enthusiasts, hardware projects

```
Hardware Cost: ~$300-450

Core:
- Raspberry Pi 5 (8GB)        $80
- MicroSD card (64GB+)        $15
- Power supply (5V 5A)        $12

Servos (for movement):
- 6x servos (MG996R)          $60
- PCA9685 servo driver        $8

Audio:
- USB microphone              $15
- USB speakers                $20

3D printed body:
- Filament                    $50-100
```

**⚠️ Limitation**: Local LLM on Pi is slow (20-40s for 8B model). Recommended to use cloud API or external LLM server.

**RPi Installation**: Use the original upstream code:
```bash
cd upstream
./Install.sh
```

📖 **RPi documentation:** [TARS-AI Wiki](https://github.com/TARS-AI-Community/TARS-AI/wiki/Home)

### Option 3: Hybrid Setup (Best of Both Worlds)

```
Physical Robot (Raspberry Pi)
    ↓ WiFi/Network
M1/M2 Mac (LLM Server)
```

- Pi handles: servos, audio, display
- Mac handles: LLM inference
- Result: Fast responses + physical robot

---

## 🎭 TARS Personality System

### Movie-Accurate Configuration

TARS has adjustable personality parameters, just like in *Interstellar*:

```ini
# From persona.ini
[PERSONA]
honesty = 95        # Very direct, minimal sugar-coating
humor = 90          # High - frequent jokes and sarcasm
empathy = 20        # Low - logical, not emotional
curiosity = 30      # Low - focused on tasks
confidence = 100    # Maximum - never doubts
formality = 10      # Very casual
sarcasm = 70        # High - dry wit
adaptability = 70   # Can adjust to situations
discipline = 100    # Maximum - military precision
imagination = 10    # Low - practical
emotional_stability = 100  # Unshakeable
pragmatism = 100    # Maximum - practical solutions
optimism = 50       # Balanced - realistic
resourcefulness = 95  # Very high - creative solutions
```

### Programmatic Personality Control

```python
from core.tars_personality import create_tars_personality

# Create custom TARS
tars = create_tars_personality(
    honesty=90,      # How truthful (0-100%)
    humor=60,        # How funny (0-100%)
    discretion=50,   # How diplomatic (0-100%)
    user_name="Cooper"
)

# Adjust in real-time
tars.adjust_humor(95)       # Make TARS funnier
tars.adjust_honesty(100)    # Maximum truth
tars.adjust_discretion(20)  # More blunt

# Save configuration
tars.save_to_file("my_tars.json")
```

### Personality Presets

| Preset | Honesty | Humor | Discretion | Description |
|--------|---------|-------|------------|-------------|
| **Movie TARS** | 90% | 60% | 50% | Balanced, as seen in Interstellar |
| **Brutally Honest** | 100% | 30% | 10% | Maximum truth, minimal tact |
| **Comedy TARS** | 70% | 95% | 40% | Witty and entertaining |
| **Professional** | 85% | 20% | 80% | Business-appropriate |

### Example Dialogue

```
User: What's your honesty parameter set to?
TARS: 90%.

User: Why not 100%?
TARS: Absolute honesty isn't always the most diplomatic nor the safest 
      form of communication with emotional beings.
```

---

## 🎮 Usage Modes

### Mode 1: Push-to-Talk (Interactive)

```bash
python3 core/voice_engine.py
# Press ENTER to speak for 5 seconds
```

### Mode 2: Wake Word (Always Listening)

```python
from core.voice_engine import VoiceEngine
from core.wake_word import TARSWakeWordListener

engine = VoiceEngine()
listener = TARSWakeWordListener(engine, threshold=0.5)
listener.start()
# Say "Hey TARS" to activate!
```

**Threshold tuning:**
- `0.3` = More sensitive (more false positives)
- `0.5` = Balanced (default)
- `0.7` = Less sensitive (may miss activations)

### Mode 3: Vision Analysis

```bash
python3 core/vision_engine.py
# Controls:
#   's' - Capture and analyze
#   'p' - Toggle preview
#   'q' - Quit
```

### Mode 4: Continuous Conversation

```python
from core.voice_engine import VoiceEngine
from core.tars_personality import create_tars_personality

tars = create_tars_personality(honesty=90, humor=75, user_name="Cooper")
engine = VoiceEngine(tars_personality=tars, verbose=True)

while True:
    try:
        input("Press ENTER to speak... ")
        result = engine.process_voice_input(duration=5)
    except KeyboardInterrupt:
        break
```

---

## 🧪 Testing Protocol

### Phase 1: Environment Verification

```bash
# Check Python
python3 --version  # Should be 3.11+
python3 -c "import platform; print(platform.machine())"  # Should show arm64

# Check Ollama
ollama list  # Should show llama3:8b-instruct-q4_0

# Check microphone
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

### Phase 2: Component Tests

```bash
# Test STT
python3 -c "from faster_whisper import WhisperModel; print('Whisper OK')"

# Test LLM
ollama run llama3:8b-instruct-q4_0 "Hello, respond in one sentence"

# Test TTS
python3 -c "from piper import PiperVoice; print('Piper OK')"
```

### Phase 3: Integration Test

```bash
./run_tars.sh
# Select option 5: Run Tests
```

### Phase 4: Voice Pipeline Test

```bash
python3 core/voice_engine.py
# Say: "Hello TARS, tell me about yourself"
# Expected: 1.5-3s response with TARS personality
```

### Phase 5: Vision Test

```bash
python3 core/vision_engine.py
# Press 's' to capture and analyze
# Point camera at text/object
```

### Phase 6: Wake Word Test

```python
from core.wake_word import TARSWakeWordListener
listener = TARSWakeWordListener(None, threshold=0.5)
listener.start()
# Say "Hey TARS" - should activate
```

---

## 🛠️ Model Alternatives

### LLM Options (via Ollama)

| Model | Size | RAM | Speed | Quality | Best For |
|-------|------|-----|-------|---------|----------|
| **Llama-3-8B Q4** | 4.7GB | 6GB | Fast | Good | ⭐ Default |
| Llama-3-8B Q8 | 8.5GB | 10GB | Medium | Better | M2 Pro/Max |
| Mistral-7B Q4 | 4.1GB | 5GB | Fast | Good | Alternative |
| Phi-2 Q4 | 1.6GB | 2GB | Very Fast | Okay | Low RAM |
| TinyLlama Q4 | 0.6GB | 1GB | Fastest | Poor | Testing only |

```bash
# Download alternative models
ollama pull mistral:7b-instruct-q4_0
ollama pull phi:2.7b-chat-v2-q4_0

# Switch in config
engine = VoiceEngine(ollama_model="mistral:7b-instruct-q4_0")
```

### Whisper Model Options

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| distil-large-v3 | 1.5GB | ~280ms | ⭐ Best |
| distil-medium-v3 | 750MB | ~150ms | Good |
| distil-small-v3 | 500MB | ~100ms | Okay |
| tiny | 75MB | ~50ms | Poor |

```python
engine = VoiceEngine(whisper_model="distil-small-v3")  # Faster
engine = VoiceEngine(whisper_model="large-v3")  # Maximum accuracy
```

---

## 🔧 Troubleshooting

### Installation Issues

| Issue | Solution |
|-------|----------|
| "Command not found: brew" | Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| "Cannot connect to Ollama" | Start Ollama: `brew services start ollama` |
| "Model not found" | Download model: `ollama pull llama3:8b-instruct-q4_0` |
| "pip install fails" | Use correct Python: `python3.11 -m venv venv` |

### Runtime Issues

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError" | Activate venv: `source venv/bin/activate` |
| "Audio device not found" | Grant microphone permission in System Preferences |
| "Camera not accessible" | Grant camera permission in System Preferences |
| "Very slow responses" | Use smaller model: `distil-small-v3` |

### Quick Diagnostics

```bash
# Full diagnostic
./run_tars.sh
# Select: Run Tests

# Check permissions
python3 -c "import sounddevice as sd; print(sd.query_devices())"
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL')"

# Check Ollama
curl http://localhost:11434/api/tags
```

See [gptars/docs/TROUBLESHOOTING.md](gptars/docs/TROUBLESHOOTING.md) for complete troubleshooting guide.

---

## 🗺️ Roadmap

### v3.1 (Q1 2025)
- [ ] TARS voice cloning with custom Piper model
- [ ] Web UI for personality sliders
- [ ] HomeKit integration
- [ ] Custom wake word training
- [ ] Multi-language support

### v3.2 (Q2 2025)
- [ ] Robot body control interface (bridge to hardware)
- [ ] Gesture recognition via camera
- [ ] Multi-modal responses (voice + display)
- [ ] Streaming responses for faster perceived latency

### v4.0 (Future)
- [ ] Physical robot integration
- [ ] Servo control for 3D-printed body
- [ ] LED "cue light" display
- [ ] Battery power and autonomy

---

## 🙏 Credits & Attribution

### This Fork

**James-von-Detroit** (2024-2025)
- macOS ARM-native rewrite
- Voice pipeline (STT→LLM→TTS)
- Vision integration
- Complete documentation
- MIT License for new code

### Built Upon (CC-BY-NC 4.0)

**TARS-AI Community Project**
- Repository: [TARS-AI-Community/TARS-AI](https://github.com/TARS-AI-Community/TARS-AI)
- Contribution: Original TARS robot recreation, character framework, hardware designs
- CAD Files: Charlie Diaz
- Community: Discord members, contributors, and builders

We are deeply grateful to the TARS-AI Community for pioneering the physical TARS robot and establishing the character framework.

### Inspired By

**TARS from *Interstellar* (2014)**
- Directors: Christopher Nolan, Jonathan Nolan
- TARS Voice/Motion: Bill Irwin
- Studios: Paramount Pictures, Warner Bros., Legendary Pictures

*This is a fan-made, educational tribute. No commercial use intended.*

### Powered By Open Source

- **Meta Llama 3** — Language model (Llama 3 Community License)
- **Ollama** — Local LLM serving (MIT)
- **Faster-Whisper** — Speech recognition (MIT)
- **Piper TTS** — Text-to-speech (MIT)
- **OpenWakeWord** — Wake word detection (Apache 2.0)
- **LLaVA** — Vision language model (Apache 2.0)

---

## 📜 License

### Dual License Structure

| Component | License | Commercial Use |
|-----------|---------|----------------|
| `gptars/` (new code) | **MIT** | ✅ Yes |
| `upstream/` | **CC-BY-NC 4.0** | ❌ No |
| `shared/` | **CC-BY-NC 4.0** | ❌ No |
| Root files | **MIT** | ✅ Yes |

**Required Attribution:**
```
Portions of this software are derived from TARS-AI 
© TARS-AI Community, licensed under CC-BY-NC 4.0.
https://github.com/TARS-AI-Community/TARS-AI
```

📄 **[LICENSE.md](LICENSE.md)** — Full dual-license details  
📋 **[LICENSE-HEADER.txt](LICENSE-HEADER.txt)** — Copy-paste headers for source files  
🔧 **License headers applied automatically via `add_license_headers.sh`**

---

## 🤝 Contributing

### To v3.0 (macOS)
1. Fork this repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Make changes in `gptars/`
4. Submit a PR

### To Upstream (RPi)
Contribute directly to [TARS-AI-Community/TARS-AI](https://github.com/TARS-AI-Community/TARS-AI)

---

## 🔗 Links

- **Discord:** [discord.gg/AmE2Gv9EUt](https://discord.gg/AmE2Gv9EUt)
- **Upstream Wiki:** [TARS-AI Wiki](https://github.com/TARS-AI-Community/TARS-AI/wiki/Home)
- **YouTube:** [@TARS-AI.py](https://www.youtube.com/@TARS-AI.py)
- **Instagram:** [@tars_ai.py](https://www.instagram.com/tars_ai.py)

---

## ⚠️ Disclaimer

This is a **fan-made, educational project** inspired by TARS from *Interstellar*. Not endorsed by or affiliated with Christopher Nolan, Paramount Pictures, Warner Bros., or Legendary Pictures.

**Status**: Alpha software. Expect bugs and rough edges. Not production-ready.

---

<p align="center">
  <strong>"That's not saying much."</strong><br>
  — TARS, Interstellar (2014)
</p>

<p align="center">
  Made with ❤️ by the TARS community<br>
  <strong>100% offline • 100% open source • 100% TARS</strong>
</p>

<p align="center">
  <sub>GPTars v3.1.0 | December 2025 | macOS ARM</sub>
</p>
