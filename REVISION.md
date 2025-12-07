# Revision History

All notable changes to this fork are documented here.

---

## [3.1.0] — 2025-12-07

### 🎉 Release: Fully Working macOS Voice Pipeline

This release fixes all macOS ARM compatibility issues and delivers a working end-to-end voice assistant.

### Fixed — macOS ARM Compatibility
- **Piper TTS** — Switched from pip package to native binary (no `piper-phonemize` ARM64 wheel)
- **Piper path** — Fixed binary path resolution (`voices/piper/piper` not `voices/piper`)
- **tflite-runtime** — Removed (no macOS ARM wheels); OpenWakeWord uses ONNX instead
- **hyperdb-python** — Updated to v0.1.4 (v0.0.5 doesn't exist)
- **Piper URL** — Corrected to `aarch64` (not `arm64`) for macOS download
- **Module imports** — Fixed relative imports in `core/` package

### Added — Package Structure
- `gptars/core/__init__.py` — Proper Python package with exports
- PYTHONPATH setup in `run_tars.sh` for module execution

### Changed — Run Script
- Updated to run Python modules (`python3 -m core.voice_engine`)
- Fixed TTS test to use absolute paths
- Updated chat mode to use correct `TARSPersonality` class

### Verified Working
- ✅ Whisper STT (distil-large-v3, 1.51GB)
- ✅ Ollama LLM (llama3:8b)
- ✅ Piper TTS (native binary)
- ✅ OpenWakeWord (ONNX framework)
- ✅ VoiceEngine initialization
- ✅ 7/7 installer verification checks

### Known Issues — TODO for v3.2.0
These issues are documented for tracking and future resolution:

1. **Microphone Permission Dialog** — The macOS microphone permission dialog only appears when triggered from Terminal.app directly, not from VS Code's integrated terminal. This is expected macOS behavior (permission is granted to the parent application).
   - **Workaround:** Run `./run_tars.sh` from Terminal.app for first-time permission grant
   - **File:** `gptars/macos/install_macos.sh` (smoke test section)

2. **Piper dylib Loading** — Piper binary may show warnings about missing dylibs on some systems. The binary still functions but logs warnings.
   - **Affected:** `voices/piper/piper` binary
   - **Impact:** Cosmetic (warnings only, TTS still works)

3. **Whisper Model Download** — First run downloads 1.51GB Whisper model which can timeout on slow connections.
   - **Workaround:** Run voice_engine once before using run_tars.sh
   - **Potential Fix:** Add model download to installer with progress bar

4. **Wake Word Sensitivity** — OpenWakeWord may have false positives/negatives depending on microphone quality and ambient noise.
   - **File:** `gptars/core/wake_word.py`
   - **Potential Fix:** Add configurable threshold settings

5. **Vision Mode Untested** — LLaVA vision mode has not been fully tested on macOS ARM.
   - **File:** `gptars/core/vision_engine.py`
   - **Status:** Needs testing with llava model

6. **No Graceful Shutdown** — Ctrl+C during voice loop may leave audio resources in inconsistent state.
   - **File:** `gptars/core/voice_engine.py`
   - **Potential Fix:** Add signal handlers for cleanup

---

## [3.0.0-alpha] — 2024-12-07

### 🎉 Major Release: Complete Fork Restructuring + macOS v3.0

This release transforms the repository into a professionally maintained fork with clean separation between upstream code and new contributions.

### Added — Fork Architecture
- **`upstream/`** — All original TARS-AI Community code, preserved untouched
- **`shared/`** — Hardware files (3D prints, CAD) usable by both versions
- **`gptars/`** — Complete v3.0 macOS ARM implementation
- **Dual licensing** — Clear CC-BY-NC (upstream) + MIT (new code) separation
- **`FORK-STRATEGY.md`** — Documentation of fork architecture decisions
- **Professional README** — Hub-style README with badges, structure diagram

### Added — gptars v3.0 (macOS ARM)
- **100% offline operation** — No internet required after installation
- **Llama-3-8B-Instruct** — Local LLM via Ollama with Metal GPU acceleration
- **Faster-Whisper STT** — Speech-to-text with distil-large-v3 model (~280ms)
- **Piper TTS** — High-quality text-to-speech (en_US-lessac-medium voice)
- **LLaVA Vision** — Camera analysis via webcam ("TARS, look at this")
- **OpenWakeWord** — "Hey TARS" wake word detection
- **Sub-2s latency** — Complete STT → LLM → TTS pipeline
- **Adjustable personality** — Honesty, humor, discretion, sarcasm sliders
- **One-click installer** — `gptars/macos/install_macos.sh`

### Added — Installer Enhancements
- Full logging to `~/tars-install-YYYYMMDD-HHMMSS.log`
- Error collection and summary report
- Ctrl+C handling with partial completion report
- Post-install verification checks
- Model download selection (interactive)

### Changed
- Root README now serves as hub pointing to both versions
- Documentation consolidated under `gptars/docs/`
- Clear attribution to TARS-AI Community throughout

### Technical Details
- **Platform:** macOS 13+ on Apple Silicon (M1/M2/M3/M4)
- **Python:** 3.11+
- **RAM:** 16GB recommended (8GB minimum)
- **Disk:** ~15GB for models

---

## Pre-Fork History

For changes before this fork's restructuring, see:
- [TARS-AI Community Releases](https://github.com/TARS-AI-Community/TARS-AI/releases)
- `upstream/` directory preserves the original v2 code

---

## Versioning

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** — Incompatible changes
- **MINOR** — New features, backwards compatible
- **PATCH** — Bug fixes, backwards compatible
- **-alpha/-beta/-rc** — Pre-release versions
