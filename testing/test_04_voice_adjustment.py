#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit

"""
Test 04: Distortion/Noise Reduction in Output

Rationale: Background noise or synthesis glitches cause "choppy" audio, fixed 
in voice agent troubleshooting by input leveling and noise gates—relevant for 
TARS' hardware integration.

This test demonstrates audio post-processing techniques using pydub.

Usage:
    cd /home/runner/work/tars-ai/tars-ai
    python3 testing/test_04_voice_adjustment.py

Requirements:
    - gptars package installed
    - pydub
    - ffmpeg (for pydub audio processing)
"""

import os
import sys
import time
import wave
from io import BytesIO
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Test configuration
TEST_TEXT = "All systems green. Ready for deployment."
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_raw_tts(text, voice_model_path):
    """
    Generate raw TTS audio without post-processing.
    
    Args:
        text: Text to synthesize
        voice_model_path: Path to Piper .onnx model
        
    Returns:
        tuple: (audio_data, sample_rate)
    """
    try:
        from piper.voice import PiperVoice
    except ImportError:
        print("❌ piper-tts not installed. Run: pip install piper-tts")
        return None, None
    
    if not voice_model_path.exists():
        print(f"❌ Voice model not found at {voice_model_path}")
        return None, None
    
    voice = PiperVoice.load(str(voice_model_path))
    sample_rate = voice.config.sample_rate
    
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        voice.synthesize_wav(text, wav_file)
    
    wav_buffer.seek(0)
    audio_data, _ = sf.read(wav_buffer)
    
    return audio_data, sample_rate


def noise_reduced_tts_elevenlabs(text, api_key=None):
    """
    Generate TTS with ElevenLabs and apply post-processing.
    
    Args:
        text: Text to synthesize
        api_key: ElevenLabs API key
        
    Returns:
        tuple: (audio_bytes, sample_rate)
    """
    try:
        from elevenlabs import generate
    except ImportError:
        print("⚠️  elevenlabs not installed. Skipping ElevenLabs test.")
        return None, None
    
    api_key = api_key or os.getenv("ELEVEN_API_KEY")
    if not api_key:
        print("⚠️  No ElevenLabs API key found. Skipping ElevenLabs test.")
        return None, None
    
    try:
        audio_bytes = generate(
            text=text,
            voice="Adam",
            model="eleven_turbo_v2",
            api_key=api_key
        )
        return audio_bytes, 22050
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None


def apply_noise_reduction(audio_data, sample_rate):
    """
    Apply noise reduction and audio enhancement.
    
    Args:
        audio_data: Audio as numpy array
        sample_rate: Sample rate in Hz
        
    Returns:
        Enhanced audio as numpy array
    """
    try:
        from pydub import AudioSegment
        from pydub.effects import normalize, compress_dynamic_range
    except ImportError:
        print("❌ pydub not installed. Run: pip install pydub")
        print("   Also requires: brew install ffmpeg")
        return None
    
    # Convert numpy array to AudioSegment
    # First, convert float32 to int16
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    # Create AudioSegment from raw data
    audio = AudioSegment(
        audio_int16.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,  # 16-bit
        channels=1
    )
    
    # Apply filters
    print("  Applying filters:")
    print("    - High-pass filter (300 Hz) to remove low-frequency noise")
    print("    - Low-pass filter (3000 Hz) to remove high-frequency artifacts")
    print("    - Normalization to level volume")
    print("    - Dynamic range compression to smooth peaks")
    
    # 1. Remove extreme frequencies
    audio = audio.high_pass_filter(300)  # Remove low rumble
    audio = audio.low_pass_filter(3000)  # Remove high-frequency artifacts
    
    # 2. Normalize volume
    audio = normalize(audio)
    
    # 3. Compress dynamic range to smooth peaks/valleys
    audio = compress_dynamic_range(
        audio,
        threshold=-20.0,  # dB threshold
        ratio=4.0,        # Compression ratio
        attack=5.0,       # Attack time (ms)
        release=50.0      # Release time (ms)
    )
    
    # Convert back to numpy array
    samples = np.array(audio.get_array_of_samples())
    audio_float = samples.astype(np.float32) / 32767.0
    
    return audio_float


def calculate_snr(signal):
    """
    Calculate simple Signal-to-Noise Ratio estimate.
    
    Args:
        signal: Audio signal as numpy array
        
    Returns:
        Estimated SNR in dB
    """
    # Split signal into speech and silence regions (simple threshold)
    threshold = 0.01
    speech_samples = signal[np.abs(signal) > threshold]
    noise_samples = signal[np.abs(signal) <= threshold]
    
    if len(speech_samples) == 0 or len(noise_samples) == 0:
        return 0.0
    
    signal_power = np.mean(speech_samples ** 2)
    noise_power = np.mean(noise_samples ** 2)
    
    if noise_power == 0:
        return 100.0  # No noise detected
    
    snr = 10 * np.log10(signal_power / noise_power)
    return snr


