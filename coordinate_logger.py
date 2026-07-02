"""
Dark War Survival Bot - Coordinate Logger Module
Captures mouse clicks to log building coordinates for precise OCR scanning

Version: 2.1.0
Features:
- Mouse click capture with pynput
- Window-relative coordinate conversion
- JSON storage format for coordinates
- Building type association
- ROI size configuration
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import logging

# Try to import pynput for mouse capture
try:
    from pynput import mouse
    import pygetwindow as gw
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("WARNING: pynput not available. Install with: pip install pynput")


class CoordinateLogger:
    """Handles mouse click capture and coordinate logging for building detection"""

    def __init__(self, data_dir: str = "building_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Coordinate storage
        self.coordinates_file = self.data_dir / "building_coordinates.json"
        self.coordinates = {}

        # Current logging state
        self.is_logging = False
        self.current_building_type = None
        self.current_building_name = None
        self.target_window = None
        self.window_info = {}

        # Configuration
        self.config = {
            "default_roi_width": 150,
            "default_roi_height": 80,
            "coordinate_version": "1.0",
            "auto_save": True,
            "click_timeout": 30.0,  # seconds
            "coordinate_precision": 1  # decimal places
        }

        # Setup logging
        self.setup_logging()

        # Load existing coordinates
        self.load_coordinates()

        # Mouse listener
        self.mouse_listener = None

        # Callbacks
        self.on_coordinate_logged = None
        self.on_logging_started = None
        self.on_logging_stopped = None

    def setup_logging(self):
        """Setup logging for coordinate logger"""
        log_file = self.data_dir / "coordinate_logger.log"
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_coordinates(self):
        """Load existing coordinates from JSON file"""
        if self.coordinates_file.exists():
            try:
                with open(self.coordinates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.coordinates = data.get("buildings", {})
                self.window_info = data.get("window_info", {})

                self.logger.info(f"Loaded {len(self.coordinates)} building coordinates")

            except Exception as e:
                self.logger.error(f"Failed to load coordinates: {e}")
                self.coordinates = {}
                self.window_info = {}
        else:
            self.coordinates = {}
            self.window_info = {}

    def save_coordinates(self):
        """Save coordinates to JSON file"""
        try:
            data = {
                "version": self.config["coordinate_version"],
                "created": datetime.now().isoformat(),
                "window_info": self.window_info,
                "config": self.config,
                "buildings": self.coordinates
            }

            with open(self.coordinates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info("Coordinates saved successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save coordinates: {e}")
            return False

    def set_target_window(self, window_title: str) -> bool:
        """Set the target window for coordinate capture"""
        try:
            if not PYNPUT_AVAILABLE:
                return False

            # Find the window
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                self.logger.error(f"Window '{window_title}' not found")
                return False

            self.target_window = windows[0]

            # Store window information
            self.window_info = {
                "title": self.target_window.title,
                "width": self.target_window.width,
                "height": self.target_window.height,
                "left": self.target_window.left,
                "top": self.target_window.top,
                "last_updated": datetime.now().isoformat()
            }

            self.logger.info(f"Target window set: {window_title} ({self.target_window.width}x{self.target_window.height})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set target window: {e}")
            return False

    def start_logging_building(self, building_type: str, building_name: str) -> bool:
        """Start logging coordinates for a specific building"""
        if not PYNPUT_AVAILABLE:
            self.logger.error("Cannot start logging: pynput not available")
            return False

        if not self.target_window:
            self.logger.error("Cannot start logging: no target window set")
            return False

        if self.is_logging:
            self.logger.warning("Already logging - stop current logging first")
            return False

        # Set current building
        self.current_building_type = building_type
        self.current_building_name = building_name
        self.is_logging = True

        # Start mouse listener
        try:
            self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
            self.mouse_listener.start()

            self.logger.info(f"Started logging coordinates for {building_name} ({building_type})")

            if self.on_logging_started:
                self.on_logging_started(building_type, building_name)

            return True

        except Exception as e:
            self.logger.error(f"Failed to start mouse listener: {e}")
            self.is_logging = False
            return False

    def stop_logging(self):
        """Stop coordinate logging"""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None

        self.is_logging = False
        self.current_building_type = None
        self.current_building_name = None

        self.logger.info("Stopped coordinate logging")

        if self.on_logging_stopped:
            self.on_logging_stopped()

    def _on_mouse_click(self, x: int, y: int, button, pressed: bool):
        """Handle mouse click events"""
        if not pressed or not self.is_logging:
            return

        if button != mouse.Button.left:
            return

        try:
            # Check if click is within target window
            if not self._is_click_in_target_window(x, y):
                return

            # Convert to window-relative coordinates
            relative_x, relative_y = self._convert_to_relative(x, y)

            # Create coordinate entry
            coordinate_id = f"{self.current_building_type}_{len([k for k in self.coordinates.keys() if k.startswith(self.current_building_type)]) + 1}"

            coordinate_entry = {
                "building_name": self.current_building_name,
                "building_type": self.current_building_type,
                "absolute": {
                    "x": round(x, self.config["coordinate_precision"]),
                    "y": round(y, self.config["coordinate_precision"])
                },
                "relative": {
                    "x": round(relative_x, 4),
                    "y": round(relative_y, 4)
                },
                "roi_size": {
                    "width": self.config["default_roi_width"],
                    "height": self.config["default_roi_height"]
                },
                "window_info": {
                    "title": self.window_info["title"],
                    "width": self.window_info["width"],
                    "height": self.window_info["height"]
                },
                "timestamp": datetime.now().isoformat(),
                "confidence": 1.0,
                "manual": True,
                "verified": False
            }

            # Store coordinate
            self.coordinates[coordinate_id] = coordinate_entry

            # Auto-save if enabled
            if self.config["auto_save"]:
                self.save_coordinates()

            self.logger.info(f"Logged coordinate for {self.current_building_name} at ({x}, {y}) -> ({relative_x:.3f}, {relative_y:.3f})")

            # Notify callback
            if self.on_coordinate_logged:
                self.on_coordinate_logged(coordinate_id, coordinate_entry)

            # Stop logging (one click per building)
            self.stop_logging()

        except Exception as e:
            self.logger.error(f"Error processing mouse click: {e}")

    def _is_click_in_target_window(self, x: int, y: int) -> bool:
        """Check if click coordinates are within the target window"""
        if not self.target_window:
            return False

        try:
            # Update window position (in case it moved)
            window_left = self.target_window.left
            window_top = self.target_window.top
            window_right = window_left + self.target_window.width
            window_bottom = window_top + self.target_window.height

            return (window_left <= x <= window_right and
                   window_top <= y <= window_bottom)

        except Exception:
            return False

    def _convert_to_relative(self, abs_x: int, abs_y: int) -> Tuple[float, float]:
        """Convert absolute coordinates to window-relative coordinates"""
        if not self.target_window:
            return 0.0, 0.0

        # Calculate relative position within window
        rel_x = (abs_x - self.target_window.left) / self.target_window.width
        rel_y = (abs_y - self.target_window.top) / self.target_window.height

        # Clamp to [0, 1] range
        rel_x = max(0.0, min(1.0, rel_x))
        rel_y = max(0.0, min(1.0, rel_y))

        return rel_x, rel_y

    def convert_relative_to_absolute(self, rel_x: float, rel_y: float, window_width: int, window_height: int) -> Tuple[int, int]:
        """Convert relative coordinates back to absolute coordinates for a given window size"""
        abs_x = int(rel_x * window_width)
        abs_y = int(rel_y * window_height)
        return abs_x, abs_y

    def get_coordinates_for_window(self, window_width: int, window_height: int) -> Dict[str, Dict]:
        """Get coordinates adjusted for a specific window size"""
        adjusted_coordinates = {}

        for coord_id, coord_data in self.coordinates.items():
            rel_x = coord_data["relative"]["x"]
            rel_y = coord_data["relative"]["y"]

            abs_x, abs_y = self.convert_relative_to_absolute(rel_x, rel_y, window_width, window_height)

            # Create adjusted coordinate data
            adjusted_coord = coord_data.copy()
            adjusted_coord["absolute"]["x"] = abs_x
            adjusted_coord["absolute"]["y"] = abs_y

            adjusted_coordinates[coord_id] = adjusted_coord

        return adjusted_coordinates

    def delete_coordinate(self, coordinate_id: str) -> bool:
        """Delete a coordinate entry"""
        if coordinate_id in self.coordinates:
            del self.coordinates[coordinate_id]

            if self.config["auto_save"]:
                self.save_coordinates()

            self.logger.info(f"Deleted coordinate {coordinate_id}")
            return True
        return False

    def update_coordinate_name(self, coordinate_id: str, new_name: str) -> bool:
        """Update the name of a coordinate entry"""
        if coordinate_id in self.coordinates:
            self.coordinates[coordinate_id]["building_name"] = new_name

            if self.config["auto_save"]:
                self.save_coordinates()

            self.logger.info(f"Updated coordinate {coordinate_id} name to {new_name}")
            return True
        return False

    def get_coordinate_statistics(self) -> Dict[str, Any]:
        """Get statistics about logged coordinates"""
        if not self.coordinates:
            return {
                "total_coordinates": 0,
                "building_types": {},
                "window_coverage": {},
                "last_updated": None
            }

        building_types = {}
        for coord_data in self.coordinates.values():
            building_type = coord_data["building_type"]
            building_types[building_type] = building_types.get(building_type, 0) + 1

        # Calculate window coverage
        if self.coordinates:
            x_coords = [coord["relative"]["x"] for coord in self.coordinates.values()]
            y_coords = [coord["relative"]["y"] for coord in self.coordinates.values()]

            coverage = {
                "x_range": f"{min(x_coords):.2f} - {max(x_coords):.2f}",
                "y_range": f"{min(y_coords):.2f} - {max(y_coords):.2f}",
                "spread_x": max(x_coords) - min(x_coords),
                "spread_y": max(y_coords) - min(y_coords)
            }
        else:
            coverage = {}

        timestamps = [coord["timestamp"] for coord in self.coordinates.values()]
        last_updated = max(timestamps) if timestamps else None

        return {
            "total_coordinates": len(self.coordinates),
            "building_types": building_types,
            "window_coverage": coverage,
            "last_updated": last_updated,
            "available": PYNPUT_AVAILABLE
        }


# Quick test function
def test_coordinate_logger():
    """Test the coordinate logger functionality"""
    logger = CoordinateLogger()

    print("Coordinate Logger Test")
    print("=" * 50)
    print(f"Pynput available: {PYNPUT_AVAILABLE}")
    print(f"Coordinates loaded: {len(logger.coordinates)}")

    # Show statistics
    stats = logger.get_coordinate_statistics()
    print("Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nTest completed!")


if __name__ == "__main__":
    test_coordinate_logger()