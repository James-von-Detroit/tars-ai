# macOS Installation Guide - gptars v3.0 Alpha

Complete step-by-step installation guide for Apple Silicon Macs.

---

## 🎯 Prerequisites

### Hardware Requirements
- **Mac:** M1, M2, M3, or M4 (Apple Silicon)
- **RAM:** 16GB minimum, 32GB+ recommended
- **Storage:** 15GB free space (for models and dependencies)
- **macOS:** Version 13.0 (Ventura) or later

### Software Prerequisites
- **Terminal access** (comes with macOS)
- **Admin privileges** (for installing Homebrew)
- **Internet connection** (for initial download only)

---

## 📋 Installation Methods

### Method 1: Automated Installation (Recommended)

The easiest way to install gptars. One script does everything.

```bash
# Clone the repository
git clone https://github.com/[your-repo]/gptars.git
cd gptars

# Make installer executable
chmod +x macos/install_macos.sh

# Run installer
./macos/install_macos.sh
```

The installer will:
1. ✅ Install Homebrew (if not present)
2. ✅ Install system dependencies (cmake, ffmpeg, portaudio, Python 3.11)
3. ✅ Install and start Ollama
4. ✅ Download Llama-3-8B-Instruct model (~4.7 GB)
5. ✅ Create Python virtual environment
6. ✅ Install all Python dependencies
7. ✅ Download Faster-Whisper model (~1.5 GB)
8. ✅ Install Piper TTS with voice model
9. ✅ Setup wake word detection
10. ✅ Request microphone/camera permissions

**Time:** 15-25 minutes (depends on internet speed)

### Method 2: Manual Installation

For advanced users who want more control.

#### Step 1: Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# For Apple Silicon, add Homebrew to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

#### Step 2: Install System Dependencies

```bash
brew update
brew install cmake ffmpeg portaudio python@3.11 git wget
```

#### Step 3: Install Ollama

```bash
# Install Ollama
brew install ollama

# Start Ollama service
brew services start ollama

# Wait a few seconds for service to start
sleep 5

# Download Llama-3 model (this takes a while)
ollama pull llama3:8b-instruct-q4_0
```

#### Step 4: Setup Python Environment

```bash
# Navigate to gptars directory
cd gptars

# Create virtual environment
python3.11 -m venv venv

# Activate environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Step 5: Install Python Dependencies

```bash
# Install from requirements file
pip install -r macos/requirements-macos.txt
```

#### Step 6: Download Speech Models

```bash
# Download Faster-Whisper model
python3 << 'EOF'
from faster_whisper import WhisperModel
import os

models_dir = "models/whisper"
os.makedirs(models_dir, exist_ok=True)

print("Downloading Whisper model...")
model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8", download_root=models_dir)
print("✓ Whisper model ready")
EOF
```

#### Step 7: Install Piper TTS

```bash
# Create voices directory
mkdir -p voices
cd voices

# Download Piper for macOS ARM
PIPER_VERSION="2023.11.14-2"
curl -L "https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/piper_macos_arm64.tar.gz" -o piper.tar.gz
tar -xzf piper.tar.gz
rm piper.tar.gz
chmod +x piper

# Download voice model
wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

cd ..
```

#### Step 8: Install Wake Word Detection

```bash
pip install openwakeword

# Download wake word models (automatic on first use)
python3 << 'EOF'
from openwakeword.model import Model
import os

models_dir = "models/wakeword"
os.makedirs(models_dir, exist_ok=True)

print("Downloading wake word models...")
model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
print("✓ Wake word models ready")
EOF
```

#### Step 9: Grant Permissions

```bash
# Run permission script
osascript macos/microphone_permissions.scpt
```

Or manually:
1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Microphone** and enable for **Terminal** (or your Python app)
3. Select **Camera** and enable for **Terminal** (or your Python app)

---

## ✅ Verification

### Test 1: Check Ollama

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Should return JSON with installed models
```

### Test 2: Check Python Environment

```bash
source venv/bin/activate
python3 -c "import faster_whisper, openwakeword, cv2; print('✓ All imports successful')"
```

### Test 3: Test TARS Personality

```bash
python3 core/tars_personality.py
```

Should output TARS personality configuration and prompts.

### Test 4: Test Voice Pipeline (Without Recording)

```bash
python3 << 'EOF'
from core.voice_engine import VoiceEngine
import numpy as np

engine = VoiceEngine(verbose=True)

# Test text-to-speech only
test_audio = engine.text_to_speech("Systems online. Ready for operation.")
print(f"✓ Generated {len(test_audio)} audio samples")

# Test LLM
response = engine.get_tars_response("Hello TARS")
print(f"✓ TARS response: {response}")
EOF
```

