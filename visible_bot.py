"""
Visible bot with clear feedback and slower actions
"""

import time
import pyautogui
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def visible_bot_test():
    """Run bot with highly visible actions"""
    print("=== VISIBLE BOT TEST ===")
    print("This will perform ONE action with clear visual feedback")
    print()

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    # Find window
    if not window_manager.find_window():
        print("ERROR: BlueStacks window not found!")
        print("Please make sure:")
        print("1. BlueStacks is running")
        print("2. Dark War Survival is open")
        print("3. Game is visible (not minimized)")
        return False

    print("✓ BlueStacks window found")
    window_rect = window_manager.get_window_rect()
    print(f"✓ Window location: {window_rect}")

    # Focus window
    print("\nBringing BlueStacks to front...")
    window_manager.focus_window()
    time.sleep(2)  # Give time to see window focus

    # Capture screenshot
    print("Capturing screenshot...")
    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("ERROR: Could not capture screenshot")
        return False
    print("✓ Screenshot captured")

    # Look for mail icon (most visible action)
    print("\nLooking for mail icon...")
    mail_match = template_matcher.find_template(screenshot, "mail_icon")

    if mail_match:
        center_x, center_y = template_matcher.get_template_center(mail_match)
        window_x, window_y, _, _ = window_rect
        abs_x = window_x + center_x
        abs_y = window_y + center_y

        print(f"✓ Mail icon found!")
        print(f"  Relative position: ({center_x}, {center_y})")
        print(f"  Absolute screen position: ({abs_x}, {abs_y})")
        print(f"  Confidence: {mail_match.confidence:.3f}")

        # Show current mouse position
        current_mouse = pyautogui.position()
        print(f"  Current mouse position: {current_mouse}")

        print("\n🎯 GETTING READY TO CLICK MAIL ICON")
        print("👀 WATCH YOUR BLUESTACKS WINDOW!")
        print("You should see:")
        print("1. Mouse cursor move to the mail icon")
        print("2. A click action")
        print("3. Possibly a mail menu opening")

        # Countdown
        for i in range(5, 0, -1):
            print(f"Clicking mail in {i} seconds...")
            time.sleep(1)

        print("\n🖱️ CLICKING NOW!")

        # Move mouse slowly and visibly
        print(f"Moving mouse to ({abs_x}, {abs_y})...")
        pyautogui.moveTo(abs_x, abs_y, duration=1.0)  # Slow movement
        time.sleep(0.5)

        print("CLICKING!")
        pyautogui.click(duration=0.2)  # Visible click
        time.sleep(1)

        print("✓ Click completed!")
        print("\nDid you see:")
        print("- Mouse cursor move to mail icon?")
        print("- The click happen?")
        print("- Any response from the game?")

        return True

    else:
        print("❌ Mail icon not found")
        print("This could mean:")
        print("1. Game screen has changed")
        print("2. Template image doesn't match current game version")
        print("3. Game is showing a different interface")

        # Try other templates
        print("\nChecking other UI elements...")
        all_matches = template_matcher.find_all_templates(screenshot)
        if all_matches:
            print("Found these templates:")
            for match in all_matches:
                print(f"  ✓ {match.template_name} at ({match.x}, {match.y}) - confidence {match.confidence:.3f}")
        else:
            print("❌ No templates found at all!")

        return False

if __name__ == "__main__":
    visible_bot_test()