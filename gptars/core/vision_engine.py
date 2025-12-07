"""
core/vision_engine.py

Vision System for gptars v3.0 Alpha

Enables TARS to "see" through MacBook webcam using vision models.
Supports LLaVA-1.6 and Moondream2 for image understanding.

Commands:
- "TARS, analyze" - Analyze current camera view
- "TARS, look at this" - Describe what's in frame
- "TARS, what do you see?" - Get vision description

Author: gptars v3.0
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple
import base64
from io import BytesIO

import cv2
import numpy as np
from PIL import Image
import requests


class VisionEngine:
    """
    Vision processing for TARS using webcam and vision models.
    
    Supports:
    - Live camera feed from MacBook webcam
    - Image capture and analysis
    - Integration with LLaVA or Moondream2 via Ollama
    """
    
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        vision_model: str = "llava:7b",  # or "moondream" when available
        camera_index: int = 0,
        verbose: bool = True
    ):
        """
        Initialize vision engine.
        
        Args:
            ollama_url: Ollama server URL
            vision_model: Vision model name (llava, moondream, bakllava)
            camera_index: Camera device index (0 for default webcam)
            verbose: Print status messages
        """
        self.ollama_url = ollama_url
        self.vision_model = vision_model
        self.camera_index = camera_index
        self.verbose = verbose
        
        self.camera = None
        self.last_frame = None
        
        if self.verbose:
            print(f"✓ Vision Engine initialized")
            print(f"  Model: {vision_model}")
            print(f"  Camera: Index {camera_index}")
    
    def start_camera(self) -> bool:
        """
        Start the camera feed.
        
        Returns:
            True if camera started successfully
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                if self.verbose:
                    print(f"❌ Failed to open camera {self.camera_index}")
                return False
            
            # Set camera properties for better quality
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            if self.verbose:
                print("✓ Camera started")
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop the camera feed."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            if self.verbose:
                print("✓ Camera stopped")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera.
        
        Returns:
            Frame as numpy array (BGR format) or None if failed
        """
        if self.camera is None or not self.camera.isOpened():
            if not self.start_camera():
                return None
        
        ret, frame = self.camera.read()
        
        if not ret:
            if self.verbose:
                print("❌ Failed to capture frame")
            return None
        
        self.last_frame = frame
        return frame
    
    def frame_to_base64(self, frame: np.ndarray) -> str:
        """
        Convert frame to base64 string for API transmission.
        
        Args:
            frame: Frame as numpy array (BGR)
            
        Returns:
            Base64 encoded JPEG string
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Resize if too large (to reduce API payload)
        max_size = 1024
        if max(pil_image.size) > max_size:
            pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to JPEG bytes
        buffer = BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)
        img_bytes = buffer.getvalue()
        
        # Encode to base64
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def analyze_image(
        self,
        frame: np.ndarray,
        prompt: str = "Describe what you see in this image in detail."
    ) -> str:
        """
        Analyze an image using vision model.
        
        Args:
            frame: Image frame as numpy array
            prompt: Question or instruction for the vision model
            
        Returns:
            Model's description/analysis
        """
        start_time = time.time()
        
        if self.verbose:
            print(f"🔍 Analyzing image with prompt: '{prompt}'")
        
        # Convert frame to base64
        image_b64 = self.frame_to_base64(frame)
        
        try:
            # Call Ollama vision API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.vision_model,
                    "prompt": prompt,
                    "images": [image_b64],
                    "stream": False
                },
                timeout=60  # Vision models can be slow
            )
            response.raise_for_status()
            
            result = response.json()
            description = result.get('response', '').strip()
            
            elapsed = time.time() - start_time
            
            if self.verbose:
                print(f"✓ Analysis completed in {elapsed:.2f}s")
                print(f"📸 Vision: {description}")
            
            return description
            
        except Exception as e:
            error_msg = f"Error analyzing image: {e}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return "Visual sensors experiencing difficulties."
    
    def tars_see(self, prompt: Optional[str] = None) -> str:
        """
        TARS looks through camera and describes what he sees.
        
        Args:
            prompt: Optional custom prompt for analysis
            
        Returns:
            TARS's vision-based response
        """
        # Capture frame
        frame = self.capture_frame()
        
        if frame is None:
            return "Camera systems offline. Cannot acquire visual data."
        
        # Default TARS-style prompt
        if prompt is None:
            prompt = (
                "You are TARS from Interstellar. Analyze this image and describe "
                "what you see in a concise, direct manner with your characteristic "
                "dry wit if appropriate. Keep it brief like a status report."
            )
        
        # Analyze
        description = self.analyze_image(frame, prompt)
        
        return description
    
    def show_preview(self, frame: np.ndarray, window_name: str = "TARS Vision"):
        """
        Display frame in a window (useful for debugging).
        
        Args:
            frame: Frame to display
            window_name: Window title
        """
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)
    
    def capture_and_save(self, filepath: str = "/tmp/tars_capture.jpg") -> bool:
        """
        Capture and save current frame to file.
        
        Args:
            filepath: Where to save the image
            
        Returns:
            True if successful
        """
        frame = self.capture_frame()
        
        if frame is None:
            return False
        
        try:
            cv2.imwrite(filepath, frame)
            if self.verbose:
                print(f"✓ Image saved to {filepath}")
            return True
        except Exception as e:
            if self.verbose:
                print(f"❌ Error saving image: {e}")
            return False
    
    def interactive_mode(self):
        """
        Run interactive vision mode.
        Press 's' to capture and analyze, 'q' to quit.
        """
        print("\n" + "=" * 70)
        print("TARS VISION SYSTEM - Interactive Mode")
        print("=" * 70)
        print("\nControls:")
        print("  's' - Capture and analyze current view")
        print("  'p' - Show preview window")
        print("  'q' - Quit")
        print("=" * 70 + "\n")
        
        if not self.start_camera():
            print("❌ Cannot start camera. Exiting.")
            return
        
        show_preview = False
        
        try:
            while True:
                # Capture frame
                frame = self.capture_frame()
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Show preview if enabled
                if show_preview:
                    self.show_preview(frame)
                
                # Check for key press
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('s'):
                    print("\n📸 Capturing and analyzing...")
                    description = self.tars_see()
                    print(f"\n🤖 TARS: {description}\n")
                
                elif key == ord('p'):
                    show_preview = not show_preview
                    if show_preview:
                        print("✓ Preview enabled")
                    else:
                        print("✓ Preview disabled")
                        cv2.destroyAllWindows()
                
                elif key == ord('q'):
                    break
                
                # Small delay to prevent high CPU usage
                time.sleep(0.03)
        
        except KeyboardInterrupt:
            print("\n\n👋 Vision system shutting down.")
        
        finally:
            self.stop_camera()
            cv2.destroyAllWindows()


def main():
    """Main entry point for vision engine."""
    print("\n" + "=" * 70)
    print("gptars v3.0 Alpha - Vision Engine")
    print("=" * 70)
    print()
    
    # Check if Ollama is running
    print("Checking Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        print("✓ Ollama is running")
        
        # Check if vision model is available
        models = response.json().get('models', [])
        vision_models = [m for m in models if 'llava' in m.get('name', '').lower()]
        
        if not vision_models:
            print("\n⚠️  Warning: No LLaVA model detected in Ollama")
            print("To install: ollama pull llava:7b")
            print()
            
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("\nPlease start Ollama:")
        print("  brew services start ollama")
        print("or")
        print("  ollama serve")
        sys.exit(1)
    
    print()
    
    # Initialize vision engine
    engine = VisionEngine(verbose=True)
    
    # Run interactive mode
    engine.interactive_mode()


if __name__ == "__main__":
    main()
