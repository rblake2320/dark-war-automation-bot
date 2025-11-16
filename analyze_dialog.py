"""
Analyze the confirmation dialog that appears
"""

import cv2
import numpy as np
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config
import time

def analyze_dialog():
    """Click build button and analyze the dialog that appears"""
    print("=== DIALOG ANALYSIS ===")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("Setup failed")
        return

    time.sleep(2)

    # Get initial state
    initial = window_manager.capture_window()
    build_match = template_matcher.find_template(initial, "build_scrapyard_btn")

    if not build_match:
        print("Build button not found")
        return

    # Click build button
    center_x, center_y = template_matcher.get_template_center(build_match)
    print(f"Clicking build button at ({center_x}, {center_y})")

    window_manager.click_relative(center_x, center_y)
    time.sleep(3)

    # Get dialog state
    dialog = window_manager.capture_window()
    cv2.imwrite("dialog_analysis.png", dialog)

    # Find differences
    diff = cv2.absdiff(initial, dialog)
    cv2.imwrite("dialog_diff.png", diff)

    # Create a mask of what changed
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
    cv2.imwrite("dialog_mask.png", mask)

    # Find the dialog area (largest changed region)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get the largest contour (likely the dialog)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        print(f"Dialog detected at: ({x}, {y}) size: {w}x{h}")

        # Extract just the dialog area
        dialog_area = dialog[y:y+h, x:x+w]
        cv2.imwrite("dialog_extracted.png", dialog_area)

        # Look for button-like regions in the dialog
        dialog_hsv = cv2.cvtColor(dialog_area, cv2.COLOR_BGR2HSV)

        # Look for different colored regions that could be buttons
        # Green buttons
        green_lower = np.array([40, 50, 50])
        green_upper = np.array([80, 255, 255])
        green_mask = cv2.inRange(dialog_hsv, green_lower, green_upper)
        cv2.imwrite("dialog_green_regions.png", green_mask)

        # Blue buttons
        blue_lower = np.array([100, 50, 50])
        blue_upper = np.array([130, 255, 255])
        blue_mask = cv2.inRange(dialog_hsv, blue_lower, blue_upper)
        cv2.imwrite("dialog_blue_regions.png", blue_mask)

        # White/light buttons
        white_lower = np.array([0, 0, 200])
        white_upper = np.array([180, 30, 255])
        white_mask = cv2.inRange(dialog_hsv, white_lower, white_upper)
        cv2.imwrite("dialog_white_regions.png", white_mask)

        # Find button candidates in each color
        for color_name, color_mask in [("green", green_mask), ("blue", blue_mask), ("white", white_mask)]:
            button_contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            print(f"\n{color_name.upper()} REGIONS:")
            for i, contour in enumerate(button_contours):
                area = cv2.contourArea(contour)
                if area > 200:  # Reasonable button size
                    bx, by, bw, bh = cv2.boundingRect(contour)
                    # Convert back to full screen coordinates
                    screen_x = x + bx + bw//2
                    screen_y = y + by + bh//2
                    print(f"  Button {i+1}: area={area:.0f}, screen_pos=({screen_x}, {screen_y})")

    print("\nFiles created:")
    print("- dialog_analysis.png (dialog state)")
    print("- dialog_diff.png (what changed)")
    print("- dialog_mask.png (change mask)")
    print("- dialog_extracted.png (just the dialog)")
    print("- dialog_*_regions.png (potential buttons by color)")

def test_specific_position():
    """Test clicking a specific position to confirm build"""
    print("\n=== TESTING SPECIFIC POSITIONS ===")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        return

    time.sleep(2)

    # Click build again
    screenshot = window_manager.capture_window()
    build_match = template_matcher.find_template(screenshot, "build_scrapyard_btn")

    if build_match:
        center_x, center_y = template_matcher.get_template_center(build_match)
        window_manager.click_relative(center_x, center_y)
        time.sleep(3)

        # Try a very specific position based on typical dialog layouts
        # Usually confirm buttons are in bottom right of dialog
        height, width = screenshot.shape[:2]

        # Try bottom-right area of screen (where confirm usually is)
        test_positions = [
            (width // 2 + 120, height // 2 + 80),  # Bottom right of dialog
            (width // 2 + 100, height // 2 + 100), # Further bottom right
            (width // 2 + 80, height // 2 + 120),  # Even further
        ]

        for i, (test_x, test_y) in enumerate(test_positions):
            print(f"Testing position {i+1}: ({test_x}, {test_y})")
            window_manager.click_relative(test_x, test_y)
            time.sleep(2)

            # Check if build button disappeared
            check_screenshot = window_manager.capture_window()
            build_check = template_matcher.find_template(check_screenshot, "build_scrapyard_btn")

            if not build_check:
                print(f"SUCCESS! Position {i+1} worked!")
                print("Scrapyard construction should have started!")
                return True

        print("None of the test positions worked")

    return False

if __name__ == "__main__":
    analyze_dialog()
    test_specific_position()