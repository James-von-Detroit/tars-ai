# TARS Hardware Options & M1 Mac Alpha Test Setup

## Quick Answers to Your Questions

### 1. Would Ollama be an option?
**YES!** Ollama is the **recommended** option for local LLM with TARS. It's what I documented in ARM-MAC-LOCAL-LLM-GUIDE.md.

### 2. Can Llama 3-8B (Q4) support voice operations and talk like movie TARS?
**YES!** Llama 3-8B Q4 is perfect for this:
- Supports all voice operations (STT + TTS work independently of LLM)
- Character personality system ensures TARS-like responses
- Q4 quantization runs smoothly on M1 Mac
- Voice quality depends on TTS choice, not LLM

### 3. What's the general hardware for a working TARS?
**Two main options:**
1. **Software-only** (M1 Mac, any computer) - AI brain only
2. **Physical robot** (Raspberry Pi + servos + 3D printed body) - Full robot

### 4. Is Raspberry Pi feasible for local LLM like Ollama?
**Depends on the Pi:**
- **Raspberry Pi 4 (4GB/8GB)**: Can run tiny models (1-3B), very slow
- **Raspberry Pi 5 (8GB)**: Can run 7B models, slow but usable
- **Not recommended** for primary LLM - better to use cloud API or external server

### 5. Strongest/efficient model for small hardware to fit in working TARS?
**Best options by size:**
- **Raspberry Pi**: Phi-2 (2.7B Q4) or TinyLlama (1.1B)
- **M1 Mac in TARS body**: Llama 3-8B Q4 (recommended)
- **Cloud API in robot**: Any model (GPT-4, Claude, etc.)

---

## Hardware Configuration Options

### Option 1: M1 Mac Development Setup (Recommended for Alpha Test) ⭐

**What you get:**
- Full AI intelligence with local LLM
- Fast response times (1-3 seconds)
- All memory and learning features
- Zero ongoing costs
- Perfect for development and testing

**Hardware:**
- M1 MacBook Pro (your hardware)
- Ollama running Llama 3-8B Q4
- Optional: USB microphone for voice input
- Optional: Speakers for voice output

**Setup time:** 15-30 minutes

**Use case:** Pure software development, AI testing, character personality tuning

---

### Option 2: Raspberry Pi Robot (Physical TARS)

**What you get:**
- Physical robot body
- Servo movement
- Local computing
- Portable

**Hardware needed:**
```
Core:
- Raspberry Pi 5 (8GB) - $80
- MicroSD card (64GB+) - $15
- Power supply (5V 5A) - $12

Servos (for movement):
- 6x servos (MG996R or similar) - $60
- PCA9685 servo driver board - $8

Audio:
- USB microphone - $15
- USB speakers or audio HAT - $20

Display (optional):
- 4-7" touchscreen - $40-80

Battery (for portable):
- Power bank (20,000+ mAh) - $30-50

3D printed body:
- Filament cost - $50-100

Total: ~$300-450
```

**Limitations:**
- Slow LLM inference (5-15 sec for tiny models)
- Limited to 1-3B models realistically
- Better with cloud API for good responses

---

### Option 3: Hybrid Setup (Best of Both Worlds)

**Architecture:**
```
Physical Robot (Raspberry Pi)
    ↓
Network Connection
    ↓
M1 Mac (LLM Server)
    or
Cloud API (OpenAI, etc.)
```

**What you get:**
- Physical robot body with servos
- Fast AI responses (M1 Mac or cloud)
- Best quality and portability

**Setup:**
- Raspberry Pi runs servos, audio, display
- LLM runs on M1 Mac (via network) or cloud
- TARS sends requests over WiFi/network

---

## Raspberry Pi Ollama Performance Reality Check

### Raspberry Pi 5 (8GB) Performance

