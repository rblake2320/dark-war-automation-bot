"""
Dark War Survival Bot Control Center
Unified interface for BlueStacks and Phone automation with speed controls
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import pygetwindow as gw
import pyautogui
from datetime import datetime
import json
import os

class BotControlCenter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dark War Survival Bot Control Center")
        self.root.geometry("800x600")

        # Bot state
        self.bot_running = False
        self.bot_thread = None
        self.target_window = None
        self.automation_mode = "phone"  # "phone" or "bluestacks"

        # Performance settings
        self.click_speed = 0.1  # Delay between clicks
        self.cycle_speed = 1.0  # Delay between cycles
        self.actions_per_cycle = 5

        # Statistics
        self.stats = {
            "cycles": 0,
            "clicks": 0,
            "start_time": None,
            "errors": 0
        }

        self.setup_ui()
        self.refresh_windows()

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

    def refresh_windows(self):
        """Refresh the list of available windows"""
        windows = []
        try:
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if (window.title.strip() and
                    window.width > 200 and
                    window.height > 300 and
                    window.visible):

                    display_name = f"{window.title[:50]} [{window.width}x{window.height}]"
                    windows.append(display_name)

            self.window_combo['values'] = windows

            # Auto-select based on mode
            if self.mode_var.get() == "phone":
                for i, window_name in enumerate(windows):
                    if "Dark War" in window_name or "S22" in window_name:
                        self.window_combo.current(i)
                        break
            else:  # BlueStacks
                for i, window_name in enumerate(windows):
                    if "BlueStacks" in window_name:
                        self.window_combo.current(i)
                        break

            self.log(f"Found {len(windows)} available windows")

        except Exception as e:
            self.log(f"Error refreshing windows: {e}")

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
        """Test clicking on the target window"""
        window = self.get_target_window()
        if not window:
            self.log("No window selected for testing")
            return

        try:
            window.activate()
            time.sleep(0.5)

            x, y, w, h = window.left, window.top, window.width, window.height
            center_x = x + w // 2
            center_y = y + h // 2

            self.log(f"Test clicking at ({center_x}, {center_y})")
            pyautogui.click(center_x, center_y)
            self.log("Test click performed!")

        except Exception as e:
            self.log(f"Test click failed: {e}")

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
        """Main bot automation loop"""
        while self.bot_running:
            try:
                # Focus window if enabled
                if self.focus_window_var.get():
                    self.target_window.activate()
                    time.sleep(0.1)

                # Perform automation cycle
                if self.automation_mode == "phone":
                    self.phone_automation_cycle()
                else:
                    self.bluestacks_automation_cycle()

                self.stats["cycles"] += 1

                # Update status every 10 cycles
                if self.stats["cycles"] % 10 == 0:
                    self.root.after(0, self.update_status)

                # Wait between cycles
                time.sleep(self.cycle_speed)

            except Exception as e:
                self.stats["errors"] += 1
                self.root.after(0, lambda: self.log(f"Bot error: {e}"))
                time.sleep(1)  # Brief pause on error

    def phone_automation_cycle(self):
        """Perform one cycle of phone automation"""
        x, y, w, h = self.target_window.left, self.target_window.top, self.target_window.width, self.target_window.height

        # Define click areas based on enabled settings
        click_areas = []

        if self.phone_areas["mail"].get():
            click_areas.append((x + w - 30, y + h//2, "Mail"))
        if self.phone_areas["heroes"].get():
            click_areas.append((x + 50, y + h - 80, "Heroes"))
        if self.phone_areas["world"].get():
            click_areas.append((x + w - 50, y + h - 80, "World"))
        if self.phone_areas["events"].get():
            click_areas.append((x + w - 40, y + 200, "Events"))
        if self.phone_areas["vip"].get():
            click_areas.append((x + 40, y + 100, "VIP"))
        if self.phone_areas["center"].get():
            click_areas.append((x + w//2, y + h//2, "Center"))

        # Perform clicks
        actions_performed = min(self.actions_per_cycle, len(click_areas))

        for i in range(actions_performed):
            if not self.bot_running:
                break

            click_x, click_y, area_name = click_areas[i]
            pyautogui.click(click_x, click_y)
            self.stats["clicks"] += 1

            # Brief delay between clicks
            time.sleep(self.click_speed)

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

    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BotControlCenter()
    app.run()