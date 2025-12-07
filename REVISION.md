# Revision History

All notable changes to this fork are documented here.

---

## [3.3.0] — 2025-12-07

### 🎉 Major Release: Native ARM TTS & Continuous Listening Mode

This release brings significant improvements to macOS ARM compatibility, TTS quality, and user experience with a new continuous listening mode.

### Fixed — Piper TTS Native ARM64 Support
- **Piper Python Package** — Switched from x86_64 binary to native `piper-tts` Python package
- **ARM64 Compatibility** — Resolved `incompatible architecture (have 'arm64', need 'x86_64')` errors
- **TARS Voice Model** — Now using custom `TARS.onnx` voice model from upstream project
- **Upstream Parity** — TTS implementation now matches upstream TARS-AI approach exactly

### Fixed — Ollama API Compatibility
- **Native API Endpoint** — Switched from `/v1/chat/completions` to native `/api/chat`
- **Response Parsing** — Fixed JSON response parsing for native Ollama format
- **Model Selection** — Added `llama3:8b-instruct-q4_0` as recommended instruction-tuned model

### Added — Continuous Listening Mode
- **Voice Activity Detection** — Auto-detect speech start/stop without push-to-talk
- **Energy-based VAD** — Simple, reliable speech detection using audio energy levels
- **Configurable Thresholds** — Adjustable silence duration and speech length requirements
- **Mode Selection** — Interactive menu to choose between push-to-talk and continuous listening

### Added — TTS Testing Infrastructure
- **`gptars/tests/tts_comparison.py`** — Test script to compare original TARS samples vs Piper output
- **Voice Quality Benchmarking** — Side-by-side audio comparison tooling

### Changed — Installer Updates
- **Model Selection** — Added `llama3:8b-instruct-q4_0` as option 2 (recommended)
- **Reordered Options** — Better organization of LLM model choices in installer menu

### Technical Details
- **Piper Package** — `piper-tts` 1.3.0 with native ARM64 wheel (`macosx_11_0_arm64`)
- **Voice Model** — `TARS.onnx` (22050Hz, trained with Piper 1.0.0)
- **TTS Settings** — Using model defaults (noise_scale=0.667, length_scale=1, noise_w=0.8)

### Removed
- **Custom Synthesis Config** — Removed experimental TTS tuning, using model defaults instead
- **Sentence Pauses** — Removed artificial pauses between sentences (not in upstream)

---

## [3.0.2] — 2025-12-07

### 📦 Package Structure & Import Fixes

This release fixes all import errors and path issues after the repository restructure.

### Added — Package Structure
- **`gptars/__init__.py`** — Makes gptars a proper Python package with exports
- **`DEPRECATION.md`** — Complete documentation of deprecated upstream files
- **`validate_structure.sh`** — Automated validation script (21 tests)
- **`IMPLEMENTATION_COMPLETE.md`** — Comprehensive implementation summary

### Fixed — Import System
- **Package imports** — All imports now use `from gptars.core import ...` pattern
- **PYTHONPATH** — Set to repo root (not gptars/) for correct resolution
- **Virtual environment** — Now at repo root (`tars-ai/venv/`)
- **Test imports** — Updated test file to use package-style imports
- **Module execution** — Use `python3 -m gptars.core.module` pattern

### Changed — Scripts
- **`run_tars.sh`** — Auto-cd to repo root, sets PYTHONPATH, updated menu with 6 options
- **`gptars/macos/install_macos.sh`** — Enhanced smoke test validates package imports
- **All Python files** — Added proper license headers (MIT for gptars/, CC-BY-NC for upstream/)

### Changed — Documentation
- **README.md** — Added "How to Run" section at top, deprecation summary with link to DEPRECATION.md
- **LICENSE.md** — Comprehensive dual-license structure with usage scenarios
- **Repository structure** — Clear separation of MIT (gptars/) and CC-BY-NC (upstream/) code

### Validation
- ✅ All 21 structure validation tests pass
- ✅ All imports resolve correctly: `import gptars`, `from gptars.core import ...`
- ✅ Scripts work from any location
- ✅ Virtual environment at correct location

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
