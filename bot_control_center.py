"""
Dark War Survival Bot Control Center v2.0.0
Unified interface for BlueStacks and Phone automation with advanced controls

Version 2.0.0 Features:
- ESC key emergency stop with immediate response
- Smart window management (skips minimized/collapsed windows)
- Action-aware logging with result detection
- Enhanced target window selection
- Version control and backward compatibility
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import pygetwindow as gw
import pyautogui
from datetime import datetime
import json
import os
import sys
import traceback
from pathlib import Path

# Import the smart building manager
try:
    from building_manager import BuildingManager
    BUILDING_MANAGER_AVAILABLE = True
except ImportError:
    BUILDING_MANAGER_AVAILABLE = False
    print("WARNING: Building manager not available. Smart building features disabled.")

# Import the coordinate logger for precise building detection
try:
    from coordinate_logger import CoordinateLogger
    COORDINATE_LOGGER_AVAILABLE = True
except ImportError:
    COORDINATE_LOGGER_AVAILABLE = False
    print("WARNING: Coordinate logger not available. Coordinate-based building detection disabled.")

# OCR libraries for building detection
try:
    import cv2
    import numpy as np
    OCR_IMPORTS_AVAILABLE = True
except ImportError:
    OCR_IMPORTS_AVAILABLE = False

# Add keyboard library for ESC emergency stop
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("WARNING: keyboard library not available. ESC emergency stop disabled.")
    print("Install with: pip install keyboard")

# Version information
__version__ = "2.3.0"
__version_info__ = {
    "major": 2,
    "minor": 3,
    "patch": 0,
    "release_date": "2025-11-16",
    "changes": [
        "Enhanced OCR accuracy with popup text filtering",
        "Added multiple OCR configuration strategies for better number detection",
        "Implemented cross-validation between full-screen and coordinate methods",
        "Added Enhanced Scan button with automatic method selection",
        "Improved warehouse level detection (fixes 15/16 vs 29 issue)",
        "Enhanced text extraction with morphological image processing",
        "Added validation system to detect popup contamination",
        "Preserved all v2.2.0 coordinate features and v2.1.0 OCR features"
    ],
    "v2_2_changes": [
        "Added Coordinate Setup tab for precise building detection",
        "Implemented mouse click coordinate logging system with pynput",
        "Created comprehensive building coordinate management interface",
        "Added game view mode awareness (Shelter vs World View)",
        "Integrated coordinate-based building targeting system",
        "Enhanced building detection accuracy with coordinate logging",
        "Added coordinate validation and testing functionality",
        "Preserved all v2.1.0 OCR features and v2.0.0 core functionality"
    ],
    "v2_1_changes": [
        "Updated click speeds to phone-friendly range (2-20 seconds)",
        "Updated cycle speeds to realistic range (5-60 seconds)",
        "Added smart building management system with OCR detection",
        "Created Building Management tab for manual building control",
        "Implemented automatic building level detection using pytesseract",
        "Added building skip logic to avoid maxed buildings",
        "Enhanced statistics tracking for buildings and time saved",
        "Preserved all v2.0.0 features (ESC stop, error logging, smart windows)"
    ],
    "v2_0_changes": [
        "Added ESC key emergency stop with immediate response",
        "Implemented smart window management (skip minimized windows)",
        "Enhanced action-aware logging with result detection",
        "Fixed target window selection (excludes bot control center)",
        "Added version control and config migration system",
        "Improved emergency stop response time (<1 second)",
        "Enhanced test click feedback with target identification"
    ]
}

class BotControlCenter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Dark War Survival Bot v{__version__} - Control Center")
        self.root.geometry("900x700")  # Slightly larger for new features

        # Bot state
        self.bot_running = False
        self.bot_thread = None
        self.target_window = None
        self.automation_mode = "phone"  # "phone" or "bluestacks"
        self.emergency_stop_triggered = False

        # Performance settings
        self.click_speed = 0.1  # Delay between clicks
        self.cycle_speed = 1.0  # Delay between cycles
        self.actions_per_cycle = 5

        # Enhanced statistics
        self.stats = {
            "cycles": 0,
            "clicks": 0,
            "start_time": None,
            "errors": 0,
            "actions_performed": {},  # Track specific actions
            "skipped_windows": 0,
            "emergency_stops": 0
        }

        # Action-aware logging system
        self.action_history = []
        self.current_action = "Idle"

        # Comprehensive Error Logging System
        self.error_log_dir = Path("error_logs")
        self.error_log_dir.mkdir(exist_ok=True)
        self.error_log_file = self.error_log_dir / f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.error_count = 0
        self.error_history = []

        # Smart Building Management System v2.1.0
        if BUILDING_MANAGER_AVAILABLE:
            self.building_manager = BuildingManager()
            self.building_management_enabled = True
            self.ocr_status = self.building_manager.get_ocr_status()
        else:
            self.building_manager = None
            self.building_management_enabled = False
            self.ocr_status = {}

        # Coordinate Logger System for precise building detection
        if COORDINATE_LOGGER_AVAILABLE:
            self.coordinate_logger = CoordinateLogger()
            self.coordinate_setup_enabled = True
            # Set callbacks for coordinate logging feedback
            self.coordinate_logger.on_coordinate_logged = self.on_coordinate_logged
            self.coordinate_logger.on_logging_started = self.on_coordinate_logging_started
            self.coordinate_logger.on_logging_stopped = self.on_coordinate_logging_stopped
        else:
            self.coordinate_logger = None
            self.coordinate_setup_enabled = False

        # Window management
        self.excluded_window_titles = [
            "Dark War Survival Bot Control Center",
            "Bot Control Center",
            "Control Center",
            "Python",
            "Command Prompt",
            "PowerShell"
        ]

        # Load or migrate configuration
        self.load_or_migrate_config()

        self.setup_ui()
        self.setup_emergency_stop()
        self.refresh_windows()

        # Show version info on startup
        self.log(f"Bot Control Center v{__version__} initialized")
        self.log("New features: ESC emergency stop, smart window management, enhanced logging")

    def load_or_migrate_config(self):
        """Load configuration with automatic migration from v1.x"""
        config_path = "bot_config.json"

        if not os.path.exists(config_path):
            self.log("No configuration found, using defaults")
            self.create_default_config()
            return

        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            # Check if this is an old v1.x config
            config_version = config.get("version", "1.0.0")

            if config_version.startswith("1."):
                self.log(f"Migrating configuration from v{config_version} to v{__version__}")
                config = self.migrate_v1_to_v2(config)
                self.save_config(config)
                self.log("Configuration migrated successfully!")

            # Apply configuration
            self.apply_config(config)

        except Exception as e:
            self.log(f"Configuration migration failed: {e}")
            self.log("Using default settings")
            self.create_default_config()

    def create_default_config(self):
        """Create default v2.0 configuration"""
        default_config = {
            "version": __version__,
            "window_title": "BlueStacks App Player",
            "phone_window_title": "Dark War",
            "action_delay_min": 0.1,
            "action_delay_max": 0.5,
            "template_threshold": 0.8,
            "emergency_stop_keys": ["esc"],
            "enable_detailed_logging": True,
            "skip_minimized_windows": True,
            "phone_mode": {
                "click_areas": {
                    "mail": True,
                    "heroes": True,
                    "world": True,
                    "events": True,
                    "vip": True,
                    "center": True
                }
            }
        }

        self.save_config(default_config)
        self.apply_config(default_config)

    def migrate_v1_to_v2(self, old_config):
        """Migrate v1.x config to v2.0 format"""
        new_config = {
            "version": __version__,
            "window_title": old_config.get("window_title", "BlueStacks App Player"),
            "phone_window_title": old_config.get("window_title", "Dark War"),
            "action_delay_min": old_config.get("action_delay_min", 0.1),
            "action_delay_max": old_config.get("action_delay_max", 0.5),
            "template_threshold": old_config.get("template_threshold", 0.8),
            "emergency_stop_keys": ["esc"],  # New feature
            "enable_detailed_logging": True,  # New feature
            "skip_minimized_windows": True,  # New feature
            "phone_mode": {
                "click_areas": {
                    "mail": old_config.get("gather_resources", True),
                    "heroes": old_config.get("upgrade_buildings", True),
                    "world": old_config.get("train_troops", True),
                    "events": True,
                    "vip": True,
                    "center": True
                }
            }
        }

        return new_config

    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open("bot_config.json", "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save configuration: {e}")

    def apply_config(self, config):
        """Apply configuration settings"""
        self.config = config
        self.click_speed = config.get("action_delay_min", 0.1)
        self.cycle_speed = config.get("action_delay_max", 0.5)

    def setup_emergency_stop(self):
        """Setup ESC key emergency stop monitoring"""
        if not KEYBOARD_AVAILABLE:
            self.log("WARNING: Keyboard library not available - ESC emergency stop disabled")
            return

        # Start emergency stop monitoring thread
        self.emergency_thread = threading.Thread(target=self.monitor_emergency_keys, daemon=True)
        self.emergency_thread.start()
        self.log("ESC emergency stop monitoring active")

    def monitor_emergency_keys(self):
        """Monitor for ESC key press (runs in background thread)"""
        if not KEYBOARD_AVAILABLE:
            return

        while True:
            try:
                # Check for ESC key every 50ms for immediate response
                if keyboard.is_pressed('esc'):
                    if self.bot_running:
                        self.emergency_stop_triggered = True
                        self.bot_running = False
                        self.stats["emergency_stops"] += 1

                        # Log emergency stop
                        self.root.after(0, lambda: self.log("🚨 EMERGENCY STOP - ESC key pressed!"))
                        self.root.after(0, lambda: self.log("Bot stopped immediately"))

                        # Visual feedback
                        self.root.after(0, self.show_emergency_stop_feedback)

                        # Wait for key release to avoid multiple triggers
                        while keyboard.is_pressed('esc'):
                            time.sleep(0.1)

                time.sleep(0.05)  # Check every 50ms for fast response
            except Exception as e:
                # Ignore errors in emergency monitoring to keep it running
                time.sleep(1)

    def show_emergency_stop_feedback(self):
        """Show visual feedback for emergency stop"""
        try:
            # Flash the window title
            original_title = self.root.title()
            self.root.title("🚨 EMERGENCY STOP ACTIVATED 🚨")

            # Restore title after 2 seconds
            self.root.after(2000, lambda: self.root.title(original_title))

            # Show popup (optional - can be disabled if annoying)
            # messagebox.showinfo("Emergency Stop", "Bot stopped by ESC key")

        except Exception:
            pass  # Ignore errors in UI feedback

    def is_window_usable(self, window):
        """Enhanced window state detection - skips unusable windows"""
        if not window:
            return False, "Window not found"

        try:
            # Check if window exists
            if not hasattr(window, 'title') or not window.title:
                return False, "Window has no title"

            # Check if minimized
            if hasattr(window, 'isMinimized') and window.isMinimized:
                return False, f"Window is minimized: {window.title}"

            # Check if window is too small (collapsed)
            min_width, min_height = 300, 400
            if window.width < min_width or window.height < min_height:
                return False, f"Window too small: {window.title} ({window.width}x{window.height})"

            # Check if visible
            if hasattr(window, 'visible') and not window.visible:
                return False, f"Window not visible: {window.title}"

            # Check if window is the bot control center itself
            for excluded in self.excluded_window_titles:
                if excluded.lower() in window.title.lower():
                    return False, f"Excluded window: {window.title}"

            return True, f"Window is usable: {window.title}"

        except Exception as e:
            return False, f"Error checking window state: {e}"

    def get_click_area_info(self, x, y, window):
        """Determine what we're clicking and provide context"""
        if not window:
            return "Unknown area", "No window context"

        # Get window dimensions for relative positioning
        w, h = window.width, window.height
        rel_x = (x - window.left) / w
        rel_y = (y - window.top) / h

        # Phone mode click areas with enhanced detection
        if self.automation_mode == "phone":
            # Mail/Rewards (right side, middle)
            if rel_x > 0.8 and 0.3 < rel_y < 0.7:
                return "Mail/Rewards icon", "Collecting messages and rewards"

            # Heroes (bottom left)
            elif rel_x < 0.2 and rel_y > 0.8:
                return "Heroes button", "Opening character management"

            # World (bottom right)
            elif rel_x > 0.8 and rel_y > 0.8:
                return "World features", "Accessing world map and exploration"

            # Events (right side, upper)
            elif rel_x > 0.8 and rel_y < 0.3:
                return "Events panel", "Checking limited-time activities"

            # VIP (left side, upper)
            elif rel_x < 0.2 and rel_y < 0.3:
                return "VIP benefits", "Accessing premium features"

            # Center area
            elif 0.3 < rel_x < 0.7 and 0.3 < rel_y < 0.7:
                return "Base center", "Interacting with main buildings"

            else:
                return "General area", "Unspecified interaction"

        else:  # BlueStacks mode
            return "Game interface", "Template-based interaction"

    def log_action(self, action_name, x, y, result_text="", action_type="CLICK"):
        """Enhanced logging with action awareness and results"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Determine click context
        area_name, context = self.get_click_area_info(x, y, self.target_window)

        # Create detailed log message
        log_message = f"[{action_type}] {area_name} at ({x}, {y})"
        if result_text:
            log_message += f" - {result_text}"

        self.log(log_message)

        # Track action statistics
        if area_name in self.stats["actions_performed"]:
            self.stats["actions_performed"][area_name] += 1
        else:
            self.stats["actions_performed"][area_name] = 1

        # Add to detailed history
        action_record = {
            "timestamp": timestamp,
            "action_type": action_type,
            "area_name": area_name,
            "coordinates": (x, y),
            "context": context,
            "result": result_text,
            "cycle": self.stats["cycles"],
            "window": self.target_window.title if self.target_window else "Unknown"
        }

        self.action_history.append(action_record)

        # Keep only last 1000 actions to prevent memory bloat
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-1000:]

    def detect_action_result(self, area_name):
        """Simulate result detection - in reality this would use computer vision"""
        # This is a placeholder for result detection
        # In a real implementation, you would:
        # 1. Take a screenshot before and after clicking
        # 2. Use template matching to detect changes
        # 3. Analyze color changes or new UI elements
        # 4. Return meaningful results

        result_messages = {
            "Mail/Rewards icon": "found 2 rewards to collect",
            "Heroes button": "opened character menu",
            "World features": "accessed world map",
            "Events panel": "checking event progress",
            "VIP benefits": "accessed VIP features",
            "Base center": "interacting with buildings",
            "General area": "performed general action"
        }

        return result_messages.get(area_name, "action completed")

    def setup_ui(self):
        """Create the control interface"""
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Control Tab
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Bot Control")
        self.setup_control_tab(control_frame)

        # Settings Tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        self.setup_settings_tab(settings_frame)

        # Log Tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Activity Log")
        self.setup_log_tab(log_frame)

        # Building Management Tab (v2.1.0)
        if self.building_management_enabled:
            building_frame = ttk.Frame(notebook)
            notebook.add(building_frame, text="Building Management")
            self.setup_building_management_tab(building_frame)

        # Coordinate Setup Tab (v2.2.0)
        if self.coordinate_setup_enabled:
            coordinate_frame = ttk.Frame(notebook)
            notebook.add(coordinate_frame, text="Coordinate Setup")
            self.setup_coordinate_setup_tab(coordinate_frame)

    def setup_control_tab(self, parent):
        """Setup the main control tab"""
        # Mode Selection
        mode_frame = ttk.LabelFrame(parent, text="Automation Mode")
        mode_frame.pack(fill="x", padx=5, pady=5)

        self.mode_var = tk.StringVar(value="phone")
        ttk.Radiobutton(mode_frame, text="Phone Mirroring", variable=self.mode_var,
                       value="phone", command=self.mode_changed).pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="BlueStacks", variable=self.mode_var,
                       value="bluestacks", command=self.mode_changed).pack(side="left", padx=10)

        # Window Selection
        window_frame = ttk.LabelFrame(parent, text="Target Window")
        window_frame.pack(fill="x", padx=5, pady=5)

        self.window_var = tk.StringVar()
        self.window_combo = ttk.Combobox(window_frame, textvariable=self.window_var,
                                        width=50, state="readonly")
        self.window_combo.pack(side="left", padx=10, pady=5)

        ttk.Button(window_frame, text="Refresh",
                  command=self.refresh_windows).pack(side="left", padx=5)
        ttk.Button(window_frame, text="Test Click",
                  command=self.test_click).pack(side="left", padx=5)
        ttk.Button(window_frame, text="Error Review",
                  command=self.show_error_review_window).pack(side="left", padx=5)

        # Speed Controls
        speed_frame = ttk.LabelFrame(parent, text="Speed Controls")
        speed_frame.pack(fill="x", padx=5, pady=5)

        # Click Speed (Phone-Friendly Range)
        tk.Label(speed_frame, text="Click Speed:").grid(row=0, column=0, sticky="w", padx=5)
        self.click_speed_var = tk.DoubleVar(value=5.0)
        click_scale = ttk.Scale(speed_frame, from_=2.0, to=20.0, variable=self.click_speed_var,
                               orient="horizontal", length=200)
        click_scale.grid(row=0, column=1, padx=5)
        self.click_speed_label = tk.Label(speed_frame, text="5.0s")
        self.click_speed_label.grid(row=0, column=2, padx=5)
        click_scale.configure(command=self.update_click_speed)

        # Cycle Speed (Realistic Game Pacing)
        tk.Label(speed_frame, text="Cycle Speed:").grid(row=1, column=0, sticky="w", padx=5)
        self.cycle_speed_var = tk.DoubleVar(value=10.0)
        cycle_scale = ttk.Scale(speed_frame, from_=5.0, to=60.0, variable=self.cycle_speed_var,
                               orient="horizontal", length=200)
        cycle_scale.grid(row=1, column=1, padx=5)
        self.cycle_speed_label = tk.Label(speed_frame, text="10.0s")
        self.cycle_speed_label.grid(row=1, column=2, padx=5)
        cycle_scale.configure(command=self.update_cycle_speed)

        # Actions per cycle
        tk.Label(speed_frame, text="Actions/Cycle:").grid(row=2, column=0, sticky="w", padx=5)
        self.actions_var = tk.IntVar(value=5)
        actions_scale = ttk.Scale(speed_frame, from_=1, to=10, variable=self.actions_var,
                                 orient="horizontal", length=200)
        actions_scale.grid(row=2, column=1, padx=5)
        self.actions_label = tk.Label(speed_frame, text="5")
        self.actions_label.grid(row=2, column=2, padx=5)
        actions_scale.configure(command=self.update_actions)

        # Control Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", padx=5, pady=10)

        self.start_button = ttk.Button(button_frame, text="START BOT",
                                      command=self.start_bot, style="Green.TButton")
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(button_frame, text="STOP BOT",
                                     command=self.stop_bot, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        self.emergency_button = ttk.Button(button_frame, text="EMERGENCY STOP",
                                          command=self.emergency_stop)
        self.emergency_button.pack(side="left", padx=5)

        # Status Display
        status_frame = ttk.LabelFrame(parent, text="Status")
        status_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, width=80)
        self.status_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.log("Bot Control Center initialized")
        self.log("Select your target window and click START BOT")

    def setup_settings_tab(self, parent):
        """Setup the settings tab"""
        # Window Management
        wm_frame = ttk.LabelFrame(parent, text="Window Management")
        wm_frame.pack(fill="x", padx=5, pady=5)

        self.focus_window_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(wm_frame, text="Auto-focus target window",
                       variable=self.focus_window_var).pack(anchor="w", padx=10, pady=5)

        self.minimize_others_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(wm_frame, text="Minimize other windows during automation",
                       variable=self.minimize_others_var).pack(anchor="w", padx=10, pady=5)

        # Click Areas for Phone Mode
        phone_frame = ttk.LabelFrame(parent, text="Phone Mode Click Areas")
        phone_frame.pack(fill="x", padx=5, pady=5)

        self.phone_areas = {
            "mail": tk.BooleanVar(value=True),
            "heroes": tk.BooleanVar(value=True),
            "world": tk.BooleanVar(value=True),
            "events": tk.BooleanVar(value=True),
            "vip": tk.BooleanVar(value=True),
            "center": tk.BooleanVar(value=True)
        }

        for area, var in self.phone_areas.items():
            ttk.Checkbutton(phone_frame, text=area.capitalize(),
                           variable=var).pack(anchor="w", padx=10, pady=2)

        # Performance
        perf_frame = ttk.LabelFrame(parent, text="Performance")
        perf_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(perf_frame, text="Close Other Windows",
                  command=self.close_other_windows).pack(side="left", padx=5, pady=5)
        ttk.Button(perf_frame, text="Optimize for Speed",
                  command=self.optimize_speed).pack(side="left", padx=5, pady=5)

    def setup_log_tab(self, parent):
        """Setup the log tab"""
        self.log_text = scrolledtext.ScrolledText(parent, height=25, width=80)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Add any pending logs
        if hasattr(self, '_pending_logs'):
            for pending_msg in self._pending_logs:
                self.log_text.insert(tk.END, pending_msg)
            del self._pending_logs
            self.log_text.see(tk.END)

        # Clear button
        ttk.Button(parent, text="Clear Log",
                  command=lambda: self.log_text.delete(1.0, tk.END)).pack(pady=5)

    def setup_building_management_tab(self, parent):
        """Setup the Building Management tab (v2.1.0)"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="🏗️ Building Management Configuration")
        config_frame.pack(fill="x", padx=5, pady=5)

        # Enable/disable smart skip
        self.enable_smart_skip_var = tk.BooleanVar(value=self.building_manager.config["enable_smart_skip"])
        ttk.Checkbutton(config_frame, text="Enable Smart Building Skip",
                       variable=self.enable_smart_skip_var,
                       command=self.toggle_smart_skip).pack(anchor="w", padx=10, pady=5)

        # Enable/disable OCR
        self.enable_ocr_var = tk.BooleanVar(value=self.building_manager.config["enable_ocr_detection"])
        ocr_cb = ttk.Checkbutton(
            config_frame,
            text="Enable OCR Auto-Detection",
            variable=self.enable_ocr_var,
            command=self.toggle_ocr_detection
        )
        ocr_cb.pack(anchor="w", padx=10, pady=(5, 2))
        self.ocr_checkbox = ocr_cb

        self.ocr_status_label = ttk.Label(
            config_frame,
            text="",
            foreground="gray",
            wraplength=600,
            justify="left"
        )
        self.ocr_status_label.pack(anchor="w", padx=12, pady=(0, 8))

        # Action buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.ocr_scan_button = ttk.Button(
            button_frame,
            text="📷 Scan Window",
            command=self.scan_buildings_ocr
        )
        self.ocr_scan_button.pack(side="left", padx=5)

        # Coordinate-based scan button
        self.coordinate_scan_button = ttk.Button(
            button_frame,
            text="📍 Scan Coordinates",
            command=self.scan_buildings_coordinates
        )
        self.coordinate_scan_button.pack(side="left", padx=5)

        self.clipboard_scan_button = ttk.Button(
            button_frame,
            text="📋 Scan Clipboard Image",
            command=self.scan_clipboard_image
        )
        self.clipboard_scan_button.pack(side="left", padx=5)

        # Enhanced scan button (uses all improvements)
        self.enhanced_scan_button = ttk.Button(
            button_frame,
            text="🎯 Enhanced Scan",
            command=self.scan_buildings_enhanced
        )
        self.enhanced_scan_button.pack(side="left", padx=5)

        # LLM Strategic Tips button
        self.strategic_tips_button = ttk.Button(
            button_frame,
            text="🤖 Strategic Tips",
            command=self.get_strategic_tips
        )
        self.strategic_tips_button.pack(side="left", padx=5)

        ttk.Button(button_frame, text="🔄 Refresh List",
                  command=self.refresh_building_list).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🗑️ Reset All",
                  command=self.reset_all_buildings).pack(side="left", padx=5)

        # Statistics section
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Statistics")
        stats_frame.pack(fill="x", padx=5, pady=5)

        self.stats_label = ttk.Label(stats_frame, text="Loading statistics...")
        self.stats_label.pack(padx=10, pady=10)

        # Building list section
        list_frame = ttk.LabelFrame(main_frame, text="📋 Building Status")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create treeview for buildings
        columns = ("building", "area", "status", "level", "confidence", "date")
        self.building_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=12)

        # Configure columns
        self.building_tree.heading("#0", text="Building", anchor="w")
        self.building_tree.heading("building", text="Type", anchor="w")
        self.building_tree.heading("area", text="Area", anchor="w")
        self.building_tree.heading("status", text="Status", anchor="center")
        self.building_tree.heading("level", text="Level", anchor="center")
        self.building_tree.heading("confidence", text="Confidence", anchor="center")
        self.building_tree.heading("date", text="Date", anchor="w")

        # Configure column widths
        self.building_tree.column("#0", width=100)
        self.building_tree.column("building", width=80)
        self.building_tree.column("area", width=80)
        self.building_tree.column("status", width=80)
        self.building_tree.column("level", width=60)
        self.building_tree.column("confidence", width=80)
        self.building_tree.column("date", width=100)

        # Add scrollbar
        tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.building_tree.yview)
        self.building_tree.configure(yscrollcommand=tree_scroll.set)

        # Pack treeview and scrollbar
        self.building_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        tree_scroll.pack(side="right", fill="y")

        # Context menu for buildings
        self.building_tree.bind("<Button-3>", self.show_building_context_menu)
        self.building_tree.bind("<Double-1>", self.toggle_building_maxed)

        # Initial data load
        self.refresh_building_list()
        self.update_building_stats()
        self.update_ocr_controls()

    def setup_coordinate_setup_tab(self, parent):
        """Setup the Coordinate Setup tab for precise building detection"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Instructions Section
        instructions_frame = ttk.LabelFrame(scrollable_frame, text="📖 Setup Instructions")
        instructions_frame.pack(fill="x", padx=5, pady=5)

        instructions_text = """IMPORTANT: Before logging coordinates, make sure you are in SHELTER VIEW!

