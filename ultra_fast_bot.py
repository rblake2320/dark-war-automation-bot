"""
Ultra-fast continuous bot - no waiting around!
"""

import time
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from config import get_config

def ultra_fast_continuous():
    """Ultra-fast continuous automation with no delays"""
    print("=== ULTRA FAST CONTINUOUS BOT ===")
    print("Maximum speed automation - 0.5 second cycles!")
    print("This will rapidly perform all available actions")
    print("Press Ctrl+C to stop")
    print()

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("ERROR: Cannot access game")
        return

    cycle = 0
    actions_this_session = 0
    start_time = time.time()

    try:
        while True:
            cycle += 1
            cycle_start = time.time()

            # Ultra-fast screenshot and analysis
            screenshot = window_manager.capture_window()
            if screenshot is None:
                continue

            # Get all high-confidence matches
            all_matches = template_matcher.find_all_templates(screenshot)
            good_matches = [m for m in all_matches if m.confidence > 0.87]

            if good_matches:
                print(f"CYCLE {cycle}: {len(good_matches)} targets found")

                # Execute all actions rapidly
                for i, match in enumerate(good_matches[:3]):  # Max 3 per cycle for speed
                    center_x, center_y = template_matcher.get_template_center(match)

                    # Ultra-fast click
                    window_manager.click_relative(center_x, center_y, duration=0.05)

                    print(f"  -> {match.template_name} ({center_x},{center_y}) conf:{match.confidence:.2f}")

                    # Action-specific quick follow-ups
                    if 'build' in match.template_name:
                        # Quick build confirmations
                        for dx, dy in [(50, 50), (0, 80), (100, 60)]:
                            window_manager.click_relative(center_x + dx, center_y + dy, duration=0.05)
                    elif 'upgrade' in match.template_name:
                        # Quick building clicks
                        window_manager.click_relative(center_x, center_y + 35, duration=0.05)
                        window_manager.click_relative(center_x + 40, center_y + 40, duration=0.05)

                actions_this_session += len(good_matches[:3])

            else:
                print(f"CYCLE {cycle}: No targets (scanning...)")

            cycle_time = time.time() - cycle_start

            # Mini stats every 20 cycles
            if cycle % 20 == 0:
                elapsed = time.time() - start_time
                print(f"\n--- SPEED STATS ---")
                print(f"Cycles: {cycle} | Actions: {actions_this_session}")
                print(f"Runtime: {elapsed:.1f}s | Speed: {cycle/elapsed:.1f} cyc/s")
                print(f"Action rate: {actions_this_session/elapsed:.1f} act/s")
                print("------------------")

            # Ultra-short pause (just enough to not overwhelm the game)
            time.sleep(0.1)

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n=== ULTRA FAST BOT STOPPED ===")
        print(f"Total cycles: {cycle}")
        print(f"Total actions: {actions_this_session}")
        print(f"Runtime: {elapsed:.1f} seconds")
        print(f"Cycle speed: {cycle/elapsed:.1f} cycles/second")
        print(f"Action speed: {actions_this_session/elapsed:.1f} actions/second")
        print(f"Average: {actions_this_session/cycle:.1f} actions per cycle")

def burst_mode():
    """10-second burst of maximum speed actions"""
    print("=== 10-SECOND BURST MODE ===")
    print("Maximum speed for 10 seconds!")

    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window() or not window_manager.focus_window():
        print("Setup failed")
        return

    print("Starting 10-second burst in 3 seconds...")
    time.sleep(1)
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    print("GO!")

    start_time = time.time()
    action_count = 0

    while time.time() - start_time < 10:  # 10 second burst
        screenshot = window_manager.capture_window()
        if screenshot:
            matches = template_matcher.find_all_templates(screenshot)
            good_matches = [m for m in matches if m.confidence > 0.85]

            for match in good_matches[:2]:  # Max 2 per burst cycle
                center_x, center_y = template_matcher.get_template_center(match)
                window_manager.click_relative(center_x, center_y, duration=0.03)
                action_count += 1

        time.sleep(0.05)  # 20 cycles per second

    elapsed = time.time() - start_time
    print(f"\nBURST COMPLETE!")
    print(f"Actions in 10 seconds: {action_count}")
    print(f"Speed: {action_count/elapsed:.1f} actions/second")

if __name__ == "__main__":
    print("ULTRA FAST BOT OPTIONS:")
    print("1. Ultra Fast Continuous (runs until stopped)")
    print("2. 10-Second Burst Mode (maximum speed test)")

    choice = input("Choose option (1 or 2): ").strip()

    if choice == "2":
        burst_mode()
    else:
        ultra_fast_continuous()