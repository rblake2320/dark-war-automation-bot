"""
Simple OCR Test Script
Tests basic OCR functionality for Dark War Survival Bot v2.1.0

This script provides a quick way to verify OCR is working correctly
and can read text from game screenshots.
"""

import sys
import os
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("WARNING: OCR libraries not available")
    print("Install with: pip install pytesseract Pillow")
    print("Also install Tesseract: https://github.com/tesseract-ocr/tesseract")

def test_ocr_installation():
    """Test if Tesseract OCR is properly installed"""
    if not OCR_AVAILABLE:
        return False, "OCR libraries not installed"

    try:
        version = pytesseract.get_tesseract_version()
        return True, f"Tesseract version {version} installed"
    except Exception as e:
        return False, f"Tesseract not found: {e}"

def test_simple_ocr():
    """Test OCR on a simple test image"""
    if not OCR_AVAILABLE:
        return False, "OCR not available"

    try:
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont

        # Create white background image
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)

        # Draw some text
        text = "Level 25"

        # Try to use a basic font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except:
            font = ImageFont.load_default()

        # Draw text in black
        draw.text((50, 30), text, fill='black', font=font)

        # Save test image
        test_path = "ocr_test_temp.png"
        img.save(test_path)

        # Perform OCR
        ocr_text = pytesseract.image_to_string(img)
        ocr_text_cleaned = ocr_text.strip()

        # Clean up
        if os.path.exists(test_path):
            os.remove(test_path)

        # Check if OCR found the text
        success = "25" in ocr_text_cleaned or "Level" in ocr_text_cleaned

        return success, f"OCR read: '{ocr_text_cleaned}' (expected: '{text}')"

    except Exception as e:
        return False, f"OCR test failed: {e}"

def test_screenshot_ocr(screenshot_path=None):
    """Test OCR on an actual screenshot if available"""
    if not OCR_AVAILABLE:
        return False, "OCR not available"

    # Look for any screenshot in common locations
    if screenshot_path is None:
        screenshot_paths = [
            "screenshots/latest.png",
            "screenshots/debug.png",
            "current_screen.png",
            "test_screenshot.png"
        ]

        for path in screenshot_paths:
            if os.path.exists(path):
                screenshot_path = path
                break

    if screenshot_path is None or not os.path.exists(screenshot_path):
        return None, "No screenshot found for testing"

    try:
        # Load and process screenshot
        img = Image.open(screenshot_path)

        # Perform OCR with multiple confidence levels
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        # Count high-confidence text detections
        high_conf_count = sum(1 for conf in ocr_data['conf'] if int(conf) > 70)
        total_text = ' '.join([text for text in ocr_data['text'] if text.strip()])

        return True, f"Found {high_conf_count} high-confidence text elements in {screenshot_path}"

    except Exception as e:
        return False, f"Screenshot OCR failed: {e}"

def main():
    """Run all OCR tests"""
    print("=" * 60)
    print("Dark War Survival Bot - Simple OCR Test v2.1.0")
    print("=" * 60)
    print()

    tests = [
        ("OCR Installation", test_ocr_installation),
        ("Simple Text Recognition", test_simple_ocr),
        ("Screenshot OCR", test_screenshot_ocr)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"Running: {test_name}...")
        success, message = test_func()

        if success is None:
            status = "SKIP"
            symbol = "⊘"
        elif success:
            status = "PASS"
            symbol = "✓"
        else:
            status = "FAIL"
            symbol = "✗"

        print(f"  [{symbol}] {status}: {message}")
        results.append((test_name, status))
        print()

    # Summary
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)

    passed = sum(1 for _, status in results if status == "PASS")
    failed = sum(1 for _, status in results if status == "FAIL")
    skipped = sum(1 for _, status in results if status == "SKIP")

    for test_name, status in results:
        print(f"  {test_name}: {status}")

    print()
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")

    if failed > 0:
        print()
        print("RECOMMENDATION:")
        print("  1. Install Tesseract OCR if not already installed")
        print("  2. Install Python OCR libraries: pip install pytesseract Pillow")
        print("  3. Ensure Tesseract is in your system PATH")
        return 1

    print()
    print("✓ OCR system is working correctly!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