**Models that work:**
| Model | Size | RAM Usage | Response Time | Quality |
|-------|------|-----------|---------------|---------|
| TinyLlama | 1.1B Q4 | ~1GB | 5-10 sec | Poor |
| Phi-2 | 2.7B Q4 | ~2GB | 10-15 sec | Acceptable |
| Llama 3-8B Q4 | 8B Q4 | ~5GB | 20-40 sec | Good (but slow) |

**Reality:**
- 8B model on Pi 5: **20-40 seconds per response** (too slow)
- 3B model on Pi 5: **10-15 seconds** (barely acceptable)
- 1B model on Pi 5: **5-10 seconds** (fast enough but poor quality)

**Recommendation:** 
For physical robot, use **cloud API** or **external LLM server** (like your M1 Mac running Ollama as a server).

---

## M1 Mac Performance with Llama 3-8B Q4

### Expected Performance

**Model:** Llama 3-8B Q4 (4-bit quantization)
**Hardware:** M1 MacBook Pro
**RAM Usage:** ~6GB
**Response Time:** 1-3 seconds
**Quality:** Very good - comparable to GPT-3.5

### Comparison to Movie TARS

**Character Personality:** ✅ Perfect
- TARS character config controls personality
- Honesty: 95%, Humor: 90%, Sarcasm: 70%
- Example dialogue trained for TARS-like responses

**Voice Operations:** ✅ Full Support
- Speech-to-Text: Independent of LLM (Whisper, FastRTC, etc.)
- Text-to-Speech: Independent of LLM (Piper, ElevenLabs, OpenAI TTS)
- Voice quality = TTS choice, not LLM choice

**Intelligence:** ✅ Comparable
- Llama 3-8B is GPT-3.5 class
- Context understanding: Good
- Humor/sarcasm: Supported
- Memory system: Full HyperDB integration

**Limitations vs GPT-4:**
- Slightly less creative
- Occasionally misses subtle context
- Not as strong at complex reasoning

**But for TARS character:**
- More than sufficient
- Personality shines through
- Maintains character consistency
- Responds like movie TARS

---

## TARS Character Configuration Details

### Character Personality (persona.ini)

```ini
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
cheerfulness = 30   # Low - serious demeanor
engagement = 40     # Moderate - not overly chatty
respectfulness = 20 # Low - direct, can be blunt
verbosity = 10      # Very low - concise responses
```

### Character Traits (from TARS.json)

**Personality:**
- Efficient and direct in crisis
- Sophisticated humor capabilities
- Protective of crew
- Absolute loyalty with contingency planning
- Pragmatic approach to truth

**Example Dialogue Style:**
```
User: What's your honesty parameter set to?
TARS: 90%.
User: Why not 100%?
TARS: Absolute honesty isn't always the most diplomatic nor the safest form 
      of communication with emotional beings.
```

### Voice Configuration

**Voice file:** `TARS.onnx` (63MB)
- Custom trained voice model
- Sounds like movie TARS (mechanical, authoritative)
- Works with Piper TTS system

**Alternative voice options:**
- OpenAI TTS: "onyx" voice (deep, authoritative)
- ElevenLabs: Custom voice cloning
- Azure TTS: "en-US-GuyNeural" (male, professional)

---

## M1 Mac Alpha Test Installation Plan

### Phase 1: Environment Setup (10 min)

```bash
# 1. Verify Python
python3 --version  # Should be 3.8+
python3 -c "import platform; print(platform.machine())"  # Should show arm64

# 2. Clone TARS
cd ~/Projects  # or your preferred location
git clone https://github.com/James-von-Detroit/tars-ai.git
cd tars-ai/src
```

### Phase 2: Install Dependencies (15 min)

```bash
# Core AI dependencies (minimal)
pip3 install openai tiktoken hyperdb-python requests python-dotenv

# Web interface
pip3 install flask flask-cors flask-socketio eventlet

# Memory and search (important for TARS intelligence)
pip3 install sentence-transformers scikit-learn bm25s pystemmer

# For better performance
pip3 install torch torchvision torchaudio
```

