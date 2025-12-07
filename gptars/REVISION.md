# Revision History

## gptars - Version Changelog

This document tracks the evolution of the TARS project from its community origins to the current macOS-native voice assistant.

---

## v3.0 Alpha — December 2024
### **"Full macOS ARM-Native Offline Voice + Vision Release"**

**🎉 Major Milestone**: Complete rewrite for Apple Silicon with full offline capabilities.

### New in v3.0

#### Core Features
- ✅ **100% Offline Voice Pipeline**
  - Speech-to-Text: Faster-Whisper (distil-large-v3) with Metal GPU acceleration (~280ms)
  - Language Model: Llama-3-8B-Instruct Q4 via Ollama (~1.4s)
  - Text-to-Speech: Piper TTS with high-quality voice (~150ms)
  - Total latency: 1.8s end-to-end on M2

- ✅ **Vision Capabilities**
  - LLaVA-1.6 (7B) for image understanding
  - MacBook webcam integration via OpenCV
  - Interactive and programmatic modes

- ✅ **Wake Word Detection**
  - "Hey TARS" always-listening mode
  - OpenWakeWord with low CPU usage
  - Background detection with callback integration

- ✅ **Enhanced Personality System**
  - Adjustable honesty slider (0-100%)
  - Adjustable humor slider (0-100%)
  - Adjustable discretion slider (0-100%)
  - Save/load configurations
  - Movie-accurate default settings (90/60/50)

#### Technical Improvements
- 🍎 **macOS ARM-Native**
  - One-click installer script (`install_macos.sh`)
  - ARM-optimized dependencies
  - Metal GPU acceleration for AI models
  - Native Python 3.11 support

- 🔒 **Security Enhancements**
  - Updated onnx: 1.16.2 → 1.17.0 (path traversal CVE)
  - Updated torch: 2.4.1 → 2.6.0 (RCE vulnerability)
  - Updated transformers: 4.45.0 → 4.48.0 (deserialization vulnerabilities)
  - Complete security advisory in SECURITY.md

- 📚 **Comprehensive Documentation**
  - Complete installation guide (MACOS_INSTALL_GUIDE.md)
  - Detailed operation manual (OPERATION_GUIDE.md)
  - Troubleshooting guide (TROUBLESHOOTING.md)
  - Quick reference card (QUICK_REFERENCE.md)
  - Security advisories (SECURITY.md)
  - Implementation summary (IMPLEMENTATION_SUMMARY.md)

- ⚖️ **Dual Licensing**
  - MIT License for new code (macOS installer, voice/vision engines, docs)
  - CC-BY-NC 4.0 for derived portions (TARS personality concepts)
  - Complete attribution documentation (LICENSE.md, ATTRIBUTION.md, CREDITS.md, NOTICE)

#### New Files & Modules
- `core/tars_personality.py` - Enhanced personality system (380 lines)
- `core/voice_engine.py` - Complete voice pipeline (420 lines)
- `core/vision_engine.py` - Camera + vision integration (380 lines)
- `core/wake_word.py` - Wake word detection system (330 lines)
- `macos/install_macos.sh` - Automated installer (260 lines)
- `macos/requirements-macos.txt` - ARM dependencies with versions
- `models/download_models.py` - Model download utility
- `run_tars.sh` - Interactive launcher
- `tests/test_tars_conversation.py` - Complete test suite (360 lines)
- 7 comprehensive documentation files (3,500+ lines)
- 4 licensing documents (licensing compliance)

#### Performance Benchmarks

| Mac Model | STT | LLM | TTS | Total Latency |
|-----------|-----|-----|-----|---------------|
| M1 | 350ms | 2.1s | 180ms | 2.6s |
| M2 | 280ms | 1.4s | 150ms | **1.8s** ✅ |
| M3 | 220ms | 0.9s | 120ms | 1.2s |
| M4 | 180ms | 0.7s | 100ms | 1.0s |

