# Deprecated Files — GPTars v3.0 Fork

This document lists files from the original TARS-AI Community v2.x codebase that are **no longer used** in GPTars v3.0 but are **preserved untouched** in `upstream/` for license compliance and future upstream sync.

## Purpose

GPTars v3.0 is a complete rewrite for macOS ARM with offline voice capabilities. We maintain the original v2 codebase in `upstream/` for:

1. **License Compliance**: The upstream code is CC-BY-NC 4.0, and we preserve proper attribution
2. **Future Sync**: Ability to pull upstream improvements if needed
3. **Transparency**: Clear documentation of what changed and why

---

## Deprecated Upstream Files

These files in `upstream/` are **NOT used** by GPTars v3.0:

### Core Application Files
| Upstream File | Status | GPTars v3.0 Replacement |
|---------------|--------|-------------------------|
| `upstream/src/app.py` | ❌ Deprecated | `gptars/core/voice_engine.py` |
| `upstream/src/main.py` | ❌ Deprecated | `gptars/core/voice_engine.py` |
| `upstream/App-Start.py` | ❌ Deprecated | `run_tars.sh` (repo root) |
| `upstream/App-Stop.py` | ❌ Deprecated | Built into run_tars.sh |
| `upstream/Install.sh` | ❌ Deprecated | `gptars/macos/install_macos.sh` |
| `upstream/lp.sh` | ❌ Deprecated | N/A (Raspberry Pi specific) |
| `upstream/toggle-autostart.sh` | ❌ Deprecated | N/A (systemd specific) |

### Raspberry Pi Hardware Files
| Upstream File | Status | Notes |
|---------------|--------|-------|
| `upstream/src/modules/module_servo.py` | ❌ Deprecated | Raspberry Pi GPIO only |
| `upstream/src/modules/module_battery.py` | ❌ Deprecated | Hardware-specific |
| `upstream/src/modules/module_controls.py` | ❌ Deprecated | Physical controller integration |
| `upstream/src/character/*/animations/` | ❌ Deprecated | Servo animations for robot body |

### Configuration Files
| Upstream File | Status | GPTars v3.0 Equivalent |
|---------------|--------|------------------------|
| `upstream/src/config.ini.template` | ❌ Deprecated | Direct Ollama config in code |
| `upstream/src/config.ini.macos` | ❌ Deprecated | Replaced by pyproject.toml + env vars |
| `upstream/.env.template` | ❌ Deprecated | No longer needed (local-only) |

### Documentation
| Upstream File | Status | GPTars v3.0 Equivalent |
|---------------|--------|------------------------|
| `upstream/README-UPSTREAM.md` | ✅ Preserved | `gptars/README.md` |
| `upstream/Documentation/` | ⚠️ Reference | `gptars/docs/` (new docs) |

---

## What We Rewrote

GPTars v3.0 is a ground-up rewrite, not a port. Here's what changed:

### Voice Pipeline: `upstream/src/app.py` → `gptars/core/voice_engine.py`
**What changed:**
- **Old**: Cloud-dependent STT/TTS with high latency (5-15s)
- **New**: 
  - Faster-Whisper with Metal GPU acceleration (~280ms STT)
  - Piper TTS for high-quality voice synthesis
  - Complete offline operation
  - <2s end-to-end latency

**Why:**
- macOS ARM has native GPU acceleration we can leverage
- Privacy-first design requires fully offline operation
- Commercial voice APIs cost $0.01-0.10 per conversation

### LLM Integration: `upstream/src/modules/module_llm.py` → `gptars/core/tars_personality.py`
**What changed:**
- **Old**: Multiple cloud API backends (OpenAI, DeepInfra)
- **New**:
  - Direct Ollama integration for local LLMs
  - Llama-3-8B-Instruct optimized for Mac
  - 1-3s response time with Q4 quantization
  - Zero API costs

**Why:**
- Eliminate recurring costs ($20-100/month)
- Remove internet dependency
- Comply with privacy-first architecture

### Vision System: New in GPTars v3.0
**File:** `gptars/core/vision_engine.py`
**What it does:**
- LLaVA-1.6 multimodal model via Ollama
- Native macOS webcam integration
- Image analysis and description
- Vision-augmented conversations

**Why:**
- Not present in upstream (added for v3.0)
- Demonstrates full offline multimodal AI

### Wake Word: New in GPTars v3.0
**File:** `gptars/core/wake_word.py`
**What it does:**
- OpenWakeWord for "Hey TARS" detection
- Always-on listening with low CPU usage
- Hands-free activation

**Why:**
- Not present in upstream (added for v3.0)
- Essential for voice assistant UX

### Installer: `upstream/Install.sh` → `gptars/macos/install_macos.sh`
**What changed:**
- **Old**: Raspberry Pi dependencies (GPIO, servos, systemd)
- **New**:
  - macOS ARM-specific (Homebrew, PyObjC)
  - Full logging and error handling
  - Interactive model selection
  - Smoke tests for validation
  - Auto-detect repo structure

**Why:**
- Different OS, different dependencies
- Professional installer experience
- Better error recovery

---

## License Compliance Note

> **IMPORTANT**: All files in `upstream/` remain under **CC-BY-NC 4.0** license from TARS-AI Community.
> 
> They are **preserved untouched** for:
> - Attribution requirements
> - Historical reference
> - Potential future upstream sync
> 
> **DO NOT modify files in `upstream/`** — all new work goes in `gptars/` under MIT license.

---

## For Upstream Contributors

If you're a TARS-AI Community contributor and want to see what changed:

1. **Voice Pipeline**: Compare `upstream/src/app.py` vs `gptars/core/voice_engine.py`
2. **LLM Backend**: Compare `upstream/src/modules/module_llm.py` vs `gptars/core/tars_personality.py`
3. **Architecture**: We removed hardware dependencies and rewrote for Apple Silicon

**Our changes are intentional:**
- Upstream targets Raspberry Pi hardware robots
- GPTars targets macOS software-only offline voice assistants
- Both are valid approaches for different use cases

---

## Questions?

- **Upstream project**: https://github.com/TARS-AI-Community/TARS-AI
- **This fork (v3.0)**: https://github.com/James-von-Detroit/tars-ai
- **Discord**: https://discord.gg/AmE2Gv9EUt

Last updated: December 2025