def measure_distortion(audio, sample_rate):
    """
    Measure audio distortion using simple metrics.
    
    Args:
        audio: Audio as numpy array
        sample_rate: Sample rate in Hz
        
    Returns:
        dict: Distortion metrics
    """
    # Calculate peak level
    peak_level = np.max(np.abs(audio))
    
    # Calculate RMS level
    rms_level = np.sqrt(np.mean(audio ** 2))
    
    # Calculate crest factor (peak-to-RMS ratio)
    crest_factor = peak_level / rms_level if rms_level > 0 else 0
    
    # Estimate SNR
    snr = calculate_snr(audio)
    
    # Check for clipping (values at or near ±1.0)
    clipping_count = np.sum(np.abs(audio) >= 0.99)
    clipping_percent = (clipping_count / len(audio)) * 100
    
    return {
        'peak_level': peak_level,
        'rms_level': rms_level,
        'crest_factor': crest_factor,
        'snr_db': snr,
        'clipping_percent': clipping_percent
    }


def play_audio(audio, sample_rate, label=""):
    """Play audio through speakers."""
    if label:
        print(f"🔊 Playing: {label}")
    sd.play(audio, sample_rate)
    sd.wait()


def save_audio(audio, sample_rate, filename):
    """Save audio to WAV file."""
    output_path = OUTPUT_DIR / filename
    sf.write(output_path, audio, sample_rate)
    print(f"💾 Saved to: {output_path}")
    return output_path


def compare_spectrograms(raw_audio, processed_audio, sample_rate):
    """
    Generate spectrograms for comparison (requires matplotlib).
    
    Args:
        raw_audio: Original audio
        processed_audio: Processed audio
        sample_rate: Sample rate
    """
    try:
        import matplotlib.pyplot as plt
        from scipy import signal
    except ImportError:
        print("⚠️  matplotlib/scipy not installed. Skipping spectrogram.")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Raw audio spectrogram
    f, t, Sxx = signal.spectrogram(raw_audio, sample_rate)
    ax1.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud')
    ax1.set_ylabel('Frequency [Hz]')
    ax1.set_xlabel('Time [sec]')
    ax1.set_title('Raw Audio Spectrogram')
    ax1.set_ylim([0, 4000])
    
    # Processed audio spectrogram
    f, t, Sxx = signal.spectrogram(processed_audio, sample_rate)
    ax2.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud')
    ax2.set_ylabel('Frequency [Hz]')
    ax2.set_xlabel('Time [sec]')
    ax2.set_title('Processed Audio Spectrogram')
    ax2.set_ylim([0, 4000])
    
    plt.tight_layout()
    
    output_path = OUTPUT_DIR / "test_04_spectrogram_comparison.png"
    plt.savefig(output_path)
    print(f"📊 Spectrogram saved to: {output_path}")
    plt.close()


