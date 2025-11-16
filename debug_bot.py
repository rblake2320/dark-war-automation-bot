"""
Debug version of the bot with visual feedback
"""

import time
import cv2
import pyautogui
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def debug_bot_clicks():
    """Debug the bot by showing exactly where it's trying to click"""
    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    print("=== Debug Bot Clicks ===")
    print()

    # Find window
    if not window_manager.find_window():
        print("[-] BlueStacks window not found")
        return False

    print(f"[+] Found window: {window_manager.window.title}")
    print(f"[+] Window position: {window_manager.get_window_rect()}")

    # Focus window
    if not window_manager.focus_window():
        print("[-] Could not focus window")
        return False

    # Capture screenshot
    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("[-] Could not capture screenshot")
        return False

    print("[+] Screenshot captured")

    # Test template detection
    print("\nTesting template detection:")
    print("-" * 50)

    templates_to_test = [
        "build_scrapyard_btn",
        "mail_icon",
        "upgrade_number_2",
        "upgrade_number_3"
    ]

    for template_name in templates_to_test:
        match = template_matcher.find_template(screenshot, template_name)
        if match:
            print(f"[+] {template_name}: Found at ({match.x}, {match.y}) - confidence {match.confidence:.3f}")

            # Get center coordinates
            center_x, center_y = template_matcher.get_template_center(match)
            print(f"    Template center: ({center_x}, {center_y})")

            # Calculate absolute screen coordinates
            window_rect = window_manager.get_window_rect()
            if window_rect:
                window_x, window_y, _, _ = window_rect
                abs_x = window_x + center_x
                abs_y = window_y + center_y
                print(f"    Absolute screen position: ({abs_x}, {abs_y})")

                # Show where we would click
                print(f"    Would click at: ({abs_x}, {abs_y})")
        else:
            print(f"[-] {template_name}: Not found")
        print()

    # Ask if user wants to see a test click
    response = input("\nDo you want to see a test click on the mail icon? (y/n): ").lower()

    if response == 'y':
        mail_match = template_matcher.find_template(screenshot, "mail_icon")
        if mail_match:
            print("\nPerforming test click in 3 seconds...")
            print("Watch your BlueStacks window!")

            for i in range(3, 0, -1):
                print(f"Clicking in {i}...")
                time.sleep(1)

            # Get center and click
            center_x, center_y = template_matcher.get_template_center(mail_match)

            # Show mouse position before click
            current_pos = pyautogui.position()
            print(f"Current mouse position: {current_pos}")

            # Perform the click with slow movement
            window_manager.click_relative(center_x, center_y, duration=0.5)

            print(f"Clicked at relative position ({center_x}, {center_y})")
            print("Did you see the click happen? Did it click the right spot?")
        else:
            print("Mail icon not found, can't test click")

    return True

def show_mouse_position():
    """Show current mouse position for 10 seconds"""
    print("Showing mouse position for 10 seconds...")
    print("Move your mouse over game elements to see coordinates")
    print("Press Ctrl+C to stop")

    try:
        for i in range(100):  # 10 seconds at 0.1s intervals
            x, y = pyautogui.position()
            print(f"\rMouse position: ({x:4d}, {y:4d})", end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped")

def capture_current_screenshot():
    """Capture and save current screenshot"""
    config = get_config()
    window_manager = WindowManager(config.window_title)

    if window_manager.find_window() and window_manager.focus_window():
        screenshot = window_manager.capture_window()
        if screenshot is not None:
            cv2.imwrite("debug_screenshot.png", screenshot)
            print("Screenshot saved as debug_screenshot.png")
            return True

    print("Could not capture screenshot")
    return False

if __name__ == "__main__":
    print("Debug Options:")
    print("1. Test bot clicks and show coordinates")
    print("2. Show mouse position (move over game elements)")
    print("3. Capture current screenshot")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        debug_bot_clicks()
    elif choice == "2":
        show_mouse_position()
    elif choice == "3":
        capture_current_screenshot()
    else:
        print("Invalid choice")