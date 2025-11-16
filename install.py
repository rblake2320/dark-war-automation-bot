#!/usr/bin/env python3
"""
Dark War Survival Bot - Installation Script v2.1.0
Automatically installs dependencies and sets up the bot
Includes OCR support and enhanced diagnostics
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
    # Core dependencies
    dependencies = [
        "opencv-python",
        "pyautogui",
        "pygetwindow",
        "pillow",
        "numpy",
        "psutil"
    ]

    # Optional OCR dependencies (v2.1.0)
    ocr_dependencies = [
        "pytesseract",
        "opencv-python-headless"
    ]

    print("\n[INFO] Installing core dependencies...")
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False

    print("\n[INFO] Installing OCR dependencies (v2.1.0)...")
    print("[INFO] Note: Tesseract OCR must be installed separately")
    print("[INFO] Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    print("[INFO] Linux: sudo apt-get install tesseract-ocr")
    print("[INFO] Mac: brew install tesseract")

    for dep in ocr_dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"[WARN] OCR dependency {dep} failed - OCR features may be limited")
            # Continue anyway since OCR is optional

    # Optional keyboard hook dependency
    print("\n[INFO] Installing keyboard hook support...")
    if not run_command("pip install keyboard", "Installing keyboard"):
        print("[WARN] Keyboard hook failed - ESC emergency stop may be limited")

    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "templates",
        "logs",
        "screenshots",
        "error_logs",  # v2.1.0
        "building_data"  # v2.1.0
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
    "version": "2.1.0",
    "window_title": "BlueStacks App Player",
    "phone_window_title": "Dark War",
    "action_delay_min": 0.1,
    "action_delay_max": 0.5,
    "template_threshold": 0.8,
    "emergency_stop_key": "esc",
    "emergency_stop_keys": ["esc"],
    "max_runtime_hours": 12,
    "enable_logging": true,
    "enable_ocr": true,
    "ocr_confidence_threshold": 0.7,
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

    # Test core imports
    try:
        import cv2
        import pyautogui
        import pygetwindow
        import PIL
        import numpy
        import psutil
        print("[SUCCESS] All core dependencies imported successfully")
    except ImportError as e:
        print(f"[ERROR] Core import failed: {e}")
        return False

    # Test optional OCR imports (v2.1.0)
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("[SUCCESS] OCR dependencies available and working")
    except ImportError:
        print("[WARN] OCR dependencies not available - OCR features disabled")
    except Exception as e:
        print(f"[WARN] Tesseract not found: {e}")
        print("[INFO] Install Tesseract to enable OCR features")

    # Test keyboard hook (v2.1.0)
    try:
        import keyboard
        print("[SUCCESS] Keyboard hook support available")
    except ImportError:
        print("[WARN] Keyboard library not available - ESC stop may be limited")

    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE! (v2.1.0)")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("1. Launch the Bot Control Center:")
    print("   • Double-click: LAUNCH_BOT_CONTROL.bat")
    print("   • OR run: python bot_control_center.py")
    print()
    print("2. Test OCR System (NEW in v2.1.0):")
    print("   • Simple test: python simple_ocr_test.py")
    print("   • Full diagnostics: python test_ocr_debug.py")
    print()
    print("3. Optimize Performance (Recommended):")
    print("   • Run: python performance_optimizer.py")
    print()
    print("4. Quick Test:")
    print("   • Phone Mode: python phone_rapid_bot.py")
    print("   • BlueStacks: python main.py --detect-window")
    print()
    print("5. Read Documentation:")
    print("   • README.md - Complete setup guide")
    print("   • CHANGELOG.md - Version 2.1.0 release notes")
    print("   • SESSION_CONTINUITY_GUIDE.md - Advanced features")
    print()
    print("🚀 Ready to automate Dark War Survival!")
    print("✨ New in v2.1.0: Smart building management & OCR detection!")

def main():
    """Main installation function"""
    print("="*60)
    print("🤖 Dark War Survival Bot v2.1.0 - Installation Script")
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