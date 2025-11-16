"""
Simple confirmation test - just try common confirm button locations
"""

import time
import cv2
import numpy as np
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def simple_confirm_test():
    """Simple test to click Build and then try to confirm"""
    print("=== SIMPLE CONFIRM TEST ===")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("Setup failed")
        return False

    time.sleep(2)

    # Step 1: Click Build Scrapyard
    screenshot = window_manager.capture_window()
    build_match = template_matcher.find_template(screenshot, "build_scrapyard_btn")

    if not build_match:
        print("Build button not found")
        return False

    center_x, center_y = template_matcher.get_template_center(build_match)
    print(f"Clicking Build Scrapyard at ({center_x}, {center_y})")

    cv2.imwrite("before_build_click.png", screenshot)
    window_manager.click_relative(center_x, center_y)

    print("Waiting 3 seconds for dialog...")
    time.sleep(3)

    # Step 2: Take screenshot after click
    after_screenshot = window_manager.capture_window()
    cv2.imwrite("after_build_click.png", after_screenshot)

    diff = cv2.absdiff(screenshot, after_screenshot)
    change = diff.sum()
    print(f"Screen change detected: {change}")

    if change > 1000000:
        print("Dialog opened! Trying to confirm...")

        # Get screen dimensions
        height, width = after_screenshot.shape[:2]

        # Try common confirmation areas
        confirm_positions = [
            (width // 2, height // 2 + 100),     # Bottom center of dialog
            (width // 2 + 80, height // 2 + 50), # Bottom right of dialog
            (width // 2, height // 2 + 150),     # Lower center
            (width // 2 - 50, height // 2 + 100),# Bottom left
            (width // 2 + 50, height // 2 + 100) # Bottom right
        ]

        for i, (confirm_x, confirm_y) in enumerate(confirm_positions):
            print(f"Trying confirm position {i+1}: ({confirm_x}, {confirm_y})")

            # Click potential confirm button
            window_manager.click_relative(confirm_x, confirm_y)
            time.sleep(3)

            # Check if build button is gone
            test_screenshot = window_manager.capture_window()
            build_test = template_matcher.find_template(test_screenshot, "build_scrapyard_btn")

            if not build_test:
                print(f"SUCCESS! Position {i+1} worked!")
                print("Build Scrapyard construction started!")
                cv2.imwrite(f"success_after_confirm_{i+1}.png", test_screenshot)
                return True
            elif i == 0:
                # Save first attempt for analysis
                cv2.imwrite(f"confirm_attempt_{i+1}.png", test_screenshot)

        print("None of the confirm positions worked")

        # Try clicking anywhere in the center area (dialog background)
        print("Trying center dialog click...")
        window_manager.click_relative(width // 2, height // 2)
        time.sleep(3)

        final_test = window_manager.capture_window()
        build_final = template_matcher.find_template(final_test, "build_scrapyard_btn")

        if not build_final:
            print("SUCCESS! Center click worked!")
            return True

        print("Dialog handling failed")
        return False

    else:
        print("No dialog appeared, checking if build started immediately...")

        build_match_after = template_matcher.find_template(after_screenshot, "build_scrapyard_btn")
        if not build_match_after:
            print("SUCCESS! Build started immediately!")
            return True
        else:
            print("No change - might need resources")
            return False

if __name__ == "__main__":
    result = simple_confirm_test()
    if result:
        print("\n🎉 SCRAPYARD CONSTRUCTION STARTED!")
        print("Check your game for the building timer!")
    else:
        print("\n❌ Construction failed to start")
        print("Check screenshot files to see what happened")