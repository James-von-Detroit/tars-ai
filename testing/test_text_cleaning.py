#!/usr/bin/env python3
"""Test the TTS text cleaning function."""

import sys
sys.path.insert(0, 'gptars')
import re

def clean_text_for_tts(text):
    """Clean text for TTS - removes markdown, asterisks, etc."""
    # First: Handle markdown bold/strong BEFORE anything else
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** → bold
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__ → bold
    
    # Second: Remove stage directions/actions in asterisks
    text = re.sub(r'\*[^*]+\*', '', text)
    
    # Third: Handle any remaining single asterisk italic
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* → italic
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_ → italic
    
    # Clean up multiple exclamation/question marks
    text = re.sub(r'!+', '!', text)
    text = re.sub(r'\?+', '?', text)
    
    # Remove orphaned asterisks
    text = re.sub(r'(?<!\w)[*_]+(?!\w)', '', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# Test cases based on actual TARS output
# Note: For TARS, *text* is always a stage direction, so it gets removed
test_cases = [
    ('*adjusting humor to 100%* Hello Cooper!', 'Hello Cooper!'),
    ('**Bold text** and *italic* here', 'Bold text and here'),  # *italic* removed as stage direction
    ('Multiple!!! exclamation??? marks', 'Multiple! exclamation? marks'),
    ('Normal text should pass through fine.', 'Normal text should pass through fine.'),
    ('*cue light: humor 50%* Roger that!', 'Roger that!'),
    ('*processing* Ah, yes! I see what you did there.', 'Ah, yes! I see what you did there.'),
    ('Keep em coming, Cooper!', 'Keep em coming, Cooper!'),
    ('Roger that, Cooper! *adjusting humor to 60%*', 'Roger that, Cooper!'),
    ('Test with **bold** text only', 'Test with bold text only'),
]

print('Testing text cleaning for TTS:')
print('=' * 70)

all_passed = True
for input_text, expected in test_cases:
    result = clean_text_for_tts(input_text)
    passed = result == expected
    status = '✓' if passed else '✗'
    
    print(f'{status} IN:  "{input_text}"')
    print(f'  OUT: "{result}"')
    if not passed:
        print(f'  EXP: "{expected}"')
        all_passed = False
    print()

print('=' * 70)
if all_passed:
    print('All tests passed! ✓')
else:
    print('Some tests failed! ✗')
