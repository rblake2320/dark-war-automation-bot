"""
Rapid automation bot for phone mirroring - no user input required
"""

import pygetwindow as gw
import pyautogui
import time

def run_rapid_phone_automation():
    """Run rapid automation without user input"""
    print("=== RAPID PHONE AUTOMATION ===")
    print("Automatically clicking your Dark War Survival phone game!")
    print("Press Ctrl+C to stop")
    print()

    # Find Dark War window
    dark_war_window = None
    all_windows = gw.getAllWindows()

    for window in all_windows:
        if "Dark War" in window.title and window.width > 300 and window.height > 700:
            dark_war_window = window
            break

    if not dark_war_window:
        print("Dark War window not found!")
        return

    print(f"Found: {dark_war_window.title}")
    print(f"Size: {dark_war_window.width}x{dark_war_window.height}")

    # Focus window
    dark_war_window.activate()
    time.sleep(2)

    # Get coordinates
    x, y, w, h = dark_war_window.left, dark_war_window.top, dark_war_window.width, dark_war_window.height
    print(f"Window position: ({x}, {y}) size: {w}x{h}")

    # Define high-value click areas for Dark War Survival
    click_areas = [
        {
            "name": "Mail/Rewards",
            "x": x + w - 30,
            "y": y + h//2,
            "priority": 1,  # Highest priority
        },
        {
            "name": "Heroes",
            "x": x + 50,
            "y": y + h - 80,
            "priority": 2,
        },
        {
            "name": "World",
            "x": x + w - 50,
            "y": y + h - 80,
            "priority": 2,
        },
        {
            "name": "Events (right)",
            "x": x + w - 40,
            "y": y + 200,
            "priority": 3,
        },
        {
            "name": "VIP (left)",
            "x": x + 40,
            "y": y + 100,
            "priority": 3,
        },
        {
            "name": "Center base",
            "x": x + w//2,
            "y": y + h//2,
            "priority": 4,
        },
        {
            "name": "Upper center",
            "x": x + w//2,
            "y": y + h//3,
            "priority": 4,
        },
        {
            "name": "Lower center",
            "x": x + w//2,
            "y": y + 2*h//3,
            "priority": 4,
        }
    ]

    # Sort by priority
    click_areas.sort(key=lambda area: area["priority"])

    print(f"\nConfigured {len(click_areas)} click areas")
    print("Starting rapid automation...")

    cycle = 0
    total_clicks = 0

    try:
        while True:
            cycle += 1
            cycle_clicks = 0

            print(f"\nCycle {cycle}:", end=" ")

            # Execute clicks by priority
            for area in click_areas[:5]:  # Top 5 priority areas per cycle
                pyautogui.click(area["x"], area["y"])
                print(f"{area['name'][:8]}", end=" ")
                cycle_clicks += 1
                total_clicks += 1
                time.sleep(0.2)  # Brief delay between clicks

            print(f"({cycle_clicks} clicks)")

            # Stats every 10 cycles
            if cycle % 10 == 0:
                elapsed_minutes = cycle * 2 / 60  # Assuming ~2 seconds per cycle
                print(f"\n--- Stats: {cycle} cycles, {total_clicks} total clicks, {elapsed_minutes:.1f} min runtime ---")

            # Short pause between cycles
            time.sleep(1.5)

    except KeyboardInterrupt:
        print(f"\n\nAutomation stopped!")
        print(f"Total cycles: {cycle}")
        print(f"Total clicks: {total_clicks}")
        print(f"Average: {total_clicks/cycle:.1f} clicks per cycle")

def quick_test():
    """Quick 30-second test"""
    print("=== 30-SECOND RAPID TEST ===")

    # Find window
    for window in gw.getAllWindows():
        if "Dark War" in window.title and window.width > 300:
            print(f"Testing on: {window.title}")
            window.activate()
            time.sleep(1)

            x, y, w, h = window.left, window.top, window.width, window.height

            # 30-second rapid test
            start_time = time.time()
            clicks = 0

            while time.time() - start_time < 30:
                # Rapid clicks on key areas
                areas = [
                    (x + w - 30, y + h//2),     # Mail
                    (x + 50, y + h - 80),       # Heroes
                    (x + w - 50, y + h - 80),   # World
                    (x + w//2, y + h//2),       # Center
                ]

                for click_x, click_y in areas:
                    pyautogui.click(click_x, click_y)
                    clicks += 1
                    time.sleep(0.1)

            print(f"30-second test complete: {clicks} clicks")
            print(f"Rate: {clicks/30:.1f} clicks per second")
            return

    print("Dark War window not found")

if __name__ == "__main__":
    print("PHONE AUTOMATION OPTIONS:")
    print("1. Continuous rapid automation")
    print("2. 30-second speed test")
    print()

    choice = input("Choose (1 or 2), or just press Enter for continuous: ").strip()

    if choice == "2":
        quick_test()
    else:
        run_rapid_phone_automation()