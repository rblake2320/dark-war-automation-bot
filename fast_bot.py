"""
Fast-moving bot - no delays, rapid actions
"""

import time
import cv2
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def fast_automation_cycle():
    """Single fast automation cycle with minimal delays"""
    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        return False

    # Rapid screenshot
    screenshot = window_manager.capture_window()
    if screenshot is None:
        return False

    actions_performed = 0

    print("RAPID SCAN: Looking for all available actions...")

    # Get ALL available actions at once
    all_matches = template_matcher.find_all_templates(screenshot)
    actionable_items = [match for match in all_matches if match.confidence > 0.85]

    print(f"Found {len(actionable_items)} high-confidence targets")

    # Priority order for actions
    action_priority = {
        'build_scrapyard_btn': 1,
        'mail_icon': 2,
        'upgrade_number_2': 3,
        'upgrade_number_3': 4,
    }

    # Sort by priority
    prioritized_actions = sorted(actionable_items,
                                key=lambda x: action_priority.get(x.template_name, 10))

    # Execute actions rapidly
    for i, match in enumerate(prioritized_actions[:4]):  # Max 4 actions per cycle
        center_x, center_y = template_matcher.get_template_center(match)

        print(f"RAPID ACTION {i+1}: {match.template_name} at ({center_x}, {center_y})")

        # Fast click
        window_manager.click_relative(center_x, center_y, duration=0.1)
        time.sleep(0.3)  # Minimal delay

        # If it's a build action, try quick confirmation
        if 'build' in match.template_name.lower():
            # Quick confirmation attempts
            confirm_positions = [
                (center_x + 50, center_y + 50),
                (center_x, center_y + 100),
                (center_x + 100, center_y + 80),
            ]

            for conf_x, conf_y in confirm_positions:
                window_manager.click_relative(conf_x, conf_y, duration=0.1)
                time.sleep(0.2)

        # If it's a building, try upgrade clicks
        elif 'upgrade' in match.template_name.lower():
            # Quick building interaction
            building_clicks = [
                (center_x, center_y + 40),      # Below the number
                (center_x + 30, center_y + 30), # Diagonal
                (center_x - 30, center_y + 30), # Other diagonal
            ]

            for build_x, build_y in building_clicks:
                window_manager.click_relative(build_x, build_y, duration=0.1)
                time.sleep(0.1)

        actions_performed += 1

    print(f"CYCLE COMPLETE: {actions_performed} actions in ~{actions_performed * 0.5:.1f} seconds")
    return actions_performed > 0

def rapid_fire_bot():
    """Continuous rapid-fire automation"""
    print("=== RAPID FIRE BOT ACTIVATED ===")
    print("This bot moves FAST - minimal delays between actions")
    print("Press Ctrl+C to stop")
    print()

    cycle = 0
    total_actions = 0
    start_time = time.time()

    try:
        while True:
            cycle += 1
            print(f"\n--- RAPID CYCLE {cycle} ---")

            cycle_start = time.time()
            success = fast_automation_cycle()
            cycle_time = time.time() - cycle_start

            if success:
                total_actions += 1
                print(f"Cycle {cycle} completed in {cycle_time:.1f}s")
            else:
                print(f"Cycle {cycle} - no actions available")

            # Very short break between cycles
            time.sleep(0.5)

            # Stats every 10 cycles
            if cycle % 10 == 0:
                elapsed = time.time() - start_time
                print(f"\n=== STATS ===")
                print(f"Cycles: {cycle}")
                print(f"Active cycles: {total_actions}")
                print(f"Runtime: {elapsed:.1f}s")
                print(f"Speed: {cycle/elapsed:.1f} cycles/sec")

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n=== RAPID BOT STOPPED ===")
        print(f"Total cycles: {cycle}")
        print(f"Active cycles: {total_actions}")
        print(f"Runtime: {elapsed:.1f} seconds")
        print(f"Average speed: {cycle/elapsed:.1f} cycles/second")

def speed_test():
    """Test how fast the bot can perform actions"""
    print("=== SPEED TEST ===")
    print("Testing maximum action speed...")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("Setup failed")
        return

    screenshot = window_manager.capture_window()
    all_matches = template_matcher.find_all_templates(screenshot)

    if not all_matches:
        print("No targets found for speed test")
        return

    print(f"Speed testing with {len(all_matches)} targets")

    start_time = time.time()

    # Rapid-fire clicking
    for i, match in enumerate(all_matches[:10]):  # Test with first 10 targets
        center_x, center_y = template_matcher.get_template_center(match)
        window_manager.click_relative(center_x, center_y, duration=0.05)  # Ultra-fast clicks

    end_time = time.time()

    total_time = end_time - start_time
    clicks_per_second = len(all_matches[:10]) / total_time

    print(f"SPEED TEST RESULTS:")
    print(f"10 clicks in {total_time:.2f} seconds")
    print(f"Speed: {clicks_per_second:.1f} clicks/second")
    print(f"Average click time: {total_time/10:.3f} seconds")

if __name__ == "__main__":
    print("FAST BOT OPTIONS:")
    print("1. Rapid Fire Mode (continuous fast automation)")
    print("2. Speed Test (measure maximum speed)")
    print("3. Single Fast Cycle (test run)")

    choice = input("Choose option (1-3): ").strip()

    if choice == "1":
        rapid_fire_bot()
    elif choice == "2":
        speed_test()
    else:
        print("Running single fast cycle...")
        result = fast_automation_cycle()
        if result:
            print("Fast cycle completed successfully!")
        else:
            print("Fast cycle completed - no actions available")