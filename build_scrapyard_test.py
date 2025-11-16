"""
Simple test to build the scrapyard
"""

import time
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def build_scrapyard():
    """Try to build the scrapyard"""
    print("=== BUILD SCRAPYARD TEST ===")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    # Setup
    if not window_manager.find_window() or not window_manager.focus_window():
        print("ERROR: Could not setup BlueStacks")
        return False

    print("BlueStacks ready")
    time.sleep(2)

    # Get screenshot
    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("ERROR: No screenshot")
        return False

    # Find build button
    build_match = template_matcher.find_template(screenshot, "build_scrapyard_btn")
    if build_match:
        center_x, center_y = template_matcher.get_template_center(build_match)
        print(f"Found Build Scrapyard button at ({center_x}, {center_y})")
        print(f"Confidence: {build_match.confidence:.3f}")

        print("\nClicking Build Scrapyard in 3 seconds...")
        print("WATCH YOUR GAME SCREEN!")

        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)

        print("CLICKING BUILD SCRAPYARD!")
        window_manager.click_relative(center_x, center_y)

        print("Waiting 10 seconds for construction to start...")
        time.sleep(10)

        # Check if button is gone (construction started)
        new_screenshot = window_manager.capture_window()
        if new_screenshot is not None:
            build_match_after = template_matcher.find_template(new_screenshot, "build_scrapyard_btn")

            if not build_match_after:
                print("SUCCESS: Build button disappeared - construction started!")
                return True
            elif build_match_after.confidence < build_match.confidence - 0.1:
                print("PARTIAL SUCCESS: Button changed - something happened!")
                return True
            else:
                print("NO CHANGE: Button still there - check resources or game state")
                return False
    else:
        print("Build Scrapyard button not found")
        return False

if __name__ == "__main__":
    success = build_scrapyard()
    if success:
        print("\nThe bot successfully performed a game action!")
    else:
        print("\nThe bot action didn't work as expected.")