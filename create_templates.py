"""
Template Creation Helper for Dark War Survival Bot
This script helps you create template images from your game screenshot
"""

import cv2
import numpy as np
import os
from window_manager import WindowManager
from config import get_config

def create_templates_from_screenshot():
    """Capture screenshot and let user create templates"""
    config = get_config()
    window_manager = WindowManager(config.window_title)

    print("=== Dark War Survival Template Creator ===")
    print()

    # Find and focus window
    if not window_manager.find_window():
        print("[-] BlueStacks window not found. Please start BlueStacks and Dark War Survival.")
        return False

    if not window_manager.focus_window():
        print("[-] Could not focus window")
        return False

    print("[+] Window found and focused")

    # Capture screenshot
    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("[-] Could not capture screenshot")
        return False

    print("[+] Screenshot captured")

    # Create templates directory
    os.makedirs("templates", exist_ok=True)

    # Save full screenshot for reference
    cv2.imwrite("templates/full_screenshot.png", screenshot)
    print("[+] Full screenshot saved as templates/full_screenshot.png")

    # Based on your screenshot, I can see these coordinates for UI elements:
    templates_to_create = [
        {
            "name": "build_scrapyard_btn",
            "description": "Build Scrapyard button with checkmark",
            "coords": (75, 1087, 300, 50),  # Approximate coordinates
            "priority": "HIGH - This button is visible and ready to click"
        },
        {
            "name": "upgrade_number_2",
            "description": "Building with upgrade number '2'",
            "coords": (200, 290, 30, 30),
            "priority": "HIGH - Multiple buildings show this"
        },
        {
            "name": "upgrade_number_3",
            "description": "Building with upgrade number '3'",
            "coords": (445, 528, 30, 30),
            "priority": "HIGH - Tower with upgrade number"
        },
        {
            "name": "mail_icon",
            "description": "Mail icon in bottom right",
            "coords": (650, 1055, 50, 50),
            "priority": "MEDIUM - For collecting rewards"
        },
        {
            "name": "resource_wood",
            "description": "Wood resource icon",
            "coords": (402, 10, 80, 40),
            "priority": "MEDIUM - For resource tracking"
        },
        {
            "name": "resource_gems",
            "description": "Gem resource icon",
            "coords": (490, 10, 80, 40),
            "priority": "MEDIUM - For resource tracking"
        }
    ]

    print("\nCreating template images from your screenshot...")
    print("=" * 60)

    height, width = screenshot.shape[:2]

    for template in templates_to_create:
        name = template["name"]
        desc = template["description"]
        x, y, w, h = template["coords"]
        priority = template["priority"]

        # Adjust coordinates if they're outside the screenshot
        x = max(0, min(x, width - w))
        y = max(0, min(y, height - h))
        w = min(w, width - x)
        h = min(h, height - y)

        # Extract the region
        if w > 0 and h > 0:
            template_image = screenshot[y:y+h, x:x+w]

            # Save template
            template_path = f"templates/{name}.png"
            cv2.imwrite(template_path, template_image)

            print(f"[+] {name:<25} - {desc}")
            print(f"    File: {template_path}")
            print(f"    Size: {w}x{h}")
            print(f"    Priority: {priority}")
            print()
        else:
            print(f"[-] {name} - Invalid coordinates, skipped")

    # Create a simple template from a solid color region (for testing)
    print("Creating additional test templates...")

    # Try to find uniform colored regions that could be UI elements
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

    # Look for brown/wooden UI elements (common in this game)
    brown_lower = np.array([10, 100, 100])
    brown_upper = np.array([20, 255, 255])
    brown_mask = cv2.inRange(hsv, brown_lower, brown_upper)

    # Find contours for brown elements
    contours, _ = cv2.findContours(brown_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Save a few good-sized contours as potential UI elements
    good_contours = [c for c in contours if cv2.contourArea(c) > 500 and cv2.contourArea(c) < 5000]

    for i, contour in enumerate(good_contours[:3]):  # Max 3 templates
        x, y, w, h = cv2.boundingRect(contour)
        template_image = screenshot[y:y+h, x:x+w]
        template_path = f"templates/ui_element_{i+1}.png"
        cv2.imwrite(template_path, template_image)
        print(f"[+] ui_element_{i+1:<15} - Detected UI element")
        print(f"    File: {template_path}")
        print(f"    Size: {w}x{h}")
        print()

    print("=" * 60)
    print(f"Template creation complete!")
    print(f"Created templates in: templates/")
    print()
    print("Next steps:")
    print("1. Run: python main.py --test-templates")
    print("2. If templates work, run: python main.py --max-cycles 3")
    print("3. Watch the bot in action!")

    return True

if __name__ == "__main__":
    create_templates_from_screenshot()