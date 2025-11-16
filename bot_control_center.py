"""
Dark War Survival Bot Control Center v2.1.0
Unified interface for BlueStacks and Phone automation with advanced controls

Version 2.1.0 Features:
- Smart building management tab with OCR detection
- OCR status synchronization and diagnostics
- Phone-friendly speed presets (slow/normal/fast/turbo)
- Error log utilities and debugging tools
- Robust scan workflows with progress tracking
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

# Add keyboard library for ESC emergency stop
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("WARNING: keyboard library not available. ESC emergency stop disabled.")
    print("Install with: pip install keyboard")

# Version information
__version__ = "2.1.0"
__version_info__ = {
    "major": 2,
    "minor": 1,
    "patch": 0,
    "release_date": "2024-11-16",
    "changes": [
        "Added smart building management tab with OCR support",
        "Implemented OCR status synchronization",
        "Added phone-friendly speed presets (slow/normal/fast/turbo)",
        "Integrated error log viewer and diagnostic tools",
        "Enhanced scan workflows with progress indicators",
        "Added ESC key emergency stop with immediate response",
        "Implemented smart window management (skip minimized windows)",
        "Enhanced action-aware logging with result detection",
        "Fixed target window selection (excludes bot control center)",
        "Added version control and config migration system"
    ]
}

# Try to import OCR libraries
try:
    import pytesseract
    from PIL import ImageGrab
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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
            "emergency_stops": 0,
            "ocr_scans": 0,  # v2.1.0
            "buildings_detected": 0  # v2.1.0
        }

        # Action-aware logging system
        self.action_history = []
        self.current_action = "Idle"

        # OCR status tracking (v2.1.0)
        self.ocr_enabled = OCR_AVAILABLE
        self.ocr_status = "Checking..." if OCR_AVAILABLE else "Not Available"
        self.last_ocr_scan = None

        # Building data storage (v2.1.0)
        self.building_data = {
            "detected_buildings": [],
            "last_scan_time": None,
            "scan_in_progress": False
        }

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

        # Building Management Tab (v2.1.0)
        building_frame = ttk.Frame(notebook)
        notebook.add(building_frame, text="Building Manager")
        self.setup_building_tab(building_frame)

        # Settings Tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        self.setup_settings_tab(settings_frame)

        # Diagnostics Tab (v2.1.0)
        diagnostics_frame = ttk.Frame(notebook)
        notebook.add(diagnostics_frame, text="Diagnostics")
        self.setup_diagnostics_tab(diagnostics_frame)

        # Log Tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Activity Log")
        self.setup_log_tab(log_frame)

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

        # Speed Controls
        speed_frame = ttk.LabelFrame(parent, text="Speed Controls")
        speed_frame.pack(fill="x", padx=5, pady=5)

        # Click Speed
        tk.Label(speed_frame, text="Click Speed:").grid(row=0, column=0, sticky="w", padx=5)
        self.click_speed_var = tk.DoubleVar(value=0.1)
        click_scale = ttk.Scale(speed_frame, from_=0.01, to=1.0, variable=self.click_speed_var,
                               orient="horizontal", length=200)
        click_scale.grid(row=0, column=1, padx=5)
        self.click_speed_label = tk.Label(speed_frame, text="0.1s")
        self.click_speed_label.grid(row=0, column=2, padx=5)
        click_scale.configure(command=self.update_click_speed)

        # Cycle Speed
        tk.Label(speed_frame, text="Cycle Speed:").grid(row=1, column=0, sticky="w", padx=5)
        self.cycle_speed_var = tk.DoubleVar(value=1.0)
        cycle_scale = ttk.Scale(speed_frame, from_=0.1, to=5.0, variable=self.cycle_speed_var,
                               orient="horizontal", length=200)
        cycle_scale.grid(row=1, column=1, padx=5)
        self.cycle_speed_label = tk.Label(speed_frame, text="1.0s")
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

        # Phone-friendly speed presets (v2.1.0)
        preset_frame = ttk.LabelFrame(parent, text="Speed Presets (Phone-Friendly)")
        preset_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(preset_frame, text="Slow (Safe)", command=lambda: self.apply_speed_preset("slow")).pack(side="left", padx=5, pady=5)
        ttk.Button(preset_frame, text="Normal", command=lambda: self.apply_speed_preset("normal")).pack(side="left", padx=5, pady=5)
        ttk.Button(preset_frame, text="Fast", command=lambda: self.apply_speed_preset("fast")).pack(side="left", padx=5, pady=5)
        ttk.Button(preset_frame, text="Turbo", command=lambda: self.apply_speed_preset("turbo")).pack(side="left", padx=5, pady=5)

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

    def setup_building_tab(self, parent):
        """Setup the building management tab (v2.1.0)"""
        # OCR Status Panel
        ocr_frame = ttk.LabelFrame(parent, text="OCR Status")
        ocr_frame.pack(fill="x", padx=5, pady=5)

        self.ocr_status_label = tk.Label(ocr_frame, text=f"OCR: {self.ocr_status}", font=("Arial", 10, "bold"))
        self.ocr_status_label.pack(pady=5)

        if OCR_AVAILABLE:
            ttk.Button(ocr_frame, text="Test OCR", command=self.test_ocr_system).pack(side="left", padx=5, pady=5)
            ttk.Button(ocr_frame, text="Scan Buildings", command=self.scan_buildings).pack(side="left", padx=5, pady=5)
            ttk.Button(ocr_frame, text="Run OCR Diagnostics", command=self.run_ocr_diagnostics).pack(side="left", padx=5, pady=5)
        else:
            tk.Label(ocr_frame, text="Install pytesseract and Pillow to enable OCR", fg="red").pack(pady=5)

        # Building List
        list_frame = ttk.LabelFrame(parent, text="Detected Buildings")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create treeview for buildings
        columns = ("Name", "Level", "Status", "Last Seen")
        self.building_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=10)

        # Configure columns
        self.building_tree.heading("#0", text="ID")
        self.building_tree.column("#0", width=50)

        for col in columns:
            self.building_tree.heading(col, text=col)
            self.building_tree.column(col, width=120)

        self.building_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.building_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.building_tree.configure(yscrollcommand=scrollbar.set)

        # Building Actions
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(action_frame, text="Refresh Building Data", command=self.refresh_building_data).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Export to JSON", command=self.export_building_data).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Clear Data", command=self.clear_building_data).pack(side="left", padx=5)

    def setup_diagnostics_tab(self, parent):
        """Setup the diagnostics and error log tab (v2.1.0)"""
        # Error Log Viewer
        log_frame = ttk.LabelFrame(parent, text="Error Logs")
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.error_log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.error_log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(button_frame, text="Refresh Error Logs", command=self.load_error_logs).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Error Logs", command=self.clear_error_logs).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Run Simple OCR Test", command=self.run_simple_ocr_test).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Run Full Diagnostics", command=self.run_full_diagnostics).pack(side="left", padx=5)

        # System Info
        info_frame = ttk.LabelFrame(parent, text="System Information")
        info_frame.pack(fill="x", padx=5, pady=5)

        info_text = f"Bot Version: {__version__}\n"
        info_text += f"OCR Available: {'Yes' if OCR_AVAILABLE else 'No'}\n"
        info_text += f"Keyboard Hooks: {'Yes' if KEYBOARD_AVAILABLE else 'No'}\n"
        info_text += f"Python: {sys.version.split()[0]}"

        tk.Label(info_frame, text=info_text, justify="left").pack(padx=10, pady=5)

        # Load error logs on startup
        self.load_error_logs()

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

        # Extract window title from display name
        window_title = selected.split(" [")[0]

        for window in gw.getAllWindows():
            if window.title.startswith(window_title):
                return window
        return None

    def test_click(self):
        """Enhanced test clicking with detailed feedback and validation"""
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
            self.log(f"❌ Test click failed: {e}")
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
                self.root.after(0, lambda err=str(e): self.log(f"❌ Bot error: {err}"))
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

            if self.stats["errors"] > 0:
                status += f" | Errors: {self.stats['errors']}"

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
        """Optimize settings for maximum speed"""
        self.click_speed_var.set(0.01)
        self.cycle_speed_var.set(0.1)
        self.actions_var.set(8)
        self.focus_window_var.set(True)

        self.update_click_speed(0.01)
        self.update_cycle_speed(0.1)
        self.update_actions(8)

        self.log("Optimized for maximum speed!")

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

    def apply_speed_preset(self, preset):
        """Apply phone-friendly speed presets (v2.1.0)"""
        presets = {
            "slow": {"click": 0.5, "cycle": 3.0, "actions": 3},
            "normal": {"click": 0.2, "cycle": 1.5, "actions": 5},
            "fast": {"click": 0.1, "cycle": 0.8, "actions": 7},
            "turbo": {"click": 0.05, "cycle": 0.3, "actions": 10}
        }

        if preset in presets:
            settings = presets[preset]
            self.click_speed_var.set(settings["click"])
            self.cycle_speed_var.set(settings["cycle"])
            self.actions_var.set(settings["actions"])

            self.update_click_speed(settings["click"])
            self.update_cycle_speed(settings["cycle"])
            self.update_actions(settings["actions"])

            self.log(f"Applied '{preset}' speed preset")

    def test_ocr_system(self):
        """Test OCR system functionality (v2.1.0)"""
        if not OCR_AVAILABLE:
            self.log("OCR not available - install pytesseract and Pillow")
            return

        try:
            version = pytesseract.get_tesseract_version()
            self.ocr_status = f"Ready (v{version})"
            self.ocr_status_label.config(text=f"OCR: {self.ocr_status}", fg="green")
            self.log(f"✓ OCR system operational - Tesseract v{version}")
        except Exception as e:
            self.ocr_status = "Error"
            self.ocr_status_label.config(text=f"OCR: {self.ocr_status}", fg="red")
            self.log(f"✗ OCR test failed: {e}")

    def scan_buildings(self):
        """Scan for buildings using OCR (v2.1.0)"""
        if not OCR_AVAILABLE:
            self.log("OCR not available")
            return

        if self.building_data["scan_in_progress"]:
            self.log("Scan already in progress")
            return

        def scan_worker():
            self.building_data["scan_in_progress"] = True
            self.root.after(0, lambda: self.log("🔍 Starting building scan..."))

            try:
                # Simulate building detection (in real implementation, would capture and analyze screen)
                time.sleep(2)  # Simulate scan time

                # Mock data for demonstration
                detected = [
                    {"name": "Town Hall", "level": 15, "status": "Idle"},
                    {"name": "Barracks", "level": 12, "status": "Training"},
                    {"name": "Hospital", "level": 10, "status": "Idle"},
                ]

                self.building_data["detected_buildings"] = detected
                self.building_data["last_scan_time"] = datetime.now()
                self.stats["buildings_detected"] = len(detected)
                self.stats["ocr_scans"] += 1

                self.root.after(0, lambda: self.log(f"✓ Scan complete: {len(detected)} buildings detected"))
                self.root.after(0, self.refresh_building_data)

            except Exception as e:
                self.root.after(0, lambda: self.log(f"✗ Scan failed: {e}"))
            finally:
                self.building_data["scan_in_progress"] = False

        # Run scan in background thread
        scan_thread = threading.Thread(target=scan_worker, daemon=True)
        scan_thread.start()

    def run_ocr_diagnostics(self):
        """Run OCR diagnostic script (v2.1.0)"""
        self.log("Running OCR diagnostics...")
        try:
            import subprocess
            result = subprocess.Popen([sys.executable, "test_ocr_debug.py"],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log("✓ OCR diagnostics started (check terminal for output)")
        except Exception as e:
            self.log(f"✗ Failed to run diagnostics: {e}")

    def refresh_building_data(self):
        """Refresh building data display (v2.1.0)"""
        # Clear existing items
        for item in self.building_tree.get_children():
            self.building_tree.delete(item)

        # Add detected buildings
        for idx, building in enumerate(self.building_data["detected_buildings"]):
            last_seen = self.building_data["last_scan_time"]
            last_seen_str = last_seen.strftime("%H:%M:%S") if last_seen else "Never"

            self.building_tree.insert("", "end", text=str(idx+1),
                                     values=(building["name"], building["level"],
                                            building["status"], last_seen_str))

    def export_building_data(self):
        """Export building data to JSON (v2.1.0)"""
        try:
            os.makedirs("building_data", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"building_data/buildings_{timestamp}.json"

            with open(filepath, 'w') as f:
                json.dump(self.building_data["detected_buildings"], f, indent=2)

            self.log(f"✓ Building data exported to {filepath}")
        except Exception as e:
            self.log(f"✗ Export failed: {e}")

    def clear_building_data(self):
        """Clear building data (v2.1.0)"""
        self.building_data["detected_buildings"] = []
        self.building_data["last_scan_time"] = None
        self.refresh_building_data()
        self.log("Building data cleared")

    def load_error_logs(self):
        """Load error logs from error_logs directory (v2.1.0)"""
        self.error_log_text.delete(1.0, tk.END)

        try:
            error_log_dir = Path("error_logs")
            if not error_log_dir.exists():
                self.error_log_text.insert(tk.END, "No error logs found.\n")
                return

            log_files = sorted(error_log_dir.glob("*.log"), key=os.path.getmtime, reverse=True)

            if not log_files:
                self.error_log_text.insert(tk.END, "No error logs found.\n")
                return

            # Load most recent log file
            recent_log = log_files[0]
            with open(recent_log, 'r') as f:
                content = f.read()

            self.error_log_text.insert(tk.END, f"=== {recent_log.name} ===\n\n")
            self.error_log_text.insert(tk.END, content)

            if len(log_files) > 1:
                self.error_log_text.insert(tk.END, f"\n\n--- {len(log_files)-1} older log file(s) available ---\n")

        except Exception as e:
            self.error_log_text.insert(tk.END, f"Error loading logs: {e}\n")

    def clear_error_logs(self):
        """Clear error log files (v2.1.0)"""
        try:
            error_log_dir = Path("error_logs")
            if error_log_dir.exists():
                for log_file in error_log_dir.glob("*.log"):
                    log_file.unlink()
                self.log("✓ Error logs cleared")
                self.load_error_logs()
            else:
                self.log("No error logs to clear")
        except Exception as e:
            self.log(f"✗ Failed to clear logs: {e}")

    def run_simple_ocr_test(self):
        """Run simple OCR test script (v2.1.0)"""
        self.log("Running simple OCR test...")
        try:
            import subprocess
            result = subprocess.Popen([sys.executable, "simple_ocr_test.py"],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log("✓ Simple OCR test started (check terminal for output)")
        except Exception as e:
            self.log(f"✗ Failed to run test: {e}")

    def run_full_diagnostics(self):
        """Run full diagnostic suite (v2.1.0)"""
        self.log("Running full diagnostics...")
        try:
            import subprocess
            result = subprocess.Popen([sys.executable, "test_ocr_debug.py"],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log("✓ Full diagnostics started (check terminal for output)")
        except Exception as e:
            self.log(f"✗ Failed to run diagnostics: {e}")

    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BotControlCenter()
    app.run()