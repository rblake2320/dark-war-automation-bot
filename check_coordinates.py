"""
Check bot coordinates without user input
"""

from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def check_coordinates():
    """Check where the bot thinks it should click"""
    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    print("=== Checking Bot Coordinates ===")

    # Find window
    if not window_manager.find_window():
        print("[-] BlueStacks window not found")
        return False

    window_rect = window_manager.get_window_rect()
    print(f"[+] Window found at: {window_rect}")

    # Focus and capture
    if not window_manager.focus_window():
        print("[-] Could not focus window")
        return False

    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("[-] Could not capture screenshot")
        return False

    print(f"[+] Screenshot captured: {screenshot.shape}")

    # Check templates
    templates_to_check = [
        "build_scrapyard_btn",
        "mail_icon",
        "upgrade_number_2",
        "upgrade_number_3"
    ]

    for template_name in templates_to_check:
        match = template_matcher.find_template(screenshot, template_name)
        if match:
            center_x, center_y = template_matcher.get_template_center(match)

            # Calculate absolute coordinates
            window_x, window_y, _, _ = window_rect
            abs_x = window_x + center_x
            abs_y = window_y + center_y

            print(f"[+] {template_name}:")
            print(f"    Relative: ({center_x}, {center_y})")
            print(f"    Absolute: ({abs_x}, {abs_y})")
            print(f"    Confidence: {match.confidence:.3f}")
        else:
            print(f"[-] {template_name}: Not found")

    return True

if __name__ == "__main__":
    check_coordinates()