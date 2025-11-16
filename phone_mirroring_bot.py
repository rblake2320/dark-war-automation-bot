"""
Bot for phone mirroring - works with screen mirroring software
"""

import pygetwindow as gw
import pyautogui
import cv2
import time
from template_matcher import TemplateMatcher

def find_mirroring_window():
    """Find the phone mirroring window"""
    print("Looking for phone mirroring window...")

    # Common mirroring software window titles
    possible_titles = [
        "scrcpy",           # scrcpy
        "Your Phone",       # Microsoft Your Phone
        "Phone Link",       # Microsoft Phone Link
        "LetsView",         # LetsView
        "ApowerMirror",     # ApowerMirror
        "Vysor",            # Vysor
        "AirServer",        # AirServer
        "Android",          # Generic Android
        "iPhone",           # iPhone mirroring
        "Screen Mirror",    # Generic screen mirror
        "Remote Control",   # Remote control apps
        "TeamViewer",       # TeamViewer
        "Chrome",           # If using web-based mirroring
        "Edge",             # Microsoft Edge for phone link
    ]

    all_windows = gw.getAllWindows()

    print(f"Found {len(all_windows)} windows:")
    for i, window in enumerate(all_windows):
        if window.title.strip():  # Only show windows with titles
            print(f"  {i+1}. '{window.title}' - Size: {window.width}x{window.height}")

    # Try to find mirroring windows
    for title_pattern in possible_titles:
        for window in all_windows:
            if title_pattern.lower() in window.title.lower() and window.width > 200 and window.height > 300:
                print(f"\nFound potential mirroring window: '{window.title}'")
                return window

    # If no automatic detection, let user choose
    print(f"\nCould not auto-detect mirroring window.")
    print("Which window contains your Dark War Survival game?")

    try:
        choice = input("Enter window number (1-{}): ".format(len(all_windows)))
        window_index = int(choice) - 1
        if 0 <= window_index < len(all_windows):
            selected_window = all_windows[window_index]
            print(f"Selected: '{selected_window.title}'")
            return selected_window
    except:
        pass

    return None

def capture_phone_screen():
    """Capture the current phone screen and create new templates"""
    print("=== PHONE SCREEN CAPTURE ===")

    window = find_mirroring_window()
    if not window:
        print("No mirroring window found!")
        return False

    try:
        # Focus the window
        window.activate()
        time.sleep(2)

        # Get window position
        x, y, width, height = window.left, window.top, window.width, window.height
        print(f"Capturing from: ({x}, {y}) size: {width}x{height}")

        # Capture the window
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot_cv = cv2.cvtColor(pyautogui.screenshot(region=(x, y, width, height)), cv2.COLOR_RGB2BGR)

        # Save the full screenshot
        cv2.imwrite("phone_game_screen.png", screenshot_cv)
        print("Phone game screen saved as: phone_game_screen.png")

        # Now I can see your actual game interface and create proper templates!
        analyze_phone_game_interface(screenshot_cv)

        return True

    except Exception as e:
        print(f"Error capturing screen: {e}")
        return False

def analyze_phone_game_interface(screenshot):
    """Analyze the phone game interface to find actionable elements"""
    print("\n=== ANALYZING PHONE GAME INTERFACE ===")

    height, width = screenshot.shape[:2]
    print(f"Game screen size: {width}x{height}")

    # Based on your screenshots, I can see several actionable elements:
    # Let me create templates for the elements I can identify

    # Create templates directory for phone game
    import os
    os.makedirs("phone_templates", exist_ok=True)

    # Define areas where I can see clickable elements from your screenshot
    phone_elements = [
        {
            "name": "heroes_button",
            "description": "Heroes button (bottom left)",
            "area": (0, height-150, 120, 150),  # Bottom left area
        },
        {
            "name": "world_button",
            "description": "World button (bottom right)",
            "area": (width-120, height-150, 120, 150),  # Bottom right area
        },
        {
            "name": "mail_icon",
            "description": "Mail icon (right side)",
            "area": (width-80, height//2-100, 80, 200),  # Right side
        },
        {
            "name": "vip_button",
            "description": "VIP button (left side)",
            "area": (0, 100, 100, 100),  # Left side top
        },
        {
            "name": "events_button",
            "description": "Events (right side)",
            "area": (width-150, 100, 150, 200),  # Right side events area
        }
    ]

    # Extract and save templates
    for element in phone_elements:
        x, y, w, h = element["area"]

        # Make sure coordinates are within bounds
        x = max(0, min(x, width - w))
        y = max(0, min(y, height - h))
        w = min(w, width - x)
        h = min(h, height - y)

        if w > 0 and h > 0:
            template_image = screenshot[y:y+h, x:x+w]
            template_path = f"phone_templates/{element['name']}.png"
            cv2.imwrite(template_path, template_image)
            print(f"Created: {template_path} - {element['description']}")

def test_phone_automation():
    """Test automation on phone mirroring"""
    print("\n=== TESTING PHONE AUTOMATION ===")

    window = find_mirroring_window()
    if not window:
        print("No mirroring window found!")
        return False

    # Focus window
    window.activate()
    time.sleep(2)

    # Capture current state
    x, y, width, height = window.left, window.top, window.width, window.height
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    screenshot_cv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Load templates
    template_matcher = TemplateMatcher(templates_dir="phone_templates")

    # Find actionable elements
    matches = template_matcher.find_all_templates(screenshot_cv)

    if matches:
        print(f"Found {len(matches)} actionable elements:")
        for match in matches:
            if match.confidence > 0.7:
                center_x, center_y = template_matcher.get_template_center(match)
                screen_x = x + center_x
                screen_y = y + center_y
                print(f"  {match.template_name}: confidence {match.confidence:.3f} at screen ({screen_x}, {screen_y})")

        # Test clicking the most confident match
        best_match = max(matches, key=lambda m: m.confidence)
        if best_match.confidence > 0.8:
            center_x, center_y = template_matcher.get_template_center(best_match)
            screen_x = x + center_x
            screen_y = y + center_y

            print(f"\nTesting click on {best_match.template_name}...")
            print("Watch your phone screen!")

            for i in range(3, 0, -1):
                print(f"Clicking in {i}...")
                time.sleep(1)

            pyautogui.click(screen_x, screen_y)
            print(f"Clicked at ({screen_x}, {screen_y})")

            return True
    else:
        print("No actionable elements found")
        return False

if __name__ == "__main__":
    print("=== PHONE MIRRORING BOT SETUP ===")
    print("This bot will work with your phone mirrored to PC!")
    print()

    print("Step 1: Capture your phone game screen...")
    if capture_phone_screen():
        print("\nStep 2: Test automation...")
        test_phone_automation()
    else:
        print("Setup failed - could not capture phone screen")