#### Credits
- **Creator**: James-von-Detroit
- **Built upon**: TARS-AI Community project (CC-BY-NC 4.0)
- **Built upon**: James-von-Detroit/tars-ai fork (CC-BY-NC 4.0)
- **Total new code**: 2,010 lines (core modules + tools)
- **Total documentation**: 3,500+ lines
- **Total files**: 25 files created

### Breaking Changes
- Complete rewrite - not compatible with v2.x hardware control
- Requires macOS 13+ and Apple Silicon
- Python 3.11+ required
- New file structure (gptars/ directory)

### Known Issues
- Wake word detection has ~1-2s delay after trigger
- Vision mode requires good lighting
- M1 8GB models may experience slower LLM responses
- Alpha status - expect bugs and rough edges

---

## v2.x Series — 2023-2024
### **Hardware Integration & Foundation**

**Credit**: James-von-Detroit/tars-ai fork

### Key Features
- Hardware control for physical TARS robot
- Servo integration for articulation
- LED cue light control
- Battery monitoring
- Raspberry Pi support
- Local LLM experimentation (Ollama)
- ChatUI for software-only mode
- Memory system with HyperDB
- Character system with personality traits

### Innovations
- First integration of local LLMs (Ollama)
- M1 Mac testing and optimization
- ARM Mac support documentation
- Software-only mode (config.ini.macos)
- Enhanced memory with vector database

### Technical Details
- Platform: Raspberry Pi 4/5, macOS ARM
- LLM: Ollama with various models
- Memory: HyperDB with RAG
- Character: JSON-based with persona.ini

### Documentation
- ARM-MAC-LOCAL-LLM-GUIDE.md
- MACOS-SETUP-GUIDE.md
- M1-ALPHA-TEST-SETUP.md

### Credits
- **Fork maintainer**: James-von-Detroit
- **Based on**: TARS-AI Community v1.x
- **License**: CC-BY-NC 4.0 (inherited)

---

## v1.x Series — 2022-2023
### **Original TARS Robot Recreation**

**Credit**: TARS-AI Community

### Foundation
The original TARS-AI Community project that started it all:

- Physical robot chassis design
- CAD files by Charlie Diaz (miniaturized from film designs)
- Servo control systems
- Original character personality framework
- Community guidelines and attribution standards
- Hardware schematics and build guides

### Vision
- Recreate TARS from *Interstellar* as a physical robot
- Open-source hardware and software
- Community-driven development
- Educational and non-commercial focus

### Key Components
- 3D-printed body parts
- Articulated segments with servos
- LED matrix for "cue light"
- Raspberry Pi control
- Basic AI integration

### Cultural Impact
- Established TARS-AI Community
- Discord server for builders
- Reddit community (r/TARS_AI)
- Inspired multiple forks and derivatives
- Set attribution standards for character use