1. Switch to Shelter View (not World map)
2. Center your base view and ensure building names are visible
3. Select target window and a building type to log
4. Click on the building name/level text when prompted
5. Repeat for all building types you want to automate

⚠️ Warning: Coordinates logged in World View will not work!"""

        instructions_label = tk.Label(instructions_frame, text=instructions_text,
                                    justify="left", wraplength=400,
                                    font=("TkDefaultFont", 9))
        instructions_label.pack(padx=10, pady=10)

        # Window Selection Section
        window_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Target Window Selection")
        window_frame.pack(fill="x", padx=5, pady=5)

        # Window dropdown
        ttk.Label(window_frame, text="Select Target Window:").pack(anchor="w", padx=10, pady=5)
        self.coord_window_var = tk.StringVar()
        self.coord_window_combo = ttk.Combobox(window_frame, textvariable=self.coord_window_var,
                                             state="readonly", width=40)
        self.coord_window_combo.pack(padx=10, pady=5, fill="x")

        # Window controls
        window_buttons = ttk.Frame(window_frame)
        window_buttons.pack(padx=10, pady=5, fill="x")

        ttk.Button(window_buttons, text="Refresh Windows",
                  command=self.refresh_coordinate_windows).pack(side="left", padx=5)
        ttk.Button(window_buttons, text="Set Target Window",
                  command=self.set_coordinate_target_window).pack(side="left", padx=5)

        # Window status
        self.coord_window_status = tk.StringVar(value="No window selected")
        ttk.Label(window_frame, textvariable=self.coord_window_status,
                 font=("TkDefaultFont", 9, "italic")).pack(padx=10, pady=5)

        # Building Type Selection
        building_frame = ttk.LabelFrame(scrollable_frame, text="🏗️ Building Type Selection")
        building_frame.pack(fill="x", padx=5, pady=5)

        # Building type dropdown
        ttk.Label(building_frame, text="Select Building Type:").pack(anchor="w", padx=10, pady=5)
        self.building_type_var = tk.StringVar()
        self.building_type_combo = ttk.Combobox(building_frame, textvariable=self.building_type_var,
                                              state="readonly", width=40)

        # Populate with building types
        building_types = [
            ("hunter", "Hunter's Hut - Resource gathering building"),
            ("kitchen", "Kitchen - Food production building"),
            ("tower", "Tower/Watch Tower - Defense building"),
            ("farm", "Farm - Food production building"),
            ("warehouse", "Warehouse - Storage building"),
            ("barracks", "Barracks - Military training"),
            ("wall", "Wall - Defensive structure"),
            ("mine", "Mine - Resource gathering"),
            ("lumber", "Lumber Mill - Wood production"),
            ("quarry", "Quarry - Stone production"),
            ("forge", "Forge - Equipment crafting"),
            ("academy", "Academy - Research building")
        ]

        self.building_type_combo['values'] = [f"{btype} - {desc}" for btype, desc in building_types]
        self.building_type_combo.pack(padx=10, pady=5, fill="x")

        # Coordinate Logging Section
        logging_frame = ttk.LabelFrame(scrollable_frame, text="📍 Coordinate Logging")
        logging_frame.pack(fill="x", padx=5, pady=5)

        # Current logging status
        self.coord_logging_status = tk.StringVar(value="Ready to log coordinates")
        ttk.Label(logging_frame, textvariable=self.coord_logging_status,
                 font=("TkDefaultFont", 10, "bold")).pack(padx=10, pady=5)

        # Logging controls
        logging_buttons = ttk.Frame(logging_frame)
        logging_buttons.pack(padx=10, pady=5, fill="x")

        self.start_logging_btn = ttk.Button(logging_buttons, text="Start Coordinate Logging",
                                          command=self.start_coordinate_logging)
        self.start_logging_btn.pack(side="left", padx=5)

        self.stop_logging_btn = ttk.Button(logging_buttons, text="Stop Logging",
                                         command=self.stop_coordinate_logging,
                                         state="disabled")
        self.stop_logging_btn.pack(side="left", padx=5)

        # Logged Coordinates Section
        coords_frame = ttk.LabelFrame(scrollable_frame, text="📋 Logged Coordinates")
        coords_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Coordinates tree view
        coords_tree_frame = ttk.Frame(coords_frame)
        coords_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tree view with columns
        columns = ("building_type", "building_name", "coordinates", "timestamp")
        self.coords_tree = ttk.Treeview(coords_tree_frame, columns=columns, show="headings", height=8)

        # Define column headings
        self.coords_tree.heading("building_type", text="Type")
        self.coords_tree.heading("building_name", text="Building Name")
        self.coords_tree.heading("coordinates", text="Coordinates (x, y)")
        self.coords_tree.heading("timestamp", text="Timestamp")

        # Define column widths
        self.coords_tree.column("building_type", width=100)
        self.coords_tree.column("building_name", width=150)
        self.coords_tree.column("coordinates", width=120)
        self.coords_tree.column("timestamp", width=150)

        # Scrollbar for tree view
        coords_scrollbar = ttk.Scrollbar(coords_tree_frame, orient="vertical", command=self.coords_tree.yview)
        self.coords_tree.configure(yscrollcommand=coords_scrollbar.set)

        self.coords_tree.pack(side="left", fill="both", expand=True)
        coords_scrollbar.pack(side="right", fill="y")

        # Coordinate management buttons
        coords_buttons = ttk.Frame(coords_frame)
        coords_buttons.pack(padx=10, pady=5, fill="x")

        ttk.Button(coords_buttons, text="Refresh List",
                  command=self.refresh_coordinates_list).pack(side="left", padx=5)
        ttk.Button(coords_buttons, text="Delete Selected",
                  command=self.delete_selected_coordinate).pack(side="left", padx=5)
        ttk.Button(coords_buttons, text="Test Coordinate",
                  command=self.test_selected_coordinate).pack(side="left", padx=5)
        ttk.Button(coords_buttons, text="Export Coordinates",
                  command=self.export_coordinates).pack(side="left", padx=5)

        # Statistics Section
        stats_frame = ttk.LabelFrame(scrollable_frame, text="📊 Coordinate Statistics")
        stats_frame.pack(fill="x", padx=5, pady=5)

        self.coord_stats_text = tk.Text(stats_frame, height=4, wrap="word",
                                       font=("TkDefaultFont", 9))
        self.coord_stats_text.pack(padx=10, pady=10, fill="x")

        # Initialize the coordinate setup
        self.refresh_coordinate_windows()
        self.refresh_coordinates_list()
        self.update_coordinate_statistics()

    def refresh_ocr_status(self):
        """Pull the latest OCR engine status from the manager"""
        if self.building_manager:
            self.ocr_status = self.building_manager.get_ocr_status()
        else:
            self.ocr_status = {}

    def update_ocr_controls(self):
        """Synchronize OCR UI controls with runtime status"""
        if not hasattr(self, "ocr_status_label"):
            return

        self.refresh_ocr_status()
        status = self.ocr_status or {}

        libraries_available = status.get("libraries_available", False)
        tesseract_installed = status.get("tesseract_installed", False)
        tesseract_version = status.get("version")
        tesseract_cmd = status.get("tesseract_cmd")
        last_error = status.get("last_error")

        # Keep UI checkbox in sync with current config
        if self.building_manager:
            self.enable_ocr_var.set(self.building_manager.config.get("enable_ocr_detection", False))

        lines = []
        color = "gray"

        if not libraries_available:
            lines.append("❌ OCR Python libraries missing (pytesseract, opencv-python, pillow, numpy).")
            lines.append("Install with: pip install pytesseract opencv-python pillow numpy")
            color = "orange"
            self.ocr_checkbox.state(["disabled"])
            self.ocr_scan_button.state(["disabled"])
        elif tesseract_installed:
            version_text = f"{tesseract_version}" if tesseract_version else "unknown version"
            lines.append(f"✅ Tesseract detected ({version_text})")
            if tesseract_cmd:
                lines.append(f"Path: {tesseract_cmd}")
            if last_error:
                lines.append(f"Previous issue: {last_error}")
            color = "green"
            self.ocr_checkbox.state(["!disabled"])
            self.ocr_scan_button.state(["!disabled"])
        else:
            lines.append("❌ Tesseract executable not detected.")
            if last_error:
                lines.append(f"Details: {last_error}")
            lines.append("Install from https://github.com/UB-Mannheim/tesseract/wiki")
            color = "orange"
            # Allow enabling checkbox so user can leave setting on, but disable scan button to prevent failures
            self.ocr_checkbox.state(["!disabled"])
            self.ocr_scan_button.state(["disabled"])

        self.ocr_status_label.config(text="\n".join(lines), foreground=color)

    def toggle_smart_skip(self):
        """Toggle smart building skip feature"""
        if self.building_manager:
            self.building_manager.config["enable_smart_skip"] = self.enable_smart_skip_var.get()
            self.building_manager.save_config()
            status = "enabled" if self.enable_smart_skip_var.get() else "disabled"
            self.log(f"🏗️ Smart building skip {status}")

    def toggle_ocr_detection(self):
        """Toggle OCR auto-detection feature"""
        if self.building_manager:
            self.building_manager.config["enable_ocr_detection"] = self.enable_ocr_var.get()
            self.building_manager.save_config()
            status = "enabled" if self.enable_ocr_var.get() else "disabled"
            self.log(f"👁️ OCR building detection {status}")
            self.update_ocr_controls()
            self.update_building_stats()

    def scan_buildings_ocr(self):
        """Scan current screen for building levels using OCR"""
        if not self.building_manager:
            messagebox.showwarning("OCR Scan", "Building manager not available")
            return

        self.building_manager.setup_ocr_engine()
        self.update_ocr_controls()

        status = self.ocr_status or {}
        if not status.get("libraries_available", False):
            install_msg = (
                "OCR Python libraries are missing.\n"
                "Install with: pip install pytesseract opencv-python pillow numpy"
            )
            self.log(f"❌ OCR Scan blocked - {install_msg}")
            messagebox.showwarning("OCR Scan", install_msg)
            return

        if not status.get("tesseract_installed", False):
            install_msg = (
                "Tesseract OCR is not detected. Install it from "
                "https://github.com/UB-Mannheim/tesseract/wiki and restart the bot."
            )
            details = status.get("last_error")
            if details:
                install_msg += f"\nDetails: {details}"
            self.log(f"❌ OCR Scan blocked - {install_msg}")
            messagebox.showwarning("OCR Scan", install_msg)
            return

        try:
            target_window = self.get_target_window()
            if not target_window:
                messagebox.showwarning(
                    "OCR Scan",
                    "No target window selected. Please select a game window first."
                )
                return

            target_window.activate()
            time.sleep(0.2)

            left, top, width, height = (
                target_window.left,
                target_window.top,
                target_window.width,
                target_window.height,
            )
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot_array = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)

            self.log(f"📷 Capturing OCR screenshot: {target_window.title} ({width}x{height})")

            result = self.building_manager.scan_buildings_with_ocr(screenshot_bgr)

            if result.get("success", False):
                detected = result["detected_buildings"]
                self.log(f"📷 OCR Scan completed: {len(detected)} buildings analyzed")

                maxed_count = sum(1 for b in detected.values() if b.get("is_maxed"))
                if maxed_count > 0:
                    self.log(f"   ✅ Found {maxed_count} maxed buildings")

                self.refresh_building_list()

                summary = result.get("summary", {}) or {}
                confidence = summary.get("confidence", {}) or {}
                lines_detected = summary.get("lines_detected")
                auto_marked = summary.get("auto_marked")

                message_lines = [
                    f"Scanned {len(detected)} buildings.",
                    f"Auto-marked maxed buildings: {auto_marked or 0}",
                ]

                if lines_detected is not None:
                    message_lines.append(f"OCR lines analyzed: {lines_detected}")

                if confidence.get("mean_confidence") is not None:
                    mean_conf = confidence["mean_confidence"]
                    sample_size = confidence.get("sample_size")
                    conf_line = f"Average confidence: {mean_conf}%"
                    if sample_size:
                        conf_line += f" (n={sample_size})"
                    message_lines.append(conf_line)

                debug_paths = summary.get("debug_paths", {}) or {}
                if debug_paths:
                    message_lines.append("Debug images saved to OCR debug folder.")

                messagebox.showinfo("OCR Scan Complete", "\n".join(message_lines))
            else:
                error_msg = result.get("error", "Unknown error")
                summary = result.get("summary", {}) or {}
                details = []

                if summary.get("message"):
                    details.append(summary["message"])

                confidence = summary.get("confidence", {}) or {}
                if confidence.get("error"):
                    details.append(f"Confidence analysis error: {confidence['error']}")

                ocr_status = result.get("ocr_status")
                if ocr_status:
                    self.building_manager.ocr_engine.update(ocr_status)

                full_message = error_msg
                if details:
                    full_message += "\n\n" + "\n".join(details)

                self.log(f"❌ OCR Scan failed: {full_message}")
                messagebox.showerror("OCR Scan Failed", full_message)

            self.update_building_stats()

        except Exception as e:
            self.log_error(e, "OCR Building Scan", "ocr_scan_buildings")
            messagebox.showerror("OCR Scan Error", f"Failed to scan buildings:\n{str(e)}")

        finally:
            self.update_ocr_controls()

    def scan_buildings_coordinates(self):
        """Scan buildings using logged coordinate positions"""
        if not self.building_manager:
            messagebox.showwarning("Coordinate Scan", "Building manager not available")
            return

        if not self.coordinate_setup_enabled:
            messagebox.showwarning("Coordinate Scan", "Coordinate setup not available")
            return

        # Check if any coordinates have been logged
        coord_status = self.building_manager.get_coordinate_status()
        if not coord_status.get("available", False):
            messagebox.showwarning("Coordinate Scan", "Coordinate logger not available")
            return

        if coord_status.get("total_coordinates", 0) == 0:
            messagebox.showinfo(
                "Coordinate Scan",
                "No coordinates logged yet.\n\n"
                "Go to the 'Coordinate Setup' tab to log building positions first."
            )
            return

        try:
            # Get target window
            if not self.window_combo.get():
                messagebox.showwarning(
                    "Coordinate Scan",
                    "No target window selected. Please select a game window first."
                )
                return

            window_title = self.window_combo.get().split(" (")[0]

            self.log(f"📍 Starting coordinate-based building scan on: {window_title}")
            self.log(f"🎯 Using {coord_status['total_coordinates']} logged coordinates")

            # Perform coordinate-based scan
            scan_result = self.building_manager.scan_buildings_with_coordinates(window_title)

            if scan_result["success"]:
                detected_count = scan_result["total_detected"]
                coordinates_used = scan_result.get("coordinates_used", 0)

                self.log(f"📊 Coordinate scan completed: {detected_count}/{coordinates_used} buildings detected")

                # Update building display
                self.refresh_building_list()
                self.update_building_stats()

                # Show detailed results
                building_details = []
                for building_type, data in scan_result["detected_buildings"].items():
                    level = data["current_level"]
                    max_level = data["max_level"]
                    maxed_status = "MAXED" if data["is_maxed"] else "not maxed"
                    building_details.append(f"• {building_type}: Lv.{level}/{max_level} ({maxed_status})")

                result_message = f"Coordinate scan results:\n\n"
                result_message += f"Buildings detected: {detected_count}/{coordinates_used}\n\n"

                if building_details:
                    result_message += "Building levels:\n"
                    result_message += "\n".join(building_details)
                else:
                    result_message += "No building levels detected."

                if scan_result.get("scan_errors"):
                    result_message += f"\n\nErrors:\n"
                    for error in scan_result["scan_errors"][:5]:  # Show max 5 errors
                        result_message += f"• {error}\n"

                messagebox.showinfo("Coordinate Scan Complete", result_message)

            else:
                error_msg = scan_result.get("error", "Unknown error")
                self.log(f"❌ Coordinate scan failed: {error_msg}")
                messagebox.showerror("Coordinate Scan Failed", f"Scan failed: {error_msg}")

        except Exception as e:
            error_msg = f"Coordinate scan error: {e}"
            self.log(f"❌ {error_msg}")
            messagebox.showerror("Coordinate Scan Error", error_msg)

    def scan_buildings_enhanced(self):
        """Enhanced building scan using all accuracy improvements"""
        if not self.building_manager:
            messagebox.showwarning("Enhanced Scan", "Building manager not available")
            return

        try:
            # Get target window
            if not self.window_combo.get():
                messagebox.showwarning(
                    "Enhanced Scan",
                    "No target window selected. Please select a game window first."
                )
                return

            window_title = self.window_combo.get().split(" (")[0]

            self.log(f"🎯 Starting enhanced building scan on: {window_title}")
            self.log("🔧 Using popup filtering, coordinate targeting, and cross-validation")

            # Use enhanced scanning method
            scan_result = self.building_manager.scan_buildings_enhanced(None, window_title)

            if scan_result["success"]:
                detected_count = scan_result["total_detected"]
                method_used = scan_result["method_used"]
                accuracy_summary = scan_result.get("accuracy_summary", "Standard processing")

                self.log(f"📊 Enhanced scan completed: {detected_count} buildings detected")
                self.log(f"🔧 Method: {method_used}")
                self.log(f"⚡ Improvements: {accuracy_summary}")

                # Update building display
                self.refresh_building_list()
                self.update_building_stats()

                # Show detailed results
                building_details = []
                validation_details = []

                for building_type, data in scan_result["detected_buildings"].items():
                    level = data["current_level"]
                    max_level = data["max_level"]
                    maxed_status = "MAXED" if data["is_maxed"] else "not maxed"
                    confidence = data.get("confidence", 0.8)

                    building_details.append(f"• {building_type}: Lv.{level}/{max_level} ({maxed_status}) [{confidence:.1%}]")

                    # Add validation notes if available
                    if "validation_notes" in data:
                        for note in data["validation_notes"][:2]:  # Show max 2 notes per building
                            validation_details.append(f"  → {building_type}: {note}")

                result_message = f"Enhanced scan results:\n\n"
                result_message += f"Buildings detected: {detected_count}\n"
                result_message += f"Method: {method_used}\n"
                result_message += f"Improvements: {accuracy_summary}\n\n"

                if building_details:
                    result_message += "Building levels:\n"
                    result_message += "\n".join(building_details)

                if validation_details:
                    result_message += "\n\nValidation details:\n"
                    result_message += "\n".join(validation_details[:5])  # Show max 5 validation notes

                messagebox.showinfo("Enhanced Scan Complete", result_message)

                # Log specific warehouse detection if present
                if "warehouse" in scan_result["detected_buildings"]:
                    warehouse_data = scan_result["detected_buildings"]["warehouse"]
                    self.log(f"🏭 Warehouse detected: Level {warehouse_data['current_level']}/{warehouse_data['max_level']}")
                    if "validation_notes" in warehouse_data:
                        for note in warehouse_data["validation_notes"]:
                            self.log(f"🔍 Warehouse validation: {note}")

            else:
                error_msg = scan_result.get("error", "Unknown error")
                self.log(f"❌ Enhanced scan failed: {error_msg}")

                # Show helpful error message based on the failure
                if "No scanning method succeeded" in error_msg:
                    messagebox.showerror(
                        "Enhanced Scan Failed",
                        "No scanning method succeeded.\n\n"
                        "Suggestions:\n"
                        "• Ensure game window is visible\n"
                        "• Try logging coordinates in the Coordinate Setup tab\n"
                        "• Check that building names/levels are visible on screen\n"
                        "• Verify OCR is enabled in Building Management settings"
                    )
                else:
                    messagebox.showerror("Enhanced Scan Failed", f"Scan failed: {error_msg}")

        except Exception as e:
            error_msg = f"Enhanced scan error: {e}"
            self.log(f"❌ {error_msg}")
            messagebox.showerror("Enhanced Scan Error", error_msg)

    def get_strategic_tips(self):
        """Get AI-powered strategic recommendations for the next hour"""
        if not self.building_manager or not self.building_manager.llm_advisor:
            messagebox.showwarning(
                "Strategic Tips",
                "LLM Strategic Advisor not available.\n\n"
                "The LLM advisor requires:\n"
                "• Ollama server running\n"
                "• gemma3:latest model installed\n"
                "• llm_advisor.py module"
            )
            return

        try:
            self.log("🤖 Generating strategic recommendations...")

            # Gather current game state information
            game_state = {
                "timestamp": datetime.now().isoformat(),
                "building_count": len(self.building_manager.building_states),
                "last_scan": "recent" if self.building_manager.building_states else "none",
                "llm_advisor_stats": self.building_manager.llm_advisor.get_performance_stats()
            }

            # Add building information if available
            if self.building_manager.building_states:
                buildings_ready = []
                buildings_maxed = []
                for building_type, data in self.building_manager.building_states.items():
                    if data.get("is_maxed", False):
                        buildings_maxed.append(building_type.title())
                    else:
                        level = data.get("current_level", "?")
                        max_level = data.get("max_level", "?")
                        buildings_ready.append(f"{building_type.title()}: {level}/{max_level}")

                game_state["buildings_ready_to_upgrade"] = buildings_ready[:5]  # Top 5
                game_state["buildings_maxed"] = len(buildings_maxed)

            # Get strategic recommendations from LLM
            tips = self.building_manager.llm_advisor.get_strategic_tips(game_state)

            if tips and tips.strip():
                # Display tips in a scrollable message box
                tip_window = tk.Toplevel(self.root)
                tip_window.title("🤖 Strategic Recommendations")
                tip_window.geometry("600x400")
                tip_window.resizable(True, True)

                # Create scrollable text widget
                frame = ttk.Frame(tip_window)
                frame.pack(fill="both", expand=True, padx=10, pady=10)

                text_widget = tk.Text(frame, wrap="word", font=("Arial", 11))
                scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar.set)

                # Add content
                text_widget.insert("1.0", f"Strategic Recommendations for Next Hour\n")
                text_widget.insert("end", f"Generated: {datetime.now().strftime('%H:%M:%S')}\n")
                text_widget.insert("end", "="*50 + "\n\n")
                text_widget.insert("end", tips)

                # Add performance stats
                if game_state.get("llm_advisor_stats"):
                    stats = game_state["llm_advisor_stats"]
                    text_widget.insert("end", f"\n\n" + "="*50 + "\n")
                    text_widget.insert("end", f"LLM Advisor Performance:\n")
                    text_widget.insert("end", f"• Total queries: {stats['total_queries']}\n")
                    text_widget.insert("end", f"• Average response time: {stats['avg_response_time']}\n")
                    text_widget.insert("end", f"• Error rate: {stats['error_rate']}\n")

                text_widget.configure(state="disabled")  # Make read-only

                text_widget.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                # Add close button
                close_button = ttk.Button(tip_window, text="Close", command=tip_window.destroy)
                close_button.pack(pady=5)

                # Log the recommendations
                self.log("🤖 Strategic recommendations generated and displayed")
                self.log(f"📊 LLM stats: {stats['total_queries']} queries, {stats['avg_response_time']} avg time")

            else:
                self.log("⚠️ No strategic recommendations generated")
                messagebox.showwarning(
                    "Strategic Tips",
                    "No strategic recommendations could be generated at this time.\n\n"
                    "Try:\n"
                    "• Running a building scan first\n"
                    "• Checking Ollama server status\n"
                    "• Verifying LLM model is loaded"
                )

        except Exception as e:
            error_msg = f"Strategic tips error: {e}"
            self.log(f"❌ {error_msg}")
            messagebox.showerror("Strategic Tips Error", error_msg)

    def scan_clipboard_image(self):
        """Scan an image from clipboard for building levels using OCR"""
        if not self.building_manager:
            messagebox.showwarning("Clipboard OCR Scan", "Building manager not available")
            return

        self.building_manager.setup_ocr_engine()
        self.update_ocr_controls()

        status = self.ocr_status or {}
        if not status.get("libraries_available", False):
            install_msg = (
                "OCR Python libraries are missing.\n"
                "Install with: pip install pytesseract opencv-python pillow numpy"
            )
            self.log(f"❌ Clipboard OCR Scan blocked - {install_msg}")
            messagebox.showwarning("Clipboard OCR Scan", install_msg)
            return

        if not status.get("tesseract_installed", False):
            install_msg = (
                "Tesseract OCR is not detected. Install it from "
                "https://github.com/UB-Mannheim/tesseract/wiki and restart the bot."
            )
            details = status.get("last_error")
            if details:
                install_msg += f"\nDetails: {details}"
            self.log(f"❌ Clipboard OCR Scan blocked - {install_msg}")
            messagebox.showwarning("Clipboard OCR Scan", install_msg)
            return

        try:
            # Get image from clipboard
            try:
                from PIL import ImageGrab
                clipboard_image = ImageGrab.grabclipboard()

                if clipboard_image is None:
                    messagebox.showwarning(
                        "Clipboard OCR Scan",
                        "No image found in clipboard.\n\n"
                        "Please copy an image first:\n"
                        "1. Take a screenshot (Win+Shift+S)\n"
                        "2. Copy game screenshot to clipboard\n"
                        "3. Then click this button to scan"
                    )
                    return

                # Convert PIL image to OpenCV format
                clipboard_array = np.array(clipboard_image)

                # Handle different image modes
                if clipboard_image.mode == 'RGBA':
                    clipboard_bgr = cv2.cvtColor(clipboard_array, cv2.COLOR_RGBA2BGR)
                elif clipboard_image.mode == 'RGB':
                    clipboard_bgr = cv2.cvtColor(clipboard_array, cv2.COLOR_RGB2BGR)
                else:
                    # Convert to RGB first, then to BGR
                    rgb_image = clipboard_image.convert('RGB')
                    clipboard_array = np.array(rgb_image)
                    clipboard_bgr = cv2.cvtColor(clipboard_array, cv2.COLOR_RGB2BGR)

                width, height = clipboard_image.size
                self.log(f"📋 Scanning clipboard image: {width}x{height} pixels")

            except ImportError:
                messagebox.showerror(
                    "Clipboard OCR Scan",
                    "PIL ImageGrab not available. Install with: pip install Pillow"
                )
                return
            except Exception as e:
                messagebox.showerror(
                    "Clipboard OCR Scan",
                    f"Failed to get image from clipboard:\n{str(e)}"
                )
                return

            # Run OCR scan on clipboard image
            result = self.building_manager.scan_buildings_with_ocr(clipboard_bgr)

            if result.get("success", False):
                detected = result["detected_buildings"]
                self.log(f"📋 Clipboard OCR Scan completed: {len(detected)} buildings analyzed")

                maxed_count = sum(1 for b in detected.values() if b.get("is_maxed"))
                if maxed_count > 0:
                    self.log(f"   ✅ Found {maxed_count} maxed buildings")

                # Show detailed results for clipboard scan
                if detected:
                    building_list = []
                    for name, info in detected.items():
                        level_str = f"{info.get('current_level', '?')}/{info.get('max_level', '?')}"
                        maxed_str = " (MAXED)" if info.get('is_maxed') else ""
                        building_list.append(f"• {name.title()}: Level {level_str}{maxed_str}")

                    self.log("📋 Detected buildings:")
                    for building in building_list:
                        self.log(f"  {building}")

                self.refresh_building_list()

                summary = result.get("summary", {}) or {}
                confidence = summary.get("confidence", {}) or {}
                lines_detected = summary.get("lines_detected")
                auto_marked = summary.get("auto_marked")

                message_lines = [
                    f"Clipboard image scanned successfully!",
                    f"Found {len(detected)} buildings.",
                    f"Auto-marked maxed buildings: {auto_marked or 0}",
                ]

                if lines_detected is not None:
                    message_lines.append(f"OCR lines analyzed: {lines_detected}")

                if confidence.get("mean_confidence") is not None:
                    mean_conf = confidence["mean_confidence"]
                    sample_size = confidence.get("sample_size")
                    conf_line = f"Average confidence: {mean_conf}%"
                    if sample_size:
                        conf_line += f" (n={sample_size})"
                    message_lines.append(conf_line)

                if detected:
                    message_lines.append("\nDetected buildings:")
                    for name, info in detected.items():
                        level_str = f"{info.get('current_level', '?')}/{info.get('max_level', '?')}"
                        maxed_str = " (MAXED)" if info.get('is_maxed') else ""
                        message_lines.append(f"• {name.title()}: Level {level_str}{maxed_str}")

                messagebox.showinfo("Clipboard OCR Scan Complete", "\n".join(message_lines))
            else:
                error_msg = result.get("error", "Unknown error")
                self.log(f"❌ Clipboard OCR Scan failed: {error_msg}")

                suggestion_msg = (
                    f"{error_msg}\n\n"
                    "Suggestions:\n"
                    "• Make sure the image shows Dark War Survival buildings\n"
                    "• Ensure building names and levels are clearly visible\n"
                    "• Try a higher resolution screenshot\n"
                    "• Check that the image has good contrast"
                )
                messagebox.showerror("Clipboard OCR Scan Failed", suggestion_msg)

            self.update_building_stats()

        except Exception as e:
            self.log_error(e, "Clipboard OCR Building Scan", "clipboard_ocr_scan_buildings")
            messagebox.showerror("Clipboard OCR Scan Error", f"Failed to scan clipboard image:\n{str(e)}")

        finally:
            self.update_ocr_controls()

    def refresh_building_list(self):
        """Refresh the building list display"""
        if not self.building_manager:
            return

        # Clear existing items
        for item in self.building_tree.get_children():
            self.building_tree.delete(item)

        # Add buildings
        buildings = self.building_manager.get_building_list()

        for building in buildings:
            # Determine status icon and text
            if building["manually_maxed"]:
                status_icon = "🔒"
                status_text = "Manual"
            elif building["auto_detected_maxed"]:
                status_icon = "🤖"
                status_text = "Auto"
            else:
                status_icon = "🔄"
                status_text = "Active"

            # Format level display
            level_text = f"{building['current_level']}/{building['max_level']}" if building['current_level'] > 0 else f"?/{building['max_level']}"

            # Format confidence
            confidence_text = f"{building['confidence']:.0%}" if building['confidence'] > 0 else "N/A"

            # Format date
            date_text = building['marked_date'].split('T')[0] if building['marked_date'] else "N/A"

            # Insert into tree
            item_id = self.building_tree.insert("", "end",
                                               text=f"{status_icon} {building['name']}",
                                               values=(building['name'], building['area'], status_text,
                                                      level_text, confidence_text, date_text),
                                               tags=(building['key'],))

            # Color code based on status
            if building["is_maxed"]:
                self.building_tree.set(item_id, "status", f"✅ {status_text}")
            else:
                self.building_tree.set(item_id, "status", f"🔄 {status_text}")

    def update_building_stats(self):
        """Update building statistics display"""
        if not self.building_manager:
            return

        stats = self.building_manager.get_statistics()
        last_scan_iso = stats.get("last_scan")
        if last_scan_iso:
            try:
                last_scan_dt = datetime.fromisoformat(last_scan_iso)
                last_scan_display = last_scan_dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                last_scan_display = last_scan_iso
        else:
            last_scan_display = "Never"

        summary = stats.get("last_scan_summary") or {}
        details_parts = []

        lines_detected = summary.get("lines_detected")
        if lines_detected is not None:
            details_parts.append(f"lines {lines_detected}")

        auto_marked = summary.get("auto_marked")
        if auto_marked is not None:
            details_parts.append(f"auto-marked {auto_marked}")

        confidence = summary.get("confidence", {}) or {}
        if confidence.get("mean_confidence") is not None:
            mean_conf = confidence["mean_confidence"]
            sample_size = confidence.get("sample_size")
            conf_line = f"avg confidence {mean_conf}%"
            if sample_size:
                conf_line += f" (n={sample_size})"
            details_parts.append(conf_line)

        if summary.get("message"):
            details_parts.append(summary["message"])

        if stats.get("ocr_available"):
            version = stats.get("ocr_version") or "version unknown"
            ocr_line = f"✅ Tesseract ready ({version})"
        else:
            error = stats.get("ocr_error") or "OCR unavailable"
            ocr_line = f"❌ {error}"

        stats_lines = [
            "📊 Building Statistics:",
            f"   • Total Buildings: {stats['total_buildings']}",
            f"   • Maxed Buildings: {stats['maxed_buildings']}",
            f"   • Active Buildings: {stats['active_buildings']}",
            f"   • Skipped This Session: {stats['buildings_skipped_session']}",
            f"   • Time Saved: {stats['time_saved_minutes']} minutes",
            f"   • Last OCR Scan: {last_scan_display}",
            f"   • OCR Engine: {ocr_line}"
        ]

        if details_parts:
            stats_lines.append("   • Last Scan Details: " + "; ".join(details_parts))

        self.stats_label.config(text="\n".join(stats_lines))

    def show_building_context_menu(self, event):
        """Show context menu for building operations"""
        # Get selected item
        item = self.building_tree.selection()[0] if self.building_tree.selection() else None
        if not item:
            return

        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)

        # Get building key from tags
        building_key = self.building_tree.item(item)['tags'][0]
        building_name = building_key.split('_')[0]

        context_menu.add_command(label=f"Mark {building_name} as Maxed",
                               command=lambda: self.mark_building_maxed_manual(building_key))
        context_menu.add_command(label=f"Unmark {building_name}",
                               command=lambda: self.unmark_building_manual(building_key))
        context_menu.add_separator()
        context_menu.add_command(label="Refresh List", command=self.refresh_building_list)

        # Show menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def toggle_building_maxed(self, event):
        """Toggle building maxed status on double-click"""
        item = self.building_tree.selection()[0] if self.building_tree.selection() else None
        if not item:
            return

        building_key = self.building_tree.item(item)['tags'][0]
        building_state = self.building_manager.building_states.get(building_key, {})

        if building_state.get("manually_maxed", False) or building_state.get("auto_detected_maxed", False):
            self.unmark_building_manual(building_key)
        else:
            self.mark_building_maxed_manual(building_key)

    def mark_building_maxed_manual(self, building_key):
        """Manually mark a building as maxed"""
        building_name, area = building_key.split('_', 1)
        self.building_manager.mark_building_maxed(building_name, area, manual=True)
        self.refresh_building_list()
        self.update_building_stats()
        self.log(f"🔒 Manually marked {building_name} as maxed")

    def unmark_building_manual(self, building_key):
        """Manually unmark a building as maxed"""
        building_name, area = building_key.split('_', 1)
        self.building_manager.unmark_building_maxed(building_name, area)
        self.refresh_building_list()
        self.update_building_stats()
        self.log(f"🔄 Unmarked {building_name} - active again")

    def reset_all_buildings(self):
        """Reset all building states"""
        if messagebox.askyesno("Reset All Buildings",
                              "Reset all building states? This will mark all buildings as active again."):
            self.building_manager.reset_all_buildings()
            self.refresh_building_list()
            self.update_building_stats()
            self.log("🗑️ Reset all building states - all buildings active")

    def map_area_to_building(self, area_name):
        """Map click area names to building types for skip logic"""
        area_mapping = {
            # Common building areas that might be maxed
            "dorm": "dorm",
            "dormitory": "dorm",
            "barracks": "barracks",
            "hospital": "hospital",
            "tower": "tower",
            "wall": "wall",
            "farm": "farm",
            "lumber": "lumber_mill",
            "quarry": "quarry",
            "mine": "iron_mine",
            "warehouse": "warehouse",
            "storage": "warehouse",

            # UI areas that don't correspond to buildings (never skip)
            "mail": None,
            "rewards": None,
            "heroes": None,
            "world": None,
            "events": None,
            "vip": None,
            "center": None,
            "base center": None
        }

        # Look for building keywords in area name
        area_lower = area_name.lower()
        for keyword, building_type in area_mapping.items():
            if keyword in area_lower:
                return building_type

        # If no specific mapping found, return None (don't skip)
        return None

    def refresh_windows(self):
        """Enhanced window refresh with smart filtering and validation"""
        windows = []
        usable_windows = []
        skipped_count = 0

        try:
            all_windows = gw.getAllWindows()

            for window in all_windows:
                # Use enhanced window validation
                is_usable, reason = self.is_window_usable(window)

                if is_usable:
                    display_name = f"{window.title[:45]} [{window.width}x{window.height}]"
                    windows.append(display_name)
                    usable_windows.append(window)
                else:
                    skipped_count += 1
                    # Optionally log why windows were skipped (verbose mode)
                    if "Bot Control" in reason or "excluded" in reason.lower():
                        continue  # Don't spam log with expected exclusions

            self.window_combo['values'] = windows

            # Enhanced auto-selection with better filtering
            selected = False

            if self.mode_var.get() == "phone":
                # Look for phone mirroring indicators
                phone_keywords = ["Dark War", "S22", "Phone Link", "scrcpy", "Your Phone", "vysor"]
                for i, (window_name, window_obj) in enumerate(zip(windows, usable_windows)):
                    for keyword in phone_keywords:
                        if keyword.lower() in window_name.lower():
                            # Double-check it's not the bot itself
                            if not any(excluded.lower() in window_name.lower()
                                     for excluded in self.excluded_window_titles):
                                self.window_combo.current(i)
                                self.log(f"Auto-selected phone window: {window_obj.title}")
                                selected = True
                                break
                    if selected:
                        break

            else:  # BlueStacks mode
                bluestacks_keywords = ["BlueStacks", "LDPlayer", "NoxPlayer", "MEmu"]
                for i, (window_name, window_obj) in enumerate(zip(windows, usable_windows)):
                    for keyword in bluestacks_keywords:
                        if keyword.lower() in window_name.lower():
                            self.window_combo.current(i)
                            self.log(f"Auto-selected emulator window: {window_obj.title}")
                            selected = True
                            break
                    if selected:
                        break

            # Log results with enhanced info
            self.log(f"Found {len(windows)} usable windows (skipped {skipped_count} unusable)")

            if skipped_count > 10:  # Alert if many windows were skipped
                self.log(f"Note: {skipped_count} windows skipped (minimized, too small, or excluded)")

        except Exception as e:
            self.log(f"Error refreshing windows: {e}")
            self.log("Try closing unnecessary applications and refresh again")

    def mode_changed(self):
        """Handle mode change"""
        self.automation_mode = self.mode_var.get()
        self.log(f"Switched to {self.automation_mode} mode")
        self.refresh_windows()

    def update_click_speed(self, value):
        self.click_speed = float(value)
        self.click_speed_label.config(text=f"{self.click_speed:.2f}s")

    def update_cycle_speed(self, value):
        self.cycle_speed = float(value)
        self.cycle_speed_label.config(text=f"{self.cycle_speed:.1f}s")

    def update_actions(self, value):
        self.actions_per_cycle = int(float(value))
        self.actions_label.config(text=str(self.actions_per_cycle))

    def get_target_window(self):
        """Get the selected target window"""
        selected = self.window_var.get()
        if not selected:
            return None

        # Extract window title from display name "Window Title [WxH]"
        window_title = selected.split(" [")[0]

        # Debug log the selection
        self.log(f"🔍 Looking for window: '{window_title}' from dropdown: '{selected}'")

        # Find exact match first, then partial match
        all_windows = gw.getAllWindows()

        # Try exact title match first
        for window in all_windows:
            if window.title == window_title:
                self.log(f"✅ Found exact match: {window.title}")
                return window

        # Try partial match (startswith)
        for window in all_windows:
            if window.title.startswith(window_title):
                self.log(f"✅ Found partial match: {window.title}")
                return window

        # Try contains match as fallback
        for window in all_windows:
            if window_title.lower() in window.title.lower():
                self.log(f"✅ Found contains match: {window.title}")
                return window

        self.log(f"❌ No window found matching: '{window_title}'")
        self.log(f"Available windows: {[w.title for w in all_windows[:5]]}")
        return None

    def test_click(self):
        """Enhanced test clicking with detailed feedback and validation"""
        # Show what's currently selected
        selected = self.window_var.get()
        self.log(f"🎯 Test Click initiated on: {selected}")

        window = self.get_target_window()
        if not window:
            self.log("❌ No window selected for testing")
            self.log("Please select a target window from the dropdown first")
            return

        try:
            # Enhanced window validation
            is_usable, reason = self.is_window_usable(window)
            if not is_usable:
                self.log(f"❌ Cannot test click: {reason}")
                self.log("Try restoring the window or selecting a different target")
                return

            # Provide detailed information about the test
            self.log("🔍 TEST CLICK ANALYSIS:")
            self.log(f"  Target Window: {window.title}")
            self.log(f"  Window State: {'Active' if hasattr(window, 'isActive') and window.isActive else 'Inactive'}")
            self.log(f"  Window Size: {window.width}x{window.height}")

            # Activate and prepare window
            window.activate()
            time.sleep(0.5)

            # Calculate click position
            x, y, w, h = window.left, window.top, window.width, window.height
            center_x = x + w // 2
            center_y = y + h // 2

            # Determine what we'll be clicking on
            area_name, context = self.get_click_area_info(center_x, center_y, window)

            self.log(f"  Click Location: ({center_x}, {center_y})")
            self.log(f"  Target Area: {area_name}")
            self.log(f"  Expected Action: {context}")

            # Perform the click
            self.log("⚡ Performing test click...")
            pyautogui.click(center_x, center_y)

            # Simulate result detection
            result = self.detect_action_result(area_name)
            self.log(f"✅ Test click completed - {result}")

            # Log as action for history tracking
            self.log_action(area_name, center_x, center_y, result, "TEST_CLICK")

        except Exception as e:
            self.log_error(e, "Test Click", "test_click_execution", {
                "window_title": getattr(window, 'title', 'Unknown') if window else 'None',
                "window_size": f"{getattr(window, 'width', 0)}x{getattr(window, 'height', 0)}" if window else 'Unknown',
                "click_coordinates": f"({locals().get('center_x', 'Unknown')}, {locals().get('center_y', 'Unknown')})"
            })
            self.log("Check that the window is accessible and try again")

    def start_bot(self):
        """Start the automation bot"""
        if self.bot_running:
            return

        window = self.get_target_window()
        if not window:
            self.log("ERROR: No target window selected!")
            return

        self.target_window = window
        self.bot_running = True
        self.stats["start_time"] = time.time()
        self.stats["cycles"] = 0
        self.stats["clicks"] = 0
        self.stats["errors"] = 0

        # Update UI
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        # Start bot thread
        self.bot_thread = threading.Thread(target=self.bot_worker, daemon=True)
        self.bot_thread.start()

        self.log("BOT STARTED!")
        self.log(f"Target: {window.title}")
        self.log(f"Mode: {self.automation_mode}")
        self.log(f"Speed: {self.click_speed}s clicks, {self.cycle_speed}s cycles")

    def stop_bot(self):
        """Stop the automation bot"""
        self.bot_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log("BOT STOPPED")
        self.show_stats()

    def emergency_stop(self):
        """Emergency stop - immediate halt"""
        self.bot_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log("EMERGENCY STOP ACTIVATED!")

    def bot_worker(self):
        """Enhanced bot automation loop with fast emergency stop response"""
        self.emergency_stop_triggered = False

        while self.bot_running and not self.emergency_stop_triggered:
            try:
                # Check window state before each cycle
                is_usable, reason = self.is_window_usable(self.target_window)
                if not is_usable:
                    self.stats["skipped_windows"] += 1
                    self.root.after(0, lambda r=reason: self.log(f"⚠️  Skipping cycle: {r}"))

                    # Wait for window to become usable again
                    for _ in range(50):  # Wait up to 5 seconds (50 * 0.1s)
                        if not self.bot_running or self.emergency_stop_triggered:
                            return
                        time.sleep(0.1)
                    continue

                # Focus window if enabled
                if hasattr(self, 'focus_window_var') and self.focus_window_var.get():
                    self.target_window.activate()
                    time.sleep(0.1)

                # Perform automation cycle with enhanced logging
                if self.automation_mode == "phone":
                    self.enhanced_phone_automation_cycle()
                else:
                    self.enhanced_bluestacks_automation_cycle()

                self.stats["cycles"] += 1

                # Update status every 10 cycles
                if self.stats["cycles"] % 10 == 0:
                    self.root.after(0, self.update_status)

                # Use smaller sleep intervals for faster emergency stop response
                remaining_time = self.cycle_speed
                while remaining_time > 0 and self.bot_running and not self.emergency_stop_triggered:
                    sleep_time = min(0.1, remaining_time)  # Max 0.1s sleep intervals
                    time.sleep(sleep_time)
                    remaining_time -= sleep_time

            except Exception as e:
                self.stats["errors"] += 1
                error_record = self.log_error(e, "Bot Automation", "automation_cycle", {
                    "cycle_number": self.stats.get("cycles", 0),
                    "current_action": self.current_action,
                    "window_title": getattr(self.target_window, 'title', 'Unknown') if self.target_window else 'None'
                })
                self.root.after(0, lambda: self.log(f"❌ Bot error logged as #{error_record['id']}"))
                time.sleep(1)  # Brief pause on error

        # Clean shutdown
        if self.emergency_stop_triggered:
            self.root.after(0, lambda: self.log("🚨 Bot stopped via emergency key"))
        else:
            self.root.after(0, lambda: self.log("🛑 Bot stopped normally"))

    def enhanced_phone_automation_cycle(self):
        """Enhanced phone automation with detailed logging and result detection"""
        x, y, w, h = self.target_window.left, self.target_window.top, self.target_window.width, self.target_window.height

        # Define click areas with enhanced information
        available_areas = []

        # Check if phone_areas exists (for backward compatibility)
        if hasattr(self, 'phone_areas'):
            if self.phone_areas["mail"].get():
                available_areas.append((x + w - 30, y + h//2, "Mail/Rewards icon"))
            if self.phone_areas["heroes"].get():
                available_areas.append((x + 50, y + h - 80, "Heroes button"))
            if self.phone_areas["world"].get():
                available_areas.append((x + w - 50, y + h - 80, "World features"))
            if self.phone_areas["events"].get():
                available_areas.append((x + w - 40, y + 200, "Events panel"))
            if self.phone_areas["vip"].get():
                available_areas.append((x + 40, y + 100, "VIP benefits"))
            if self.phone_areas["center"].get():
                available_areas.append((x + w//2, y + h//2, "Base center"))
        else:
            # Default areas if phone_areas not initialized
            available_areas = [
                (x + w - 30, y + h//2, "Mail/Rewards icon"),
                (x + 50, y + h - 80, "Heroes button"),
                (x + w - 50, y + h - 80, "World features"),
                (x + w - 40, y + 200, "Events panel"),
                (x + 40, y + 100, "VIP benefits")
            ]

        # Perform enhanced clicks with logging
        actions_performed = min(self.actions_per_cycle, len(available_areas))

        for i in range(actions_performed):
            # Check for emergency stop before each action
            if not self.bot_running or self.emergency_stop_triggered:
                break

            click_x, click_y, area_name = available_areas[i]

            # Smart Building Management v2.1.0 - Check if we should skip this building
            if self.building_management_enabled and self.building_manager:
                # Map area names to potential building types
                building_name = self.map_area_to_building(area_name)

                if building_name and self.building_manager.should_skip_building(building_name, "phone_area"):
                    self.log(f"⏭️ Skipping {area_name} - {building_name} marked as maxed")
                    continue  # Skip this click and move to next area

            # Detect expected result before clicking
            expected_result = self.detect_action_result(area_name)

            # Perform click with enhanced logging
            self.log_action(area_name, click_x, click_y, expected_result, "AUTOMATION_CLICK")

            pyautogui.click(click_x, click_y)
            self.stats["clicks"] += 1

            # Brief delay between clicks with emergency stop check
            remaining_click_time = self.click_speed
            while remaining_click_time > 0 and self.bot_running and not self.emergency_stop_triggered:
                sleep_time = min(0.05, remaining_click_time)  # 50ms intervals
                time.sleep(sleep_time)
                remaining_click_time -= sleep_time

    def enhanced_bluestacks_automation_cycle(self):
        """Enhanced BlueStacks automation with template matching and logging"""
        x, y, w, h = self.target_window.left, self.target_window.top, self.target_window.width, self.target_window.height

        # BlueStacks-specific click areas (these would typically use template matching)
        bluestacks_areas = [
            (x + 100, y + 100, "Resource collection"),
            (x + 200, y + 150, "Building upgrade"),
            (x + w - 100, y + 100, "Troop training"),
            (x + w//2, y + h//2, "Base center"),
            (x + w - 50, y + h - 50, "Quest completion")
        ]

        actions_performed = min(self.actions_per_cycle, len(bluestacks_areas))

        for i in range(actions_performed):
            if not self.bot_running or self.emergency_stop_triggered:
                break

            click_x, click_y, area_name = bluestacks_areas[i]
            expected_result = f"Interacted with {area_name.lower()}"

            self.log_action(area_name, click_x, click_y, expected_result, "BLUESTACKS_CLICK")

            pyautogui.click(click_x, click_y)
            self.stats["clicks"] += 1

            # Brief delay with emergency stop checking
            remaining_click_time = self.click_speed
            while remaining_click_time > 0 and self.bot_running and not self.emergency_stop_triggered:
                sleep_time = min(0.05, remaining_click_time)
                time.sleep(sleep_time)
                remaining_click_time -= sleep_time

    def bluestacks_automation_cycle(self):
        """Perform one cycle of BlueStacks automation"""
        # Similar to phone but with BlueStacks-specific areas
        x, y, w, h = self.target_window.left, self.target_window.top, self.target_window.width, self.target_window.height

        # BlueStacks click areas (adjust based on game layout)
        click_areas = [
            (x + w - 100, y + h - 100, "Build"),
            (x + 100, y + h - 100, "Upgrade"),
            (x + w//2, y + h//2, "Center"),
            (x + w - 50, y + 50, "Mail"),
        ]

        actions_performed = min(self.actions_per_cycle, len(click_areas))

        for i in range(actions_performed):
            if not self.bot_running:
                break

            click_x, click_y, area_name = click_areas[i]
            pyautogui.click(click_x, click_y)
            self.stats["clicks"] += 1
            time.sleep(self.click_speed)

    def update_status(self):
        """Update the status display"""
        if self.stats["start_time"]:
            runtime = time.time() - self.stats["start_time"]
            cycles_per_min = self.stats["cycles"] / (runtime / 60) if runtime > 0 else 0
            clicks_per_min = self.stats["clicks"] / (runtime / 60) if runtime > 0 else 0

            status = f"Cycles: {self.stats['cycles']} | Clicks: {self.stats['clicks']} | "
            status += f"Runtime: {runtime/60:.1f}m | Speed: {cycles_per_min:.1f} cyc/min, {clicks_per_min:.1f} click/min"

            if self.stats["errors"] > 0 or self.error_count > 0:
                status += f" | Errors: {self.stats['errors']} (Logged: {self.error_count})"

            # Update status in the main thread
            self.status_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {status}\n")
            self.status_text.see(tk.END)

    def show_stats(self):
        """Show final statistics"""
        if self.stats["start_time"]:
            runtime = time.time() - self.stats["start_time"]
            self.log(f"Session complete: {self.stats['cycles']} cycles, {self.stats['clicks']} clicks in {runtime/60:.1f} minutes")

    def close_other_windows(self):
        """Close other windows to improve performance"""
        closed = 0
        target_title = self.target_window.title if self.target_window else ""

        for window in gw.getAllWindows():
            if (window.title != target_title and
                "Bot Control Center" not in window.title and
                window.title.strip()):
                try:
                    window.close()
                    closed += 1
                except:
                    pass

        self.log(f"Closed {closed} other windows")

    def optimize_speed(self):
        """Optimize settings for phone-friendly performance"""
        # Use conservative but efficient speeds for phone mirroring
        self.click_speed_var.set(3.0)  # 3 seconds - fast but reliable for phones
        self.cycle_speed_var.set(8.0)  # 8 seconds - allow time for game processing
        self.actions_var.set(6)       # Reduced actions to prevent overwhelming
        self.focus_window_var.set(True)

        self.update_click_speed(3.0)
        self.update_cycle_speed(8.0)
        self.log("⚡ Optimized for phone-friendly performance: 3s clicks, 8s cycles")
        self.update_actions(6)

    def log(self, message):
        """Add message to both status and log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"{timestamp} - {message}\n"

        # Add to status (if available)
        if hasattr(self, 'status_text'):
            self.status_text.insert(tk.END, log_message)
            self.status_text.see(tk.END)

        # Add to log tab (if available)
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            # Add any pending logs
            if hasattr(self, '_pending_logs'):
                for pending_msg in self._pending_logs:
                    self.log_text.insert(tk.END, pending_msg)
                del self._pending_logs
        else:
            # Store messages until log_text is ready
            if not hasattr(self, '_pending_logs'):
                self._pending_logs = []
            self._pending_logs.append(log_message)

    def log_error(self, error, context="Unknown", operation="General", additional_info=None):
        """Comprehensive error logging with storage"""
        self.error_count += 1
        timestamp = datetime.now()

        # Get full stack trace
        stack_trace = traceback.format_exc()

        # Create detailed error record
        error_record = {
            "id": self.error_count,
            "timestamp": timestamp.isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "operation": operation,
            "stack_trace": stack_trace,
            "bot_state": {
                "running": self.bot_running,
                "mode": self.automation_mode,
                "current_action": self.current_action,
                "stats": self.stats.copy(),
                "target_window": getattr(self.target_window, 'title', None) if self.target_window else None
            },
            "additional_info": additional_info or {}
        }

        # Add to memory
        self.error_history.append(error_record)

        # Log to UI
        self.log(f"🚨 ERROR #{self.error_count}: {error_record['error_type']} in {context}")
        self.log(f"   Message: {error_record['error_message']}")
        self.log(f"   Operation: {operation}")

        # Save to file
        try:
            self.save_error_to_file(error_record)
            self.log(f"   📁 Error saved to: {self.error_log_file.name}")
        except Exception as save_error:
            self.log(f"   ⚠️ Failed to save error log: {save_error}")

        return error_record

    def save_error_to_file(self, error_record):
        """Save error record to JSON file"""
        # Load existing errors if file exists
        errors_data = {"errors": []}
        if self.error_log_file.exists():
            try:
                with open(self.error_log_file, 'r', encoding='utf-8') as f:
                    errors_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                errors_data = {"errors": []}

        # Add new error
        errors_data["errors"].append(error_record)
        errors_data["last_updated"] = datetime.now().isoformat()
        errors_data["error_count"] = len(errors_data["errors"])

        # Save back to file
        with open(self.error_log_file, 'w', encoding='utf-8') as f:
            json.dump(errors_data, f, indent=2, ensure_ascii=False)

    def get_error_summary(self):
        """Get comprehensive error summary"""
        if not self.error_history:
            return "No errors logged"

        summary = f"📊 ERROR SUMMARY ({len(self.error_history)} total errors):\n"

        # Group errors by type
        error_types = {}
        for error in self.error_history:
            error_type = error["error_type"]
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(error)

        # Summary by type
        for error_type, errors in error_types.items():
            summary += f"  {error_type}: {len(errors)} occurrences\n"
            if len(errors) <= 3:
                for error in errors:
                    summary += f"    - {error['context']}: {error['error_message'][:50]}...\n"
            else:
                summary += f"    - Latest: {errors[-1]['error_message'][:50]}...\n"

        summary += f"\n📁 Error log file: {self.error_log_file}"
        return summary

    def show_error_review_window(self):
        """Open window to review all errors"""
        error_window = tk.Toplevel(self.root)
        error_window.title(f"Dark War Bot - Error Review ({len(self.error_history)} errors)")
        error_window.geometry("800x600")

        # Create notebook for different views
        notebook = ttk.Notebook(error_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Summary tab
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="Summary")

        summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, font=('Consolas', 10))
        summary_text.pack(fill="both", expand=True, padx=5, pady=5)
        summary_text.insert(tk.END, self.get_error_summary())

        # Detailed errors tab
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="Detailed Errors")

        details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, font=('Consolas', 9))
        details_text.pack(fill="both", expand=True, padx=5, pady=5)

        if self.error_history:
            for i, error in enumerate(self.error_history, 1):
                details_text.insert(tk.END, f"ERROR #{i} - {error['timestamp']}\n")
                details_text.insert(tk.END, f"Type: {error['error_type']}\n")
                details_text.insert(tk.END, f"Context: {error['context']}\n")
                details_text.insert(tk.END, f"Operation: {error['operation']}\n")
                details_text.insert(tk.END, f"Message: {error['error_message']}\n")
                details_text.insert(tk.END, f"Bot State: {error['bot_state']}\n")
                details_text.insert(tk.END, f"Stack Trace:\n{error['stack_trace']}\n")
                details_text.insert(tk.END, "="*80 + "\n\n")
        else:
            details_text.insert(tk.END, "No errors to display")

        # Buttons
        button_frame = ttk.Frame(error_window)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Clear Errors",
                  command=self.clear_error_history).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export to File",
                  command=self.export_errors).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close",
                  command=error_window.destroy).pack(side="right", padx=5)

    def clear_error_history(self):
        """Clear all error history"""
        if messagebox.askyesno("Clear Errors", "Clear all error history? This cannot be undone."):
            self.error_history = []
            self.error_count = 0
            self.log("🗑️ Error history cleared")

    def export_errors(self):
        """Export errors to a text file"""
        if not self.error_history:
            messagebox.showinfo("Export Errors", "No errors to export")
            return

        try:
            export_file = self.error_log_dir / f"error_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write("DARK WAR BOT - ERROR EXPORT\n")
                f.write("="*50 + "\n\n")
                f.write(self.get_error_summary())
                f.write("\n\nDETAILED ERRORS:\n")
                f.write("="*50 + "\n\n")

                for i, error in enumerate(self.error_history, 1):
                    f.write(f"ERROR #{i} - {error['timestamp']}\n")
                    f.write(f"Type: {error['error_type']}\n")
                    f.write(f"Context: {error['context']}\n")
                    f.write(f"Message: {error['error_message']}\n")
                    f.write(f"Operation: {error['operation']}\n")
                    f.write(f"Bot State: {error['bot_state']}\n")
                    f.write("-" * 40 + "\n\n")

            messagebox.showinfo("Export Complete", f"Errors exported to:\n{export_file}")
            self.log(f"📤 Errors exported to: {export_file.name}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export errors:\n{e}")

    # Coordinate Setup Methods
    def refresh_coordinate_windows(self):
        """Refresh the list of available windows for coordinate logging"""
        try:
            windows = gw.getWindowsWithTitle("")  # Get all windows
            window_list = []

            for window in windows:
                if (window.title and
                    window.width > 100 and window.height > 100 and
                    window.title not in self.excluded_window_titles):
                    window_list.append(f"{window.title} ({window.width}x{window.height})")

            self.coord_window_combo['values'] = window_list
            if window_list and not self.coord_window_var.get():
                self.coord_window_var.set(window_list[0])

        except Exception as e:
            self.log(f"❌ Error refreshing coordinate windows: {e}")

    def set_coordinate_target_window(self):
        """Set the target window for coordinate logging"""
        selected = self.coord_window_var.get()
        if not selected:
            messagebox.showwarning("Window Selection", "Please select a window first")
            return

        try:
            # Extract window title from selection
            window_title = selected.split(" (")[0]

            if self.coordinate_logger.set_target_window(window_title):
                self.coord_window_status.set(f"✅ Target set: {window_title}")
                self.log(f"🎯 Coordinate target window set: {window_title}")
            else:
                self.coord_window_status.set("❌ Failed to set target window")
                self.log(f"❌ Failed to set coordinate target window: {window_title}")

        except Exception as e:
            self.log(f"❌ Error setting coordinate target window: {e}")
            self.coord_window_status.set("❌ Error setting target window")

    def start_coordinate_logging(self):
        """Start coordinate logging for the selected building type"""
        if not self.coordinate_logger:
            messagebox.showerror("Error", "Coordinate logger not available")
            return

        # Get selected building type
        building_selection = self.building_type_var.get()
        if not building_selection:
            messagebox.showwarning("Building Selection", "Please select a building type first")
            return

        building_type = building_selection.split(" - ")[0]
        building_name = building_selection.split(" - ")[1] if " - " in building_selection else building_type

        # Check if target window is set
        if not self.coordinate_logger.target_window:
            messagebox.showwarning("Window Required", "Please set a target window first")
            return

        # Start logging
        if self.coordinate_logger.start_logging_building(building_type, building_name):
            self.coord_logging_status.set(f"🖱️ Click on the {building_name} building...")
            self.start_logging_btn.config(state="disabled")
            self.stop_logging_btn.config(state="normal")
            self.log(f"📍 Started coordinate logging for {building_name}")

            # Show instruction messagebox
            messagebox.showinfo("Coordinate Logging Started",
                              f"Click on the {building_name} building in the game window.\n\n"
                              f"Make sure you are in SHELTER VIEW (not World map)!\n\n"
                              f"Click directly on the building name/level text.")
        else:
            messagebox.showerror("Error", f"Failed to start coordinate logging for {building_name}")

    def stop_coordinate_logging(self):
        """Stop coordinate logging"""
        if self.coordinate_logger:
            self.coordinate_logger.stop_logging()

    def on_coordinate_logging_started(self, building_type, building_name):
        """Callback when coordinate logging starts"""
        self.log(f"🖱️ Coordinate logging started for {building_name}")

    def on_coordinate_logging_stopped(self):
        """Callback when coordinate logging stops"""
        self.coord_logging_status.set("Ready to log coordinates")
        self.start_logging_btn.config(state="normal")
        self.stop_logging_btn.config(state="disabled")
        self.log("📍 Coordinate logging stopped")

    def on_coordinate_logged(self, coordinate_id, coordinate_entry):
        """Callback when a coordinate is successfully logged"""
        building_name = coordinate_entry['building_name']
        x = coordinate_entry['absolute']['x']
        y = coordinate_entry['absolute']['y']

        self.log(f"✅ Coordinate logged for {building_name}: ({x}, {y})")
        self.coord_logging_status.set(f"✅ Logged: {building_name} at ({x}, {y})")

        # Refresh the coordinates list
        self.refresh_coordinates_list()
        self.update_coordinate_statistics()

        # Show success message
        messagebox.showinfo("Coordinate Logged",
                          f"Successfully logged coordinate for {building_name}!\n\n"
                          f"Position: ({x}, {y})\n"
                          f"ID: {coordinate_id}")

    def refresh_coordinates_list(self):
        """Refresh the coordinates list in the tree view"""
        if not self.coordinate_logger:
            return

        try:
            # Clear existing items
            for item in self.coords_tree.get_children():
                self.coords_tree.delete(item)

            # Add coordinates to tree
            for coord_id, coord_data in self.coordinate_logger.coordinates.items():
                building_type = coord_data['building_type']
                building_name = coord_data['building_name']
                x = coord_data['absolute']['x']
                y = coord_data['absolute']['y']
                timestamp = coord_data['timestamp'][:19]  # Remove microseconds

                self.coords_tree.insert("", "end", iid=coord_id, values=(
                    building_type, building_name, f"({x}, {y})", timestamp
                ))

        except Exception as e:
            self.log(f"❌ Error refreshing coordinates list: {e}")

    def delete_selected_coordinate(self):
        """Delete the selected coordinate"""
        selected_items = self.coords_tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Required", "Please select a coordinate to delete")
            return

        if messagebox.askyesno("Delete Coordinate", "Delete the selected coordinate?"):
            for item_id in selected_items:
                if self.coordinate_logger.delete_coordinate(item_id):
                    self.coords_tree.delete(item_id)
                    self.log(f"🗑️ Deleted coordinate: {item_id}")

            self.update_coordinate_statistics()

    def test_selected_coordinate(self):
        """Test the selected coordinate by taking a screenshot of that region"""
        selected_items = self.coords_tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Required", "Please select a coordinate to test")
            return

        try:
            # Get the first selected coordinate
            coord_id = selected_items[0]
            coord_data = self.coordinate_logger.coordinates[coord_id]

            building_name = coord_data['building_name']
            x = coord_data['absolute']['x']
            y = coord_data['absolute']['y']

            # Test the coordinate by clicking it (or just showing where it would click)
            self.log(f"🧪 Testing coordinate for {building_name} at ({x}, {y})")

            # For now, just show the coordinate info
            messagebox.showinfo("Coordinate Test",
                              f"Coordinate Test Results:\n\n"
                              f"Building: {building_name}\n"
                              f"Position: ({x}, {y})\n"
                              f"Coordinate ID: {coord_id}\n\n"
                              f"This would click at the logged position in the game.")

        except Exception as e:
            self.log(f"❌ Error testing coordinate: {e}")
            messagebox.showerror("Test Failed", f"Failed to test coordinate: {e}")

    def export_coordinates(self):
        """Export coordinates to a JSON file"""
        if not self.coordinate_logger or not self.coordinate_logger.coordinates:
            messagebox.showwarning("No Coordinates", "No coordinates to export")
            return

        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Coordinates"
            )

            if filename:
                # Save coordinates to the selected file
                import shutil
                shutil.copy2(self.coordinate_logger.coordinates_file, filename)
                messagebox.showinfo("Export Complete", f"Coordinates exported to:\n{filename}")
                self.log(f"📤 Coordinates exported to: {filename}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export coordinates: {e}")

    def update_coordinate_statistics(self):
        """Update the coordinate statistics display"""
        if not self.coordinate_logger:
            return

        try:
            stats = self.coordinate_logger.get_coordinate_statistics()

            stats_text = f"Total Coordinates: {stats['total_coordinates']}\n"

            if stats['building_types']:
                stats_text += "Building Types:\n"
                for building_type, count in stats['building_types'].items():
                    stats_text += f"  • {building_type}: {count}\n"

            if stats['window_coverage']:
                coverage = stats['window_coverage']
                stats_text += f"Window Coverage: X({coverage.get('x_range', 'N/A')}) Y({coverage.get('y_range', 'N/A')})\n"

            if stats['last_updated']:
                stats_text += f"Last Updated: {stats['last_updated'][:19]}"

            self.coord_stats_text.delete(1.0, tk.END)
            self.coord_stats_text.insert(1.0, stats_text)

        except Exception as e:
            self.log(f"❌ Error updating coordinate statistics: {e}")

    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BotControlCenter()
    app.run()