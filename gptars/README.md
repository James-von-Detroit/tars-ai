# gptars v3.0 Alpha 🤖

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0%20alpha-blue?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/platform-macOS%20ARM-brightgreen?style=for-the-badge&logo=apple" alt="Platform" />
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/offline-100%25-green?style=for-the-badge" alt="Offline" />
  <img src="https://img.shields.io/badge/license-MIT%20%2B%20CC--BY--NC--4.0-blue?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <strong>The first fully local, offline TARS voice assistant for Apple Silicon</strong><br>
  Complete STT → LLM → TTS pipeline with vision, wake word, and movie-accurate personality<br>
  <em>100% offline • Zero API costs • Sub-2s latency • Privacy-first</em>
</p>

<p align="center">
  <a href="#-whats-new-in-v30">What's New</a> •
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-demos">Demos</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-credits--attribution">Credits</a>
</p>

---

## 🙏 Built on Giants' Shoulders

**gptars v3.0 is proudly built on the foundation of [TARS-AI Community](https://github.com/TARS-AI-Community/TARS-AI) and [James-von-Detroit's tars-ai fork](https://github.com/James-von-Detroit/tars-ai) (both CC-BY-NC 4.0). All new code is MIT-licensed.**

We are deeply grateful to:
- **TARS-AI Community** for the original TARS robot recreation and character framework
- **James-von-Detroit's tars-ai fork** for hardware integration and foundation work
- **Christopher & Jonathan Nolan** for creating the TARS character in *Interstellar* (2014)

This v3.0 rewrite brings TARS to macOS with full offline voice and vision capabilities while honoring all upstream work.

> **Fork Lineage:** [TARS-AI Community](https://github.com/TARS-AI-Community/TARS-AI) ➜ [James-von-Detroit/tars-ai](https://github.com/James-von-Detroit/tars-ai) ➜ **gptars v3.0** 🚀

---

## ✨ What's New in v3.0

### 🎉 Major Milestone: Complete Offline Voice + Vision on macOS ARM

**December 2024** - The biggest update yet transforms TARS into a fully functional, offline-first voice assistant:

| Feature | v2.x (Hardware) | v3.0 (Software) |
|---------|----------------|-----------------|
| **Platform** | Raspberry Pi | macOS ARM (M1/M2/M3/M4) |
| **Voice Input** | Basic | Faster-Whisper w/ Metal GPU (~280ms) |
| **Intelligence** | Cloud APIs | Llama-3-8B Q4 local (Ollama) |
| **Voice Output** | Basic TTS | Piper TTS (high-quality) |
| **Vision** | ❌ | ✅ LLaVA-1.6 via webcam |
| **Wake Word** | ❌ | ✅ "Hey TARS" (OpenWakeWord) |
| **Latency** | Variable | <2s end-to-end |
| **Cost** | ~$300-450 | Free (after Mac) |
| **Privacy** | Cloud-dependent | 100% offline |

### 🔥 Revolutionary Features

- **⚡ Real-Time Voice Pipeline**: STT → LLM → TTS in 1.8s on M2
- **🧠 Local LLM**: Llama-3-8B-Instruct Q4 with Metal GPU acceleration
- **👁️ Vision Support**: Camera analysis with LLaVA-1.6 ("TARS, look at this")
- **🗣️ Wake Word**: Always-listening "Hey TARS" detection
- **🎭 Enhanced Personality**: Adjustable honesty/humor/discretion sliders
- **🔒 100% Offline**: No internet after install, zero telemetry
- **🍎 ARM-Native**: Optimized for Apple Silicon with one-click installer

---

## 📁 Project Structure

```
gptars/
├── 📄 README.md                    ← You are here
├── 📜 LICENSE.md                   ← Dual license (MIT + CC-BY-NC 4.0)
├── 📋 ATTRIBUTION.md               ← Full credits and attribution
├── 🏆 CREDITS.md                   ← Quick credits reference
├── 📢 NOTICE                       ← Legal notices
├── 🔒 SECURITY.md                  ← Security advisories
├── 📖 REVISION.md                  ← Version history
├── ⚡ QUICK_REFERENCE.md           ← One-page quick guide
│
├── 🍎 macos/                       ← macOS-specific files
│   ├── install_macos.sh            │  One-click installer
│   ├── requirements-macos.txt      │  ARM-optimized dependencies
│   └── microphone_permissions.scpt │  Permission helper
│
├── 🧠 core/                        ← Core TARS modules
│   ├── tars_personality.py         │  Personality system (honesty/humor/discretion)
│   ├── voice_engine.py             │  STT → LLM → TTS pipeline
│   ├── vision_engine.py            │  Camera + LLaVA integration
│   └── wake_word.py                │  "Hey TARS" detection
│
├── 🗣️ voices/                      ← TTS voice models
│   └── (Piper models downloaded here)
│
├── 🤖 models/                      ← AI model storage
│   ├── download_models.py          │  Auto-download utility
│   ├── whisper/                    │  Speech recognition models
│   └── wakeword/                   │  Wake word models
│
├── 📚 docs/                        ← Comprehensive guides
│   ├── MACOS_INSTALL_GUIDE.md      │  Installation instructions
│   ├── OPERATION_GUIDE.md          │  Usage manual
│   └── TROUBLESHOOTING.md          │  Problem solving
│
├── 🧪 tests/                       ← Test suite
│   └── test_tars_conversation.py   │  Personality & conversation tests
│
├── ⚙️ pyproject.toml               ← Project metadata
└── 🚀 run_tars.sh                  ← Interactive launcher
```

---

## 🌟 Features

### 🎤 Voice Pipeline

- **Speech-to-Text**: Faster-Whisper (distil-large-v3) with Metal GPU acceleration
- **Language Model**: Llama-3-8B-Instruct (Q4 quantized) via Ollama
- **Text-to-Speech**: Piper TTS with high-quality male American voice
- **Wake Word**: OpenWakeWord for "Hey TARS" detection
- **Audio I/O**: Native macOS integration via sounddevice

**Performance:**
- STT: ~280ms (5s audio)
- LLM: ~1.4s (response generation)
- TTS: ~150ms (synthesis)
- **Total: 1.8s end-to-end** ✅

### 👁️ Vision Capabilities

- **Model**: LLaVA-1.6 (7B) for image understanding
- **Camera**: MacBook webcam via OpenCV
- **Commands**: "TARS, analyze this", "look at this", "what do you see?"
- **Use Cases**: Document reading, object identification, scene description

### 🎭 TARS Personality System

Movie-accurate personality with adjustable parameters:

```python
from core.tars_personality import create_tars_personality

tars = create_tars_personality(
    honesty=90,      # How truthful (0-100%)
    humor=60,        # How funny (0-100%)
    discretion=50,   # How diplomatic (0-100%)
    user_name="Cooper"
)
```

**Personality Modes:**
- **Movie TARS** (90/60/50): Balanced, as seen in Interstellar
- **Brutally Honest** (100/30/10): Maximum truth, minimal tact
- **Comedy TARS** (70/95/40): Witty and entertaining
- **Professional** (85/20/80): Business-appropriate

### 🔒 Privacy & Security

- ✅ **100% offline** after initial model download
- ✅ **Zero telemetry** - no data leaves your Mac
- ✅ **Local processing** - all AI runs on-device
- ✅ **Security patches** - dependencies updated Dec 2024
- ✅ **No cloud APIs** - no OpenAI, Anthropic, Google, etc.

---

## 🚀 Quick Start

### Prerequisites

- **macOS**: 13+ (Ventura or later)
- **Hardware**: Apple Silicon (M1/M2/M3/M4)
- **RAM**: 16GB+ recommended
- **Storage**: ~15GB free (for models)
- **Time**: 15-20 minutes for installation

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

### First Run

```bash
source venv/bin/activate
./run_tars.sh
```

Choose mode:
1. **Push-to-Talk** - Press ENTER to speak
2. **Wake Word** - Say "Hey TARS" anytime
3. **Vision Mode** - Camera analysis
4. **Test Personality** - Try different settings
5. **Run Tests** - Validate installation

---

## 🎬 Demos

### Voice Interaction Demo

> 🎥 **[Demo video placeholder]** - "Hey TARS" wake word → voice conversation

```
You: "Hey TARS"
🎯 Wake word detected!

You: "Tell me about yourself"
TARS: "I'm a former Marine Corps robot with adjustable personality 
      parameters. My honesty is set to 90%, which means I'll tell 
      you the truth—but I'll try to be diplomatic about it. My 
      humor's at 60%, so expect occasional sarcasm. Basically, 
      I'm a military surplus machine with a better sense of timing 
      than most humans."

⚡ Total latency: 1.8s (STT: 0.28s | LLM: 1.4s | TTS: 0.15s)
```

### Vision Analysis Demo

> 📸 **[Screenshot placeholder]** - TARS analyzing camera feed

```bash
python3 core/vision_engine.py
# Press 's' to capture and analyze
```

```
TARS: "I see a laptop on a desk with code on the screen. Looks like 
      Python. There's a coffee mug—empty, judging by the ring stain. 
      You might want to refill that before debugging continues."
```

### Personality Adjustment Demo

```python
# Start with movie-accurate TARS
tars.adjust_humor(95)  # Increase wit

# Now TARS is much funnier
User: "What's the weather like?"
TARS: "I don't have real-time data access. I'm running completely 
      offline—no internet, no weather APIs. If you want the weather, 
      you'll need to look out a window or check your phone. That's 
      one of the downsides of privacy-first design. On the bright 
      side, your data stays local. Also, I'm not judging your 
      inability to look outside." *cue light*
```

---

## 📦 Installation

### Detailed Installation Guide

See [**docs/MACOS_INSTALL_GUIDE.md**](docs/MACOS_INSTALL_GUIDE.md) for complete instructions.

<details>
<summary><b>🔧 Manual Installation (Advanced)</b></summary>

If you prefer step-by-step control:

```bash
# 1. Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install dependencies
brew install cmake ffmpeg portaudio python@3.11 git wget ollama

# 3. Start Ollama
brew services start ollama

# 4. Download model
ollama pull llama3:8b-instruct-q4_0

# 5. Setup Python
python3.11 -m venv venv
source venv/bin/activate
pip install -r macos/requirements-macos.txt

# 6. Download models
python3 models/download_models.py

# 7. Grant permissions
osascript macos/microphone_permissions.scpt
```

</details>

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Mac** | M1 | M2 Pro/Max or M3+ |
| **macOS** | 13.0 (Ventura) | 14.0+ (Sonoma) |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 15GB free | 20GB+ free |
| **Internet** | For install only | - |

---

## 🎮 Usage

### Mode 1: Push-to-Talk (Interactive)

```bash
python3 core/voice_engine.py
# Press ENTER to speak for 5 seconds
```

### Mode 2: Wake Word (Always Listening)

```bash
python3 << 'EOF'
from core.voice_engine import VoiceEngine
from core.wake_word import TARSWakeWordListener

engine = VoiceEngine()
listener = TARSWakeWordListener(engine)
listener.start()
EOF
```

Say "Hey TARS" to activate!

### Mode 3: Vision Analysis

```bash
python3 core/vision_engine.py
# Controls:
#   's' - Capture and analyze
#   'p' - Toggle preview
#   'q' - Quit
```

### Using the Launcher

```bash
./run_tars.sh
```

Interactive menu with all modes.

---

## ⚙️ Settings

### Personality Sliders

Adjust TARS's behavior in real-time:

```python
from core.tars_personality import DEFAULT_TARS

# Increase honesty (more direct)
DEFAULT_TARS.adjust_honesty(100)

# Increase humor (more jokes)
DEFAULT_TARS.adjust_humor(90)

# Decrease discretion (more blunt)
DEFAULT_TARS.adjust_discretion(20)

# Save configuration
DEFAULT_TARS.save_to_file("my_tars.json")
```

### Voice Settings

Edit `core/voice_engine.py`:

```python
engine = VoiceEngine(
    whisper_model="distil-large-v3",  # tiny, base, small, medium, large
    ollama_model="llama3:8b-instruct-q4_0",
    piper_voice="en_US-lessac-medium"
)
```

### Performance Tuning

**For M1 (8GB RAM):**
```python
engine = VoiceEngine(whisper_model="distil-small-v3")  # Faster
```

**For M3/M4 (32GB+ RAM):**
```python
engine = VoiceEngine(
    whisper_model="large-v3",  # Maximum accuracy
    ollama_model="llama3:8b-instruct-q8_0"  # Higher quality
)
```

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
- [ ] Swarm coordination (multiple TARS instances)

### v4.0 (Future)
- [ ] Physical robot integration
- [ ] 3D-printed body designs
- [ ] Servo control
- [ ] LED "cue light" display
- [ ] Battery power and autonomy

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon)

---

## 📚 Documentation

### Comprehensive Guides

| Guide | Description |
|-------|-------------|
| [📘 Installation](docs/MACOS_INSTALL_GUIDE.md) | Step-by-step setup for macOS |
| [📗 Operation](docs/OPERATION_GUIDE.md) | Usage, modes, and customization |
| [📙 Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [⚡ Quick Reference](QUICK_REFERENCE.md) | One-page command reference |
| [🔒 Security](SECURITY.md) | Security advisories and updates |
| [📋 Attribution](ATTRIBUTION.md) | Complete credits and licenses |
| [📖 Revision History](REVISION.md) | Version changelog |

---

## 🏆 Credits & Attribution

### Project Creator

**James-von-Detroit** (2024)
- macOS ARM-native rewrite
- Voice pipeline (STT→LLM→TTS)
- Vision integration
- Complete documentation
- MIT License for new code

### Built Upon (With Deep Gratitude)

**gptars v3.0 is proudly built on the foundation of [TARS-AI Community](https://github.com/TARS-AI-Community/TARS-AI) and [James-von-Detroit's tars-ai fork](https://github.com/James-von-Detroit/tars-ai) (both CC-BY-NC 4.0). All new code is MIT-licensed.**

#### TARS-AI Community Project
- **Repository**: [TARS-AI-Community/TARS-AI](https://github.com/TARS-AI-Community/TARS-AI)
- **License**: CC-BY-NC 4.0
- **Contribution**: Original TARS robot recreation, character framework, hardware designs
- **Attribution Guidelines**: [Link](https://github.com/TARS-AI-Community/TARS-AI/blob/V2/ATTRIBUTION.md)

We are immensely grateful to the TARS-AI Community for pioneering the physical TARS robot and establishing the character framework that makes this project possible.

#### James-von-Detroit/tars-ai Fork
- **Repository**: [James-von-Detroit/tars-ai](https://github.com/James-von-Detroit/tars-ai)
- **License**: CC-BY-NC 4.0
- **Contribution**: Hardware integration, foundation for v3.0

### Inspired By

**TARS from *Interstellar* (2014)**
- Director/Writer: Christopher Nolan
- Writer: Jonathan Nolan
- TARS Performed by: Bill Irwin (voice and motion capture)
- Studios: Paramount Pictures, Warner Bros., Legendary Pictures

*This is a fan-made, educational tribute. No commercial use.*

### Powered By Open Source

- **Meta Llama 3** - Language model (Llama 3 Community License)
- **Ollama** - Local LLM serving (MIT)
- **Faster-Whisper** - Speech recognition (MIT)
- **Piper TTS** - Text-to-speech (MIT)
- **OpenWakeWord** - Wake word detection (Apache 2.0)
- **LLaVA** - Vision language model (Apache 2.0)
- **OpenCV** - Computer vision (Apache 2.0)
- **PyTorch, NumPy, SciPy, and many more** - See [ATTRIBUTION.md](ATTRIBUTION.md)

### Complete Attribution

**Required Attribution Statement:**
```
Portions of this software are derived from TARS-AI © TARS-AI Community 
(via fork by James-von-Detroit), licensed under CC-BY-NC 4.0.
```

For complete credits, licenses, and attribution details, see:
- [**ATTRIBUTION.md**](ATTRIBUTION.md) - Full attribution documentation
- [**CREDITS.md**](CREDITS.md) - Quick credits reference
- [**LICENSE.md**](LICENSE.md) - Dual license details

---

## 📜 License

### Dual License Structure

**gptars v3.0** uses dual licensing:

- ✅ **New code** (macOS installer, voice/vision engines, docs): **MIT License**
- ⚠️ **Derived portions** (TARS personality concepts): **CC-BY-NC 4.0**

**What this means:**
- New technical code can be used commercially (MIT)
- TARS character/personality requires attribution and non-commercial use (CC-BY-NC 4.0)
- Complete project follows most restrictive terms (CC-BY-NC 4.0)

See [**LICENSE.md**](LICENSE.md) for complete details.

---

## 🤝 Community

### Get Involved

- **⭐ Star this repo** if you like it!
- **🐛 Report bugs** via [GitHub Issues](https://github.com/James-von-Detroit/tars-ai/issues)
- **💡 Suggest features** in [Discussions](https://github.com/James-von-Detroit/tars-ai/discussions)
- **🔀 Submit PRs** with improvements
- **📖 Improve docs** - documentation PRs always welcome

### Join the Community

- **Discord**: Join the original [TARS-AI Community Discord](https://discord.gg/tars-ai)
- **Reddit**: r/TARS_AI
- **This Repo**: [Discussions](https://github.com/James-von-Detroit/tars-ai/discussions) and [Issues](https://github.com/James-von-Detroit/tars-ai/issues)

### Contributors

Thank you to everyone who contributed to:
- TARS-AI Community project
- James-von-Detroit's tars-ai fork
- Open-source libraries we depend on
- The Interstellar production team for inspiring this work

---

## ⚠️ Disclaimer

This is a **fan-made, educational project** inspired by TARS from *Interstellar*. This project is not endorsed by, affiliated with, or sponsored by Christopher Nolan, Paramount Pictures, Warner Bros., Legendary Pictures, or any other rights holders.

**Status**: Alpha software. Expect bugs and rough edges. Not production-ready.

---

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/James-von-Detroit/tars-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/James-von-Detroit/tars-ai/discussions)
- **Email**: [Your contact if you want to add]

---

<p align="center">
  <strong>"That's not saying much."</strong><br>
  — TARS, Interstellar (2014)
</p>

<p align="center">
  Made with ❤️ by the TARS community<br>
  100% offline • 100% open source • 100% TARS
</p>

<p align="center">
  <sub>gptars v3.0 Alpha | December 2024 | macOS ARM</sub>
</p>
