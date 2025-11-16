"""
Advanced OCR Debug and Diagnostic Tool
For Dark War Survival Bot v2.1.0

This script provides comprehensive OCR debugging capabilities:
- Detailed configuration checking
- Performance benchmarking
- Visual debug output
- Error logging and analysis
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

try:
    import pytesseract
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
    CV2_AVAILABLE = True
except ImportError as e:
    OCR_AVAILABLE = False
    CV2_AVAILABLE = False
    missing = str(e).split("'")[1] if "'" in str(e) else "unknown"
    print(f"WARNING: Missing dependency: {missing}")
    print("Install with: pip install pytesseract Pillow opencv-python-headless")

# Create error log directory if it doesn't exist
ERROR_LOG_DIR = Path("error_logs")
ERROR_LOG_DIR.mkdir(exist_ok=True)

class OCRDebugger:
    """Advanced OCR debugging and diagnostic tool"""

    def __init__(self, log_errors=True):
        self.log_errors = log_errors
        self.error_log_path = ERROR_LOG_DIR / f"ocr_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.test_results = []

    def log(self, message, level="INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        print(formatted)

        if self.log_errors:
            with open(self.error_log_path, 'a') as f:
                f.write(formatted + '\n')

    def test_environment(self):
        """Test OCR environment and dependencies"""
        self.log("Testing OCR Environment", "TEST")

        tests = []

        # Test 1: Check Tesseract installation
        try:
            version = pytesseract.get_tesseract_version()
            self.log(f"✓ Tesseract version: {version}", "PASS")
            tests.append(("Tesseract Installation", True))
        except Exception as e:
            self.log(f"✗ Tesseract not found: {e}", "FAIL")
            tests.append(("Tesseract Installation", False))
            return tests

        # Test 2: Check Tesseract languages
        try:
            langs = pytesseract.get_languages()
            self.log(f"✓ Available languages: {', '.join(langs[:5])}{'...' if len(langs) > 5 else ''}", "PASS")
            tests.append(("Language Support", True))
        except Exception as e:
            self.log(f"✗ Language check failed: {e}", "FAIL")
            tests.append(("Language Support", False))

        # Test 3: Check OpenCV
        if CV2_AVAILABLE:
            self.log(f"✓ OpenCV version: {cv2.__version__}", "PASS")
            tests.append(("OpenCV", True))
        else:
            self.log("✗ OpenCV not available", "FAIL")
            tests.append(("OpenCV", False))

        # Test 4: PIL/Pillow
        try:
            self.log(f"✓ PIL/Pillow version: {Image.__version__}", "PASS")
            tests.append(("PIL/Pillow", True))
        except:
            self.log("! PIL version unknown", "WARN")
            tests.append(("PIL/Pillow", True))

        return tests

    def benchmark_ocr_performance(self):
        """Benchmark OCR performance with different configurations"""
        self.log("Benchmarking OCR Performance", "TEST")

        if not OCR_AVAILABLE:
            return [("Performance Benchmark", False)]

        # Create test image
        img = Image.new('RGB', (800, 200), color='white')
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
        except:
            font = ImageFont.load_default()

        test_text = "Building Level 25"
        draw.text((50, 70), test_text, fill='black', font=font)

        # Test different OCR configurations
        configs = [
            ("Default", ""),
            ("PSM 6 (Single block)", "--psm 6"),
            ("PSM 7 (Single line)", "--psm 7"),
            ("PSM 11 (Sparse text)", "--psm 11"),
        ]

        results = []

        for config_name, config_param in configs:
            try:
                start_time = time.time()
                if config_param:
                    text = pytesseract.image_to_string(img, config=config_param)
                else:
                    text = pytesseract.image_to_string(img)
                elapsed = time.time() - start_time

                text_clean = text.strip()
                accuracy = "High" if "25" in text_clean and "Level" in text_clean else "Low"

                self.log(f"  {config_name}: {elapsed:.3f}s | Accuracy: {accuracy} | Text: '{text_clean}'", "INFO")
                results.append((config_name, True, elapsed))

            except Exception as e:
                self.log(f"  {config_name}: FAILED - {e}", "FAIL")
                results.append((config_name, False, 0))

        return results

    def test_image_preprocessing(self):
        """Test different image preprocessing techniques"""
        self.log("Testing Image Preprocessing", "TEST")

        if not OCR_AVAILABLE or not CV2_AVAILABLE:
            return [("Image Preprocessing", False)]

        # Create test image with varying contrast
        img = Image.new('RGB', (600, 150), color=(200, 200, 200))  # Gray background
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except:
            font = ImageFont.load_default()

        test_text = "Resources: 1250"
        draw.text((50, 50), test_text, fill=(50, 50, 50), font=font)

        # Convert to numpy array for OpenCV
        img_np = np.array(img)

        preprocessing_methods = [
            ("Original", img_np),
            ("Grayscale", cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)),
            ("Binary Threshold", cv2.threshold(cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY), 127, 255, cv2.THRESH_BINARY)[1]),
            ("Adaptive Threshold", cv2.adaptiveThreshold(cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
        ]

        results = []

        for method_name, processed_img in preprocessing_methods:
            try:
                # Convert back to PIL for OCR
                if len(processed_img.shape) == 2:
                    pil_img = Image.fromarray(processed_img)
                else:
                    pil_img = Image.fromarray(processed_img)

                text = pytesseract.image_to_string(pil_img)
                text_clean = text.strip()

                accuracy = "Good" if "1250" in text_clean else "Poor"
                self.log(f"  {method_name}: {accuracy} | Text: '{text_clean[:30]}...'", "INFO")
                results.append((method_name, True))

            except Exception as e:
                self.log(f"  {method_name}: FAILED - {e}", "FAIL")
                results.append((method_name, False))

        return results

    def test_confidence_levels(self):
        """Test OCR confidence scoring"""
        self.log("Testing Confidence Levels", "TEST")

        if not OCR_AVAILABLE:
            return [("Confidence Testing", False)]

        # Create clear test image
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
        except:
            font = ImageFont.load_default()

        draw.text((50, 20), "CLEAR TEXT", fill='black', font=font)

        try:
            # Get detailed OCR data including confidence
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]

            if confidences:
                avg_conf = sum(confidences) / len(confidences)
                max_conf = max(confidences)
                min_conf = min(confidences)

                self.log(f"  Average confidence: {avg_conf:.1f}%", "INFO")
                self.log(f"  Max confidence: {max_conf}%", "INFO")
                self.log(f"  Min confidence: {min_conf}%", "INFO")

                # Check confidence threshold
                high_conf_count = sum(1 for c in confidences if c > 70)
                self.log(f"  High confidence (>70%) detections: {high_conf_count}/{len(confidences)}", "INFO")

                return [("Confidence Testing", True)]
            else:
                self.log("  No confidence data available", "WARN")
                return [("Confidence Testing", False)]

        except Exception as e:
            self.log(f"  Confidence test failed: {e}", "FAIL")
            return [("Confidence Testing", False)]

    def save_debug_images(self):
        """Save debug images for visual inspection"""
        self.log("Generating Debug Images", "TEST")

        debug_dir = ERROR_LOG_DIR / "debug_images"
        debug_dir.mkdir(exist_ok=True)

        try:
            # Create sample images that represent game scenarios
            scenarios = [
                ("building_level.png", "Building Lv.15", (255, 255, 255), (0, 0, 0)),
                ("resource_count.png", "Wood: 5000", (240, 230, 140), (139, 69, 19)),
                ("troop_count.png", "Troops: 250/300", (173, 216, 230), (0, 0, 128)),
            ]

            for filename, text, bg_color, text_color in scenarios:
                img = Image.new('RGB', (400, 80), color=bg_color)
                draw = ImageDraw.Draw(img)

                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
                except:
                    font = ImageFont.load_default()

                draw.text((20, 20), text, fill=text_color, font=font)

                save_path = debug_dir / filename
                img.save(save_path)

                # Test OCR on this image
                ocr_result = pytesseract.image_to_string(img).strip()
                self.log(f"  Saved {filename} | OCR: '{ocr_result}'", "INFO")

            self.log(f"✓ Debug images saved to {debug_dir}", "PASS")
            return [("Debug Image Generation", True)]

        except Exception as e:
            self.log(f"✗ Debug image generation failed: {e}", "FAIL")
            return [("Debug Image Generation", False)]

    def run_all_tests(self):
        """Run complete OCR diagnostic suite"""
        self.log("=" * 70, "INFO")
        self.log("Dark War Survival Bot - Advanced OCR Debug v2.1.0", "INFO")
        self.log("=" * 70, "INFO")
        self.log(f"Error log: {self.error_log_path}", "INFO")
        self.log("", "INFO")

        all_results = []

        # Run all test suites
        test_suites = [
            ("Environment Check", self.test_environment),
            ("Performance Benchmark", self.benchmark_ocr_performance),
            ("Image Preprocessing", self.test_image_preprocessing),
            ("Confidence Levels", self.test_confidence_levels),
            ("Debug Images", self.save_debug_images),
        ]

        for suite_name, test_func in test_suites:
            self.log(f"\n{'=' * 70}", "INFO")
            self.log(f"{suite_name}", "INFO")
            self.log(f"{'=' * 70}", "INFO")

            try:
                results = test_func()
                all_results.extend(results)
            except Exception as e:
                self.log(f"Test suite failed: {e}", "FAIL")
                all_results.append((suite_name, False))

            self.log("", "INFO")

        # Final summary
        self.log("=" * 70, "INFO")
        self.log("Test Summary", "INFO")
        self.log("=" * 70, "INFO")

        passed = sum(1 for _, result in all_results if result is True)
        failed = sum(1 for _, result in all_results if result is False)
        total = len(all_results)

        for test_name, result in all_results:
            status = "PASS" if result else "FAIL"
            symbol = "✓" if result else "✗"
            self.log(f"{symbol} {test_name}: {status}", "INFO")

        self.log("", "INFO")
        self.log(f"Results: {passed}/{total} passed, {failed}/{total} failed", "INFO")

        if failed == 0:
            self.log("✓ All OCR systems operational!", "PASS")
            return 0
        else:
            self.log(f"! {failed} test(s) failed - check error log for details", "WARN")
            return 1

def main():
    """Main entry point"""
    debugger = OCRDebugger(log_errors=True)
    return debugger.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
