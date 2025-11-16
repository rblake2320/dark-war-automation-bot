"""
Dark War Survival Automation Bot
Main entry point for the bot
"""

import os
import sys
import time
import keyboard
import argparse
from datetime import datetime, timedelta

from config import get_config, save_config
from bot_logger import setup_logging, log_bot_stats
from window_manager import WindowManager
from template_matcher import TemplateMatcher
from game_tasks import DarkWarBot

def print_banner():
    """Print bot startup banner"""
    banner = """
================================================================================
                         Dark War Survival Bot
                          Automation System v1.0
================================================================================
"""
    print(banner)

def detect_window():
    """Test window detection"""
    config = get_config()
    window_manager = WindowManager(config.window_title)

    print(f"Looking for window: {config.window_title}")

    if window_manager.find_window():
        print(f"[+] Window found: {window_manager.window_title}")

        if window_manager.focus_window():
            print("[+] Window focused successfully")
            rect = window_manager.get_window_rect()
            if rect:
                print(f"Window position: {rect}")
                return True
        else:
            print("[-] Failed to focus window")
    else:
        print("[-] Window not found")
        print("\nTroubleshooting:")
        print("1. Make sure BlueStacks is running")
        print("2. Make sure Dark War Survival is open")
        print("3. Try different window titles in config")

    return False

def test_templates():
    """Test template matching"""
    config = get_config()
    window_manager = WindowManager(config.window_title)
    template_matcher = TemplateMatcher()

    if not window_manager.find_window():
        print("[-] BlueStacks window not found")
        return False

    if not window_manager.focus_window():
        print("[-] Could not focus window")
        return False

    print("Capturing screenshot...")
    screenshot = window_manager.capture_window()
    if screenshot is None:
        print("[-] Could not capture screenshot")
        return False

    print("Testing all templates...")
    results = template_matcher.test_all_templates(screenshot)

    if not results:
        print("No templates found in templates/ directory")
        print("\nTo create templates:")
        print("1. Take screenshots of game UI elements")
        print("2. Save them as PNG files in templates/ directory")
        print("3. Name them: gather_btn.png, upgrade_btn.png, etc.")
        return False

    found_count = sum(1 for r in results.values() if r['found'])
    total_count = len(results)

    for template_name, result in results.items():
        status = "[+]" if result['found'] else "[-]"
        confidence = result['confidence']
        position = result['position'] if result['found'] else "Not found"
        print(f"{status} {template_name:<20} - {confidence:.3f} - {position}")

    print(f"\nTemplate Test Results: {found_count}/{total_count} found ({found_count/total_count*100:.1f}%)")

    return found_count > 0

def create_sample_config():
    """Create sample configuration file"""
    config = get_config()
    save_config(config)
    print(f"Sample configuration created: bot_config.json")
    print("Edit this file to customize bot behavior")

def run_bot(max_cycles: int = None, verbose: bool = False):
    """Main bot execution loop"""
    config = get_config()
    logger = setup_logging(config.log_level, config.save_screenshots)

    print_banner()

    logger.info("Starting Dark War Survival Bot")
    logger.info(f"Emergency stop key: {config.emergency_stop_key.upper()}")
    logger.info(f"Max runtime: {config.max_runtime_hours} hours")

    # Initialize bot
    bot = DarkWarBot(config)

    # Test window detection
    if not bot.window_manager.find_window():
        logger.error("BlueStacks window not found. Please start BlueStacks and Dark War Survival.")
        return False

    if not bot.window_manager.focus_window():
        logger.error("Could not focus BlueStacks window")
        return False

    logger.info("Bot initialized successfully")

    # Main execution loop
    start_time = time.time()
    last_break = time.time()
    cycle = 0

    try:
        while True:
            cycle += 1
            cycle_start = time.time()

            # Check for emergency stop
            if keyboard.is_pressed(config.emergency_stop_key):
                logger.info(f"Emergency stop key ({config.emergency_stop_key.upper()}) pressed")
                break

            # Check max runtime
            runtime_hours = (time.time() - start_time) / 3600
            if runtime_hours >= config.max_runtime_hours:
                logger.info(f"Max runtime ({config.max_runtime_hours}h) reached")
                break

            # Check max cycles (for testing)
            if max_cycles and cycle > max_cycles:
                logger.info(f"Max cycles ({max_cycles}) reached")
                break

            # Cycle header
            logger.info("=" * 60)
            logger.info(f"CYCLE {cycle} - Runtime: {runtime_hours:.1f}h")
            logger.info("=" * 60)

            # Get next task
            task = bot.get_next_task()
            if task:
                success = bot.execute_task(task)
                if verbose:
                    logger.info(f"Task result: {'SUCCESS' if success else 'FAILED'}")
            else:
                logger.info("No tasks available, waiting...")

            # Random delay between actions
            bot.wait_with_random_delay()

            # Break time check
            time_since_break = (time.time() - last_break) / 60
            if time_since_break >= config.break_interval_minutes:
                logger.info(f"Taking break for {config.break_duration_minutes} minutes")
                time.sleep(config.break_duration_minutes * 60)
                last_break = time.time()

            # Print statistics every 10 cycles
            if cycle % 10 == 0:
                log_bot_stats({
                    "Runtime": f"{runtime_hours:.1f} hours",
                    "Cycles Completed": cycle,
                    "Task Statistics": {
                        f"{task}: {stats['success']} success, {stats['failed']} failed"
                        for task, stats in bot.stats.items()
                    }
                })

    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    finally:
        # Final statistics
        total_runtime = (time.time() - start_time) / 3600
        logger.info("Bot execution completed")
        log_bot_stats({
            "Total Runtime": f"{total_runtime:.1f} hours",
            "Total Cycles": cycle,
            "Final Statistics": bot.stats
        })

    return True

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description="Dark War Survival Automation Bot")
    parser.add_argument("--detect-window", action="store_true",
                       help="Test window detection only")
    parser.add_argument("--test-templates", action="store_true",
                       help="Test template matching only")
    parser.add_argument("--create-config", action="store_true",
                       help="Create sample configuration file")
    parser.add_argument("--max-cycles", type=int,
                       help="Maximum number of cycles to run (for testing)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Handle specific commands
    if args.detect_window:
        return detect_window()
    elif args.test_templates:
        return test_templates()
    elif args.create_config:
        create_sample_config()
        return True
    else:
        # Run the bot
        return run_bot(args.max_cycles, args.verbose)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)