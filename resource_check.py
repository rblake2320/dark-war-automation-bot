"""
Check current resources and find what actions are actually possible
"""

import cv2
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def check_game_state():
    """Check what the bot can actually do in current game state"""
    print("=== GAME STATE ANALYSIS ===")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    # Setup
    if not window_manager.find_window() or not window_manager.focus_window():
        print("ERROR: Could not access BlueStacks")
        return

    # Get screenshot
    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("ERROR: No screenshot")
        return

    # Save current state
    cv2.imwrite("current_state_analysis.png", screenshot)
    print("Screenshot saved as current_state_analysis.png")

    print("\n=== RESOURCE ANALYSIS ===")

    # Check resources
    wood_found = template_matcher.find_template(screenshot, "resource_wood")
    gems_found = template_matcher.find_template(screenshot, "resource_gems")

    if wood_found:
        print(f"Wood resources detected at ({wood_found.x}, {wood_found.y})")
    if gems_found:
        print(f"Gems detected at ({gems_found.x}, {gems_found.y})")

    print("\n=== AVAILABLE ACTIONS ===")

    # Check all available actions
    actionable_elements = []

    # Build Scrapyard
    build_btn = template_matcher.find_template(screenshot, "build_scrapyard_btn")
    if build_btn:
        print(f"[AVAILABLE] Build Scrapyard - Confidence: {build_btn.confidence:.3f}")
        actionable_elements.append(("build_scrapyard", build_btn))

    # Mail
    mail_btn = template_matcher.find_template(screenshot, "mail_icon")
    if mail_btn:
        print(f"[AVAILABLE] Mail (rewards) - Confidence: {mail_btn.confidence:.3f}")
        actionable_elements.append(("mail", mail_btn))

    # Buildings that can be upgraded
    upgrade_2 = template_matcher.find_template(screenshot, "upgrade_number_2")
    if upgrade_2:
        print(f"[AVAILABLE] Building with upgrade level 2 - Confidence: {upgrade_2.confidence:.3f}")
        actionable_elements.append(("upgrade_building_2", upgrade_2))

    upgrade_3 = template_matcher.find_template(screenshot, "upgrade_number_3")
    if upgrade_3:
        print(f"[AVAILABLE] Building with upgrade level 3 - Confidence: {upgrade_3.confidence:.3f}")
        actionable_elements.append(("upgrade_building_3", upgrade_3))

    print(f"\nTotal actionable elements found: {len(actionable_elements)}")

    if not actionable_elements:
        print("\n[PROBLEM] No actionable elements found!")
        print("This means:")
        print("1. Game is on wrong screen (menu, loading, etc.)")
        print("2. All actions already completed")
        print("3. Templates don't match current game version")
        return

    print("\n=== RECOMMENDED ACTIONS ===")

    # Prioritize actions
    if any(action[0] == "mail" for action in actionable_elements):
        print("1. CLICK MAIL - Most likely to work (collect rewards)")

    if any(action[0].startswith("upgrade_building") for action in actionable_elements):
        print("2. CLICK BUILDING - Click on building to see upgrade options")

    if any(action[0] == "build_scrapyard" for action in actionable_elements):
        print("3. BUILD SCRAPYARD - May need resources")

    print("\nLet's try the most reliable action...")
    return True

def try_mail_action():
    """Try clicking mail as it's most likely to work"""
    print("\n=== TRYING MAIL ACTION ===")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        return False

    screenshot = window_manager.capture_window()
    if screenshot is None:
        return False

    mail_match = template_matcher.find_template(screenshot, "mail_icon")
    if mail_match:
        center_x, center_y = template_matcher.get_template_center(mail_match)
        print(f"Clicking mail at ({center_x}, {center_y})")

        # Click mail
        window_manager.click_relative(center_x, center_y)
        print("Mail clicked - check for mail interface opening")
        return True

    print("Mail not found")
    return False

if __name__ == "__main__":
    check_game_state()
    print("\n" + "="*50)
    try_mail_action()