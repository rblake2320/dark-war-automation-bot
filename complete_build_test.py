"""
Complete build sequence - handle confirmation dialogs
"""

import time
import cv2
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def complete_build_sequence():
    """Full build sequence with confirmation handling"""
    print("=== COMPLETE BUILD SEQUENCE ===")
    print("This will click Build Scrapyard AND handle any confirmation dialogs")
    print()

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("ERROR: Could not access game")
        return False

    time.sleep(2)

    print("STEP 1: Take initial screenshot")
    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("ERROR: No screenshot")
        return False

    cv2.imwrite("step1_initial.png", screenshot)
    print("Initial state saved")

    print("\nSTEP 2: Find and click Build Scrapyard")
    build_match = template_matcher.find_template(screenshot, "build_scrapyard_btn")

    if not build_match:
        print("ERROR: Build Scrapyard button not found")
        return False

    center_x, center_y = template_matcher.get_template_center(build_match)
    print(f"Found Build Scrapyard at ({center_x}, {center_y})")

    print("Clicking Build Scrapyard...")
    window_manager.click_relative(center_x, center_y)

    print("\nSTEP 3: Wait for confirmation dialog")
    time.sleep(3)  # Wait for dialog to appear

    # Take screenshot after first click
    step2_screenshot = window_manager.capture_window()
    cv2.imwrite("step2_after_click.png", step2_screenshot)

    # Check if screen changed (dialog opened)
    diff = cv2.absdiff(screenshot, step2_screenshot)
    change_amount = diff.sum()
    print(f"Screen change after click: {change_amount}")

    if change_amount > 1000000:
        print("Dialog likely opened! Looking for confirmation buttons...")

        # Common confirmation button patterns
        confirm_patterns = [
            # Look for green buttons, checkmarks, "Build", "Confirm", "Yes" etc.
            # We'll search for green colored regions that could be confirm buttons
        ]

        # Convert to HSV to find green buttons
        hsv = cv2.cvtColor(step2_screenshot, cv2.COLOR_BGR2HSV)

        # Green color range for buttons
        lower_green = cv2.array([40, 50, 50])
        upper_green = cv2.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        # Find green regions (potential confirm buttons)
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        potential_buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # Button-sized areas
                x, y, w, h = cv2.boundingRect(contour)
                potential_buttons.append((x + w//2, y + h//2, area))

        if potential_buttons:
            # Sort by area (bigger buttons more likely to be confirm)
            potential_buttons.sort(key=lambda x: x[2], reverse=True)

            print(f"Found {len(potential_buttons)} potential confirm buttons")

            # Click the largest green button
            confirm_x, confirm_y, area = potential_buttons[0]
            print(f"Clicking potential confirm button at ({confirm_x}, {confirm_y})")

            window_manager.click_relative(confirm_x, confirm_y)

            print("\nSTEP 4: Wait for construction to start")
            time.sleep(5)

            # Check final state
            final_screenshot = window_manager.capture_window()
            cv2.imwrite("step3_final.png", final_screenshot)

            # Check if build button is gone (construction started)
            build_match_final = template_matcher.find_template(final_screenshot, "build_scrapyard_btn")

            if not build_match_final:
                print("SUCCESS! Build Scrapyard button is gone - construction started!")
                print("Check your game for:")
                print("- Construction timer")
                print("- Resources consumed")
                print("- Building in progress")
                return True
            else:
                print("Build button still there, but dialog was handled")
                print("Might need more resources or different approach")
                return False
        else:
            print("No confirm buttons found in dialog")

            # Try clicking in common confirm button areas
            height, width = step2_screenshot.shape[:2]

            # Common confirm button positions
            confirm_areas = [
                (width // 2, height // 2 + 50),      # Center-bottom of dialog
                (width // 2 + 100, height // 2),     # Right side of dialog
                (width // 2, height - 100),          # Bottom center
            ]

            for i, (click_x, click_y) in enumerate(confirm_areas):
                print(f"Trying confirm area {i+1}: ({click_x}, {click_y})")
                window_manager.click_relative(click_x, click_y)
                time.sleep(2)

                # Check if build button disappeared
                test_screenshot = window_manager.capture_window()
                build_test = template_matcher.find_template(test_screenshot, "build_scrapyard_btn")
                if not build_test:
                    print(f"SUCCESS! Area {i+1} worked - construction started!")
                    return True

            print("Could not find working confirm button")
            return False
    else:
        print("No dialog appeared - build might have started immediately")

        # Check if build button disappeared
        build_match_immediate = template_matcher.find_template(step2_screenshot, "build_scrapyard_btn")
        if not build_match_immediate:
            print("SUCCESS! Build started immediately!")
            return True
        else:
            print("Build button still there and no dialog - might need resources")
            return False

if __name__ == "__main__":
    success = complete_build_sequence()

    print(f"\n{'='*50}")
    print("Files created for analysis:")
    print("- step1_initial.png (before clicking)")
    print("- step2_after_click.png (after first click)")
    print("- step3_final.png (final state)")

    if success:
        print("\n🎉 BUILD SEQUENCE SUCCESSFUL!")
        print("The scrapyard construction should have started!")
    else:
        print("\n❌ BUILD SEQUENCE FAILED")
        print("Check the screenshot files to see what happened")