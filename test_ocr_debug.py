#!/usr/bin/env python3
"""
Debug OCR functionality for Dark War Survival Bot
"""

import os
import sys
import pyautogui
import pygetwindow as gw
import cv2
import numpy as np
from PIL import Image
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import pytesseract
    print("✅ pytesseract imported successfully")

    # Check if Tesseract path is set correctly
    print(f"🔍 Tesseract command: {pytesseract.pytesseract.tesseract_cmd}")

    # Test Tesseract version
    version = pytesseract.get_tesseract_version()
    print(f"📋 Tesseract version: {version}")

except Exception as e:
    print(f"❌ Error with pytesseract: {e}")
    sys.exit(1)

def test_ocr_on_screenshot():
    """Test OCR on current screenshot"""
    print("\n🔍 Testing OCR on current screen...")

    try:
        # Get all windows
        windows = gw.getAllWindows()
        dark_war_windows = [w for w in windows if "dark war" in w.title.lower()]

        print(f"📱 Found {len(dark_war_windows)} Dark War windows:")
        for i, window in enumerate(dark_war_windows):
            print(f"  {i+1}. {window.title} - {window.width}x{window.height}")

        if not dark_war_windows:
            print("⚠️  No Dark War windows found. Taking full screen screenshot...")
            screenshot = pyautogui.screenshot()
        else:
            # Use first Dark War window
            window = dark_war_windows[0]
            print(f"📸 Using window: {window.title}")

            # Focus window
            window.activate()
            time.sleep(0.5)

            # Take screenshot of window
            left, top, width, height = window.left, window.top, window.width, window.height
            screenshot = pyautogui.screenshot(region=(left, top, width, height))

        # Save screenshot for debugging
        screenshot_path = "debug_screenshot.png"
        screenshot.save(screenshot_path)
        print(f"💾 Screenshot saved to: {screenshot_path}")

        # Convert to OpenCV format
        screenshot_array = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)

        # Test OCR with different configurations
        configs = [
            '--psm 6',
            '--psm 8',
            '--psm 7',
            '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.:/%()- '
        ]

        print("\n🔤 Testing OCR with different configurations:")

        for i, config in enumerate(configs):
            try:
                print(f"\n--- Config {i+1}: {config} ---")
                text = pytesseract.image_to_string(screenshot, config=config)
                lines = text.strip().split('\n')
                print(f"📝 Extracted {len(lines)} lines:")

                # Show first 10 lines
                for j, line in enumerate(lines[:10]):
                    if line.strip():
                        print(f"  {j+1}: '{line.strip()}'")

                if len(lines) > 10:
                    print(f"  ... and {len(lines) - 10} more lines")

            except Exception as e:
                print(f"❌ Config {i+1} failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_building_detection():
    """Test building detection patterns"""
    print("\n🏗️ Testing building detection patterns...")

    # Sample text that should be found in Dark War
    test_texts = [
        "Kitchen Lv.12",
        "Tower 10/25",
        "Farm Level 15/25",
        "Watchtower Lvl 8",
        "Gathering Ground 20/20",
        "Dorm MAX",
        "Hero Hall maxed"
    ]

    import re

    # Test patterns from building_manager.py
    max_patterns = [
        r'level\s*(\d+)\s*/\s*(\d+)',
        r'lv\.?\s*(\d+)\s*/\s*(\d+)',
        r'lv\.?\s*(\d+)',
        r'(\d+)\s*/\s*(\d+)',
        r'(\d+)\/(\d+)',
        r'max',
        r'maxed',
        r'(\d+)\s*%',
        r'lvl\.?\s*(\d+)\s*/\s*(\d+)',
        r'level:\s*(\d+)\s*/\s*(\d+)',
    ]

    building_registry = {
        "kitchen": {"max_level": 25},
        "tower": {"max_level": 25},
        "farm": {"max_level": 25},
        "watchtower": {"max_level": 25},
        "gathering_ground": {"max_level": 20},
        "dorm": {"max_level": 10},
        "hero_hall": {"max_level": 25}
    }

    for text in test_texts:
        print(f"\n🔍 Testing: '{text}'")
        text_lower = text.lower()

        # Check for building names
        for building_name in building_registry.keys():
            if building_name.replace('_', ' ') in text_lower or building_name in text_lower:
                print(f"  ✅ Found building: {building_name}")

                # Check for level patterns
                for pattern in max_patterns:
                    matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                    for match in matches:
                        print(f"  📊 Pattern '{pattern}' matched: {match.groups()}")
                break
        else:
            print(f"  ❌ No building name found")

if __name__ == "__main__":
    print("🤖 Dark War Survival OCR Debug Tool")
    print("=" * 50)

    # Test building detection patterns
    test_building_detection()

    # Test OCR on actual screenshot
    success = test_ocr_on_screenshot()

    print(f"\n🎯 Test completed. Success: {success}")
    print("\nFiles created:")
    print("- debug_screenshot.png (screenshot used for OCR)")
    print("\nNext steps:")
    print("1. Check debug_screenshot.png to see what OCR is analyzing")
    print("2. Look at the extracted text above")
    print("3. Compare with what you see in the game")