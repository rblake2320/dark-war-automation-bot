"""
Diagnose why the bot isn't actually affecting the game
"""

import cv2
import time
import pyautogui
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def diagnose_bot_problem():
    """Find out why the bot isn't working"""
    print("=== BOT PROBLEM DIAGNOSIS ===")
    print()

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    # Step 1: Basic setup check
    print("STEP 1: Basic Setup Check")
    print("-" * 30)

    if not window_manager.find_window():
        print("[FAIL] BlueStacks window not found")
        return

    print("[PASS] BlueStacks window found")
    window_rect = window_manager.get_window_rect()
    print(f"Window: {window_rect}")

    if not window_manager.focus_window():
        print("[FAIL] Could not focus window")
        return

    print("[PASS] Window focused")
    time.sleep(2)

    # Step 2: Screenshot and template check
    print("\nSTEP 2: Screenshot and Template Analysis")
    print("-" * 40)

    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("[FAIL] Could not capture screenshot")
        return

    print(f"[PASS] Screenshot captured: {screenshot.shape}")

    # Save current screenshot for analysis
    cv2.imwrite("current_game_state.png", screenshot)
    print("[INFO] Current screenshot saved as 'current_game_state.png'")

    # Check all templates
    results = template_matcher.test_all_templates(screenshot)
    found_templates = {name: data for name, data in results.items() if data['found']}

    print(f"\n[INFO] Found {len(found_templates)} out of {len(results)} templates:")
    for name, data in found_templates.items():
        pos = data['position']
        conf = data['confidence']
        print(f"  {name}: {pos} (confidence: {conf:.3f})")

    if not found_templates:
        print("[PROBLEM] No templates found! This is the main issue.")
        print("Solutions:")
        print("1. Game screen has changed since templates were created")
        print("2. Game is on a different interface (menu, loading screen, etc.)")
        print("3. Template images don't match current game version")
        return

    # Step 3: Test actual clicking
    print("\nSTEP 3: Click Test")
    print("-" * 20)

    # Find the most confident template to test
    best_template = max(found_templates.items(), key=lambda x: x[1]['confidence'])
    template_name, template_data = best_template

    print(f"[INFO] Testing click on most confident template: {template_name}")
    print(f"[INFO] Confidence: {template_data['confidence']:.3f}")
    print(f"[INFO] Position: {template_data['position']}")

    # Get the exact match for center calculation
    match = template_matcher.find_template(screenshot, template_name)
    if match:
        center_x, center_y = template_matcher.get_template_center(match)

        # Calculate screen coordinates
        window_x, window_y = window_rect[0], window_rect[1]
        screen_x = window_x + center_x
        screen_y = window_y + center_y

        print(f"[INFO] Will click at screen position: ({screen_x}, {screen_y})")

        # Take a "before" screenshot
        before_screenshot = window_manager.capture_window()
        cv2.imwrite("before_click.png", before_screenshot)
        print("[INFO] Before-click screenshot saved")

        print("\n[ACTION] Performing test click in 3 seconds...")
        print("WATCH YOUR SCREEN CAREFULLY!")

        for i in range(3, 0, -1):
            print(f"Clicking in {i}...")
            time.sleep(1)

        # Perform the click with very visible movement
        current_pos = pyautogui.position()
        print(f"[INFO] Moving mouse from {current_pos} to ({screen_x}, {screen_y})")

        pyautogui.moveTo(screen_x, screen_y, duration=1.5)
        time.sleep(0.5)
        pyautogui.click()
        print("[ACTION] Click performed!")

        # Wait and take "after" screenshot
        time.sleep(3)
        after_screenshot = window_manager.capture_window()
        cv2.imwrite("after_click.png", after_screenshot)
        print("[INFO] After-click screenshot saved")

        # Compare before and after
        print("\nSTEP 4: Change Detection")
        print("-" * 25)

        # Simple difference calculation
        diff = cv2.absdiff(before_screenshot, after_screenshot)
        diff_sum = diff.sum()

        print(f"[INFO] Screenshot difference: {diff_sum}")

        if diff_sum > 1000000:  # Significant change threshold
            print("[SUCCESS] Significant change detected - bot click worked!")
        elif diff_sum > 100000:  # Minor change
            print("[PARTIAL] Minor change detected - click may have worked")
        else:
            print("[PROBLEM] No significant change detected")
            print("Possible issues:")
            print("1. Clicking wrong coordinates")
            print("2. Game element is not clickable")
            print("3. Game is in wrong state (menu, popup, etc.)")
            print("4. Template is matching background, not actual button")

        # Save difference image for analysis
        cv2.imwrite("click_difference.png", diff)
        print("[INFO] Difference image saved as 'click_difference.png'")

    print("\n=== DIAGNOSIS COMPLETE ===")
    print("Check these files for analysis:")
    print("- current_game_state.png (what bot sees)")
    print("- before_click.png (before clicking)")
    print("- after_click.png (after clicking)")
    print("- click_difference.png (what changed)")

if __name__ == "__main__":
    diagnose_bot_problem()