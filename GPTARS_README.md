# gptars v3.0 Alpha - New Addition to TARS-AI Repository

## What is gptars?

**gptars v3.0 Alpha** is a complete, standalone implementation of a TARS voice assistant specifically designed for Apple Silicon Macs (M1/M2/M3/M4). It lives in the `/gptars` directory of this repository.

This is a **separate, independent project** from the main TARS-AI codebase, focused on:
- **100% offline operation** on macOS
- **Voice-first interaction** (STT → LLM → TTS)
- **Vision capabilities** via webcam
- **No hardware requirements** (software-only)

## Key Differences from Main TARS-AI

| Feature | Main TARS-AI | gptars v3.0 |
|---------|-------------|-------------|
| **Platform** | Raspberry Pi + Hardware | macOS (Software Only) |
| **Target Users** | Robot builders | Mac users |
| **Setup Complexity** | High (servos, 3D printing) | Low (software install) |
| **Primary Use** | Physical robot | Voice assistant |
| **Installation** | Multi-step hardware | One-click script |
| **Cost** | $300-450 (full robot) | Free (after Mac) |

## Quick Start

```bash
cd gptars
./macos/install_macos.sh
./run_tars.sh
```

**Full documentation:** See `/gptars/README.md`

## Why a Separate Implementation?

The main TARS-AI project focuses on creating a physical robot with servos, motors, and a 3D-printed body. Many users wanted just the AI/voice capabilities without building the hardware.

**gptars v3.0** provides:
1. A fully functional TARS assistant for Mac users
2. An alternative for those who want to test TARS AI before building hardware
3. A development platform for personality and conversation features
4. A standalone voice assistant that's ready to use immediately

## Relationship to Main Project

- **gptars is inspired by** the main TARS-AI project
- **Shares the TARS personality** and character design
- **Can be a stepping stone** to building the full robot
- **Focuses on AI/software** while main project includes hardware
- **Fully credited** to original TARS-AI community and contributors

## For Robot Builders

If you want the **physical TARS robot**, use the main project in `/src`.

If you want to **test the AI first** or just want a **voice assistant**, use `/gptars`.

You can use both! Many developers use gptars for rapid AI development, then port working features to the physical robot.

## Documentation

All gptars documentation is self-contained in `/gptars`:
- `/gptars/README.md` - Main overview
- `/gptars/docs/` - Complete guides
- `/gptars/QUICK_REFERENCE.md` - Quick start

## Status

**Version:** 3.0.0-alpha  
**Status:** Feature-complete, ready for testing  
**Platform:** macOS 13+ on Apple Silicon (M1/M2/M3/M4)  
**License:** MIT (same as parent project)

## Get Started

```bash
cd gptars
cat README.md
```

---

Both projects share the same goal: bringing TARS from Interstellar to life. Choose the path that fits your needs! 🤖