### Phase 3: Install Ollama + Llama 3-8B (10 min)

```bash
# Install Ollama
brew install ollama

# Download Llama 3-8B Q4 (recommended for M1)
ollama pull llama3:8b-instruct-q4_0

# Alternative models:
# ollama pull llama3:8b  # Full precision (slower, better quality)
# ollama pull mistral:7b-instruct-q4_0  # Alternative, also good

# Start Ollama server (in separate terminal, keep running)
ollama serve
```

### Phase 4: Configure TARS for Local LLM (5 min)

```bash
# Copy macOS config
cp config.ini.macos config.ini

# Edit config.ini
nano config.ini
```

**Key settings to verify/change:**

```ini
[LLM]
llm_backend = ooba  # This works with Ollama
base_url = http://localhost:11434/v1
openai_model = llama3:8b-instruct-q4_0  # Match what you pulled
contextsize = 4000
max_tokens = 1000
temperature = 0.8
top_p = 0.9

[CHAR]
character_card_path = character/TARS/TARS.json
user_name = YourName  # Change this to your name

[CHATUI]
enabled = True  # Web interface

[CONTROLS]
enabled = False  # No hardware

[UI]
UI_enabled = False  # No visual UI

[TTS]
ttsoption = piper  # or openai for voice
toggle_charvoice = True
voice_only = False

[STT]
stt_processor = external  # Text-only for now, or openai for voice
```

**Setup environment:**
```bash
# Create .env file
cp ../.env.template ../.env
nano ../.env
```

Add:
```bash
OPENAI_API_KEY=not-needed-for-local
```

### Phase 5: Test Basic Functionality (5 min)

```bash
# Terminal 1: Keep Ollama running
ollama serve

# Terminal 2: Start TARS
cd ~/Projects/tars-ai/src
python3 app.py
```

**Expected output:**
```
LOAD: Script running from: /path/to/tars-ai/src
LOAD: Found existing memory: TARS.pickle.gz
LOAD: Memory loaded successfully
LOAD: ChatUI starting on port 5012...
LOAD: TARS-AI v4.0 running.
```

### Phase 6: Alpha Test Protocol (30 min)

**Test 1: Basic Response**
```
Open: http://localhost:5012
Send: "Hello TARS, systems check"
Expected: TARS responds in character with status
```

**Test 2: Character Personality**
```
Send: "Tell me a joke"
Expected: Sarcastic/dry humor, maybe cue light reference
```

**Test 3: Honesty Parameter**
```
Send: "What's your honesty parameter?"
Expected: "95%" or similar direct response
```

**Test 4: Memory System**
```
Send: "My name is [YourName] and I'm testing you"
Restart TARS: Ctrl+C then python3 app.py
Send: "What's my name?"
Expected: TARS remembers your name
```

**Test 5: Problem Solving**
```
Send: "How would you solve the chicken-or-egg problem?"
Expected: Pragmatic TARS-style response with humor
```

**Test 6: Response Time**
```
Measure: Time from sending message to receiving response
Expected: 1-3 seconds on M1 Mac
```

**Test 7: Context Understanding**
```
Send: "I'm planning a trip to Mars"
Send: "What should I pack?"
Expected: TARS references your Mars trip, gives practical advice
```

**Test 8: Personality Tuning**
```
Edit: src/character/TARS/persona.ini
Change: humor = 90 to humor = 30
Restart TARS
Send: "Tell me a joke"
Expected: Less humor, more serious responses
```

---

## Voice Operation Setup (Optional - for full TARS experience)

### Option 1: OpenAI Voice (Easiest, costs money)

```ini
[STT]
stt_processor = openai  # Whisper API

[TTS]
ttsoption = openai
openai_voice = onyx  # Deep, authoritative (closest to TARS)
```

In `.env`:
```bash
OPENAI_API_KEY=sk-your-real-key-here
```

**Cost:** ~$0.01-0.05 per conversation with voice

