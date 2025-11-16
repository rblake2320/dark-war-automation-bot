"""
Dark War Survival Bot - Smart Building Management System
Handles building state tracking, OCR detection, and skip logic

Version 2.1.0 Features:
- Building registry with max levels
- JSON persistence for building states
- OCR integration for automatic level detection
- Smart skip logic to avoid maxed buildings
- Statistics tracking for efficiency
"""

import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# OCR imports (optional - graceful fallback if not available)
try:
    import cv2
    import numpy as np
    import pytesseract
    from PIL import Image
    from pytesseract import Output
    from pytesseract.pytesseract import TesseractNotFoundError

    # Attempt to locate Tesseract executable for Windows users
    if sys.platform == "win32":
        tesseract_paths = [
            r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
            r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
            r"C:\\ProgramData\\chocolatey\\bin\\tesseract.exe",
            r"C:\\ProgramData\\chocolatey\\lib\\tesseract\\tools\\tesseract.exe",
            r"C:\\Users\\techai\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"
        ]

        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
        else:
            discovered = shutil.which("tesseract")
            if discovered:
                pytesseract.pytesseract.tesseract_cmd = discovered

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("WARNING: OCR libraries not available. Auto-detection disabled.")
    print("Install with: pip install pytesseract opencv-python pillow")

