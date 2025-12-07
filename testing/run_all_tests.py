#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024–2025 James-von-Detroit

"""
Voice Test Runner

Simple script to run all voice adjustment tests in sequence.

Usage:
    cd /home/runner/work/tars-ai/tars-ai
    python3 testing/run_all_tests.py
    
    # Or run specific tests:
    python3 testing/run_all_tests.py --tests 1,3,4
"""

import sys
import argparse
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


def run_test(test_number):
    """Run a specific test."""
    test_file = REPO_ROOT / "testing" / f"test_{test_number:02d}_voice_adjustment.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print("\n" + "=" * 70)
    print(f"RUNNING TEST {test_number:02d}")
    print("=" * 70)
    print()
    
    try:
        # Import and run the test module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            f"test_{test_number:02d}",
            test_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Run the main function
        if hasattr(module, 'main'):
            module.main()
            return True
        else:
            print(f"⚠️  Test module has no main() function")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run voice adjustment tests."""
    parser = argparse.ArgumentParser(
        description="Run TARS-AI voice adjustment tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python3 testing/run_all_tests.py
  
  # Run specific tests
  python3 testing/run_all_tests.py --tests 1,3
  
  # Run with more details
  python3 testing/run_all_tests.py --verbose

Tests:
  01 - Latency Reduction (chunked TTS)
  02 - Prosody Correction (naturalness)
  03 - VAD/Interruption Handling
  04 - Distortion/Noise Reduction
        """
    )
    
    parser.add_argument(
        '--tests',
        type=str,
        help='Comma-separated test numbers to run (e.g., 1,3,4). Default: all tests'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show verbose output'
    )
    
    args = parser.parse_args()
    
    # Determine which tests to run
    if args.tests:
        test_numbers = [int(n.strip()) for n in args.tests.split(',')]
    else:
        test_numbers = [1, 2, 3, 4]
    
    print("\n" + "=" * 70)
    print("TARS-AI VOICE ADJUSTMENT TEST SUITE")
    print("=" * 70)
    print()
    print("This suite contains four tests to diagnose and improve voice quality:")
    print("  01 - Latency Reduction via Chunked TTS Synthesis")
    print("  02 - Prosody Correction for Natural Intonation")
    print("  03 - VAD/Interruption Handling for Responsive Dialogue")
    print("  04 - Distortion/Noise Reduction in Output")
    print()
    print(f"Running tests: {', '.join([f'{n:02d}' for n in test_numbers])}")
    print()
    print("Note: Some tests require optional dependencies (elevenlabs, webrtcvad).")
    print("      Tests will skip features that require missing dependencies.")
    print()
    
    try:
        input("Press ENTER to start, or Ctrl+C to cancel... ")
    except (EOFError, KeyboardInterrupt):
        print("\n\n👋 Cancelled.")
        sys.exit(0)
    
    # Run tests
    results = {}
    for test_num in test_numbers:
        success = run_test(test_num)
        results[test_num] = success
        
        if test_num < max(test_numbers):
            print("\n")
            try:
                input("Press ENTER to continue to next test, or Ctrl+C to stop... ")
            except (EOFError, KeyboardInterrupt):
                print("\n\n⚠️  Test suite interrupted by user")
                break
    
    # Summary
    print("\n\n")
    print("=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)
    print()
    
    for test_num in test_numbers:
        status = "✓ COMPLETED" if results.get(test_num, False) else "✗ FAILED/SKIPPED"
        print(f"  Test {test_num:02d}: {status}")
    
    print()
    print("Output files saved in: testing/output/")
    print()
    print("For detailed documentation, see: testing/README.md")
    print()


if __name__ == "__main__":
    main()
