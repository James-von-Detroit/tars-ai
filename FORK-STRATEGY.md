# Fork Strategy

This document explains how this fork is structured and why, ensuring long-term maintainability and clean upstream synchronization.

---

## 🎯 Goals

1. **Stay in sync with upstream forever** — No merge conflicts when pulling from TARS-AI-Community
2. **Keep all v3.0 work intact** — macOS ARM, offline voice, vision, wake word
3. **Clear licensing** — Know exactly what's CC-BY-NC vs MIT
4. **Professional appearance** — Easy to understand for new contributors

---

## 📁 Directory Structure

```
tars-ai/
├── upstream/          # 🔒 LOCKED — Original TARS-AI code
│   ├── src/           #    Original Python modules
│   ├── Install.sh     #    Raspberry Pi installer
│   └── ...            #    All other upstream files
│
├── gptars/            # 🆕 NEW — v3.0 macOS implementation
│   ├── core/          #    Voice, vision, wake word engines
│   ├── macos/         #    macOS-specific installer
│   └── ...            #    All v3.0 code
│
├── shared/            # 🔗 SHARED — Hardware files
│   ├── 3d Printer Files/
│   └── CAD/
│
└── [root files]       # 🆕 NEW — Fork-specific docs
```

---

## 🔒 The Golden Rule

> **Never modify files in `upstream/`**

This folder is a **read-only mirror** of the upstream TARS-AI-Community repository. By keeping it untouched:

1. `git pull upstream V2` will **never** have merge conflicts
2. We can **cherry-pick** upstream improvements easily
3. License compliance is **automatic** — upstream files keep their original license
4. Contributors **know immediately** what came from upstream

---

## 🔄 Syncing with Upstream

### One-time setup (already done)
```bash
git remote add upstream https://github.com/TARS-AI-Community/TARS-AI.git
```

### Regular sync process
```bash
# Fetch upstream changes
git fetch upstream

# See what's new
git log upstream/V2 --oneline -10

# Merge upstream into your branch
git checkout V2
git merge upstream/V2

# This will ONLY affect upstream/ folder — no conflicts with gptars/
```

### If upstream adds new root files
If TARS-AI-Community adds new files at their root level:
```bash
# Move them to upstream/ to maintain our structure
git mv new-upstream-file.py upstream/
git commit -m "chore: relocate upstream file to upstream/"
```

---

## 🏷️ Licensing Strategy

### Why dual licensing?

The upstream TARS-AI project uses **CC-BY-NC 4.0**, which:
- ✅ Allows sharing and adaptation
- ❌ Prohibits commercial use
- Requires attribution

For the **new v3.0 code**, we use **MIT**, which:
- ✅ Allows commercial use
- ✅ Is maximally permissive
- Only requires license inclusion

### How it's organized

| Location | License | Why |
|----------|---------|-----|
| `upstream/` | CC-BY-NC 4.0 | Original upstream code, untouched |
| `shared/` | CC-BY-NC 4.0 | Hardware files from upstream |
| `gptars/` | MIT | New code, written from scratch |
| Root files | MIT | Fork-specific documentation |

### File headers

All files in `gptars/` should include this header:
```python
# MIT License — Copyright (c) 2024-2025 James-von-Detroit
# Part of gptars v3.0: https://github.com/James-von-Detroit/tars-ai
```

Files in `upstream/` retain their original headers (CC-BY-NC).

---

## 🛠️ Development Workflow

### Adding new v3.0 features
1. Create files in `gptars/`
2. Add MIT license header
3. Update `gptars/docs/` if needed
4. Submit PR

### Porting upstream features to v3.0
1. Check the upstream code for the feature
2. **Rewrite** it for macOS in `gptars/` (don't copy-paste)
3. Credit the original in comments if substantially derived
4. Note: If heavily derived, it inherits CC-BY-NC

### Fixing bugs in upstream code
1. **Don't fix it here** — contribute to upstream directly
2. Link: [TARS-AI-Community/TARS-AI](https://github.com/TARS-AI-Community/TARS-AI)
3. Once merged upstream, sync here with `git pull upstream V2`

---

## 📋 Checklist for Contributors

Before submitting a PR, verify:

- [ ] New code is in `gptars/`, not `upstream/`
- [ ] Files in `gptars/` have MIT license headers
- [ ] No modifications to `upstream/` files
- [ ] Documentation updated in `gptars/docs/`
- [ ] REVISION.md updated if significant change

---

## 🤔 FAQ

### Q: Why not just fork and modify upstream files directly?
**A:** This creates merge conflicts forever. Every upstream update would require manual conflict resolution. Our structure means zero conflicts.

### Q: Can I copy code from `upstream/` to `gptars/`?
**A:** You can be *inspired* by it, but if you substantially copy it, the copy inherits CC-BY-NC licensing. Better to rewrite for MIT.

### Q: What if upstream restructures their repo?
**A:** We handle it during sync. Move their new structure into `upstream/` and document in REVISION.md.

### Q: Can I use `gptars/` commercially?
**A:** Yes! The MIT-licensed code in `gptars/` can be used commercially. But don't include the TARS character personality (that's CC-BY-NC derived).

---

## 📚 References

- [Upstream Repository](https://github.com/TARS-AI-Community/TARS-AI)
- [CC-BY-NC 4.0 License](https://creativecommons.org/licenses/by-nc/4.0/)
- [MIT License](https://opensource.org/licenses/MIT)
- [Git subtree vs subdirectory strategies](https://www.atlassian.com/git/tutorials/git-subtree)
