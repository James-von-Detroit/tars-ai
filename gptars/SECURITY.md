# Security Advisory - gptars v3.0 Alpha

## Update: December 2024

### Security Vulnerabilities Fixed

Three critical security vulnerabilities have been identified and patched in the gptars v3.0 dependencies.

---

## Vulnerabilities Addressed

### 1. ONNX Path Traversal Vulnerability

**Package:** `onnx`  
**Affected Version:** < 1.17.0  
**Patched Version:** 1.17.0  
**Severity:** Medium to High  

**Description:**
Open Neural Network Exchange (ONNX) had a path traversal vulnerability that could allow an attacker to access files outside the intended directory structure.

**Impact on gptars:**
- Used for wake word detection models
- Could potentially affect model loading security

**Fix:**
Updated `onnx` from 1.16.2 to 1.17.0

---

### 2. PyTorch Remote Code Execution (RCE)

**Package:** `torch`  
**Affected Version:** < 2.6.0  
**Patched Version:** 2.6.0  
**Severity:** Critical  

**Description:**
PyTorch's `torch.load` function with `weights_only=True` could still lead to remote code execution through maliciously crafted model files.

**Impact on gptars:**
- Used for vision model support (LLaVA)
- Could allow RCE if malicious models are loaded
- Affects any code using torch.load

**Fix:**
Updated `torch` from 2.4.1 to 2.6.0

---

### 3. Hugging Face Transformers Deserialization Vulnerability

**Package:** `transformers`  
**Affected Version:** >= 0, < 4.48.0  
**Patched Version:** 4.48.0  
**Severity:** High  

**Description:**
Deserialization of untrusted data in Hugging Face Transformers could lead to arbitrary code execution when loading models from untrusted sources.

**Impact on gptars:**
- Used for vision models and potentially text generation
- Multiple deserialization vulnerabilities present
- Could execute arbitrary code during model loading

**Fix:**
Updated `transformers` from 4.45.0 to 4.48.0

---

## What Users Should Do

### If You've Already Installed gptars v3.0

**Option 1: Update Dependencies (Recommended)**

```bash
cd gptars
source venv/bin/activate
pip install --upgrade onnx==1.17.0 torch==2.6.0 transformers==4.48.0
```

**Option 2: Reinstall from Updated Requirements**

```bash
cd gptars
source venv/bin/activate
pip install -r macos/requirements-macos.txt --upgrade
```

**Option 3: Full Reinstall**

```bash
cd gptars
rm -rf venv
./macos/install_macos.sh
```

### For New Installations

The updated requirements are now in the repository. Simply run:

```bash
./macos/install_macos.sh
```

All new installations will use the patched versions.

---

## Security Best Practices

### For gptars Users

1. **Only Use Trusted Models**
   - Download models only from official sources (Ollama, HuggingFace verified)
   - Never load models from untrusted third parties
   - Verify model checksums when possible

2. **Keep Dependencies Updated**
   - Regularly update Python packages: `pip list --outdated`
   - Check for security advisories
   - Run `pip install --upgrade` periodically

3. **Isolated Environment**
   - Always use the virtual environment (venv)
   - Don't run gptars with elevated privileges
   - Consider sandboxing if processing untrusted data

4. **Network Isolation**
   - gptars is designed for offline use
   - Consider network isolation for sensitive deployments
   - Monitor network activity if concerned

### For Developers

1. **Code Security**
   - Never use `torch.load()` on untrusted files
   - Always validate model sources
   - Use `weights_only=True` with updated torch
   - Implement input validation

2. **Model Loading**
   ```python
   # Safe model loading (with updated torch 2.6.0)
   import torch
   
   # For PyTorch models
   model = torch.load("model.pt", weights_only=True)
   
   # For transformers
   from transformers import AutoModel
   model = AutoModel.from_pretrained("model", trust_remote_code=False)
   ```

3. **Regular Audits**
   - Run `pip-audit` to check for vulnerabilities
   - Monitor CVE databases
   - Subscribe to security mailing lists

---

## Verification

### Check Your Installed Versions

```bash
source venv/bin/activate
pip list | grep -E "onnx|torch|transformers"
```

**Should show:**
```
onnx                     1.17.0
torch                    2.6.0
transformers             4.48.0
```

### Run Security Audit

```bash
pip install pip-audit
pip-audit
```

Should show no critical vulnerabilities.

---

## Impact Assessment

### Risk Level: Medium

**Why Medium and Not Critical?**

1. **Limited Attack Surface**
   - gptars primarily uses pre-downloaded, verified models
   - Users typically use models from Ollama (trusted source)
   - Vision features are optional

2. **Mitigation Factors**
   - Runs in isolated virtual environment
   - No elevated privileges required
   - Designed for offline use (limited network exposure)
   - Users control model sources

3. **Exploitation Requirements**
   - Attacker needs to provide malicious model file
   - User must actively load that file
   - Requires user error or social engineering

**However:**
- If you load models from untrusted sources, risk is HIGH
- If you modified code to accept external input, risk is HIGH
- Always better to patch immediately

---

## Timeline

- **December 7, 2024:** Vulnerabilities reported via dependency scan
- **December 7, 2024:** Dependencies updated to patched versions
- **December 7, 2024:** Security advisory published

---

## Additional Resources

### CVE References

- **ONNX Path Traversal:** Search CVE database for ONNX vulnerabilities
- **PyTorch RCE:** PyTorch security advisories
- **Transformers Deserialization:** Hugging Face security bulletins

### Security Tools

```bash
# Install security audit tools
pip install pip-audit safety

# Run audit
pip-audit

# Check with safety
safety check
```

### Reporting Security Issues

If you discover a security vulnerability in gptars:

1. **Do NOT** open a public GitHub issue
2. Email: [security contact - to be added]
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

## Questions?

- Check `TROUBLESHOOTING.md` for update issues
- Open a GitHub issue for non-security questions
- Join Discord for community support

---

**Remember:** Security is a shared responsibility. Keep your dependencies updated and only use models from trusted sources.

**Status:** All known vulnerabilities patched as of December 7, 2024.
