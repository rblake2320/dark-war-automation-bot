"""
Dark War Survival Bot - Smart Building Management System
Handles building state tracking, OCR detection, and coordinate-based scanning

Version 2.3.0 Features:
- Enhanced OCR accuracy with popup filtering
- Multiple OCR configuration strategies for number detection
- Cross-validation between scanning methods
- Coordinate-based building detection system
- Mouse click coordinate logging integration
- Precise building region scanning with OCR
- Building registry with max levels
- JSON persistence for building states
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

# Coordinate logger for precise building detection
try:
    from coordinate_logger import CoordinateLogger
    COORDINATE_LOGGER_AVAILABLE = True
except ImportError:
    COORDINATE_LOGGER_AVAILABLE = False

# LLM Advisor for strategic intelligence and OCR error correction
try:
    from llm_advisor import LLMAdvisor
    LLM_ADVISOR_AVAILABLE = True
except ImportError:
    LLM_ADVISOR_AVAILABLE = False

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
            "ocr_roi_start_ratio": 0.70,  # focus on bottom 30% of screen (less noise from popups)
            "ocr_scale_factor": 3.0,  # higher scaling for better number detection
            "ocr_adaptive_block_size": 31,
            "ocr_adaptive_c": 5,
            "save_ocr_debug_images": True,  # enable debug to see what OCR captures
            "ocr_debug_limit": 50,  # save more debug images for analysis
            # New popup detection parameters
            "enable_popup_filtering": True,
            "popup_keywords": ["upgrade", "to lv", "requirements", "insufficient", "cost", "timer", "confirm"]
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

        # Coordinate logger for precise building detection
        if COORDINATE_LOGGER_AVAILABLE:
            self.coordinate_logger = CoordinateLogger(data_dir)
            self.coordinate_based_scanning = True
        else:
            self.coordinate_logger = None
            self.coordinate_based_scanning = False

        # LLM Advisor for strategic intelligence and OCR error correction
        self.llm_advisor = None
        if LLM_ADVISOR_AVAILABLE:
            try:
                self.llm_advisor = LLMAdvisor(
                    model="gemma3:latest",  # Fast model for real-time usage
                    timeout=10,
                    enabled=True
                )
                self.logger.info("LLM Advisor initialized successfully")
            except Exception as e:
                self.logger.warning(f"LLM Advisor initialization failed: {e}")
                self.llm_advisor = None
        else:
            self.logger.info("LLM Advisor not available (llm_advisor.py not found)")

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

    def get_coordinate_status(self):
        """Return a snapshot of coordinate-based scanning availability"""
        if not self.coordinate_logger:
            return {
                "available": False,
                "coordinate_logger_loaded": False,
                "total_coordinates": 0,
                "building_types": {},
                "last_updated": None,
                "error": "Coordinate logger not initialized"
            }

        stats = self.coordinate_logger.get_coordinate_statistics()
        return {
            "available": self.coordinate_based_scanning,
            "coordinate_logger_loaded": True,
            "total_coordinates": stats.get("total_coordinates", 0),
            "building_types": stats.get("building_types", {}),
            "window_coverage": stats.get("window_coverage", {}),
            "last_updated": stats.get("last_updated"),
            "coordinates_file": str(self.coordinate_logger.coordinates_file) if self.coordinate_logger else None
        }

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

    def scan_buildings_with_coordinates(self, window_title, window_width=None, window_height=None):
        """Use coordinate-based scanning for precise building level detection"""
        base_result = {
            "success": False,
            "detected_buildings": {},
            "total_detected": 0,
            "method": "coordinates"
        }

        if not self.coordinate_based_scanning:
            message = "Coordinate-based scanning not available. Coordinate logger not initialized."
            self.logger.warning(message)
            return {**base_result, "error": message}

        if not self.coordinate_logger.coordinates:
            message = "No building coordinates logged. Use Coordinate Setup tab to log building positions."
            self.logger.warning(message)
            return {**base_result, "error": message}

        try:
            # Get target window for coordinate validation
            if not self.coordinate_logger.set_target_window(window_title):
                message = f"Failed to set target window: {window_title}"
                self.logger.error(message)
                return {**base_result, "error": message}

            # Get window dimensions for coordinate adjustment
            target_window = self.coordinate_logger.target_window
            current_width = target_window.width if target_window else window_width
            current_height = target_window.height if target_window else window_height

            if not current_width or not current_height:
                message = "Could not determine window dimensions for coordinate adjustment"
                self.logger.error(message)
                return {**base_result, "error": message}

            # Get adjusted coordinates for current window size
            adjusted_coordinates = self.coordinate_logger.get_coordinates_for_window(
                current_width, current_height
            )

            detected_buildings = {}
            scan_errors = []

            self.logger.info(f"📍 Starting coordinate-based scan for {len(adjusted_coordinates)} buildings")

            for coord_id, coord_data in adjusted_coordinates.items():
                try:
                    building_type = coord_data['building_type']
                    building_name = coord_data['building_name']
                    x = coord_data['absolute']['x']
                    y = coord_data['absolute']['y']
                    roi_width = coord_data.get('roi_size', {}).get('width', 150)
                    roi_height = coord_data.get('roi_size', {}).get('height', 80)

                    self.logger.info(f"🔍 Scanning {building_name} at ({x}, {y})")

                    # Take screenshot of the specific building region
                    building_result = self._scan_building_coordinate_region(
                        x, y, roi_width, roi_height, building_type, building_name
                    )

                    if building_result['success']:
                        detected_buildings[building_type] = building_result['building_data']
                        self.logger.info(f"✅ Detected {building_name}: {building_result['building_data']}")
                    else:
                        scan_errors.append(f"{building_name}: {building_result.get('error', 'Unknown error')}")
                        self.logger.warning(f"❌ Failed to detect {building_name}: {building_result.get('error')}")

                except Exception as e:
                    error_msg = f"Error scanning {coord_id}: {e}"
                    scan_errors.append(error_msg)
                    self.logger.error(error_msg)

            # Update statistics
            self.stats["buildings_scanned"] += len(adjusted_coordinates)
            self.stats["buildings_auto_detected"] += len(detected_buildings)
            self.stats["last_scan_time"] = datetime.now().isoformat()
            self.stats["last_scan_summary"] = {
                "total_coordinates": len(adjusted_coordinates),
                "successful_detections": len(detected_buildings),
                "failed_detections": len(scan_errors),
                "method": "coordinate_based"
            }

            success = len(detected_buildings) > 0
            result = {
                **base_result,
                "success": success,
                "detected_buildings": detected_buildings,
                "total_detected": len(detected_buildings),
                "scan_errors": scan_errors,
                "coordinates_used": len(adjusted_coordinates)
            }

            if success:
                self.logger.info(f"📊 Coordinate scan completed: {len(detected_buildings)}/{len(adjusted_coordinates)} buildings detected")
            else:
                self.logger.warning(f"📊 Coordinate scan completed with no detections. Errors: {scan_errors}")

            return result

        except Exception as e:
            error_msg = f"Coordinate-based scanning failed: {e}"
            self.logger.error(error_msg)
            return {**base_result, "error": error_msg}

    def _scan_building_coordinate_region(self, x, y, roi_width, roi_height, building_type, building_name):
        """Scan a specific coordinate region for building level information"""
        try:
            import pyautogui

            # Calculate ROI bounds (centered on coordinate)
            left = max(0, x - roi_width // 2)
            top = max(0, y - roi_height // 2)
            width = roi_width
            height = roi_height

            # Take screenshot of the region
            region_screenshot = pyautogui.screenshot(region=(left, top, width, height))

            # Convert to OpenCV format for OCR processing
            region_cv = cv2.cvtColor(np.array(region_screenshot), cv2.COLOR_RGB2BGR)

            # Use existing OCR processing methods on this region
            extracted_text = self._extract_text_from_region(region_cv, building_name)

            if not extracted_text:
                return {
                    "success": False,
                    "error": f"No text detected in region for {building_name}",
                    "region_bounds": {"x": left, "y": top, "width": width, "height": height}
                }

            # Parse building level from extracted text
            parsed_result = self._parse_coordinate_region_text(extracted_text, building_type, building_name)

            if parsed_result['found']:
                # Update building state
                building_data = {
                    "current_level": parsed_result['current_level'],
                    "max_level": parsed_result['max_level'],
                    "is_maxed": parsed_result['is_maxed'],
                    "last_updated": datetime.now().isoformat(),
                    "detection_method": "coordinate_ocr",
                    "coordinate_region": {"x": left, "y": top, "width": width, "height": height}
                }

                self.building_states[building_type] = building_data
                self._auto_save_if_enabled()

                return {
                    "success": True,
                    "building_data": building_data,
                    "extracted_text": extracted_text
                }
            else:
                return {
                    "success": False,
                    "error": f"Could not parse level information for {building_name}",
                    "extracted_text": extracted_text
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Region scanning error: {e}",
                "building_name": building_name
            }

    def _extract_text_from_region(self, region_image, building_name):
        """Extract text from a building coordinate region using enhanced OCR for numbers"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(region_image, cv2.COLOR_BGR2GRAY)

            # Enhanced scaling for better number recognition
            scale_factor = self.config.get("ocr_scale_factor", 3.0)  # Use higher scaling
            height, width = gray.shape
            scaled_gray = cv2.resize(gray, (int(width * scale_factor), int(height * scale_factor)))

            # Try multiple OCR configurations for best results
            ocr_configs = [
                # Configuration 1: Numbers and building text (comprehensive)
                {
                    'config': r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/.: ',
                    'preprocess': 'adaptive'
                },
                # Configuration 2: Number-optimized (for standalone numbers like "29")
                {
                    'config': r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789/',
                    'preprocess': 'binary'
                },
                # Configuration 3: Single line text (for "Warehouse 29" type text)
                {
                    'config': r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/.: ',
                    'preprocess': 'enhanced'
                }
            ]

            best_text = ""
            best_confidence = 0

            for i, config_info in enumerate(ocr_configs):
                try:
                    # Apply different preprocessing based on config
                    if config_info['preprocess'] == 'adaptive':
                        # Standard adaptive thresholding
                        block_size = self.config.get("ocr_adaptive_block_size", 31)
                        c = self.config.get("ocr_adaptive_c", 5)
                        processed = cv2.adaptiveThreshold(scaled_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                        cv2.THRESH_BINARY, block_size, c)
                    elif config_info['preprocess'] == 'binary':
                        # High contrast binary for numbers
                        _, processed = cv2.threshold(scaled_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    elif config_info['preprocess'] == 'enhanced':
                        # Enhanced contrast for text
                        processed = cv2.equalizeHist(scaled_gray)
                        _, processed = cv2.threshold(processed, 127, 255, cv2.THRESH_BINARY)

                    # Extract text with current configuration
                    text = pytesseract.image_to_string(processed, config=config_info['config']).strip()

                    if text and len(text) > len(best_text):
                        # Prefer longer, more complete text
                        best_text = text
                        self.logger.info(f"🔍 Config {i+1} found: '{text}' for {building_name}")

                except Exception as e:
                    self.logger.warning(f"OCR config {i+1} failed for {building_name}: {e}")
                    continue

            # If no good text found, try one more pass with very aggressive number detection
            if not best_text or not any(c.isdigit() for c in best_text):
                try:
                    # Final attempt: Focus purely on digits with maximum scaling
                    mega_scaled = cv2.resize(gray, (int(width * 5.0), int(height * 5.0)))
                    _, binary_mega = cv2.threshold(mega_scaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                    # Apply morphological operations to clean up numbers
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                    binary_mega = cv2.morphologyEx(binary_mega, cv2.MORPH_CLOSE, kernel)

                    digits_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
                    fallback_text = pytesseract.image_to_string(binary_mega, config=digits_config).strip()

                    if fallback_text and any(c.isdigit() for c in fallback_text):
                        best_text = fallback_text
                        self.logger.info(f"🔍 Fallback digit extraction found: '{fallback_text}' for {building_name}")

                except Exception as e:
                    self.logger.warning(f"Fallback OCR failed for {building_name}: {e}")

            # LLM-Enhanced OCR Correction: Try to fix garbled text with AI
            if self.llm_advisor and best_text:
                # Calculate rough confidence based on text quality
                raw_confidence = self._estimate_ocr_confidence(best_text)

                if raw_confidence < 0.7:  # Low confidence, try LLM correction
                    try:
                        corrected_text, new_confidence = self.llm_advisor.correct_ocr_text(
                            best_text,
                            f"building detection for {building_name}",
                            raw_confidence
                        )

                        if corrected_text != best_text and corrected_text.strip():
                            self.logger.info(f"🤖 LLM OCR correction: '{best_text}' → '{corrected_text}' "
                                           f"(confidence: {raw_confidence:.2f} → {new_confidence:.2f})")
                            best_text = corrected_text

                    except Exception as e:
                        self.logger.warning(f"LLM OCR correction failed for {building_name}: {e}")

            self.logger.info(f"🔍 Final extracted text for {building_name}: '{best_text}'")
            return best_text

        except Exception as e:
            self.logger.error(f"❌ Text extraction error for {building_name}: {e}")
            return ""

    def _estimate_ocr_confidence(self, text):
        """
        Estimate OCR confidence based on text characteristics.
        Used to determine when LLM correction is needed.

        Returns confidence between 0.0 and 1.0
        """
        if not text or not text.strip():
            return 0.0

        confidence = 0.8  # Base confidence

        # Penalize for suspicious characters that indicate OCR errors
        suspicious_chars = ['□', '■', '▫', '▪', '○', '●', '◦', '•', '@', '#', '$', '%', '^', '&', '*']
        for char in suspicious_chars:
            if char in text:
                confidence -= 0.2

        # Penalize for mixed case in weird patterns (OCR often gets this wrong)
        if any(c.isupper() for c in text) and any(c.islower() for c in text):
            # Check for unnatural mixed case like "ToWer" instead of "Tower"
            word_chars = ''.join(c for c in text if c.isalpha())
            if word_chars and not (word_chars.istitle() or word_chars.isupper() or word_chars.islower()):
                confidence -= 0.15

        # Boost confidence for clean patterns
        if any(pattern in text.lower() for pattern in ['lv.', 'level', 'warehouse', 'tower', 'farm']):
            confidence += 0.1

        # Boost confidence for clean numbers
        if any(c.isdigit() for c in text) and '/' in text:
            # Looks like "Level 25/30" format
            confidence += 0.1

        # Penalize for very short garbled text
        if len(text.strip()) < 3:
            confidence -= 0.3

        # Penalize for too many special characters
        special_ratio = sum(1 for c in text if not c.isalnum() and c not in ' ./') / max(1, len(text))
        if special_ratio > 0.3:
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def validate_ocr_results(self, full_screen_result, coordinate_result, building_type):
        """Cross-validate OCR results from different scanning methods"""
        validation_result = {
            "recommended_method": "coordinate",
            "recommended_result": coordinate_result,
            "confidence_boost": 0,
            "validation_notes": []
        }

        try:
            # If coordinate method failed, fall back to full-screen
            if not coordinate_result.get("success", False):
                validation_result.update({
                    "recommended_method": "full_screen",
                    "recommended_result": full_screen_result,
                    "validation_notes": ["Coordinate method failed, using full-screen as fallback"]
                })
                return validation_result

            # If full-screen method failed, use coordinate method
            if not full_screen_result.get("success", False):
                validation_result["validation_notes"].append("Full-screen method failed, coordinate method used")
                validation_result["confidence_boost"] = 0.1
                return validation_result

            # Both methods succeeded - compare results
            coord_buildings = coordinate_result.get("detected_buildings", {})
            fullscreen_buildings = full_screen_result.get("detected_buildings", {})

            # Check if both methods detected the same building
            if building_type in coord_buildings and building_type in fullscreen_buildings:
                coord_level = coord_buildings[building_type]["current_level"]
                fullscreen_level = fullscreen_buildings[building_type]["current_level"]

                if coord_level == fullscreen_level:
                    # Perfect match - high confidence
                    validation_result["confidence_boost"] = 0.2
                    validation_result["validation_notes"].append(
                        f"Both methods agree: Level {coord_level} (high confidence)"
                    )
                else:
                    # Disagreement - analyze which is more likely correct
                    building_max_level = self.building_registry.get(building_type, {}).get("max_level", 25)

                    # Coordinate method is generally more reliable due to precise targeting
                    if 1 <= coord_level <= building_max_level:
                        validation_result["validation_notes"].append(
                            f"Methods disagree: Coordinate={coord_level}, Full-screen={fullscreen_level}. "
                            f"Using coordinate method (more precise targeting)"
                        )
                        validation_result["confidence_boost"] = 0.05
                    else:
                        # Coordinate result seems invalid, use full-screen
                        validation_result.update({
                            "recommended_method": "full_screen",
                            "recommended_result": full_screen_result,
                            "validation_notes": [
                                f"Coordinate method gave invalid level {coord_level}, "
                                f"using full-screen result {fullscreen_level}"
                            ]
                        })

            elif building_type in coord_buildings:
                # Only coordinate method found the building
                validation_result["validation_notes"].append(
                    "Only coordinate method detected building (precise targeting advantage)"
                )
                validation_result["confidence_boost"] = 0.15

            elif building_type in fullscreen_buildings:
                # Only full-screen method found the building
                validation_result.update({
                    "recommended_method": "full_screen",
                    "recommended_result": full_screen_result,
                    "validation_notes": [
                        "Only full-screen method detected building, coordinate may need recalibration"
                    ]
                })

            # Additional validation based on common OCR error patterns
            if validation_result["recommended_method"] == "coordinate":
                coord_data = coord_buildings.get(building_type, {})
                level = coord_data.get("current_level", 0)

                # Check for common misreading patterns
                if level == 15 or level == 16:  # Potential popup contamination
                    validation_result["validation_notes"].append(
                        "⚠️ Detected level 15/16 - verify this isn't from upgrade popup"
                    )
                    validation_result["confidence_boost"] -= 0.1

                # Boost confidence for levels that clearly aren't from popups
                if level > 20 and level <= building_max_level:
                    validation_result["confidence_boost"] += 0.1
                    validation_result["validation_notes"].append(
                        f"High building level {level} suggests clean detection (not popup text)"
                    )

        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            validation_result["validation_notes"].append(f"Validation error: {e}")

        return validation_result

    def scan_buildings_enhanced(self, screenshot_or_window, window_title=None):
        """Enhanced building scanning with improved accuracy and validation"""
        enhanced_result = {
            "success": False,
            "detected_buildings": {},
            "total_detected": 0,
            "method_used": "enhanced",
            "accuracy_improvements": [],
            "validation_results": {}
        }

        try:
            # Determine if we have coordinate-based scanning available
            has_coordinates = (self.coordinate_based_scanning and
                             self.coordinate_logger and
                             len(self.coordinate_logger.coordinates) > 0)

            coordinate_result = None
            fullscreen_result = None

            # Try coordinate-based scanning if available
            if has_coordinates and window_title:
                try:
                    self.logger.info("🎯 Attempting coordinate-based scanning...")
                    coordinate_result = self.scan_buildings_with_coordinates(window_title)
                    if coordinate_result.get("success"):
                        enhanced_result["accuracy_improvements"].append("coordinate_targeting")
                        self.logger.info(f"✅ Coordinate scan found {coordinate_result['total_detected']} buildings")
                except Exception as e:
                    self.logger.warning(f"Coordinate scanning failed: {e}")

            # Try full-screen OCR scanning
            try:
                self.logger.info("🖼️ Attempting full-screen OCR scanning...")
                fullscreen_result = self.scan_buildings_with_ocr(screenshot_or_window)
                if fullscreen_result.get("success"):
                    enhanced_result["accuracy_improvements"].append("popup_filtering")
                    self.logger.info(f"✅ Full-screen scan found {fullscreen_result['total_detected']} buildings")
            except Exception as e:
                self.logger.warning(f"Full-screen scanning failed: {e}")

            # Cross-validate results if we have both
            if coordinate_result and fullscreen_result:
                enhanced_result["accuracy_improvements"].append("cross_validation")

                # Validate each building type found
                all_building_types = set()
                if coordinate_result.get("detected_buildings"):
                    all_building_types.update(coordinate_result["detected_buildings"].keys())
                if fullscreen_result.get("detected_buildings"):
                    all_building_types.update(fullscreen_result["detected_buildings"].keys())

                for building_type in all_building_types:
                    validation = self.validate_ocr_results(fullscreen_result, coordinate_result, building_type)
                    enhanced_result["validation_results"][building_type] = validation

                    # Use the recommended result
                    if validation["recommended_method"] == "coordinate":
                        if building_type in coordinate_result.get("detected_buildings", {}):
                            building_data = coordinate_result["detected_buildings"][building_type].copy()
                            building_data["confidence"] = min(1.0, building_data.get("confidence", 0.8) +
                                                            validation["confidence_boost"])
                            building_data["validation_notes"] = validation["validation_notes"]
                            enhanced_result["detected_buildings"][building_type] = building_data
                    else:
                        if building_type in fullscreen_result.get("detected_buildings", {}):
                            building_data = fullscreen_result["detected_buildings"][building_type].copy()
                            building_data["validation_notes"] = validation["validation_notes"]
                            enhanced_result["detected_buildings"][building_type] = building_data

                    self.logger.info(f"🔍 {building_type}: Using {validation['recommended_method']} method - {validation['validation_notes']}")

            # Use coordinate result only
            elif coordinate_result and coordinate_result.get("success"):
                enhanced_result["detected_buildings"] = coordinate_result["detected_buildings"]
                enhanced_result["method_used"] = "coordinate_only"
                self.logger.info("✅ Using coordinate-only results")

            # Use full-screen result only
            elif fullscreen_result and fullscreen_result.get("success"):
                enhanced_result["detected_buildings"] = fullscreen_result["detected_buildings"]
                enhanced_result["method_used"] = "fullscreen_only"
                self.logger.info("✅ Using full-screen only results")

            # No successful scans
            else:
                error_msg = "No scanning method succeeded"
                self.logger.error(f"❌ {error_msg}")
                return {**enhanced_result, "error": error_msg}

            # Update final results
            enhanced_result["total_detected"] = len(enhanced_result["detected_buildings"])
            enhanced_result["success"] = enhanced_result["total_detected"] > 0

            # Add accuracy summary
            if enhanced_result["success"]:
                accuracy_summary = []
                if "coordinate_targeting" in enhanced_result["accuracy_improvements"]:
                    accuracy_summary.append("Precise coordinate targeting used")
                if "popup_filtering" in enhanced_result["accuracy_improvements"]:
                    accuracy_summary.append("Popup text filtering applied")
                if "cross_validation" in enhanced_result["accuracy_improvements"]:
                    accuracy_summary.append("Cross-method validation performed")

                enhanced_result["accuracy_summary"] = "; ".join(accuracy_summary)
                self.logger.info(f"🎯 Enhanced scan complete: {enhanced_result['accuracy_summary']}")

            return enhanced_result

        except Exception as e:
            error_msg = f"Enhanced scanning failed: {e}"
            self.logger.error(error_msg)
            return {**enhanced_result, "error": error_msg}

    def _parse_coordinate_region_text(self, text, building_type, building_name):
        """Parse building level information from coordinate region OCR text"""
        try:
            # Use existing building parsing logic but adapted for coordinate regions
            text_lower = text.lower()

            # Check if this looks like building text
            building_keywords = ['hut', 'kitchen', 'tower', 'farm', 'warehouse', 'barracks', 'wall', 'mine', 'mill', 'quarry', 'forge', 'academy']
            has_building_keyword = any(keyword in text_lower for keyword in building_keywords)

            if not has_building_keyword and building_type not in text_lower:
                return {"found": False, "reason": "No building keywords found in region text"}

            # Look for level patterns
            import re
            level_patterns = [
                r'lv\.?\s*(\d+)\s*/\s*(\d+)',  # Lv.12/25, Lv 12/25
                r'level:?\s*(\d+)\s*/\s*(\d+)',  # Level: 12/25, Level 12/25
                r'(\d+)\s*/\s*(\d+)',  # 12/25
            ]

            max_level = self.building_registry.get(building_type, {}).get("max_level", 25)

            for pattern in level_patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    current_level = int(match.group(1))
                    detected_max = int(match.group(2))

                    # Validate detected levels
                    if 1 <= current_level <= max_level and detected_max == max_level:
                        return {
                            "found": True,
                            "current_level": current_level,
                            "max_level": max_level,
                            "is_maxed": current_level == max_level,
                            "confidence": 0.9,
                            "matched_pattern": pattern,
                            "matched_text": match.group(0)
                        }

            # Check for maxed indicators
            maxed_indicators = ['max', 'maxed', '100%', f'{max_level}/{max_level}']
            for indicator in maxed_indicators:
                if indicator in text_lower:
                    return {
                        "found": True,
                        "current_level": max_level,
                        "max_level": max_level,
                        "is_maxed": True,
                        "confidence": 0.85,
                        "matched_pattern": "maxed_indicator",
                        "matched_text": indicator
                    }

            return {"found": False, "reason": "No valid level pattern found", "text_analyzed": text}

        except Exception as e:
            return {"found": False, "reason": f"Parsing error: {e}"}

    def _is_popup_text(self, text_line):
        """Detect if a line of text is from a popup dialog (like upgrade dialogs)"""
        if not self.config.get("enable_popup_filtering", False):
            return False

        text_lower = text_line.lower().strip()
        popup_keywords = self.config.get("popup_keywords", [])

        # Check for popup keywords
        for keyword in popup_keywords:
            if keyword in text_lower:
                return True

        # Specific patterns that indicate popup/dialog text
        popup_patterns = [
            r'upgrade.*to\s+lv\.?\s*\d+',  # "Upgrade Warehouse to Lv.16"
            r'to\s+lv\.?\s*\d+\s*\(',      # "to Lv.16(15/16)"
            r'\(\d+/\d+\)',                # "(15/16)" - requirement indicators
            r'confirm|cancel|ok',          # Dialog buttons
            r'cost:|requires?:',           # Resource requirements
            r'timer?:\s*\d+',              # Construction timers
            r'insufficient\s+resources?',  # Error messages
        ]

        for pattern in popup_patterns:
            if re.search(pattern, text_lower):
                self.logger.info(f"🚫 Filtering popup text: '{text_line.strip()}'")
                return True

        return False

    def _get_building_confidence_score(self, text_line, building_match, level_match):
        """Calculate confidence score for building detection"""
        confidence = 0.5  # Base confidence

        # Higher confidence for direct building name matches
        building_keywords = ['hut', 'kitchen', 'tower', 'farm', 'warehouse', 'barracks']
        for keyword in building_keywords:
            if keyword in text_line.lower():
                confidence += 0.2
                break

        # Higher confidence for clear level patterns
        if re.search(r'\b\d+/\d+\b', text_line):  # Clear X/Y pattern
            confidence += 0.2

        # Lower confidence for small isolated numbers (might be UI elements)
        if level_match and len(level_match) == 1 and int(level_match) < 5:
            confidence -= 0.1

        # Higher confidence if building name is at start of line
        if text_line.lower().strip().startswith(tuple(building_keywords)):
            confidence += 0.15

        return min(1.0, max(0.0, confidence))

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

                # Skip popup/dialog text that can cause false readings
                if self._is_popup_text(line):
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