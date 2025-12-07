# Attribution

## gptars v3.0 - Full Attribution and Credits

This document provides comprehensive attribution for all components of gptars v3.0, following the guidelines established by the TARS-AI Community.

---

## Upstream Projects

### TARS-AI Community Project

**gptars v3.0** is derived from the TARS-AI Community project, which recreates the TARS robot from the film *Interstellar*.

- **Repository:** https://github.com/TARS-AI-Community/TARS-AI
- **License:** Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC 4.0)
- **Attribution Guidelines:** https://github.com/TARS-AI-Community/TARS-AI/blob/V2/ATTRIBUTION.md

**What we derived:**
- TARS character personality concepts and behavior patterns
- Character configuration structure (persona.ini format)
- System prompt engineering patterns for TARS personality
- Attribution and community guidelines

**Attribution Statement:**
```
Portions of this software are derived from TARS-AI © TARS-AI Community 
(via fork by James-von-Detroit), licensed under CC-BY-NC 4.0.
```

### James-von-Detroit/tars-ai Fork

**gptars v3.0** builds upon the James-von-Detroit fork of TARS-AI.

- **Repository:** https://github.com/James-von-Detroit/tars-ai
- **License:** CC-BY-NC 4.0 (inherited from upstream)

This fork provided the foundation and inspired the macOS-native rewrite.

---

## Original TARS Character

### From the Film *Interstellar* (2014)

**TARS** is a character from the motion picture *Interstellar*.

- **Film:** *Interstellar* (2014)
- **Director/Writer:** Christopher Nolan
- **Writer:** Jonathan Nolan
- **Studios:** Paramount Pictures, Warner Bros., Legendary Pictures
- **TARS Performed by:** Bill Irwin (voice and motion capture)
- **Production Design:** Nathan Crowley

**Disclaimer:** This project is a fan-made tribute and educational implementation. We claim no rights to the TARS character or *Interstellar* intellectual property. All character elements are used for educational and non-commercial purposes under fair use principles.

**Statement:**
```
This project includes AI-generated elements inspired by Bill Irwin's 
portrayal of TARS in the film Interstellar (2014), directed by 
Christopher Nolan.
```

---

## Original CAD Designs

### Charlie Diaz - Miniaturized CAD

While gptars v3.0 is software-only, the original TARS-AI Community project includes CAD designs:

- **Original CAD Designer:** Charlie Diaz
- **Description:** "Miniaturized CAD designs based on the mechanical puppet designs by Christopher Nolan, Nathan Crowley, and the production team who originally brought TARS to life"
- **Additional Modifications:** TARS-AI Community contributors

*Note: gptars v3.0 does not include physical hardware designs but acknowledges this heritage.*

---

## Open Source Dependencies

### Core AI and ML Libraries

#### Meta Llama 3
- **Project:** Llama 3 Language Model
- **Creator:** Meta AI (Facebook AI Research)
- **License:** Llama 3 Community License
- **Website:** https://ai.meta.com/llama/
- **Usage:** Primary language model for TARS intelligence

#### Ollama
- **Project:** Local LLM serving platform
- **Creator:** Ollama team
- **License:** MIT License
- **Website:** https://ollama.ai
- **GitHub:** https://github.com/ollama/ollama
- **Usage:** Local model serving with Metal GPU acceleration

### Speech Recognition

#### Faster-Whisper
- **Project:** Fast Whisper transcription with CTranslate2
- **Creator:** SYSTRAN
- **License:** MIT License
- **GitHub:** https://github.com/SYSTRAN/faster-whisper
- **Usage:** Speech-to-text with Metal GPU support

#### OpenAI Whisper
- **Project:** Whisper speech recognition models
- **Creator:** OpenAI
- **License:** MIT License
- **GitHub:** https://github.com/openai/whisper
- **Usage:** Base models for Faster-Whisper

### Text-to-Speech

#### Piper TTS
- **Project:** Fast, local neural text-to-speech
- **Creator:** Rhasspy project / Michael Hansen
- **License:** MIT License
- **GitHub:** https://github.com/rhasspy/piper
- **Usage:** High-quality TTS for TARS voice

### Wake Word Detection

#### OpenWakeWord
- **Project:** Open-source wake word detection
- **Creator:** David Scripka
- **License:** Apache 2.0
- **GitHub:** https://github.com/dscripka/openWakeWord
- **Usage:** "Hey TARS" wake word detection

### Vision Models

#### LLaVA
- **Project:** Large Language and Vision Assistant
- **Creators:** University of Wisconsin-Madison, Microsoft Research, Columbia University
- **License:** Apache 2.0
- **Website:** https://llava-vl.github.io
- **Usage:** Vision language model for camera analysis

#### OpenCV
- **Project:** Open Source Computer Vision Library
- **License:** Apache 2.0
- **Website:** https://opencv.org
- **Usage:** Camera capture and image processing

### Python Libraries

