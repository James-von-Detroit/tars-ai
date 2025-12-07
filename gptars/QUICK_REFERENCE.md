# gptars v3.0 Alpha - Quick Reference

One-page reference for common operations.

> **🔒 Security:** Dependencies updated Dec 2024. See [SECURITY.md](SECURITY.md)

---

## 🚀 Installation (One Command)

```bash
git clone [repo] && cd gptars && ./macos/install_macos.sh
```

**Time:** 15-20 minutes | **Size:** ~15GB | **Requirements:** macOS 13+, M1+

> **Update existing installation:** `pip install --upgrade onnx==1.17.0 torch==2.6.0 transformers==4.48.0`

---

## 🎯 Quick Start

```bash
source venv/bin/activate
./run_tars.sh
# Choose option 1 for Push-to-Talk
```

---

## 🎤 Voice Modes

### Push-to-Talk
```bash
python3 core/voice_engine.py
# Press ENTER to speak
```

### Wake Word (Always Listening)
```bash
python3 -c "from core.voice_engine import VoiceEngine; from core.wake_word import TARSWakeWordListener; engine = VoiceEngine(); listener = TARSWakeWordListener(engine); listener.start()"
# Say "Hey TARS"
```

---

## 👁️ Vision

```bash
python3 core/vision_engine.py
# Press 's' to analyze, 'p' for preview, 'q' to quit
```

---

## 🎭 Personality Quick Adjust

```python
from core.tars_personality import create_tars_personality

# Create custom TARS
tars = create_tars_personality(
    honesty=100,    # Maximum truth
    humor=90,       # Very witty
    discretion=30,  # Very direct
    user_name="Your Name"
)

# Save for later
tars.save_to_file("my_tars.json")
```

**Presets:**
- **Movie TARS:** honesty=90, humor=60, discretion=50
- **Serious TARS:** honesty=85, humor=20, discretion=80
- **Comedy TARS:** honesty=70, humor=95, discretion=40
- **Brutally Honest:** honesty=100, humor=30, discretion=10

---

## 🔧 Common Fixes

### Ollama Not Running
```bash
brew services start ollama
# or
ollama serve
```

### Model Not Found
```bash
ollama pull llama3:8b-instruct-q4_0
```

### Permission Denied (Microphone)
```
System Preferences → Security & Privacy → Privacy → Microphone → Enable Terminal
```

### Slow Performance
```python
# Use smaller models
engine = VoiceEngine(whisper_model="distil-small-v3")
```

---

## 📊 Performance Targets

| Mac | STT | LLM | TTS | Total |
|-----|-----|-----|-----|-------|
| M1 | 350ms | 2.1s | 180ms | ~2.6s |
| M2 | 280ms | 1.4s | 150ms | ~1.8s |
| M3 | 220ms | 0.9s | 120ms | ~1.2s |
| M4 | 180ms | 0.7s | 100ms | ~1.0s |

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

---

## 📚 Documentation

- **Installation:** `docs/MACOS_INSTALL_GUIDE.md`
- **Usage:** `docs/OPERATION_GUIDE.md`
- **Problems:** `docs/TROUBLESHOOTING.md`
- **Overview:** `README.md`

---

## 🆘 Get Help

1. Check `TROUBLESHOOTING.md`
2. Search GitHub issues
3. Join Discord
4. Open new issue

---

## 🎯 Most Common Commands

```bash
# Start TARS
./run_tars.sh

# Activate environment
source venv/bin/activate

# Check Ollama status
curl http://localhost:11434/api/tags

# List models
ollama list

# Stop Ollama
brew services stop ollama

# Update dependencies
pip install -r macos/requirements-macos.txt --upgrade

# Run specific test
pytest tests/test_tars_conversation.py::TestPersonalitySettings -v
```

---

## 📝 Example Conversation Starters

- "Hello TARS, tell me about yourself"
- "What's your humor setting at?"
- "Adjust your honesty to 95%"
- "Can you help me with a problem?"
- "Tell me a joke"
- "What can you see right now?" (with vision)
- "Analyze this image" (with vision)

---

## 💡 Pro Tips

1. **Lower wake word threshold** (0.3) if TARS doesn't respond
2. **Raise threshold** (0.7) if too many false activations
3. **Use smaller Whisper** (tiny/base) for faster STT on M1
4. **Close other apps** to free RAM for better performance
5. **Adjust humor up** (90+) for more entertaining TARS
6. **Save personality configs** for different use cases
7. **Use vision mode** for document analysis, object identification

---

**Remember:** Everything runs 100% offline after installation! 🔒

---

For complete documentation, see `README.md` and files in `docs/` directory.
