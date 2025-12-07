# TARS-AI on ARM MacBook Pro: Local LLM Setup & Testing Plan

## Quick Answers

### ✅ **YES - TARS-AI can use a local on-device LLM**
TARS-AI supports multiple local LLM backends:
- **Ollama** (Recommended for Mac - optimized for Apple Silicon)
- **Ooba** (Text Generation WebUI)
- **Tabby** (TabbyAPI)

### ✅ **YES - TARS-AI works on ARM-based MacBook Pro (M1/M2/M3)**
The AI components are Python-based and fully compatible with Apple Silicon. Only Raspberry Pi hardware components need to be disabled.

---

## Local LLM Options for ARM MacBook Pro

### Option 1: Ollama (Recommended) ⭐

**Why Ollama?**
- Native Apple Silicon optimization (Metal GPU acceleration)
- Easy installation with Homebrew
- Good performance on M1/M2/M3 chips
- Large model library (Llama, Mistral, Phi, etc.)
- Compatible with OpenAI API format

**Performance on Apple Silicon:**
- M1 Pro/Max: Can run 7B-13B models smoothly
- M2 Pro/Max: Can run 13B-30B models smoothly
- M3 Pro/Max: Can run 30B+ models smoothly
- Unified memory helps with larger models

**Installation:**
```bash
# Install Ollama
brew install ollama

# Download a model (examples)
ollama pull llama2            # 7B model, good for testing
ollama pull mistral           # 7B model, high quality
ollama pull llama2:13b        # 13B model, better quality
ollama pull phi               # 2.7B model, fast and efficient

# Start Ollama server
ollama serve
```

**TARS Configuration:**
Edit `config.ini`:
```ini
[LLM]
llm_backend = ooba  # Ollama uses OpenAI-compatible API
base_url = http://localhost:11434/v1
openai_model = llama2  # or mistral, phi, etc.
contextsize = 4000
max_tokens = 1000
temperature = 0.8
```

**Set empty API key in `.env`:**
```bash
OPENAI_API_KEY=placeholder  # Required but not used for local
```

### Option 2: LM Studio (Alternative)

**LM Studio** also works great on ARM Macs:
- GUI interface for model management
- Optimized for Apple Silicon
- Built-in OpenAI-compatible API server

