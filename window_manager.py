"""
Window detection and management for BlueStacks
"""

import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
import time
from typing import Tuple, Optional
import logging

class WindowManager:
    def __init__(self, window_title: str = "BlueStacks App Player"):
        self.window_title = window_title
        self.window = None
        self.logger = logging.getLogger(__name__)

    def find_window(self) -> bool:
        """Find and store reference to BlueStacks window"""
        try:
            # Try different variations of BlueStacks window titles
            variations = [
                "BlueStacks App Player",
                "BlueStacks",
                "BlueStacks 5",
                "BlueStacks 4"
            ]

            for title in variations:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    self.window = windows[0]
                    self.window_title = title
                    self.logger.info(f"Found window: {title}")
                    return True

            self.logger.error("BlueStacks window not found")
            return False

        except Exception as e:
            self.logger.error(f"Error finding window: {e}")
            return False

    def focus_window(self) -> bool:
        """Bring BlueStacks window to foreground"""
        if not self.window:
            if not self.find_window():
                return False

        try:
            # Restore window if minimized
            if self.window.isMinimized:
                self.window.restore()

            # Activate and bring to front
            self.window.activate()
            time.sleep(0.5)

            self.logger.info("Window focused successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error focusing window: {e}")
            return False

    def get_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """Get window position and size (x, y, width, height)"""
        if not self.window:
            if not self.find_window():
                return None

        try:
            return (self.window.left, self.window.top, self.window.width, self.window.height)
        except Exception as e:
            self.logger.error(f"Error getting window rect: {e}")
            return None

    def capture_window(self) -> Optional[np.ndarray]:
        """Capture screenshot of BlueStacks window"""
        rect = self.get_window_rect()
        if not rect:
            return None

        try:
            x, y, width, height = rect
            # Take screenshot of the specific window area
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            # Convert PIL image to OpenCV format
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return screenshot_cv

        except Exception as e:
            self.logger.error(f"Error capturing window: {e}")
            return None

    def click_relative(self, x: int, y: int, duration: float = 0.1) -> bool:
        """Click at position relative to window"""
        rect = self.get_window_rect()
        if not rect:
            return False

        try:
            window_x, window_y, _, _ = rect
            absolute_x = window_x + x
            absolute_y = window_y + y

            pyautogui.click(absolute_x, absolute_y, duration=duration)
            self.logger.debug(f"Clicked at relative position ({x}, {y})")
            return True

        except Exception as e:
            self.logger.error(f"Error clicking: {e}")
            return False

    def is_window_active(self) -> bool:
        """Check if BlueStacks window is currently active"""
        if not self.window:
            return False

        try:
            return self.window.isActive
        except Exception:
            return False