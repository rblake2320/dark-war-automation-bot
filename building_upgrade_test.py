"""
Test clicking on building to upgrade it
"""

import time
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def test_building_upgrade():
    """Click on a building to try upgrading it"""
    print("=== BUILDING UPGRADE TEST ===")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("ERROR: Could not access BlueStacks")
        return False

    time.sleep(2)

    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("ERROR: No screenshot")
        return False

    # Find building with upgrade number 2
    upgrade_match = template_matcher.find_template(screenshot, "upgrade_number_2")
    if upgrade_match:
        center_x, center_y = template_matcher.get_template_center(upgrade_match)

        # Click on the building (above the number)
        building_x = center_x
        building_y = center_y - 50  # Click well above the number to hit the building

        print(f"Found building with upgrade level 2")
        print(f"Number at: ({center_x}, {center_y})")
        print(f"Will click building at: ({building_x}, {building_y})")

        print("\nClicking building in 3 seconds...")
        print("WATCH FOR BUILDING MENU TO OPEN!")

        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)

        print("CLICKING BUILDING!")
        window_manager.click_relative(building_x, building_y)

        print("Waiting for building menu to appear...")
        time.sleep(5)

        # Check if anything changed
        new_screenshot = window_manager.capture_window()
        if new_screenshot is not None:
            # Look for the building upgrade number again
            upgrade_match_after = template_matcher.find_template(new_screenshot, "upgrade_number_2")

            if not upgrade_match_after:
                print("SUCCESS: Building interface opened (number disappeared)!")
                print("Look for upgrade buttons or building info!")
                return True
            else:
                print("Building menu might have opened briefly")
                print("Try clicking closer to the center of the building")
                return False

    else:
        print("No building with upgrade level 2 found")
        return False

if __name__ == "__main__":
    success = test_building_upgrade()
    if success:
        print("\nThe bot opened a building interface!")
        print("This proves the bot CAN affect your game!")
    else:
        print("\nLet's try a different approach...")