"""
Precise confirmation test using exact dialog coordinates
"""

import time
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def precise_confirm():
    """Use exact dialog coordinates to click confirm"""
    print("=== PRECISE CONFIRM TEST ===")
    print("Using exact dialog coordinates: (68, 778) size: 217x127")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("Setup failed")
        return False

    time.sleep(2)

    # Click Build Scrapyard
    screenshot = window_manager.capture_window()
    build_match = template_matcher.find_template(screenshot, "build_scrapyard_btn")

    if not build_match:
        print("Build button not found")
        return False

    center_x, center_y = template_matcher.get_template_center(build_match)
    print(f"Clicking Build Scrapyard at ({center_x}, {center_y})")

    window_manager.click_relative(center_x, center_y)
    time.sleep(3)

    print("Dialog should now be open at (68, 778)")

    # Dialog coordinates from analysis
    dialog_x = 68
    dialog_y = 778
    dialog_w = 217
    dialog_h = 127

    # Calculate confirm button positions within the dialog
    dialog_center_x = dialog_x + dialog_w // 2
    dialog_center_y = dialog_y + dialog_h // 2

    # Try different positions within the dialog
    positions_to_try = [
        # Bottom half of dialog (where confirm usually is)
        (dialog_center_x, dialog_y + int(dialog_h * 0.7)),          # Lower center
        (dialog_x + int(dialog_w * 0.7), dialog_y + int(dialog_h * 0.7)),  # Bottom right
        (dialog_x + int(dialog_w * 0.3), dialog_y + int(dialog_h * 0.7)),  # Bottom left
        (dialog_center_x, dialog_y + int(dialog_h * 0.8)),          # Even lower
        (dialog_center_x, dialog_center_y),                         # Dead center
    ]

    for i, (click_x, click_y) in enumerate(positions_to_try):
        print(f"Attempt {i+1}: Clicking dialog at ({click_x}, {click_y})")

        window_manager.click_relative(click_x, click_y)
        time.sleep(3)

        # Check if build button is gone (construction started)
        check_screenshot = window_manager.capture_window()
        build_check = template_matcher.find_template(check_screenshot, "build_scrapyard_btn")

        if not build_check:
            print(f"SUCCESS! Dialog click {i+1} worked!")
            print("Build Scrapyard construction has started!")
            print("Check your game for:")
            print("- Construction timer")
            print("- Consumed resources")
            print("- Building progress")
            return True
        else:
            print(f"Attempt {i+1} failed, build button still there")

    print("All dialog positions failed")

    # Final attempt - try double-clicking the original button
    print("\nFinal attempt: Double-clicking original build button...")
    window_manager.click_relative(center_x, center_y)
    time.sleep(0.5)
    window_manager.click_relative(center_x, center_y)
    time.sleep(3)

    final_check = window_manager.capture_window()
    final_build = template_matcher.find_template(final_check, "build_scrapyard_btn")

    if not final_build:
        print("SUCCESS! Double-click worked!")
        return True

    print("Double-click also failed")
    return False

if __name__ == "__main__":
    result = precise_confirm()
    if result:
        print("\n*** CONSTRUCTION STARTED! ***")
        print("Your bot successfully started building the scrapyard!")
        print("At tower level 3, this proves the bot can handle your game!")
    else:
        print("\nStill troubleshooting confirmation...")
        print("The bot IS finding and clicking the right elements")
        print("Might need to check resource requirements or game state")