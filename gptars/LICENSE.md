# License

## Dual License Notice

**gptars v3.0** uses a dual-licensing structure to properly attribute derivative works while allowing new contributions under a permissive license.

### Summary

- **Portions derived from upstream projects:** CC-BY-NC 4.0 (see below)
- **All new code and documentation:** MIT License (see below)

---

## Part 1: Upstream Derivative Works (CC-BY-NC 4.0)

Portions of this software are derived from:
- **TARS-AI Community project** (https://github.com/TARS-AI-Community/TARS-AI)
- **James-von-Detroit/tars-ai fork** (https://github.com/James-von-Detroit/tars-ai)

These portions are licensed under **Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC 4.0)**.

**Covered Components:**
- TARS character personality and behavior concepts
- Original TARS prompt engineering patterns
- Character configuration file structure (persona.ini format)
- Attribution and credit guidelines

**Full CC-BY-NC 4.0 License Text:**
See https://creativecommons.org/licenses/by-nc/4.0/legalcode

**Attribution Notice:**
```
Portions of this software are derived from TARS-AI © TARS-AI Community 
(via fork by James-von-Detroit), licensed under CC-BY-NC 4.0.
```

**You must:**
- Provide attribution to TARS-AI Community and James-von-Detroit
- Indicate if you modified the derived portions
- Not use for commercial purposes
- Share adaptations under the same license

---

## Part 2: New Contributions (MIT License)

All original code, documentation, and implementations created specifically for **gptars v3.0** are licensed under the **MIT License**.

**Covered Components:**
- macOS ARM-native installation scripts (`macos/install_macos.sh`)
- Voice pipeline implementation (`core/voice_engine.py`)
- Vision integration (`core/vision_engine.py`)
- Wake word detection (`core/wake_word.py`)
- Enhanced personality system (`core/tars_personality.py`)
- macOS-specific requirements and configuration
- All documentation in `docs/` directory
- Test suite in `tests/` directory
- Build and helper scripts
- Project structure and organization

**MIT License Text:**

```
MIT License

Copyright (c) 2024 James-von-Detroit

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## How This Works Together

1. **If you use only the new MIT-licensed components** (voice pipeline, macOS installer, etc.): MIT License applies. You can use commercially.

2. **If you use the TARS character/personality derived portions**: CC-BY-NC 4.0 applies. You must:
   - Provide attribution
   - Not use commercially
   - Share adaptations under CC-BY-NC 4.0

3. **If you use the complete gptars v3.0 project**: Both licenses apply. The more restrictive terms (CC-BY-NC 4.0) govern commercial use and attribution.

---

## Third-Party Dependencies

This project uses open-source dependencies (Ollama, Llama 3, Faster-Whisper, Piper TTS, OpenWakeWord, etc.). Each retains its own license. See `CREDITS.md` for details.

---

## Questions About Licensing?

- **For upstream TARS-AI:** See https://github.com/TARS-AI-Community/TARS-AI/blob/V2/ATTRIBUTION.md
- **For new MIT-licensed code:** Contact James-von-Detroit
- **For commercial use inquiries:** Contact TARS-AI Community for CC-BY-NC 4.0 portions

---

## SPDX Identifiers

```
SPDX-License-Identifier: MIT AND CC-BY-NC-4.0
```

Where:
- `MIT`: New contributions
- `CC-BY-NC-4.0`: Derived upstream works
