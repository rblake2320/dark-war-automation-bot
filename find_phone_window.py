"""
Simple tool to find your phone mirroring window
"""

import pygetwindow as gw
import pyautogui
import cv2
import time

def find_phone_window():
    """Find the window showing your phone game"""
    print("=== FINDING YOUR PHONE GAME WINDOW ===")
    print()

    all_windows = gw.getAllWindows()
    visible_windows = []

    # Filter to only show reasonable windows
    for window in all_windows:
        try:
            if (window.title.strip() and
                window.width > 200 and
                window.height > 300 and
                window.visible):
                visible_windows.append(window)
        except:
            continue

    print(f"Found {len(visible_windows)} potential windows:")
    for i, window in enumerate(visible_windows):
        try:
            title = window.title[:50]  # Truncate long titles
            print(f"{i+1:2d}. {title:<50} [{window.width}x{window.height}]")
        except:
            print(f"{i+1:2d}. [Title display error] [{window.width}x{window.height}]")

    print()
    print("Which window shows your Dark War Survival game?")
    print("(Look for your phone mirroring app - scrcpy, Your Phone, etc.)")

    try:
        choice = input("Enter window number: ")
        window_index = int(choice) - 1

        if 0 <= window_index < len(visible_windows):
            selected_window = visible_windows[window_index]
            print(f"Selected: {selected_window.title[:50]}")

            # Test capture
            print("Testing capture...")
            selected_window.activate()
            time.sleep(2)

            x, y, w, h = selected_window.left, selected_window.top, selected_window.width, selected_window.height
            screenshot = pyautogui.screenshot(region=(x, y, w, h))

            # Convert to OpenCV format and save
            screenshot_cv = cv2.cvtColor(pyautogui.screenshot(region=(x, y, w, h)), cv2.COLOR_RGB2BGR)
            cv2.imwrite("phone_capture_test.png", screenshot_cv)

            print("SUCCESS: Phone screen captured!")
            print("Saved as: phone_capture_test.png")
            print(f"Window coordinates: x={x}, y={y}, w={w}, h={h}")

            return selected_window

    except ValueError:
        print("Invalid input")
    except Exception as e:
        print(f"Error: {e}")

    return None

def create_phone_templates(window):
    """Create templates from your actual phone game"""
    print("\n=== CREATING PHONE GAME TEMPLATES ===")

    # Focus the window
    window.activate()
    time.sleep(2)

    # Capture current game state
    x, y, w, h = window.left, window.top, window.width, window.height
    screenshot = pyautogui.screenshot(region=(x, y, w, h))
    screenshot_cv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    print(f"Captured game screen: {w}x{h}")
    cv2.imwrite("current_phone_game.png", screenshot_cv)

    # Create templates directory
    import os
    os.makedirs("phone_templates", exist_ok=True)

    # Based on your Dark War Survival screenshot, create templates for key areas
    # I can see: Heroes button (bottom left), World button (bottom right),
    # Mail icons (right side), VIP (left side), Events (right side)

    templates_to_create = [
        # Bottom navigation
        ("heroes_btn", 0, h-120, 100, 120, "Heroes button (bottom left)"),
        ("world_btn", w-100, h-120, 100, 120, "World button (bottom right)"),

        # Right side UI
        ("mail_icon", w-80, h//2-50, 80, 100, "Mail notifications (right)"),
        ("events_area", w-120, 150, 120, 200, "Events area (right side)"),

        # Left side UI
        ("vip_area", 0, 50, 80, 100, "VIP area (left side)"),

        # Top UI
        ("resources_area", 100, 0, w-200, 100, "Resource display (top)"),

        # Center areas for buildings/actions
        ("center_left", w//4-50, h//2-50, 100, 100, "Center left area"),
        ("center_right", 3*w//4-50, h//2-50, 100, 100, "Center right area"),
    ]

    for name, tx, ty, tw, th, description in templates_to_create:
        # Ensure coordinates are within bounds
        tx = max(0, min(tx, w - tw))
        ty = max(0, min(ty, h - th))
        tw = min(tw, w - tx)
        th = min(th, h - ty)

        if tw > 10 and th > 10:  # Only create reasonable sized templates
            template_region = screenshot_cv[ty:ty+th, tx:tx+tw]
            template_path = f"phone_templates/{name}.png"
            cv2.imwrite(template_path, template_region)
            print(f"Created: {name}.png - {description}")

    print(f"\nTemplates created in: phone_templates/")
    print("Next: Run phone automation test!")

if __name__ == "__main__":
    window = find_phone_window()
    if window:
        create_phone_templates(window)
        print("\nSetup complete!")
        print("Your phone mirroring is ready for automation!")
    else:
        print("Setup failed - please try again")