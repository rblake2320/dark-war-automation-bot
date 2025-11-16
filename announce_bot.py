"""
Bot with audio/visual announcements before each action
"""

import time
import sys
from game_tasks import DarkWarBot
from config import get_config
from bot_logger import setup_logging

def announce_bot():
    """Run bot with clear announcements"""
    print("=== ANNOUNCING BOT ===")
    print("This bot will announce each action before doing it")
    print()

    config = get_config()
    logger = setup_logging("INFO", False)  # No file logging for clarity

    # Initialize bot
    bot = DarkWarBot(config)

    # Test setup
    if not bot.window_manager.find_window():
        print("ERROR: BlueStacks window not found")
        return

    if not bot.window_manager.focus_window():
        print("ERROR: Could not focus window")
        return

    print("✓ Bot initialized successfully")
    print()

    # Run a few cycles with announcements
    for cycle in range(1, 4):
        print(f"=================== CYCLE {cycle} ===================")
        print("Getting next task...")

        task = bot.get_next_task()
        if task:
            print(f"📋 NEXT TASK: {task.name.upper()}")
            print(f"⏰ TASK PRIORITY: {task.priority}")
            print()

            print("🎯 GETTING READY TO ACT...")
            print("👀 WATCH YOUR BLUESTACKS WINDOW NOW!")
            print()

            # Countdown
            for i in range(3, 0, -1):
                print(f"Executing {task.name} in {i}...")
                sys.stdout.flush()
                time.sleep(1)

            print(f"🤖 EXECUTING: {task.name.upper()}")
            print("📸 Taking screenshot...")

            # Execute the task
            start_time = time.time()
            success = bot.execute_task(task)
            duration = time.time() - start_time

            if success:
                print(f"✅ SUCCESS: {task.name} completed in {duration:.1f}s")
            else:
                print(f"❌ FAILED: {task.name} failed after {duration:.1f}s")

            print()
            print("🔄 Waiting before next task...")
            time.sleep(3)  # Short delay between cycles
        else:
            print("⏸️ No tasks available")
            break

    print("\n🏁 DEMO COMPLETE")
    print("Did you see the bot actions happen?")

if __name__ == "__main__":
    announce_bot()