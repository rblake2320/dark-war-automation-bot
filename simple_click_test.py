"""
Simple click test without Unicode issues
"""

import time
import pyautogui
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def simple_click_test():
    """Simple test that shows exactly what's happening"""
    print("=== SIMPLE CLICK TEST ===")
    print("Watch your BlueStacks window for mouse movement and clicks!")
    print()

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    # Find window
    if not window_manager.find_window():
        print("BlueStacks window not found!")
        return False

    print(f"[OK] BlueStacks found: {window_manager.window_title}")
    window_rect = window_manager.get_window_rect()
    print(f"[OK] Window location: x={window_rect[0]}, y={window_rect[1]}, w={window_rect[2]}, h={window_rect[3]}")

    # Focus window
    print("\nFocusing BlueStacks window...")
    window_manager.focus_window()
    time.sleep(2)

    # Get current mouse position for reference
    start_mouse = pyautogui.position()
    print(f"[OK] Current mouse position: {start_mouse}")

    # Capture screenshot
    print("Capturing screenshot...")
    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("[ERROR] Could not capture screenshot")
        return False

    print("[OK] Screenshot captured successfully")

    # Look for mail icon
    print("\nSearching for mail icon...")
    mail_match = template_matcher.find_template(screenshot, "mail_icon")

    if mail_match:
        center_x, center_y = template_matcher.get_template_center(mail_match)
        print(f"[FOUND] Mail icon at relative position ({center_x}, {center_y})")
        print(f"[FOUND] Confidence: {mail_match.confidence:.3f}")

        # Calculate absolute position
        window_x, window_y = window_rect[0], window_rect[1]
        click_x = window_x + center_x
        click_y = window_y + center_y
        print(f"[CALC] Will click at screen position ({click_x}, {click_y})")

        print("\n*** STARTING CLICK TEST ***")
        print("You should see the mouse cursor move slowly to the mail icon")

        # Countdown
        for i in range(3, 0, -1):
            print(f"Clicking in {i}...")
            time.sleep(1)

        print("MOVING MOUSE...")
        # Move mouse very slowly so you can see it
        pyautogui.moveTo(click_x, click_y, duration=2.0)

        print("PAUSING...")
        time.sleep(1)

        print("CLICKING!")
        pyautogui.click()

        print("WAITING...")
        time.sleep(2)

        # Check final mouse position
        final_mouse = pyautogui.position()
        print(f"[OK] Mouse moved from {start_mouse} to {final_mouse}")

        print("\n*** CLICK TEST COMPLETE ***")
        print("Did you see:")
        print("1. Mouse cursor move to the mail icon?")
        print("2. A click action happen?")
        print("3. Any response from the game (menu opening, etc.)?")

        return True

    else:
        print("[ERROR] Mail icon not found!")

        # Show what templates were found
        print("\nChecking all templates...")
        all_matches = template_matcher.find_all_templates(screenshot)
        for match in all_matches:
            if match.confidence > 0.7:  # Only show confident matches
                print(f"[FOUND] {match.template_name} at ({match.x}, {match.y}) - confidence {match.confidence:.3f}")

        return False

if __name__ == "__main__":
    simple_click_test()