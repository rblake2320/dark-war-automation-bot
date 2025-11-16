#!/usr/bin/env python3
"""
Dark War Survival Bot - Installation Script
Automatically installs dependencies and sets up the bot
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed:")
        print(f"[ERROR] {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"[INFO] Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("[ERROR] Python 3.7 or higher is required!")
        print("[ERROR] Please upgrade Python and try again.")
        return False

    print("[SUCCESS] Python version is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    dependencies = [
        "opencv-python",
        "pyautogui",
        "pygetwindow",
        "pillow",
        "numpy",
        "psutil"
    ]

    print("\n[INFO] Installing dependencies...")
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "templates",
        "logs",
        "screenshots"
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[SUCCESS] Created directory: {directory}")
        else:
            print(f"[INFO] Directory already exists: {directory}")

def create_default_config():
    """Create default configuration file"""
    config_content = """{
    "window_title": "BlueStacks App Player",
    "phone_window_title": "Dark War",
    "action_delay_min": 0.1,
    "action_delay_max": 0.5,
    "template_threshold": 0.8,
    "emergency_stop_key": "f9",
    "max_runtime_hours": 12,
    "enable_logging": true,
    "phone_mode": {
        "click_areas": {
            "mail": true,
            "heroes": true,
            "world": true,
            "events": true,
            "vip": true,
            "center": true
        }
    },
    "bluestacks_mode": {
        "gather_resources": true,
        "upgrade_buildings": true,
        "train_troops": true,
        "attack_monsters": false,
        "arena_battles": false
    }
}"""

    if not os.path.exists("bot_config.json"):
        with open("bot_config.json", "w") as f:
            f.write(config_content)
        print("[SUCCESS] Created default bot_config.json")
    else:
        print("[INFO] bot_config.json already exists")

def test_installation():
    """Test if the installation was successful"""
    print("\n[INFO] Testing installation...")

    # Test imports
    try:
        import cv2
        import pyautogui
        import pygetwindow
        import PIL
        import numpy
        import psutil
        print("[SUCCESS] All dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE!")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("1. Launch the Bot Control Center:")
    print("   • Double-click: LAUNCH_BOT_CONTROL.bat")
    print("   • OR run: python bot_control_center.py")
    print()
    print("2. Optimize Performance (Recommended):")
    print("   • Run: python performance_optimizer.py")
    print()
    print("3. Quick Test:")
    print("   • Phone Mode: python phone_rapid_bot.py")
    print("   • BlueStacks: python main.py --detect-window")
    print()
    print("4. Read Documentation:")
    print("   • README.md - Complete setup guide")
    print("   • COMPLETE_BOT_SOLUTION.md - Advanced features")
    print("   • PHONE_BOT_READY.md - Phone setup guide")
    print()
    print("🚀 Ready to automate Dark War Survival!")

def main():
    """Main installation function"""
    print("="*60)
    print("🤖 Dark War Survival Bot - Installation Script")
    print("="*60)

    # Check system requirements
    print(f"[INFO] Operating System: {platform.system()}")
    print(f"[INFO] Platform: {platform.platform()}")

    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("\n[ERROR] Dependency installation failed!")
        sys.exit(1)

    # Create directories and config
    create_directories()
    create_default_config()

    # Test installation
    if not test_installation():
        print("\n[ERROR] Installation test failed!")
        sys.exit(1)

    # Success
    print_next_steps()

if __name__ == "__main__":
    main()