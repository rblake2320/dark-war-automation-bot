#!/usr/bin/env python3
"""
Simple OCR test without Unicode characters
"""

import os
import sys
import pyautogui
import pygetwindow as gw
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import pytesseract
    print("SUCCESS: pytesseract imported")

    # Check if Tesseract path is set correctly
    print(f"Tesseract command: {pytesseract.pytesseract.tesseract_cmd}")

    # Test Tesseract version
    version = pytesseract.get_tesseract_version()
    print(f"Tesseract version: {version}")

except Exception as e:
    print(f"ERROR with pytesseract: {e}")
    sys.exit(1)

def find_dark_war_window():
    """Find Dark War window"""
    print("\nFinding Dark War windows...")

    windows = gw.getAllWindows()
    dark_war_windows = []

    for window in windows:
        title_lower = window.title.lower()
        if "dark war" in title_lower or "darkwar" in title_lower:
            dark_war_windows.append(window)
            print(f"Found: {window.title} - {window.width}x{window.height}")

    return dark_war_windows

def test_simple_ocr():
    """Test OCR functionality"""
    print("\n=== TESTING OCR ===")

    # Find Dark War windows
    dark_war_windows = find_dark_war_window()

    if dark_war_windows:
        window = dark_war_windows[0]
        print(f"Using window: {window.title}")

        # Focus and screenshot
        try:
            window.activate()
            time.sleep(0.5)

            left, top, width, height = window.left, window.top, window.width, window.height
            print(f"Window bounds: {left}, {top}, {width}, {height}")

            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot.save("test_screenshot.png")
            print("Screenshot saved as test_screenshot.png")

            # Test basic OCR
            print("\nTesting basic OCR...")
            text = pytesseract.image_to_string(screenshot)
            lines = text.strip().split('\n')

            print(f"OCR found {len(lines)} lines of text:")
            for i, line in enumerate(lines[:20]):  # Show first 20 lines
                if line.strip():
                    print(f"Line {i+1}: '{line.strip()}'")

            # Look for building-related keywords
            print("\nLooking for building keywords...")
            building_keywords = ['kitchen', 'tower', 'farm', 'level', 'lv', 'max', 'watchtower', 'gathering', 'dorm']
            found_keywords = []

            for line in lines:
                line_lower = line.lower()
                for keyword in building_keywords:
                    if keyword in line_lower:
                        found_keywords.append(f"{keyword}: {line.strip()}")

            if found_keywords:
                print("Found building-related text:")
                for item in found_keywords:
                    print(f"  {item}")
            else:
                print("No building keywords found in OCR text")

            return True

        except Exception as e:
            print(f"Error during OCR test: {e}")
            return False
    else:
        print("No Dark War windows found!")
        return False

if __name__ == "__main__":
    print("Dark War Survival OCR Test")
    print("=" * 40)

    success = test_simple_ocr()
    print(f"\nTest completed. Success: {success}")