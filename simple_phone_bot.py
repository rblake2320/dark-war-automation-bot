"""
Simple phone automation - direct screen capture and click
"""

import pygetwindow as gw
import pyautogui
import time
import numpy as np

def setup_phone_automation():
    """Set up automation for phone mirroring"""
    print("=== SIMPLE PHONE BOT SETUP ===")
    print()

    # Find Dark War window
    all_windows = gw.getAllWindows()
    dark_war_window = None

    for window in all_windows:
        if "Dark War" in window.title:
            dark_war_window = window
            break

    if not dark_war_window:
        # Try the Samsung phone window
        for window in all_windows:
            if "S22" in window.title or "Ron" in window.title:
                if window.width < 500 and window.height > 800:  # Phone-like dimensions
                    dark_war_window = window
                    break

    if not dark_war_window:
        print("Could not find phone mirroring window!")
        print("Make sure Dark War Survival is open and mirrored to your PC")
        return None

    print(f"Found window: {dark_war_window.title}")
    print(f"Size: {dark_war_window.width}x{dark_war_window.height}")

    # Focus the window
    dark_war_window.activate()
    time.sleep(2)

    return dark_war_window

def test_phone_clicks(window):
    """Test clicking on phone interface"""
    print("\n=== TESTING PHONE CLICKS ===")
    print("This will test clicking on your phone game!")

    # Get window position
    x, y, w, h = window.left, window.top, window.width, window.height
    print(f"Window at: ({x}, {y}) size: {w}x{h}")

    # Define click areas based on typical Dark War Survival layout
    click_areas = [
        {
            "name": "Heroes (bottom left)",
            "x": x + 50,
            "y": y + h - 100,
            "description": "Heroes button area"
        },
        {
            "name": "World (bottom right)",
            "x": x + w - 50,
            "y": y + h - 100,
            "description": "World button area"
        },
        {
            "name": "Mail (right side)",
            "x": x + w - 30,
            "y": y + h//2,
            "description": "Mail notifications"
        },
        {
            "name": "Center area",
            "x": x + w//2,
            "y": y + h//2,
            "description": "Center of base"
        },
        {
            "name": "VIP (top left)",
            "x": x + 30,
            "y": y + 80,
            "description": "VIP area"
        }
    ]

    print("\nAvailable click areas:")
    for i, area in enumerate(click_areas):
        print(f"{i+1}. {area['name']} - {area['description']}")

    # Test each area
    for i, area in enumerate(click_areas):
        print(f"\nTesting area {i+1}: {area['name']}")
        print(f"Will click at ({area['x']}, {area['y']})")
        print("Watch your phone screen!")

        # Countdown
        for count in range(3, 0, -1):
            print(f"Clicking in {count}...")
            time.sleep(1)

        print("CLICKING!")
        pyautogui.click(area['x'], area['y'])
        print("Click performed!")

        # Wait to see result
        time.sleep(3)

        # Ask user if it worked
        response = input("Did that click do something on your phone? (y/n): ").lower()
        if response == 'y':
            print(f"SUCCESS: {area['name']} is clickable!")
        else:
            print(f"No effect from {area['name']}")

def rapid_phone_automation(window):
    """Rapid automation on phone interface"""
    print("\n=== RAPID PHONE AUTOMATION ===")
    print("This will rapidly click multiple areas on your phone game!")
    print("Press Ctrl+C to stop")

    x, y, w, h = window.left, window.top, window.width, window.height

    # Focus on actionable areas
    action_areas = [
        (x + w - 30, y + h//2),      # Mail area
        (x + 50, y + h - 100),       # Heroes
        (x + w - 50, y + h - 100),   # World
        (x + w//2, y + h//2 - 50),   # Center-top
        (x + w//2, y + h//2 + 50),   # Center-bottom
        (x + 30, y + 80),            # VIP area
        (x + w - 60, y + 150),       # Right side events
    ]

    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"Cycle {cycle}: Performing {len(action_areas)} rapid clicks...")

            for i, (click_x, click_y) in enumerate(action_areas):
                pyautogui.click(click_x, click_y)
                print(f"  Click {i+1} at ({click_x}, {click_y})")
                time.sleep(0.3)  # Brief delay between clicks

            print(f"Cycle {cycle} complete. Waiting 2 seconds...")
            time.sleep(2)

    except KeyboardInterrupt:
        print(f"\nRapid automation stopped after {cycle} cycles")

if __name__ == "__main__":
    window = setup_phone_automation()

    if window:
        print("\nChoose mode:")
        print("1. Test individual click areas")
        print("2. Rapid automation mode")

        choice = input("Enter choice (1 or 2): ")

        if choice == "2":
            rapid_phone_automation(window)
        else:
            test_phone_clicks(window)
    else:
        print("Setup failed - could not find phone window")