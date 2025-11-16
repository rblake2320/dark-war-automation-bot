"""
Focused bot test that targets the Build Scrapyard button specifically
"""

import time
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def focused_scrapyard_test():
    """Test specifically clicking the Build Scrapyard button"""
    print("=== FOCUSED SCRAPYARD BUILD TEST ===")
    print("This will specifically target the 'Build Scrapyard' action")
    print()

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    # Setup
    if not window_manager.find_window():
        print("[ERROR] BlueStacks not found")
        return False

    if not window_manager.focus_window():
        print("[ERROR] Could not focus window")
        return False

    print("[OK] BlueStacks focused")
    time.sleep(2)

    # Capture screenshot
    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("[ERROR] Could not capture screenshot")
        return False

    print("[OK] Screenshot captured")

    # Look specifically for Build Scrapyard button
    print("\nLooking for Build Scrapyard button...")
    build_match = template_matcher.find_template(screenshot, "build_scrapyard_btn")

    if build_match:
        print(f"[FOUND] Build Scrapyard button!")
        print(f"Position: ({build_match.x}, {build_match.y})")
        print(f"Confidence: {build_match.confidence:.3f}")

        center_x, center_y = template_matcher.get_template_center(build_match)
        print(f"Center: ({center_x}, {center_y})")

        print("\n🎯 ABOUT TO BUILD SCRAPYARD")
        print("This should start construction of a new building!")
        print("Watch for:")
        print("- Build menu to appear")
        print("- Construction to start")
        print("- Resources to be consumed")
        print("- Timer to appear on building")

        # Countdown
        for i in range(5, 0, -1):
            print(f"Building scrapyard in {i}...")
            time.sleep(1)

        print("\n🏗️ BUILDING SCRAPYARD NOW!")

        # Click the build button
        window_manager.click_relative(center_x, center_y)
        print(f"Clicked Build Scrapyard at ({center_x}, {center_y})")

        # Wait and see what happens
        print("\nWaiting to see construction start...")
        time.sleep(8)

        # Take another screenshot to see changes
        after_screenshot = window_manager.capture_window()
        if after_screenshot is not None:
            # Check if the build button is still there
            build_match_after = template_matcher.find_template(after_screenshot, "build_scrapyard_btn")

            if not build_match_after:
                print("✅ SUCCESS! Build Scrapyard button is gone - construction likely started!")
                print("Check your game for:")
                print("- New construction timer")
                print("- Resources consumed")
                print("- Building in progress")
                return True
            else:
                print("⚠️ Build button still there - might need to confirm or have insufficient resources")
                return False

    else:
        print("[NOT FOUND] Build Scrapyard button not detected")
        print("Possible reasons:")
        print("1. Already built")
        print("2. Insufficient resources")
        print("3. Wrong game screen")
        print("4. Template doesn't match current UI")

        # Show what templates we CAN find
        print("\nTemplates we CAN detect:")
        all_matches = template_matcher.find_all_templates(screenshot)
        for match in all_matches:
            if match.confidence > 0.8:
                print(f"  {match.template_name}: {match.confidence:.3f}")

        return False

if __name__ == "__main__":
    focused_scrapyard_test()