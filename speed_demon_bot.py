"""
Speed Demon Bot - The fastest automation for Dark War Survival
"""

import time
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def speed_demon():
    """Fastest possible automation - no delays, maximum efficiency"""
    print("=== SPEED DEMON ACTIVATED ===")
    print("Fastest possible automation for Dark War Survival!")
    print("This will perform actions as fast as the game can handle")
    print("Press Ctrl+C to stop")
    print()

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("Cannot access game")
        return

    cycle = 0
    actions = 0
    start_time = time.time()

    # Priority targets (most important first)
    priority_targets = [
        'build_scrapyard_btn',
        'mail_icon',
        'upgrade_number_3',
        'upgrade_number_2'
    ]

    try:
        while True:
            cycle += 1

            # Lightning-fast screenshot
            screenshot = window_manager.capture_window()
            if screenshot is None:
                continue

            # Find priority targets first
            targets_found = []
            for priority in priority_targets:
                match = template_matcher.find_template(screenshot, priority)
                if match and match.confidence > 0.85:
                    targets_found.append((priority, match))

            # If no priority targets, find any targets
            if not targets_found:
                all_matches = template_matcher.find_all_templates(screenshot)
                targets_found = [(m.template_name, m) for m in all_matches if m.confidence > 0.9]

            if targets_found:
                print(f"C{cycle}: {len(targets_found)} targets -> ", end="")

                for target_name, match in targets_found[:2]:  # Max 2 per cycle for speed
                    center_x, center_y = template_matcher.get_template_center(match)

                    # Lightning click
                    window_manager.click_relative(center_x, center_y, duration=0.02)
                    print(f"{target_name[:8]}({center_x},{center_y}) ", end="")

                    # Instant follow-up actions
                    if 'build' in target_name:
                        # Rapid build confirmation attempts
                        window_manager.click_relative(center_x + 60, center_y + 70, duration=0.02)
                        window_manager.click_relative(center_x + 80, center_y + 50, duration=0.02)
                    elif 'upgrade' in target_name:
                        # Rapid building interaction
                        window_manager.click_relative(center_x, center_y + 30, duration=0.02)
                        window_manager.click_relative(center_x + 30, center_y + 35, duration=0.02)
                    elif 'mail' in target_name:
                        # Quick mail interaction
                        time.sleep(0.5)  # Brief pause for mail menu

                    actions += 1

                print()  # New line after cycle
            else:
                if cycle % 50 == 0:  # Only print every 50 cycles when no targets
                    print(f"C{cycle}: Scanning...")

            # Micro-pause (just enough to not crash the game)
            time.sleep(0.02)

            # Stats every 100 cycles
            if cycle % 100 == 0:
                elapsed = time.time() - start_time
                print(f"\n--- SPEED STATS ---")
                print(f"Cycles: {cycle}")
                print(f"Actions: {actions}")
                print(f"Runtime: {elapsed:.1f}s")
                print(f"Speed: {cycle/elapsed:.1f} cycles/sec")
                print(f"Efficiency: {actions/cycle*100:.1f}% action rate")
                print("------------------")

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n=== SPEED DEMON RESULTS ===")
        print(f"Cycles completed: {cycle}")
        print(f"Actions performed: {actions}")
        print(f"Total runtime: {elapsed:.1f} seconds")
        print(f"Cycle rate: {cycle/elapsed:.1f} cycles/second")
        print(f"Action rate: {actions/elapsed:.1f} actions/second")
        print(f"Efficiency: {actions/cycle*100:.1f}% of cycles had actions")

        if actions > 0:
            print(f"\nSUCCESS: Your bot performed {actions} game actions!")
            print("The bot is working and affecting your game at maximum speed!")
        else:
            print(f"\nNo actions performed - check game state or resources")

if __name__ == "__main__":
    speed_demon()