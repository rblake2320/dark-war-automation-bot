"""
Better building click with proper positioning
"""

import time
import cv2
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def better_building_test():
    """Click building with better positioning"""
    print("=== IMPROVED BUILDING TEST ===")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("ERROR: Setup failed")
        return False

    time.sleep(2)

    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("ERROR: No screenshot")
        return False

    print(f"Screenshot size: {screenshot.shape}")

    # Find building with upgrade number
    upgrade_match = template_matcher.find_template(screenshot, "upgrade_number_2")
    if upgrade_match:
        center_x, center_y = template_matcher.get_template_center(upgrade_match)

        print(f"Upgrade number found at: ({center_x}, {center_y})")

        # Better building click positioning - click down and left from the number
        building_x = center_x - 30  # Left of the number
        building_y = center_y + 30  # Below the number (into the building)

        # Make sure we're within screen bounds
        height, width = screenshot.shape[:2]
        building_x = max(50, min(building_x, width - 50))
        building_y = max(50, min(building_y, height - 50))

        print(f"Will click building at: ({building_x}, {building_y})")
        print("This should be on the actual building structure")

        # Save screenshot with click point marked
        marked_screenshot = screenshot.copy()
        cv2.circle(marked_screenshot, (building_x, building_y), 10, (0, 255, 0), 3)
        cv2.imwrite("click_target.png", marked_screenshot)
        print("Click target marked in click_target.png")

        print("\nClicking building in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)

        print("CLICKING BUILDING NOW!")
        result = window_manager.click_relative(building_x, building_y)
        print(f"Click result: {result}")

        print("Waiting 5 seconds to see if building menu opens...")
        time.sleep(5)

        # Take after screenshot
        new_screenshot = window_manager.capture_window()
        if new_screenshot is not None:
            cv2.imwrite("after_building_click.png", new_screenshot)

            # Calculate difference
            diff = cv2.absdiff(screenshot, new_screenshot)
            diff_sum = diff.sum()
            print(f"Screen change detected: {diff_sum}")

            if diff_sum > 5000000:  # Significant change
                print("SUCCESS: Major screen change detected!")
                print("Building interface likely opened!")
                return True
            elif diff_sum > 1000000:  # Minor change
                print("PARTIAL: Some change detected")
                return True
            else:
                print("NO CHANGE: Screen appears unchanged")
                return False

    else:
        print("No upgrade number 2 found")
        return False

if __name__ == "__main__":
    better_building_test()