### Credits
- **Community**: TARS-AI Community
- **CAD Designs**: Charlie Diaz (based on film designs by Christopher Nolan, Nathan Crowley, and production team)
- **License**: CC-BY-NC 4.0
- **Attribution Guidelines**: [Link](https://github.com/TARS-AI-Community/TARS-AI/blob/V2/ATTRIBUTION.md)

---

## Future Roadmap

### v3.1 (Q1 2025) — "Enhanced Intelligence"
- [ ] Custom TARS voice cloning with Piper training
- [ ] Web UI for personality sliders
- [ ] HomeKit integration for smart home control
- [ ] Custom wake word training ("CASE", "TARS", user-defined)
- [ ] Multi-language support (Spanish, French, German)
- [ ] Conversation history and context memory
- [ ] Plugin system for extensibility

### v3.2 (Q2 2025) — "Multi-Modal TARS"
- [ ] Hardware bridge to v2.x robot control
- [ ] Gesture recognition via camera
- [ ] Multi-modal responses (voice + display + actions)
- [ ] Swarm coordination (multiple TARS instances)
- [ ] Improved vision with object tracking
- [ ] Real-time transcription display
- [ ] Mobile app for remote control

### v4.0 (Future) — "Physical Integration"
- [ ] Complete physical robot integration
- [ ] Updated 3D-printed body designs for 2025
- [ ] Advanced servo control with choreography
- [ ] LED matrix "cue light" animations
- [ ] Battery power with autonomy
- [ ] SLAM navigation
- [ ] Environmental awareness
- [ ] Human following and interaction

### v5.0 (Vision) — "True TARS"
- [ ] Advanced emotional intelligence
- [ ] Context-aware humor generation
- [ ] Proactive assistance
- [ ] Long-term memory and relationships
- [ ] Self-learning personality adaptation
- [ ] Multi-agent coordination
- [ ] Space robot control interfaces (just kidding... or are we?)

---

## Version Comparison

| Feature | v1.x (Hardware) | v2.x (Hybrid) | v3.0 (Software) |
|---------|-----------------|---------------|-----------------|
| **Platform** | Raspberry Pi | RPi + Mac | macOS ARM |
| **Physical Robot** | ✅ Primary | ✅ Supported | 🔄 Planned (v4.0) |
| **Voice Input** | ❌ | ⚠️ Basic | ✅ Advanced |
| **Voice Output** | ❌ | ⚠️ Basic | ✅ High-quality |
| **Vision** | ❌ | ❌ | ✅ LLaVA-1.6 |
| **Wake Word** | ❌ | ❌ | ✅ "Hey TARS" |
| **Local LLM** | ❌ | ⚠️ Experimental | ✅ Production |
| **Offline** | ✅ | ⚠️ Partial | ✅ 100% |
| **Latency** | N/A | Variable | <2s |
| **ARM Optimized** | ❌ | ⚠️ Partial | ✅ Full |
| **Documentation** | ⚠️ Basic | ⚠️ Good | ✅ Comprehensive |
| **License** | CC-BY-NC 4.0 | CC-BY-NC 4.0 | MIT + CC-BY-NC 4.0 |

---

## Attribution Timeline

### December 2024 — v3.0 Attribution Standards
- Dual licensing implemented (MIT + CC-BY-NC 4.0)
- Complete attribution documentation
- ATTRIBUTION.md following upstream guidelines
- CREDITS.md for quick reference
- NOTICE file for legal compliance
- LICENSE.md with dual license structure

### 2023-2024 — v2.x Attribution
- Continued CC-BY-NC 4.0 compliance
- Fork attribution to TARS-AI Community
- Documentation of modifications

### 2022-2023 — v1.x Attribution
- Original CC-BY-NC 4.0 license
- Attribution guidelines established
- Film credits to Christopher Nolan and production team
- CAD credits to Charlie Diaz

---

## Project Evolution Stats

| Metric | v1.x | v2.x | v3.0 |
|--------|------|------|------|
| **Total Files** | ~50 | ~100 | 25 (gptars only) |
| **Lines of Code** | ~5,000 | ~8,000 | ~2,000 (new) |
| **Documentation** | ~1,000 | ~2,000 | ~3,500 |
| **Contributors** | Community | 1 (+ community) | 1 (+ community) |
| **Primary Focus** | Hardware | Hardware + Software | Software |
| **Platform** | RPi | RPi + Mac | Mac ARM |
| **Maturity** | Stable | Experimental | Alpha |

---

## Thank You

This project stands on the shoulders of giants:

1. **TARS-AI Community** — For pioneering the physical TARS recreation
2. **James-von-Detroit's v2.x** — For hardware integration and local LLM work
3. **Christopher & Jonathan Nolan** — For creating TARS in *Interstellar*
4. **Open Source Community** — For all the amazing tools we use

Each version has built upon the last, and v3.0 continues this tradition while taking TARS in a new direction: fully offline, fully functional, fully on macOS.

---

## Questions?

- **For v3.0**: See [README.md](README.md) or open an [issue](https://github.com/James-von-Detroit/tars-ai/issues)
- **For v2.x**: See [original fork](https://github.com/James-von-Detroit/tars-ai)
- **For v1.x**: See [TARS-AI Community](https://github.com/TARS-AI-Community/TARS-AI)

---

**Last Updated**: December 7, 2024  
**Current Version**: v3.0 Alpha  
**Status**: Active Development  
**License**: MIT (new code) + CC-BY-NC 4.0 (derived portions)
