# License

[![MIT License](https://img.shields.io/badge/gptars-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CC BY-NC 4.0](https://img.shields.io/badge/upstream%20%7C%20shared-CC--BY--NC%204.0-blue.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

## Dual License Structure

This repository uses a **dual-licensing model** to respect upstream work while enabling permissive licensing for new contributions.

| Folder | License | Commercial Use | Description |
|--------|---------|----------------|-------------|
| `gptars/` | **MIT** | ✅ Yes | v3.0+ macOS voice assistant (new code) |
| `upstream/` | **CC-BY-NC 4.0** | ❌ No | Original TARS-AI v2.x (archived) |
| `shared/` | **CC-BY-NC 4.0** | ❌ No | 3D models, CAD files |
| Root files | **MIT** | ✅ Yes | README, LICENSE, scripts, etc. |

---

## MIT License (gptars/ and root files)

```
MIT License

Copyright (c) 2024–2025 James-von-Detroit

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

### MIT Applies To:
- `gptars/core/` — Voice, vision, wake word engines
- `gptars/macos/` — macOS installer and requirements
- `gptars/tests/` — Test suite
- `gptars/docs/` — v3.0+ documentation
- `README.md`, `LICENSE.md`, `FORK-STRATEGY.md`, `REVISION.md`, `DEPRECATION.md`
- `run_tars.sh`, `add_license_headers.sh`, `.gitignore`

---

## Creative Commons Attribution-NonCommercial 4.0 (upstream/ and shared/)

All code in `upstream/` and `shared/` is derived from **TARS-AI Community**.

### Required Attribution:
```
Portions of this software are derived from TARS-AI 
© TARS-AI Community, licensed under CC-BY-NC 4.0.
https://github.com/TARS-AI-Community/TARS-AI
```

### CC-BY-NC 4.0 Summary:
- ✅ **Share** — copy and redistribute in any medium or format
- ✅ **Adapt** — remix, transform, and build upon the material
- ✅ **Attribution** — give appropriate credit, link to license, indicate changes
- ❌ **NonCommercial** — may NOT use for commercial purposes
- 🔗 Full text: https://creativecommons.org/licenses/by-nc/4.0/legalcode
- 📄 Local copy: [`upstream/LICENSE-UPSTREAM-CC-BY-NC-4.0`](upstream/LICENSE-UPSTREAM-CC-BY-NC-4.0)

### CC-BY-NC 4.0 Applies To:
- `upstream/src/` — Original TARS-AI v2.x Python code
- `upstream/Install.sh`, `upstream/App-Start.py`, `upstream/App-Stop.py`
- `upstream/README-UPSTREAM.md`, `upstream/ATTRIBUTION-UPSTREAM.md`
- `shared/3d Printer Files/` — STL files for physical TARS
- `shared/CAD/` — Design files
- `shared/media/` — Images, videos, branding

---

## Usage Scenarios

| Scenario | License | Commercial? |
|----------|---------|-------------|
| Using only `gptars/` code | MIT | ✅ Yes |
| Using only `upstream/` code | CC-BY-NC 4.0 | ❌ No |
| Using both together | Both apply | ❌ No (CC-BY-NC governs combined work) |
| Building commercial product on `gptars/` | MIT | ✅ Yes (must strip CC-BY-NC content) |
| Forking for personal/educational use | MIT + CC-BY-NC | ✅ Yes (non-commercial) |

---

## Why Dual License?

1. **Respect Upstream**: TARS-AI Community v2.x is CC-BY-NC 4.0, we preserve that
2. **Enable Innovation**: Our v3.0 work (macOS, offline, new features) is MIT
3. **Clear Boundaries**: `upstream/` is untouched archive, `gptars/` is new development
4. **Commercial Freedom**: If you only use `gptars/`, you have full MIT permissions

---

## License Files

| File | Purpose |
|------|---------|
| `LICENSE.md` | This file — dual license explanation |
| `LICENSE-HEADER.txt` | Copy-paste headers for source files |
| `upstream/LICENSE-UPSTREAM-CC-BY-NC-4.0` | Full CC-BY-NC 4.0 text |
| `gptars/LICENSE.md` | MIT license (for clarity) |

---

## Attribution

### Upstream Attribution (Required)
```
This software incorporates code from TARS-AI Community, licensed under 
CC-BY-NC 4.0. See upstream/LICENSE-UPSTREAM-CC-BY-NC-4.0 for details.

Original TARS-AI: https://github.com/TARS-AI-Community/TARS-AI
```

### Character Attribution
TARS character is from the film **Interstellar** (2014):
- **Directed by**: Christopher Nolan
- **Written by**: Jonathan Nolan and Christopher Nolan
- **Studio**: Paramount Pictures / Warner Bros.

This project is a fan work and is not affiliated with or endorsed by the filmmakers.

---

## Questions?

- **Upstream licensing**: [TARS-AI Community](https://github.com/TARS-AI-Community/TARS-AI)
- **Fork-specific (v3.0+)**: Open an issue on this repository
- **Commercial use of `gptars/`**: Fully permitted under MIT (see above)

---

## Summary

- ✅ **Use `gptars/` commercially**: Fully MIT licensed
- ❌ **Don't use `upstream/` commercially**: CC-BY-NC 4.0
- ✅ **Fork and modify**: Both licenses allow it (with attribution)
- ✅ **Personal/educational use**: Everything available
- 📁 **Separate cleanly**: `gptars/` vs `upstream/` folder structure

Last updated: December 2025
