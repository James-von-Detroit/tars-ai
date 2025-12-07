# Troubleshooting Guide - gptars v3.0 Alpha

Solutions for common issues and errors.

---

## 🚨 Common Issues

### Installation Issues

#### Issue: "Command not found: brew"

**Cause:** Homebrew not installed or not in PATH

**Solution:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH (Apple Silicon)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Verify
brew --version
```

#### Issue: "Cannot connect to Ollama"

**Cause:** Ollama service not running

**Solution:**
```bash
# Check if running
curl http://localhost:11434/api/tags

# If fails, start Ollama
brew services start ollama

# Or run in foreground (for debugging)
ollama serve
```

#### Issue: "Model not found: llama3:8b-instruct-q4_0"

**Cause:** Model not downloaded

**Solution:**
```bash
# Download model (takes several minutes)
ollama pull llama3:8b-instruct-q4_0

# Verify
ollama list
```

#### Issue: "pip install fails with 'no matching distribution'"

**Cause:** Wrong Python version or ARM incompatibility

**Solution:**
```bash
# Check Python version (must be 3.11+)
python3 --version

# If wrong version, install correct one
brew install python@3.11

# Create venv with specific Python
python3.11 -m venv venv
source venv/bin/activate

# Retry installation
pip install -r macos/requirements-macos.txt
```

---

### Runtime Issues

#### Issue: "ModuleNotFoundError: No module named 'faster_whisper'"

**Cause:** Virtual environment not activated

**Solution:**
```bash
# Always activate venv before running
source venv/bin/activate

# Verify activation (should show venv in prompt)
which python3

# Should output: /path/to/gptars/venv/bin/python3
```

#### Issue: "Audio device not found" or "PortAudio error"

**Cause:** Microphone permissions not granted or audio system issue

**Solution:**
```bash
# Grant microphone permission
# System Preferences → Security & Privacy → Privacy → Microphone
# Enable for Terminal

# Test audio device
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Should list your microphone and speakers
```

#### Issue: "Camera not accessible" or "Permission denied"

**Cause:** Camera permissions not granted

**Solution:**
```bash
# Grant camera permission
# System Preferences → Security & Privacy → Privacy → Camera
# Enable for Terminal

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

#### Issue: Very slow response times (10+ seconds)

**Cause:** Wrong compute device or model size too large

**Solution:**
```python
# Check Whisper is using correct device
from faster_whisper import WhisperModel
model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8")
# Should use int8 on CPU for Apple Silicon

# Try smaller models
engine = VoiceEngine(whisper_model="distil-small-v3")  # Faster

# Check Ollama model size
ollama list
# Make sure using Q4 quantization, not Q8 or FP16
```

#### Issue: "TARS responses are nonsensical"

**Cause:** Model not loaded properly or temperature too high

**Solution:**
```bash
# Reload model
ollama pull llama3:8b-instruct-q4_0

# Check Ollama status
ollama list

# Lower temperature in voice_engine.py
# Line ~180: "temperature": 0.8 → 0.6
```

---

### Wake Word Issues

#### Issue: Wake word not detected

**Cause:** Threshold too high, microphone issues, or background noise

**Solution:**
```python
# Lower threshold (more sensitive)
listener = TARSWakeWordListener(engine, threshold=0.3)

# Test in quiet environment
# Speak clearly: "Hey TARS"

# Verify microphone working
python3 -c "import sounddevice as sd; import numpy as np; audio = sd.rec(16000, samplerate=16000, channels=1); sd.wait(); print(f'Recorded {len(audio)} samples')"
```

#### Issue: Too many false activations

**Cause:** Threshold too low

**Solution:**
```python
# Raise threshold (less sensitive)
listener = TARSWakeWordListener(engine, threshold=0.7)

# Or use different wake word model
# (Currently limited to OpenWakeWord models)
```

---

### Vision Issues

#### Issue: "LLaVA model not found"

**Cause:** Vision model not downloaded

**Solution:**
```bash
# Download LLaVA
ollama pull llava:7b

# Or smaller/faster version
ollama pull llava:13b

# Verify
ollama list
```

#### Issue: Vision analysis is very slow (30+ seconds)

**Cause:** Vision models are compute-intensive

**Solution:**
```bash
# Use smaller model
ollama pull llava:7b  # Smaller than 13b

# Or use Moondream (when available)
ollama pull moondream

# Adjust timeout in vision_engine.py
# Line ~160: timeout=60 → timeout=120
```

#### Issue: "Cannot capture frame"

**Cause:** Camera in use by another app or permissions

**Solution:**
```bash
# Close other apps using camera (FaceTime, Zoom, etc.)

# Check camera index
python3 << 'EOF'
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera found at index {i}")
        cap.release()
EOF

# Use correct index in vision_engine.py
engine = VisionEngine(camera_index=0)  # Try 0, 1, 2...
```

---

### Performance Issues

#### Issue: High CPU usage when idle

**Cause:** Wake word detection or Ollama running

**Solution:**
```bash
# Wake word detection uses ~10-15% CPU (normal)
# To reduce:
# 1. Use push-to-talk mode instead
# 2. Stop Ollama when not needed:
brew services stop ollama

# To completely stop wake word:
# Press Ctrl+C in the terminal
```