def main():
    """Run distortion/noise reduction tests."""
    print("\n" + "=" * 70)
    print("TEST 04: DISTORTION/NOISE REDUCTION IN OUTPUT")
    print("=" * 70)
    print()
    print(f"Test text: \"{TEST_TEXT}\"")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Find Piper voice model
    voices_path = REPO_ROOT / "voices"
    tars_model = voices_path / "TARS.onnx"
    
    if not tars_model.exists():
        print(f"❌ TARS voice model not found at {tars_model}")
        print("   Please ensure the voices/ directory contains TARS.onnx")
        sys.exit(1)
    
    # Test 1: Raw TTS (no post-processing)
    print("-" * 70)
    print("TEST 1: RAW TTS (No Post-Processing)")
    print("-" * 70)
    print()
    
    raw_audio, sample_rate = generate_raw_tts(TEST_TEXT, tars_model)
    
    if raw_audio is None:
        print("❌ Failed to generate raw audio")
        sys.exit(1)
    
    raw_metrics = measure_distortion(raw_audio, sample_rate)
    
    print("Raw Audio Metrics:")
    print(f"  Peak level: {raw_metrics['peak_level']:.3f}")
    print(f"  RMS level: {raw_metrics['rms_level']:.3f}")
    print(f"  Crest factor: {raw_metrics['crest_factor']:.2f}")
    print(f"  SNR: {raw_metrics['snr_db']:.1f} dB")
    print(f"  Clipping: {raw_metrics['clipping_percent']:.2f}%")
    print()
    
    save_audio(raw_audio, sample_rate, "test_04_raw.wav")
    play_audio(raw_audio, sample_rate, "Raw Audio")
    
    print("\n")
    
    # Test 2: Post-processed TTS
    print("-" * 70)
    print("TEST 2: POST-PROCESSED TTS (Noise Reduction)")
    print("-" * 70)
    print()
    
    processed_audio = apply_noise_reduction(raw_audio, sample_rate)
    
    if processed_audio is None:
        print("❌ Failed to apply noise reduction")
        sys.exit(1)
    
    processed_metrics = measure_distortion(processed_audio, sample_rate)
    
    print()
    print("Processed Audio Metrics:")
    print(f"  Peak level: {processed_metrics['peak_level']:.3f}")
    print(f"  RMS level: {processed_metrics['rms_level']:.3f}")
    print(f"  Crest factor: {processed_metrics['crest_factor']:.2f}")
    print(f"  SNR: {processed_metrics['snr_db']:.1f} dB")
    print(f"  Clipping: {processed_metrics['clipping_percent']:.2f}%")
    print()
    
    save_audio(processed_audio, sample_rate, "test_04_processed.wav")
    play_audio(processed_audio, sample_rate, "Processed Audio")
    
    print("\n")
    
    # Test 3: ElevenLabs (optional)
    print("-" * 70)
    print("TEST 3: ELEVENLABS (Optional, with Post-Processing)")
    print("-" * 70)
    print()
    
    elevenlabs_bytes, elevenlabs_sr = noise_reduced_tts_elevenlabs(TEST_TEXT)
    
    if elevenlabs_bytes is not None:
        # Save raw ElevenLabs output
        output_path = OUTPUT_DIR / "test_04_elevenlabs_raw.mp3"
        with open(output_path, 'wb') as f:
            f.write(elevenlabs_bytes)
        print(f"💾 Saved raw to: {output_path}")
        
        # Convert to AudioSegment and apply processing
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_mp3(BytesIO(elevenlabs_bytes))
            
            # Apply same processing
            audio = audio.high_pass_filter(300)
            audio = audio.low_pass_filter(3000)
            audio = AudioSegment.normalize(audio)
            
            output_path = OUTPUT_DIR / "test_04_elevenlabs_processed.wav"
            audio.export(output_path, format="wav")
            print(f"💾 Saved processed to: {output_path}")
            
        except Exception as e:
            print(f"⚠️  Could not process ElevenLabs audio: {e}")
    
    print("\n")
    
    # Comparison
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    print("Metrics Comparison:")
    print(f"                     Raw        Processed    Improvement")
    print(f"  Peak Level:        {raw_metrics['peak_level']:.3f}      {processed_metrics['peak_level']:.3f}       {'✓' if abs(processed_metrics['peak_level'] - 0.7) < abs(raw_metrics['peak_level'] - 0.7) else '–'}")
    print(f"  SNR:               {raw_metrics['snr_db']:.1f} dB    {processed_metrics['snr_db']:.1f} dB     {'✓' if processed_metrics['snr_db'] > raw_metrics['snr_db'] else '–'}")
    print(f"  Clipping:          {raw_metrics['clipping_percent']:.2f}%     {processed_metrics['clipping_percent']:.2f}%      {'✓' if processed_metrics['clipping_percent'] < raw_metrics['clipping_percent'] else '–'}")
    print()
    
    print("Quality Threshold:")
    if processed_metrics['clipping_percent'] < 5.0:
        print("  ✓ Clipping < 5% (PASS)")
    else:
        print(f"  ✗ Clipping = {processed_metrics['clipping_percent']:.2f}% (FAIL - target <5%)")
    
    if processed_metrics['snr_db'] > 20:
        print("  ✓ SNR > 20 dB (PASS)")
    else:
        print(f"  ✗ SNR = {processed_metrics['snr_db']:.1f} dB (FAIL - target >20 dB)")
    
    print()
    
    # Generate spectrogram comparison
    print("Generating spectrogram comparison...")
    compare_spectrograms(raw_audio, processed_audio, sample_rate)
    
    print()
    print("Recommendations:")
    print("  - High-pass filter at 300 Hz removes low-frequency rumble")
    print("  - Low-pass filter at 3000 Hz removes TTS artifacts")
    print("  - Normalization ensures consistent volume")
    print("  - Dynamic range compression smooths audio peaks")
    print()
    print("Output files saved in:", OUTPUT_DIR)
    print()


if __name__ == "__main__":
    main()