### Test 5: Full Voice Test

```bash
python3 core/voice_engine.py
```

Press ENTER, speak for 5 seconds, and verify TARS responds.

---

## 🔧 Configuration

### Change Voice Settings

Edit `core/voice_engine.py`:

```python
# Line ~40-45
engine = VoiceEngine(
    whisper_model="distil-large-v3",  # Change to: tiny, base, small, medium, large
    ollama_model="llama3:8b-instruct-q4_0",  # Or another Ollama model
    piper_voice="en_US-lessac-medium",  # Or another Piper voice
    verbose=True
)
```

### Change Personality

```python
from core.tars_personality import create_tars_personality

tars = create_tars_personality(
    honesty=100,  # Maximum honesty
    humor=90,     # Very witty
    discretion=30,  # Very direct
    user_name="Your Name"
)
```

### Alternative Voice Models

Download additional Piper voices:

```bash
cd voices

# Male voices (TARS-like)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json

# Female voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
```

Then change `piper_voice` parameter to match the new voice.

---

## 🚀 Optional: Vision Setup

To enable vision capabilities, install LLaVA:

```bash
# Download LLaVA model (7GB)
ollama pull llava:7b

# Or smaller/faster alternative
ollama pull llava:13b
```

Test vision:

```bash
python3 core/vision_engine.py
```

Press 's' to capture and analyze camera view.

---

## 📦 Optional: Install as .app Bundle

Create a macOS application (optional):

```bash
# Install py2app
pip install py2app

# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup

APP = ['core/voice_engine.py']
DATA_FILES = [
    ('voices', ['voices/piper', 'voices/en_US-lessac-medium.onnx', 'voices/en_US-lessac-medium.onnx.json']),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['faster_whisper', 'openwakeword', 'sounddevice'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
EOF

# Build app
python setup.py py2app

# App will be in dist/voice_engine.app
```

---

## 🎯 Performance Optimization

### For M1 Macs (8GB RAM)
- Use `whisper_model="distil-small-v3"` (faster, less accurate)
- Keep Ollama model at `llama3:8b-instruct-q4_0`
- Close other applications while running

### For M2/M3 Pro/Max (16GB+ RAM)
- Use `whisper_model="distil-large-v3"` (recommended)
- Consider `llama3:8b-instruct-q8_0` (higher quality, slower)
- Can run vision models simultaneously

### For M3/M4 Max/Ultra (32GB+ RAM)
- Use `whisper_model="large-v3"` (maximum accuracy)
- Can use `llama3:70b` models if needed
- Run multiple models simultaneously

---

## 📊 Disk Space Usage

After full installation:

| Component | Size |
|-----------|------|
| Homebrew + deps | ~500 MB |
| Python environment | ~2 GB |
| Ollama + Llama-3-8B | ~5 GB |
| Whisper models | ~1.5 GB |
| Piper TTS | ~500 MB |
| Wake word models | ~100 MB |
| **Total** | **~10 GB** |

With vision (LLaVA):
- Additional ~7 GB

---

## 🔄 Updating

### Update gptars

```bash
cd gptars
git pull origin main
source venv/bin/activate
pip install -r macos/requirements-macos.txt --upgrade
```

### Update Models

```bash
# Update Ollama models
ollama pull llama3:8b-instruct-q4_0

# Update Whisper (automatic on next run)
# Update Piper voices (manual download as above)
```

---

## 🗑️ Uninstallation

### Remove gptars Only

```bash
# Stop Ollama service
brew services stop ollama

# Remove gptars directory
rm -rf ~/path/to/gptars
```

### Full Cleanup (Remove Everything)

```bash
# Stop and remove Ollama
brew services stop ollama
brew uninstall ollama
rm -rf ~/.ollama

# Remove Python packages
rm -rf ~/path/to/gptars/venv

# Remove models (optional)
rm -rf ~/path/to/gptars/models
rm -rf ~/path/to/gptars/voices

# Remove project
rm -rf ~/path/to/gptars
```

---

## 🆘 Need Help?

- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Join our Discord: [link]
- Open an issue on GitHub

---

## ✅ Installation Complete!

Once installed, you can:

1. **Run voice mode:**
   ```bash
   source venv/bin/activate
   python3 core/voice_engine.py
   ```

2. **Run with wake word:**
   ```bash
   python3 -c "from core.voice_engine import VoiceEngine; from core.wake_word import TARSWakeWordListener; engine = VoiceEngine(); listener = TARSWakeWordListener(engine); listener.start()"
   ```

3. **Test vision:**
   ```bash
   python3 core/vision_engine.py
   ```

Enjoy your TARS companion! 🤖