class BuildingManager:
    """Smart building management with OCR detection and skip logic"""

    def __init__(self, data_dir="building_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Building registry with known max levels for Dark War Survival
        self.building_registry = {
            # Defensive Buildings
            "tower": {"max_level": 25, "category": "defense", "priority": "high"},
            "wall": {"max_level": 25, "category": "defense", "priority": "medium"},
            "gate": {"max_level": 25, "category": "defense", "priority": "medium"},
            "trap": {"max_level": 20, "category": "defense", "priority": "low"},

            # Resource Buildings
            "farm": {"max_level": 25, "category": "resource", "priority": "high"},
            "lumber_mill": {"max_level": 25, "category": "resource", "priority": "high"},
            "quarry": {"max_level": 25, "category": "resource", "priority": "high"},
            "iron_mine": {"max_level": 25, "category": "resource", "priority": "high"},
            "warehouse": {"max_level": 25, "category": "storage", "priority": "high"},

            # Military Buildings
            "barracks": {"max_level": 25, "category": "military", "priority": "high"},
            "stable": {"max_level": 25, "category": "military", "priority": "high"},
            "workshop": {"max_level": 25, "category": "military", "priority": "medium"},
            "academy": {"max_level": 25, "category": "research", "priority": "high"},

            # Support Buildings
            "hospital": {"max_level": 25, "category": "support", "priority": "high"},
            "embassy": {"max_level": 25, "category": "support", "priority": "medium"},
            "prison": {"max_level": 25, "category": "support", "priority": "low"},

            # Special Buildings
            "dorm": {"max_level": 10, "category": "special", "priority": "medium"},
            "hero_hall": {"max_level": 25, "category": "special", "priority": "high"},
            "altar": {"max_level": 25, "category": "special", "priority": "medium"},

            # Alliance Buildings
            "alliance_center": {"max_level": 25, "category": "alliance", "priority": "medium"},
            "rally_point": {"max_level": 25, "category": "alliance", "priority": "low"},
        }

        # Current building states
        self.building_states = {}

        # Configuration
        self.config = {
            "enable_smart_skip": True,
            "enable_ocr_detection": OCR_AVAILABLE,
            "skip_maxed_buildings": True,
            "ocr_confidence_threshold": 0.85,
            "auto_save": True,
            "log_skipped_buildings": True,
            # OCR tuning parameters
            "ocr_roi_start_ratio": 0.55,  # focus on bottom 45% of screen by default
            "ocr_scale_factor": 2.0,
            "ocr_adaptive_block_size": 31,
            "ocr_adaptive_c": 5,
            "save_ocr_debug_images": False,
            "ocr_debug_limit": 25
        }

        # Statistics
        self.stats = {
            "buildings_scanned": 0,
            "buildings_skipped_session": 0,
            "buildings_auto_detected": 0,
            "time_saved_seconds": 0,
            "last_scan_time": None,
            "last_scan_summary": {}
        }

        # OCR runtime details
        self.ocr_engine = {
            "libraries_available": OCR_AVAILABLE,
            "tesseract_installed": False,
            "tesseract_cmd": None,
            "version": None,
            "last_error": None
        }

        # Debug directory for OCR snapshots
        self.debug_dir = self.data_dir / "ocr_debug"
        self.debug_dir.mkdir(exist_ok=True)
        self._debug_history = []

        # Setup logging first (needed for load operations)
        self.setup_logging()

        # Load existing data
        self.load_building_states()
        self.load_config()
        self.setup_ocr_engine()

    def setup_logging(self):
        """Setup logging for building manager"""
        log_file = self.data_dir / "building_manager.log"
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_ocr_engine(self):
        """Detect availability of OCR runtime components"""
        if not self.ocr_engine.get("libraries_available", False):
            self.ocr_engine.update({
                "tesseract_installed": False,
                "tesseract_cmd": None,
                "version": None,
                "last_error": "Required OCR Python libraries are not installed."
            })
            return self.ocr_engine

        cmd = getattr(pytesseract.pytesseract, "tesseract_cmd", None)
        if not cmd or not Path(str(cmd)).exists():
            discovered = shutil.which("tesseract")
            if discovered:
                pytesseract.pytesseract.tesseract_cmd = discovered
                cmd = discovered

        self.ocr_engine["tesseract_cmd"] = cmd

        try:
            version = pytesseract.get_tesseract_version()
            self.ocr_engine.update({
                "tesseract_installed": True,
                "version": str(version),
                "last_error": None
            })
            self.logger.info(f"Tesseract detected (v{version}) at {cmd}")
        except (TesseractNotFoundError, FileNotFoundError) as exc:
            self.ocr_engine.update({
                "tesseract_installed": False,
                "version": None,
                "last_error": str(exc)
            })
            self.logger.warning(f"Tesseract not available: {exc}")
        except Exception as exc:
            self.ocr_engine.update({
                "tesseract_installed": False,
                "version": None,
                "last_error": str(exc)
            })
            self.logger.error(f"Failed to initialize OCR engine: {exc}")

        return self.ocr_engine

    def get_ocr_status(self):
        """Return a snapshot of OCR availability"""
        return dict(self.ocr_engine)

    def _extract_ocr_roi(self, image):
        """Crop region of interest for building OCR"""
        height, width = image.shape[:2]
        start_ratio = float(self.config.get("ocr_roi_start_ratio", 0.55))
        start_ratio = min(max(start_ratio, 0.0), 0.95)
        start_row = int(height * start_ratio)

        roi = image[start_row:, :]
        roi_info = {
            "image_height": height,
            "image_width": width,
            "roi_start_row": start_row,
            "roi_height": roi.shape[0],
            "roi_width": roi.shape[1]
        }

        self.logger.info(
            "Using OCR ROI from row %s (%.0f%% of image height)",
            start_row,
            (1 - start_ratio) * 100
        )

        return roi, roi_info

    def _preprocess_image_for_ocr(self, roi):
        """Generate preprocessed variants for OCR"""
        summary = {}

        try:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        except cv2.error:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGRA2GRAY)

        scale_factor = float(self.config.get("ocr_scale_factor", 2.0))
        if scale_factor < 1.0:
            scale_factor = 1.0

        scaled = cv2.resize(
            gray,
            None,
            fx=scale_factor,
            fy=scale_factor,
            interpolation=cv2.INTER_CUBIC if scale_factor > 1.0 else cv2.INTER_LINEAR
        )

        denoised = cv2.bilateralFilter(scaled, 9, 75, 75)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        block_size = int(self.config.get("ocr_adaptive_block_size", 31))
        if block_size % 2 == 0:
            block_size += 1
        block_size = max(block_size, 11)
        c_value = int(self.config.get("ocr_adaptive_c", 5))

        adaptive = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            c_value
        )

        inverted = cv2.bitwise_not(adaptive)
        morph_kernel = np.ones((3, 3), np.uint8)
        morph = cv2.morphologyEx(inverted, cv2.MORPH_CLOSE, morph_kernel, iterations=1)

        variants = [
            ("enhanced", enhanced),
            ("adaptive", adaptive),
            ("morph", morph)
        ]

        summary.update({
            "scale_factor": scale_factor,
            "adaptive_block_size": block_size,
            "adaptive_c": c_value,
            "variant_count": len(variants)
        })

        return variants, summary

    def _tesseract_configs(self):
        whitelist = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.:/%()- "
        return [
            f"--oem 3 --psm 6 -c tessedit_char_whitelist={whitelist}",
            f"--oem 3 --psm 7 -c tessedit_char_whitelist={whitelist}",
            f"--oem 3 --psm 8 -c tessedit_char_whitelist={whitelist}"
        ]

    def _run_ocr_pipeline(self, variants):
        """Execute OCR against prepared variants"""
        collected_lines = []
        attempts = []

        for variant_name, variant_image in variants:
            pil_image = Image.fromarray(variant_image)
            for config in self._tesseract_configs():
                try:
                    text = pytesseract.image_to_string(pil_image, config=config)
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    if lines:
                        collected_lines.extend(lines)
                    attempts.append({
                        "variant": variant_name,
                        "config": config,
                        "lines": len(lines)
                    })
                except TesseractNotFoundError:
                    raise
                except Exception as exc:
                    self.logger.debug(
                        "OCR attempt failed for variant %s with config %s: %s",
                        variant_name,
                        config,
                        exc
                    )

        # Deduplicate lines while preserving order
        unique_lines = []
        seen = set()
        for line in collected_lines:
            normalized = line.lower()
            if normalized not in seen:
                seen.add(normalized)
                unique_lines.append(line)

        combined_text = "\n".join(unique_lines)

        # Confidence statistics using the first variant as baseline
        confidence_summary = {}
        if variants:
            try:
                data = pytesseract.image_to_data(
                    Image.fromarray(variants[0][1]),
                    config=self._tesseract_configs()[0],
                    output_type=Output.DICT
                )
                confidences = [int(float(c)) for c in data.get("conf", []) if c not in ("-1", "", None)]
                if confidences:
                    confidence_summary = {
                        "mean_confidence": round(sum(confidences) / len(confidences), 2),
                        "max_confidence": max(confidences),
                        "min_confidence": min(confidences),
                        "sample_size": len(confidences)
                    }
            except Exception as exc:
                confidence_summary = {"error": str(exc)}

        return combined_text, attempts, confidence_summary

    def _save_debug_snapshot(self, full_image, roi, variants):
        """Optionally persist debug images for troubleshooting"""
        if not self.config.get("save_ocr_debug_images", False):
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"ocr_{timestamp}"

        paths = {}
        full_path = self.debug_dir / f"{base_name}_full.png"
        cv2.imwrite(str(full_path), full_image)
        paths["full"] = str(full_path)

        roi_path = self.debug_dir / f"{base_name}_roi.png"
        cv2.imwrite(str(roi_path), roi)
        paths["roi"] = str(roi_path)

        if variants:
            variant_name, variant_image = variants[0]
            processed_path = self.debug_dir / f"{base_name}_{variant_name}.png"
            cv2.imwrite(str(processed_path), variant_image)
            paths["processed"] = str(processed_path)

        self._record_debug_files(paths.values())
        return paths

    def _record_debug_files(self, new_files):
        """Maintain rolling window of debug snapshots"""
        limit = max(int(self.config.get("ocr_debug_limit", 25)), 1)
        for file_path in new_files:
            self._debug_history.append(str(file_path))

        while len(self._debug_history) > limit:
            expired = self._debug_history.pop(0)
            try:
                os.remove(expired)
            except OSError:
                continue

    def get_building_info(self, building_name):
        """Get building registry information"""
        return self.building_registry.get(building_name.lower(), {
            "max_level": 25,
            "category": "unknown",
            "priority": "medium"
        })

    def should_skip_building(self, building_name, area_name="unknown"):
        """Determine if building should be skipped"""
        if not self.config["enable_smart_skip"]:
            return False

        building_key = f"{building_name.lower()}_{area_name}"
        building_state = self.building_states.get(building_key, {})

        # Check if manually marked as maxed
        if building_state.get("manually_maxed", False):
            self.stats["buildings_skipped_session"] += 1
            self.stats["time_saved_seconds"] += 5  # Estimate 5s saved per skip
            self.logger.info(f"Skipped {building_name} - manually marked as maxed")
            return True

        # Check if auto-detected as maxed
        if building_state.get("auto_detected_maxed", False):
            confidence = building_state.get("detection_confidence", 0)
            if confidence >= self.config["ocr_confidence_threshold"]:
                self.stats["buildings_skipped_session"] += 1
                self.stats["time_saved_seconds"] += 5
                self.logger.info(f"Skipped {building_name} - auto-detected maxed (confidence: {confidence:.2f})")
                return True

        return False

    def mark_building_maxed(self, building_name, area_name="unknown", manual=True):
        """Mark a building as maxed (manual or automatic)"""
        building_key = f"{building_name.lower()}_{area_name}"
        building_info = self.get_building_info(building_name)

        if building_key not in self.building_states:
            self.building_states[building_key] = {}

        self.building_states[building_key].update({
            "building_name": building_name,
            "area_name": area_name,
            "max_level": building_info["max_level"],
            "manually_maxed": manual,
            "auto_detected_maxed": not manual,
            "detection_confidence": 1.0 if manual else self.building_states[building_key].get("detection_confidence", 0),
            "marked_date": datetime.now().isoformat(),
            "category": building_info["category"],
            "priority": building_info["priority"]
        })

        if self.config["auto_save"]:
            self.save_building_states()

        action = "manually marked" if manual else "auto-detected"
        self.logger.info(f"Building {building_name} {action} as maxed")

    def unmark_building_maxed(self, building_name, area_name="unknown"):
        """Remove maxed status from a building"""
        building_key = f"{building_name.lower()}_{area_name}"
        if building_key in self.building_states:
            self.building_states[building_key].update({
                "manually_maxed": False,
                "auto_detected_maxed": False,
                "detection_confidence": 0.0,
                "unmarked_date": datetime.now().isoformat()
            })

            if self.config["auto_save"]:
                self.save_building_states()

            self.logger.info(f"Building {building_name} unmarked as maxed")

    def reset_all_buildings(self):
        """Reset all building states"""
        self.building_states.clear()
        self.stats["buildings_skipped_session"] = 0
        self.stats["time_saved_seconds"] = 0

        if self.config["auto_save"]:
            self.save_building_states()

        self.logger.info("All building states reset")

    def scan_buildings_with_ocr(self, screenshot_path_or_image):
        """Use OCR to detect building levels from screenshot"""
        base_result = {
            "success": False,
            "detected_buildings": {},
            "total_detected": 0
        }

        if not self.config.get("enable_ocr_detection", False):
            message = "OCR detection is disabled in settings. Enable it to scan buildings."
            self.logger.warning(message)
            return {**base_result, "error": message, "ocr_status": self.get_ocr_status()}

        if not self.ocr_engine.get("libraries_available", False):
            message = "OCR libraries (pytesseract/opencv/numpy/Pillow) are not installed."
            self.logger.error(message)
            return {**base_result, "error": message, "ocr_status": self.get_ocr_status()}

        # Refresh engine info in case system changed while running
        self.setup_ocr_engine()
        if not self.ocr_engine.get("tesseract_installed", False):
            message = (
                "tesseract is not installed or it is not in your PATH. "
                "Install it from https://github.com/UB-Mannheim/tesseract/wiki and restart the bot."
            )
            self.logger.error(message)
            return {**base_result, "error": message, "ocr_status": self.get_ocr_status()}

        try:
            # Load image input
            if isinstance(screenshot_path_or_image, str):
                image = cv2.imread(screenshot_path_or_image)
            else:
                image = np.array(screenshot_path_or_image)

            if image is None:
                message = "Could not load image for OCR scanning."
                self.logger.error(message)
                return {**base_result, "error": message}

            roi, roi_info = self._extract_ocr_roi(image)
            variants, preprocess_summary = self._preprocess_image_for_ocr(roi)

            combined_text, attempts, confidence_stats = self._run_ocr_pipeline(variants)

            if not combined_text.strip():
                message = "OCR did not return any readable text. Try adjusting lighting or zooming in."
                self.logger.warning(message)
                self.stats["last_scan_summary"] = {
                    "message": message,
                    "roi": roi_info,
                    "preprocessing": preprocess_summary,
                    "attempts": attempts,
                    "confidence": confidence_stats
                }
                return {**base_result, "error": message, "ocr_status": self.get_ocr_status(), "summary": self.stats["last_scan_summary"]}

            # Limit the amount of text logged
            log_preview = combined_text[:600].replace("\n", " | ")
            self.logger.info(f"OCR extracted text preview: {log_preview}...")

            detected_buildings = self.parse_building_levels(combined_text)

            # Update building states based on detection
            auto_detected = 0
            for building_name, level_info in detected_buildings.items():
                area_name = level_info.get("area", "detected")
                building_key = f"{building_name.lower()}_{area_name}"

                state = self.building_states.setdefault(building_key, {})
                state.update({
                    "building_name": building_name,
                    "area_name": area_name,
                    "current_level": level_info.get("current_level", state.get("current_level", 0)),
                    "max_level": level_info.get("max_level", state.get("max_level", 25)),
                    "category": self.get_building_info(building_name).get("category", "unknown"),
                    "priority": self.get_building_info(building_name).get("priority", "medium"),
                    "detection_confidence": level_info.get("confidence", 0.0),
                    "raw_text": level_info.get("raw_text", "")
                })

                if level_info.get("is_maxed"):
                    auto_detected += 1
                    state["auto_detected_maxed"] = True
                    state["manually_maxed"] = False
                    state["marked_date"] = datetime.now().isoformat()
                    self.logger.info(
                        "Auto-marked %s as maxed (confidence %.2f)",
                        building_name,
                        level_info.get("confidence", 0.0)
                    )
                else:
                    state.setdefault("auto_detected_maxed", False)

            self.stats["buildings_scanned"] += len(detected_buildings)
            self.stats["buildings_auto_detected"] += auto_detected
            self.stats["last_scan_time"] = datetime.now().isoformat()

            summary = {
                "roi": roi_info,
                "preprocessing": preprocess_summary,
                "attempts": attempts,
                "confidence": confidence_stats,
                "lines_detected": len(combined_text.splitlines()),
                "auto_marked": auto_detected
            }
            self.stats["last_scan_summary"] = summary

            debug_paths = self._save_debug_snapshot(image, roi, variants)
            if debug_paths:
                summary["debug_paths"] = debug_paths

            if self.config.get("auto_save", False):
                self.save_building_states()

            return {
                **base_result,
                "success": True,
                "detected_buildings": detected_buildings,
                "total_detected": len(detected_buildings),
                "summary": summary,
                "ocr_status": self.get_ocr_status()
            }

        except TesseractNotFoundError as exc:
            self.ocr_engine["tesseract_installed"] = False
            self.ocr_engine["last_error"] = str(exc)
            message = (
                "Tesseract engine was not found while running OCR. "
                "Reinstall Tesseract and restart the bot."
            )
            self.logger.error(message)
            return {**base_result, "error": message, "ocr_status": self.get_ocr_status()}
        except Exception as exc:
            self.logger.exception(f"OCR scan failed: {exc}")
            return {**base_result, "error": str(exc), "ocr_status": self.get_ocr_status()}

    def parse_building_levels(self, extracted_text):
        """Parse extracted text for building levels"""
        import re

        detected_buildings = {}
        lines = extracted_text.strip().split('\n')

        # Enhanced patterns for Dark War Survival
        max_patterns = [
            r'level\s*(\d+)\s*/\s*(\d+)',      # "Level 10/10"
            r'lv\.?\s*(\d+)\s*/\s*(\d+)',      # "Lv 10/10" or "Lv.10/10"
            r'lv\.?\s*(\d+)',                  # "Lv.8", "Lv 25"
            r'(\d+)\s*/\s*(\d+)',              # "10/10", "25 / 25"
            r'(\d+)\/(\d+)',                   # "10/10" without spaces
            r'max',                            # "MAX"
            r'maxed',                          # "MAXED"
            r'(\d+)\s*%',                      # "100%" for completion
            r'lvl\.?\s*(\d+)\s*/\s*(\d+)',     # "Lvl 10/10"
            r'level:\s*(\d+)\s*/\s*(\d+)',     # "Level: 10/10"
        ]

        # Building name patterns for Dark War (more flexible)
        building_keywords = [
            'hunter', 'hut', 'tower', 'wall', 'gate', 'farm', 'lumber', 'mill',
            'quarry', 'mine', 'warehouse', 'storage', 'barracks', 'stable',
            'workshop', 'academy', 'hospital', 'embassy', 'prison', 'dorm',
            'hero', 'hall', 'altar', 'alliance', 'rally', 'point', 'kitchen',
            'watchtower', 'gathering', 'ground', 'formation'
        ]

        # Add debug info
        self.logger.info(f"Parsing {len(lines)} lines of OCR text for building levels")

        # Process each line and also try combining words
        all_text_combined = " ".join(lines).lower()

        # Look for building names in individual lines and combined text
        for text_source in [lines, [all_text_combined]]:
            for line in text_source:
                line_lower = line.lower().strip()

                # Skip empty lines or very short lines
                if len(line_lower) < 3:
                    continue

                self.logger.info(f"Analyzing line: {repr(line_lower[:100])}")

                # Check for building names (from registry and common variations)
                building_variations = {
                    "hunter": ["hunter", "huntershut", "hunters"],
                    "tower": ["tower", "watchtower", "watch"],
                    "kitchen": ["kitchen"],
                    "farm": ["farm"],
                    "lumber_mill": ["lumber", "mill", "lumbermill"],
                    "quarry": ["quarry"],
                    "warehouse": ["warehouse", "storage"],
                    "dorm": ["dorm"],
                    "gathering_ground": ["gathering", "ground"],
                    "formation": ["formation"]
                }

                for building_name, variations in building_variations.items():
                    # Check if any variation appears in the line
                    found_building = False
                    for variation in variations:
                        if variation in line_lower:
                            found_building = True
                            self.logger.info(f"Found building '{building_name}' via '{variation}' in line")
                            break

                    if not found_building:
                        continue

                    # Found a building name, check for level info in same line and nearby lines
                    lines_to_check = [line_lower]

                    # Also check next few lines for level info
                    if text_source == lines:
                        current_idx = text_source.index(line)
                        for i in range(1, 3):  # Check next 2 lines
                            if current_idx + i < len(text_source):
                                lines_to_check.append(text_source[current_idx + i].lower())

                    for check_line in lines_to_check:
                        for pattern in max_patterns:
                            matches = re.finditer(pattern, check_line, re.IGNORECASE)
                            for match in matches:
                                if pattern in [r'max', r'maxed']:
                                    # Simple max indicator
                                    detected_buildings[building_name] = {
                                        "current_level": self.building_registry.get(building_name, {}).get("max_level", 25),
                                        "max_level": self.building_registry.get(building_name, {}).get("max_level", 25),
                                        "is_maxed": True,
                                        "confidence": 0.9,
                                        "detection_method": "keyword",
                                        "raw_text": line,
                                        "area": "detected"
                                    }
                                    self.logger.info(f"Detected {building_name} as MAXED via pattern {pattern}")
                                elif len(match.groups()) >= 2:
                                    # Numeric level pattern
                                    try:
                                        current = int(match.group(1))
                                        maximum = int(match.group(2)) if match.group(2) else current
                                        is_maxed = current == maximum and maximum > 15  # Only consider maxed if level is reasonable

                                        detected_buildings[building_name] = {
                                            "current_level": current,
                                            "max_level": maximum,
                                            "is_maxed": is_maxed,
                                            "confidence": 0.85 if is_maxed else 0.7,
                                            "detection_method": "numeric",
                                            "raw_text": line,
                                            "area": "detected"
                                        }
                                        self.logger.info(f"Detected {building_name} level {current}/{maximum}, maxed: {is_maxed}")
                                    except (ValueError, TypeError):
                                        continue
                                break
                        if building_name in detected_buildings:
                            break
                    if building_name in detected_buildings:
                        break

        return detected_buildings

    def get_statistics(self):
        """Get comprehensive statistics"""
        total_buildings = len(self.building_states)
        maxed_buildings = sum(1 for state in self.building_states.values()
                             if state.get("manually_maxed", False) or state.get("auto_detected_maxed", False))

        ocr_available = self.ocr_engine.get("tesseract_installed", False)
        ocr_version = self.ocr_engine.get("version")
        ocr_error = self.ocr_engine.get("last_error")

        return {
            "total_buildings": total_buildings,
            "maxed_buildings": maxed_buildings,
            "active_buildings": total_buildings - maxed_buildings,
            "buildings_skipped_session": self.stats["buildings_skipped_session"],
            "time_saved_minutes": round(self.stats["time_saved_seconds"] / 60, 1),
            "buildings_auto_detected": self.stats["buildings_auto_detected"],
            "buildings_scanned": self.stats["buildings_scanned"],
            "last_scan": self.stats["last_scan_time"],
            "last_scan_summary": self.stats.get("last_scan_summary", {}),
            "ocr_available": ocr_available,
            "ocr_version": ocr_version,
            "ocr_error": ocr_error
        }

    def get_building_list(self):
        """Get formatted building list for UI"""
        buildings = []

        for building_key, state in self.building_states.items():
            building_name = state.get("building_name", building_key.split("_")[0])
            area_name = state.get("area_name", "unknown")

            buildings.append({
                "name": building_name.title(),
                "area": area_name,
                "key": building_key,
                "manually_maxed": state.get("manually_maxed", False),
                "auto_detected_maxed": state.get("auto_detected_maxed", False),
                "is_maxed": state.get("manually_maxed", False) or state.get("auto_detected_maxed", False),
                "max_level": state.get("max_level", 25),
                "current_level": state.get("current_level", 0),
                "confidence": state.get("detection_confidence", 0),
                "category": state.get("category", "unknown"),
                "priority": state.get("priority", "medium"),
                "marked_date": state.get("marked_date", "")
            })

        # Sort by priority and name
        priority_order = {"high": 0, "medium": 1, "low": 2}
        buildings.sort(key=lambda x: (priority_order.get(x["priority"], 1), x["name"]))

        return buildings

    def save_building_states(self):
        """Save building states to JSON file"""
        data = {
            "version": "2.1.0",
            "last_updated": datetime.now().isoformat(),
            "building_states": self.building_states,
            "statistics": self.stats
        }

        state_file = self.data_dir / "building_states.json"
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info("Building states saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save building states: {e}")

    def load_building_states(self):
        """Load building states from JSON file"""
        state_file = self.data_dir / "building_states.json"

        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.building_states = data.get("building_states", {})
                self.stats.update(data.get("statistics", {}))

                # Reset session stats
                self.stats["buildings_skipped_session"] = 0

                self.logger.info(f"Loaded {len(self.building_states)} building states")
            except Exception as e:
                self.logger.error(f"Failed to load building states: {e}")
                self.building_states = {}

    def save_config(self):
        """Save configuration to JSON file"""
        config_file = self.data_dir / "config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("Configuration saved")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def load_config(self):
        """Load configuration from JSON file"""
        config_file = self.data_dir / "config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                self.config.update(loaded_config)
                self.logger.info("Configuration loaded")
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")

# Test function
if __name__ == "__main__":
    # Create test instance
    bm = BuildingManager()

    # Test basic functionality
    print("Building Manager Test:")
    print(f"OCR Available: {OCR_AVAILABLE}")

    # Mark some buildings as maxed
    bm.mark_building_maxed("dorm", "main_base", manual=True)
    bm.mark_building_maxed("tower", "north_wall", manual=True)

    # Test skip logic
    print(f"Should skip dorm: {bm.should_skip_building('dorm', 'main_base')}")
    print(f"Should skip farm: {bm.should_skip_building('farm', 'main_base')}")

    # Show statistics
    stats = bm.get_statistics()
    print(f"Statistics: {stats}")

    # Show building list
    buildings = bm.get_building_list()
    print(f"Buildings: {len(buildings)} total")

    print("Building Manager test completed!")