### Option 2: Local Voice (Free, more setup)

**Install Piper TTS:**
```bash
pip3 install piper-tts
```

**Configure:**
```ini
[TTS]
ttsoption = piper
toggle_charvoice = True  # Uses TARS.onnx voice
```

**For STT (Speech-to-Text):**
```bash
pip3 install faster-whisper
```

```ini
[STT]
stt_processor = faster-whisper
whisper_model = base  # or small, medium
```

---

## Alpha Test Success Criteria

### Must Have ✅
- [ ] TARS responds to messages
- [ ] Responses are in character (sarcastic, direct, practical)
- [ ] Response time under 5 seconds
- [ ] Memory persists across restarts
- [ ] Character personality evident
- [ ] No crashes during 30-minute test

### Should Have 👍
- [ ] Response time under 3 seconds
- [ ] Humor/sarcasm in appropriate responses
- [ ] Context understanding across multiple messages
- [ ] Web interface responsive and clean

### Nice to Have 🌟
- [ ] Voice input/output working
- [ ] Real-time conversation flow
- [ ] Complex problem-solving demonstrated
- [ ] Personality tuning responsive

---

## Troubleshooting Alpha Test

### Issue: Slow responses (>5 seconds)

**Cause:** Model too large or not quantized

**Fix:**
```bash
# Use lighter model
ollama pull llama3:8b-instruct-q4_0  # If not already
# or
ollama pull phi:2.7b-q4_0  # Even lighter
```

### Issue: Out of memory

**Cause:** M1 Mac has 8GB unified memory, model + OS too large

**Fix:**
```bash
# Close other apps
# Use smaller model
ollama pull phi:2.7b-q4_0
```

### Issue: Responses not in character

**Cause:** Prompt engineering or model limitations

**Fix:**
1. Verify character config loaded: Check console output
2. Adjust temperature: Lower = more consistent (0.6-0.7)
3. Try different model: Some models better at character consistency

### Issue: Memory not persisting

**Cause:** Memory file not saving

**Fix:**
```bash
# Check memory directory
ls -la ../memory/
# Should see TARS.pickle.gz

# If missing, check permissions
chmod 755 ../memory/
```

---

## Next Steps After Alpha Test

### 1. Performance Optimization
- Try different quantization levels
- Tune context size and max tokens
- Optimize prompt engineering

### 2. Voice Integration
- Add microphone and speakers
- Test voice recognition accuracy
- Fine-tune TARS voice output

### 3. Personality Refinement
- Adjust persona.ini values
- Test different scenarios
- Record best personality settings

### 4. Physical Robot Planning (if desired)
- Decide on Raspberry Pi vs external LLM
- Design/source 3D printed body
- Plan servo configuration
- Budget for components

---

## Summary

### For M1 Mac Alpha Test: ✅ Ready

**Hardware:** Perfect for Llama 3-8B Q4
**Model:** Excellent quality, fast responses
**Voice:** Fully supported (STT + TTS independent)
**Character:** TARS personality works perfectly
**Setup time:** ~45 minutes
**Cost:** $0 for local LLM

### For Raspberry Pi Physical Robot: ⚠️ Limitations

**Pi 5 with Ollama:** Possible but slow (20-40 sec)
**Better approach:** Pi + cloud API or Pi + M1 Mac as LLM server
**Physical components:** ~$300-450 for full robot

### Recommendation:

**Start with M1 Mac alpha test** (what you asked for):
- Develop and test AI intelligence
- Tune personality settings
- Validate character consistency
- Measure performance baseline

**Then decide on physical robot:**
- Use Pi with cloud API (fast, reliable)
- Use Pi with M1 Mac as network LLM server (fast, private)
- Wait for more powerful small form factor compute

---

## Ready to Start?

Follow Phase 1-6 of the M1 Mac Alpha Test Installation Plan above!

Estimated total time: **45 minutes to full working TARS**