#### Core Libraries
- **NumPy** - BSD License - Numerical computing
- **SciPy** - BSD License - Scientific computing
- **PyTorch** - BSD License - Deep learning framework
- **Transformers** (Hugging Face) - Apache 2.0 - Model hub
- **sounddevice** - MIT License - Audio I/O
- **soundfile** - BSD License - Audio file I/O
- **Pillow** - HPND License - Image processing
- **requests** - Apache 2.0 - HTTP library

#### macOS Integration
- **PyObjC** - MIT License - macOS framework bindings

All dependencies retain their original licenses. See `requirements-macos.txt` for complete list.

---

## New Contributions (MIT Licensed)

The following components are original work for gptars v3.0, licensed under MIT:

### Core Implementation
- **Author:** James-von-Detroit
- **License:** MIT License
- **Components:**
  - `core/tars_personality.py` - Enhanced personality system with sliders
  - `core/voice_engine.py` - Complete voice pipeline (STT→LLM→TTS)
  - `core/vision_engine.py` - Vision integration with LLaVA
  - `core/wake_word.py` - Wake word detection system

### Installation and Tools
- `macos/install_macos.sh` - One-click macOS ARM installer
- `macos/requirements-macos.txt` - ARM-optimized dependencies
- `macos/microphone_permissions.scpt` - Permission helper
- `models/download_models.py` - Model download utility
- `run_tars.sh` - Interactive launcher

### Documentation
- `README.md` - Project overview
- `docs/MACOS_INSTALL_GUIDE.md` - Installation instructions
- `docs/OPERATION_GUIDE.md` - Usage manual
- `docs/TROUBLESHOOTING.md` - Problem solving guide
- `IMPLEMENTATION_SUMMARY.md` - Technical summary
- `SIMULATED_TEST_OUTPUT.md` - Example conversations
- `QUICK_REFERENCE.md` - Quick reference card
- `SECURITY.md` - Security advisory

### Testing
- `tests/test_tars_conversation.py` - Complete test suite

### Configuration
- `pyproject.toml` - Project metadata
- `.gitignore` - Version control configuration

---

## Attribution Best Practices

### When Using gptars v3.0

**You must:**

1. **Provide Attribution**
   ```
   This project uses gptars v3.0 by James-von-Detroit.
   Portions derived from TARS-AI © TARS-AI Community, licensed under CC-BY-NC 4.0.
   Based on TARS from Interstellar (2014) by Christopher Nolan.
   ```

2. **Indicate Modifications**
   - Clearly state what you've changed
   - Maintain attribution in modified versions

3. **Follow Upstream Guidelines**
   - Review https://github.com/TARS-AI-Community/TARS-AI/blob/V2/ATTRIBUTION.md
   - Respect the CC-BY-NC 4.0 license terms

4. **Non-Commercial Use**
   - Due to CC-BY-NC 4.0 upstream license
   - No monetization of derivative works

### When Sharing Online

**Include in your README or documentation:**

```markdown
## Credits

This project is based on gptars v3.0 by James-von-Detroit, which derives from:
- TARS-AI Community project (CC-BY-NC 4.0)
- TARS character from Interstellar (2014), directed by Christopher Nolan

This is a fan-made, educational project. No commercial use.
```

**For videos/blogs/posts:**
- Credit the film *Interstellar* and Christopher Nolan
- Credit TARS-AI Community
- Credit gptars v3.0 by James-von-Detroit
- Note it's a fan project, non-commercial

---

## Community Contributions

### Contributing to gptars v3.0

When contributing to this project:

1. **New code:** Automatically licensed under MIT (unless derived from CC-BY-NC portions)
2. **Modifications to CC-BY-NC portions:** Must remain CC-BY-NC 4.0
3. **Documentation:** MIT License
4. **Always maintain attribution** in source files

### Recognition

We thank all contributors to:
- TARS-AI Community project
- James-von-Detroit fork
- All open-source dependency maintainers
- The *Interstellar* production team for inspiring this work

---

## Legal Notes

### Trademark Notice

"TARS" and "Interstellar" are trademarks of their respective owners. This project does not claim any trademark rights and uses these terms for descriptive purposes only.

### No Endorsement

This project is not endorsed by, affiliated with, or sponsored by:
- Christopher Nolan
- Paramount Pictures, Warner Bros., or Legendary Pictures
- TARS-AI Community (though we follow their guidelines)
- Meta AI, Ollama, or other dependency creators

### Fair Use

Character personality elements are used under fair use principles for:
- Educational purposes
- Non-commercial fan tribute
- Transformative implementation as software

---

## Contact

**For attribution questions:**
- gptars v3.0: James-von-Detroit (GitHub)
- Upstream TARS-AI: https://github.com/TARS-AI-Community/TARS-AI
- Commercial licensing: Contact TARS-AI Community

**For open-source dependencies:**
- See respective project websites and GitHub repositories

---

## Version History

- **v3.0 Alpha** (December 2024) - Initial release by James-von-Detroit
  - Complete rewrite for Apple Silicon
  - Fully offline voice and vision capabilities
  - MIT License for new code
  - CC-BY-NC 4.0 for derived portions

---

*This attribution document complies with CC-BY-NC 4.0 Section 3 requirements and the TARS-AI Community attribution guidelines.*

**Last Updated:** December 7, 2024
