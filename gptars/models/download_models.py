#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit
#
# Part of GPTars v3.0 — 100% offline TARS voice assistant for macOS.
# https://github.com/James-von-Detroit/tars-ai

"""
models/download_models.py

Helper script to download all required models for gptars v3.0
Ensures all models are present before first run
"""

import os
import sys
import subprocess
from pathlib import Path


def print_status(message):
    print(f"\n{'='*70}")
    print(f"  {message}")
    print(f"{'='*70}\n")


def check_ollama():
    """Check if Ollama is running and accessible."""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def download_ollama_model(model_name):
    """Download a model via Ollama."""
    print(f"📥 Downloading {model_name}...")
    print("   (This may take several minutes)")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ {model_name} downloaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download {model_name}: {e}")
        return False


def download_whisper_model(model_name="distil-large-v3"):
    """Download Whisper model via faster-whisper."""
    print(f"📥 Downloading Whisper model: {model_name}...")
    
    # Create models directory
    models_dir = Path("models/whisper")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from faster_whisper import WhisperModel
        
        model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
            download_root=str(models_dir)
        )
        print(f"✓ Whisper model {model_name} ready")
        return True
    except Exception as e:
        print(f"❌ Failed to download Whisper model: {e}")
        return False


def download_wake_word_models():
    """Download wake word detection models."""
    print(f"📥 Downloading wake word models...")
    
    models_dir = Path("models/wakeword")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from openwakeword.model import Model
        
        # This will download default models including hey_jarvis
        model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        print("✓ Wake word models ready")
        return True
    except Exception as e:
        print(f"❌ Failed to download wake word models: {e}")
        return False


def download_piper_voice(voice_name="en_US-lessac-medium"):
    """Download Piper TTS voice model."""
    print(f"📥 Downloading Piper voice: {voice_name}...")
    
    voices_dir = Path("voices")
    voices_dir.mkdir(exist_ok=True)
    
    onnx_file = voices_dir / f"{voice_name}.onnx"
    json_file = voices_dir / f"{voice_name}.onnx.json"
    
    if onnx_file.exists() and json_file.exists():
        print(f"✓ Voice {voice_name} already downloaded")
        return True
    
    base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US"
    
    # Parse voice name to get path components
    parts = voice_name.split('-')
    if len(parts) >= 3:
        speaker = parts[1]  # e.g., "lessac"
        quality = parts[2]  # e.g., "medium"
        
        onnx_url = f"{base_url}/{speaker}/{quality}/{voice_name}.onnx"
        json_url = f"{base_url}/{speaker}/{quality}/{voice_name}.onnx.json"
        
        try:
            import requests
            
            # Download ONNX file
            print(f"   Downloading {voice_name}.onnx...")
            response = requests.get(onnx_url)
            response.raise_for_status()
            with open(onnx_file, 'wb') as f:
                f.write(response.content)
            
            # Download JSON file
            print(f"   Downloading {voice_name}.onnx.json...")
            response = requests.get(json_url)
            response.raise_for_status()
            with open(json_file, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Voice {voice_name} downloaded")
            return True
        except Exception as e:
            print(f"❌ Failed to download voice: {e}")
            return False
    else:
        print(f"❌ Invalid voice name format: {voice_name}")
        return False


def main():
    print_status("gptars v3.0 - Model Download Helper")
    
    print("This script will download all required models:")
    print("  - Llama-3-8B-Instruct (Q4) via Ollama (~4.7 GB)")
    print("  - Faster-Whisper distil-large-v3 (~1.5 GB)")
    print("  - Piper TTS voice model (~50 MB)")
    print("  - Wake word detection models (~20 MB)")
    print("\nTotal download: ~6-7 GB")
    print("Estimated time: 10-20 minutes (depends on internet speed)")
    
    response = input("\nContinue? [y/N]: ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    success_count = 0
    total_count = 4
    
    # 1. Check Ollama
    print_status("Step 1/4: Checking Ollama")
    if not check_ollama():
        print("❌ Ollama is not running!")
        print("\nPlease start Ollama:")
        print("  brew services start ollama")
        print("or")
        print("  ollama serve")
        sys.exit(1)
    print("✓ Ollama is running")
    
    # 2. Download LLM
    print_status("Step 2/4: Downloading Llama-3-8B-Instruct")
    if download_ollama_model("llama3:8b-instruct-q4_0"):
        success_count += 1
    
    # 3. Download Whisper
    print_status("Step 3/4: Downloading Whisper Model")
    if download_whisper_model():
        success_count += 1
    
    # 4. Download Wake Word
    print_status("Step 4/4: Downloading Wake Word Models")
    if download_wake_word_models():
        success_count += 1
    
    # 5. Download TTS Voice
    print_status("Bonus: Downloading Piper TTS Voice")
    if download_piper_voice():
        success_count += 1
        total_count += 1
    
    # Summary
    print_status("Download Summary")
    print(f"Successfully downloaded: {success_count}/{total_count} components")
    
    if success_count == total_count:
        print("\n✅ All models downloaded successfully!")
        print("\nYou can now run gptars:")
        print("  ./run_tars.sh")
    else:
        print("\n⚠️  Some downloads failed. Check errors above.")
        print("You may need to manually download missing components.")
    
    # Optional: Download vision model
    print("\n" + "="*70)
    print("Optional: Download vision model for camera support?")
    print("  - LLaVA-7B (~4 GB)")
    response = input("Download vision model? [y/N]: ")
    
    if response.lower() == 'y':
        print_status("Downloading LLaVA Vision Model")
        if download_ollama_model("llava:7b"):
            print("✓ Vision model ready!")
        else:
            print("❌ Vision model download failed")


if __name__ == "__main__":
    main()