#### Issue: High memory usage

**Cause:** Large models loaded in memory

**Solution:**
```bash
# Check memory usage
ollama ps

# Unload models when done
ollama stop llama3:8b-instruct-q4_0

# Or restart Ollama
brew services restart ollama
```

#### Issue: System becomes unresponsive

**Cause:** Too many large models, insufficient RAM

**Solution:**
```bash
# Close unused applications
# Use Activity Monitor to check memory pressure

# For 8GB RAM systems:
# - Don't run vision models simultaneously
# - Use smaller Whisper model (tiny, base)
# - Close Ollama when not in use
```

---

## 🐛 Debugging

### Enable Verbose Mode

All components support verbose output:

```python
engine = VoiceEngine(verbose=True)  # Voice engine
vision = VisionEngine(verbose=True)  # Vision engine
detector = WakeWordDetector(verbose=True)  # Wake word
```

### Test Individual Components

#### Test Ollama Only
```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:8b-instruct-q4_0",
    "messages": [{"role": "user", "content": "Hello TARS"}]
  }'
```

#### Test Whisper Only
```python
from faster_whisper import WhisperModel
import numpy as np

model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8")
# Create 5 seconds of silence
audio = np.zeros(80000, dtype=np.float32)
segments, info = model.transcribe(audio)
print("Whisper working!")
```

#### Test Piper Only
```bash
cd voices
echo "Testing Piper TTS" | ./piper --model en_US-lessac-medium.onnx --output_file test.wav
# Should create test.wav
afplay test.wav
```

#### Test Camera Only
```python
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    cv2.imwrite("test.jpg", frame)
    print("Camera working! Check test.jpg")
cap.release()
```

### Check Logs

```bash
# Ollama logs
brew services log ollama

# System audio logs
log show --predicate 'subsystem == "com.apple.audio"' --last 1h

# Python errors (when running)
python3 core/voice_engine.py 2>&1 | tee debug.log
```

---

## 💡 Known Issues & Workarounds

### Issue: Piper TTS sounds robotic/metallic

**Status:** This is normal for neural TTS. TARS is a robot!

**Workaround:** Try different voices (see OPERATION_GUIDE.md)

### Issue: Occasional LLM hallucinations

**Status:** Normal for smaller models

**Workaround:** 
- Lower temperature (0.6 instead of 0.8)
- Use larger model (llama3:13b if you have RAM)
- Add more specific prompts

### Issue: Wake word responds to TV/radio

**Status:** False positives from audio

**Workaround:**
- Increase threshold (0.6-0.7)
- Mute TV/radio when using TARS
- Use push-to-talk mode

---

## 🔧 Advanced Troubleshooting

### Clean Reinstall

If all else fails:

```bash
# Stop services
brew services stop ollama

# Remove everything
rm -rf venv
rm -rf models
rm -rf voices
rm -rf ~/.ollama

# Reinstall
./macos/install_macos.sh
```

### Check System Requirements

```bash
# Check macOS version
sw_vers

# Check architecture
uname -m  # Should be "arm64"

# Check RAM
sysctl hw.memsize

# Check Python version
python3 --version  # Should be 3.11+

# Check disk space
df -h
```

### Report a Bug

If you found a bug not listed here:

1. Check existing GitHub issues
2. Collect information:
   ```bash
   # System info
   sw_vers > bug_report.txt
   uname -a >> bug_report.txt
   python3 --version >> bug_report.txt
   ollama --version >> bug_report.txt
   
   # Error output
   python3 core/voice_engine.py 2>&1 | tee -a bug_report.txt
   ```
3. Open issue on GitHub with bug_report.txt

---

## 📞 Getting Help

1. **Check this guide** - Most issues are covered here
2. **Read OPERATION_GUIDE.md** - Usage instructions
3. **Search GitHub issues** - Someone may have had same issue
4. **Discord community** - Real-time help
5. **Open GitHub issue** - For bugs and feature requests

---

## ✅ Still Not Working?

If nothing here helped:

1. Share your exact error message
2. Share your Mac model and macOS version
3. Share what you've already tried
4. Join Discord or open GitHub issue

We're here to help! 🤝

---

## 📋 Diagnostic Checklist

Use this checklist to diagnose issues systematically:

- [ ] Homebrew installed and working (`brew --version`)
- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Virtual environment activated (`which python3` shows venv path)
- [ ] Ollama service running (`curl http://localhost:11434/api/tags`)
- [ ] Llama-3 model downloaded (`ollama list`)
- [ ] Microphone permission granted (System Preferences → Privacy)
- [ ] Camera permission granted (System Preferences → Privacy)
- [ ] All Python packages installed (`pip list | grep faster-whisper`)
- [ ] Whisper model downloaded (check `models/whisper/` directory)
- [ ] Piper binary executable (`./voices/piper --version`)
- [ ] Piper voice model downloaded (check `voices/` directory)
- [ ] Sufficient disk space (15GB+) (`df -h`)
- [ ] Sufficient RAM (16GB recommended) (`sysctl hw.memsize`)

If all checked, gptars should work! 🎉