**Installation:**
1. Download from https://lmstudio.ai
2. Install and download models through GUI
3. Start local server (default: http://localhost:1234)

**TARS Configuration:**
```ini
[LLM]
llm_backend = ooba
base_url = http://localhost:1234/v1
openai_model = local-model
```

### Option 3: MLX (Apple's Framework)

**MLX-LM** - Apple's native ML framework for ARM:
- Maximum performance on Apple Silicon
- Requires more technical setup
- Excellent for advanced users

```bash
pip install mlx-lm

# Run a model
python -m mlx_lm.server --model mlx-community/Llama-3-8B-Instruct-4bit
```

---

## Complete ARM MacBook Pro Setup Plan

### Phase 1: Environment Setup (10 minutes)

**1. Verify Python Installation**
```bash
# Check Python version (need 3.8+)
python3 --version

# Should show arm64 architecture
python3 -c "import platform; print(platform.machine())"
# Expected output: arm64
```

**2. Install Homebrew (if not installed)**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**3. Clone TARS-AI**
```bash
git clone https://github.com/James-von-Detroit/tars-ai.git
cd tars-ai/src
```

### Phase 2: Install Core Dependencies (15 minutes)

**Minimal AI-only installation (no hardware deps):**
```bash
# Core AI dependencies
pip3 install openai tiktoken hyperdb-python requests python-dotenv

# Web interface
pip3 install flask flask-cors flask-socketio eventlet

# Memory and search
pip3 install sentence-transformers scikit-learn bm25s pystemmer flashrank

# Optional: For better performance on Apple Silicon
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Skip These (Raspberry Pi only):**
- adafruit-* packages
- evdev
- lgpio
- picamera2

### Phase 3: Install Local LLM (5 minutes)

**Install Ollama:**
```bash
brew install ollama

# Download a model appropriate for your Mac
# M1/M2 Base: Use 7B models
ollama pull llama2

# M1/M2 Pro/Max: Can handle 13B models
# ollama pull llama2:13b

# M3 Pro/Max: Can handle larger models
# ollama pull mixtral:8x7b
```

**Start Ollama:**
```bash
# In a separate terminal
ollama serve

# Test it works
ollama run llama2 "Hello, how are you?"
```

### Phase 4: Configure TARS for Local LLM (5 minutes)

**1. Copy ARM Mac configuration:**
```bash
cd tars-ai/src
cp config.ini.macos config.ini
```

**2. Edit `config.ini` for local LLM:**
```ini
[LLM]
llm_backend = ooba  # Use this for Ollama compatibility
base_url = http://localhost:11434/v1
openai_model = llama2  # or your chosen model
contextsize = 4000  # Adjust based on model
max_tokens = 1000
temperature = 0.8
top_p = 0.9
seed = -1
```

**3. Setup environment:**
```bash
cp ../.env.template ../.env
nano ../.env
```

Add (placeholder for local LLM):
```bash
OPENAI_API_KEY=not-needed-for-local
```

### Phase 5: Test & QA (10 minutes)

**1. Start TARS:**
```bash
cd tars-ai/src
python3 app.py
```

**2. Open web interface:**
```bash
open http://localhost:5012
```

**3. Test conversational AI:**
```
Test Message 1: "Hello TARS, can you hear me?"
Expected: TARS responds in character

Test Message 2: "What is 2+2?"
Expected: Mathematical response

Test Message 3: "Tell me about yourself"
Expected: TARS personality shines through

Test Message 4: "Remember, my favorite color is blue"
[Wait for response]
Then: "What's my favorite color?"
Expected: TARS recalls the memory
```

**4. Monitor Performance:**
```bash
# In another terminal
# Check CPU/Memory usage
top -pid $(pgrep -f "python3 app.py")

# Ollama memory usage
ollama ps
```

---

## ARM Mac Compatibility Notes

### ✅ Fully Compatible Components

These work perfectly on ARM Mac:
- **Python 3.8+** - Native ARM support
- **Flask/Socket.IO** - Pure Python, no issues
- **OpenAI API** - HTTP-based, architecture-agnostic
- **Ollama** - Optimized for Apple Silicon
- **HyperDB** - Pure Python vector database
- **Sentence Transformers** - Works with PyTorch ARM

### ⚠️ Skip or Replace on ARM Mac

**Hardware-specific (skip these):**
- `evdev` - Linux input devices (not needed on Mac)
- `adafruit-*` - Raspberry Pi hardware (not needed)
- `lgpio` - Raspberry Pi GPIO (not needed)
- `picamera2` - Raspberry Pi camera (not needed)

**Platform-specific alternatives:**
- `pydub` - May need `ffmpeg`: `brew install ffmpeg`
- `sounddevice` - Should work, may need `portaudio`: `brew install portaudio`

### 🔧 Potential Issues & Solutions

**Issue 1: Rosetta Dependencies**
Some packages may install x86_64 versions via Rosetta.

**Solution:**
```bash
# Force ARM64 architecture
arch -arm64 pip3 install [package]
```

**Issue 2: PyTorch Installation**
Default PyTorch may not optimize for Metal GPU.

**Solution:**
```bash
# Install with Metal Performance Shaders support
pip3 install torch torchvision torchaudio
```

**Issue 3: Sentence Transformers Slow**
First run downloads models and can be slow.

**Solution:**
```bash
# Pre-download models
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## Performance Expectations

### With Ollama on ARM Mac

| Mac Model | Model Size | Response Time | Quality |
|-----------|------------|---------------|---------|
| M1 8GB | 7B (llama2) | 2-4 sec | Good |
| M1 16GB | 7B (llama2) | 1-2 sec | Good |
| M2 Pro | 13B (llama2:13b) | 2-3 sec | Very Good |
| M2 Max | 13B (llama2:13b) | 1-2 sec | Very Good |
| M3 Pro | 30B+ | 3-5 sec | Excellent |
| M3 Max | 70B (with quantization) | 5-8 sec | Excellent |

### Memory Requirements

- **7B model**: ~6-8 GB RAM
- **13B model**: ~12-16 GB RAM
- **30B model**: ~24-32 GB RAM
- **Base system + TARS**: ~2-3 GB RAM

**Recommendation:** Keep 4-6 GB free for smooth operation.

---

## Testing Plan for ARM MacBook Pro

### Test 1: Basic Installation ✓
**Goal:** Verify TARS installs on ARM architecture
**Steps:**
1. Install dependencies: `pip3 install openai tiktoken hyperdb-python flask flask-socketio eventlet`
2. Verify ARM architecture: `python3 -c "import platform; print(platform.machine())"`
3. Expected: Output shows `arm64`

### Test 2: Local LLM Integration ✓
**Goal:** Verify Ollama works with TARS
**Steps:**
1. Install Ollama: `brew install ollama`
2. Start server: `ollama serve`
3. Configure TARS to use Ollama
4. Send test message: "Hello"
5. Expected: TARS responds using local model

### Test 3: Memory System ✓
**Goal:** Verify HyperDB works on ARM
**Steps:**
1. Start TARS
2. Send: "My name is John"
3. Restart TARS
4. Send: "What's my name?"
5. Expected: TARS remembers "John"

### Test 4: Character Personality ✓
**Goal:** Verify character system works
**Steps:**
1. Check persona.ini loads correctly
2. Send: "Tell me a joke"
3. Expected: TARS responds with humor based on settings

### Test 5: Web Interface ✓
**Goal:** Verify ChatUI works on ARM Mac
**Steps:**
1. Start TARS
2. Open http://localhost:5012
3. Send messages through web interface
4. Expected: Responsive web chat

### Test 6: Performance Benchmark ⏱️
**Goal:** Measure response times on ARM
**Steps:**
1. Use `time` command: `time curl -X POST http://localhost:5012/api/chat -d '{"message":"test"}'`
2. Record response time
3. Monitor with: `ollama ps`
4. Expected: Under 5 seconds for 7B model

---

## Recommended Setup for QA Testing

### Development Configuration

```ini
[LLM]
llm_backend = ooba
base_url = http://localhost:11434/v1
openai_model = llama2  # Fast 7B model for testing
contextsize = 2048     # Smaller context for faster responses
max_tokens = 512       # Shorter responses for testing
temperature = 0.7
top_p = 0.9

[RAG]
strategy = naive       # Simpler, faster
top_k = 3              # Fewer memories for testing

[CHATUI]
enabled = True         # Web interface for testing

[CONTROLS]
enabled = False        # No hardware

[UI]
UI_enabled = False     # No visual UI

[TTS]
ttsoption = espeak     # Simple TTS for Mac (uses 'say' command)
voice_only = False

[STT]
stt_processor = external  # Text-only for testing
```

### QA Test Checklist

- [ ] Installation completes without ARM-specific errors
- [ ] Ollama server starts and responds
- [ ] TARS app.py starts without import errors
- [ ] Web interface accessible at localhost:5012
- [ ] Basic conversation works
- [ ] Memory persistence works across restarts
- [ ] Character personality is evident
- [ ] Response times are acceptable (< 5 sec)
- [ ] No memory leaks over 30-minute test
- [ ] CPU usage reasonable (< 100% sustained)

---

## Troubleshooting ARM-Specific Issues

### Issue: "No module named 'X'" errors

**Cause:** Package not installed or wrong architecture

**Fix:**
```bash
# Reinstall with ARM architecture
arch -arm64 pip3 install [package-name]
```

### Issue: Slow responses from Ollama

**Cause:** Model too large for available RAM

**Fix:**
```bash
# Use smaller or quantized models
ollama pull llama2          # 7B (smaller)
ollama pull phi             # 2.7B (very fast)
ollama pull mistral:7b-q4   # 4-bit quantized
```

### Issue: "Address already in use" (port 5012)

**Cause:** Previous TARS instance still running

**Fix:**
```bash
lsof -ti:5012 | xargs kill -9
```

### Issue: Import errors for hardware packages

**Expected Behavior:** Can be ignored on Mac

**Fix:** These are for Raspberry Pi only:
```bash
# These errors are safe to ignore on Mac:
# - ModuleNotFoundError: No module named 'evdev'
# - ModuleNotFoundError: No module named 'adafruit_*'
# - ModuleNotFoundError: No module named 'lgpio'
```

---

## Cost Comparison: Local vs. Cloud

### Local LLM (Ollama on ARM Mac)
- **Cost:** $0 (after Mac purchase)
- **Speed:** 1-5 seconds per response
- **Privacy:** 100% local, no data leaves device
- **Quality:** Good (7B) to Excellent (70B with quantization)
- **Internet:** Not required after model download

### Cloud LLM (OpenAI)
- **Cost:** ~$0.001-0.01 per conversation
- **Speed:** 0.5-2 seconds per response
- **Privacy:** Data sent to OpenAI
- **Quality:** Excellent (GPT-4o-mini) to Outstanding (GPT-4)
- **Internet:** Always required

### Recommendation for QA/Development

**Phase 1 (Local):** Use Ollama for initial development and testing
- Zero ongoing costs
- Fast iteration
- Privacy during development

**Phase 2 (Cloud):** Switch to GPT-4o-mini for production quality
- Better responses
- More reliable
- Lower maintenance

---

## Summary: ARM Mac + Local LLM = ✅ Fully Supported

**What Works:**
✅ All AI intelligence features
✅ Memory system (HyperDB)
✅ Character personalities
✅ Web chat interface
✅ Local LLM (Ollama/LM Studio)
✅ Apple Silicon optimization
✅ Offline operation (after model download)

**What to Skip:**
❌ Raspberry Pi hardware packages
❌ Servo control
❌ Battery monitoring
❌ Linux-specific input devices

**Estimated Setup Time:**
- First time: 45 minutes
- Experienced: 15 minutes

**Storage Required:**
- TARS-AI: ~500 MB
- Ollama: ~100 MB
- 7B Model: ~4 GB
- 13B Model: ~8 GB

---

## Next Steps

1. **Review this plan** - Ensure it meets your QA testing needs
2. **Set up environment** - Follow Phase 1-4 above
3. **Run tests** - Use the testing checklist
4. **Report issues** - Document any ARM-specific problems
5. **Iterate** - Refine configuration for your use case

**Ready to start? Follow Phase 1 above!** 🚀
