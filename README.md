# 🤖 Dark War Survival Automation Bot

A comprehensive automation solution for Dark War Survival with an advanced **GUI Control Center** supporting both BlueStacks emulator and phone mirroring with real-time controls and performance optimization.

## 🎯 What This Bot Does

This is a **REAL automation bot** that will:
- Take control of your mouse and keyboard
- Detect BlueStacks window automatically
- Use computer vision to "see" the game UI
- Click buttons and perform actions automatically
- Run 24/7 to play Dark War Survival for you

## ✨ Features

### 🎛️ **GUI Control Center (NEW!)**
- **Unified Interface**: Advanced GUI wrapper for easy control
- **Mode Switching**: Seamlessly switch between BlueStacks and Phone automation
- **Real-time Controls**: Start/Stop/Emergency buttons with live monitoring
- **Speed Optimization**: Adjustable click speed, cycle speed, and actions per cycle
- **Window Management**: Auto-detect and select target windows
- **Activity Logging**: Complete activity log with timestamps
- **Performance Tools**: System optimization and window management

### 📱 **Phone Mode Automation**
- **Direct Phone Control**: Works with screen mirroring (Vysor, scrcpy, etc.)
- **Smart Click Areas**: Mail/Rewards, Heroes, World, Events, VIP, Center
- **Advanced Base Support**: Optimized for endgame content (217M+ resources)
- **Fast Performance**: 200+ clicks per minute

### 💻 **BlueStacks Mode Automation**
- **Resource Gathering**: Automatically gather food, wood, stone
- **Building Upgrades**: Upgrade buildings when resources are available
- **Troop Training**: Continuously train troops
- **Reward Collection**: Collect all types of rewards (mail, daily, achievements)
- **Troop Healing**: Heal injured troops automatically
- **Template Matching**: Computer vision for UI element recognition

### Safety Features
- **Emergency Stop**: Press F9 to stop the bot immediately
- **Runtime Limits**: Set maximum runtime (default 12 hours)
- **Break Times**: Take human-like breaks
- **Random Delays**: Randomized timing to appear more human
- **Screenshot Logging**: Save screenshots when errors occur

### Smart Detection
- **Window Management**: Automatically finds and focuses BlueStacks
- **Template Matching**: Uses OpenCV to recognize game UI elements
- **Error Recovery**: Handles common errors and retries actions
- **Statistics Tracking**: Tracks success rates for each task

## 🚀 Quick Setup Guide

### Option A: GUI Control Center (Recommended)

**Step 1: Install Dependencies**
```bash
cd dark-war-automation-bot
pip install -r requirements.txt
```

**Step 2: Optimize Performance (Recommended)**
```bash
python performance_optimizer.py
# Choose 'y' to apply automatic optimizations
```

**Step 3: Launch Control Center**
```bash
# Double-click this file for easy launch:
LAUNCH_BOT_CONTROL.bat

# OR run directly:
python bot_control_center.py
```

**Step 4: Configure and Start**
1. Select your mode (Phone or BlueStacks)
2. Choose target window from dropdown
3. Adjust speed settings (start with defaults)
4. Click "START BOT"

### Option B: Command Line Mode (Advanced Users)

**Step 1: Install Dependencies**
```bash
cd dark-war-automation-bot
pip install -r requirements.txt
```

**Step 2: Test Window Detection**
```bash
python main.py --detect-window
```

Expected output:
```
Looking for window: BlueStacks App Player
✓ Window found: BlueStacks App Player
✓ Window focused successfully
Window position: (0, 0, 1280, 720)
```

### Step 3: Create Templates

The bot needs template images to recognize game UI elements. You need to create these:

1. Open Dark War Survival in BlueStacks
2. Take screenshots of these UI elements:
   - Gather button
   - Resource nodes (food, wood, stone)
   - Upgrade button
   - Confirm button
   - Train button
   - Collect button

3. Save as PNG files in `templates/` directory:
   - `gather_btn.png`
   - `food_node.png`
   - `wood_node.png`
   - `stone_node.png`
   - `upgrade_btn.png`
   - `confirm_btn.png`
   - `train_btn.png`
   - `collect_btn.png`

### Step 4: Test Template Matching

```bash
python main.py --test-templates
```

Expected output:
```
Testing all templates...
✓ gather_btn         - 0.892 - (245, 123)
✓ food_node          - 0.834 - (156, 298)
✗ upgrade_btn        - 0.654 - Not found
...
Template Test Results: 7/10 found (70.0%)
```

### Step 5: Run the Bot (Supervised)

First, run a short test to watch it work:

```bash
python main.py --max-cycles 3 --verbose
```

### Step 6: Run Production Mode

```bash
python main.py
```

## ⚙️ Configuration

Create and edit `bot_config.json`:

```json
{
  "window_title": "BlueStacks App Player",
  "action_delay_min": 1.5,
  "action_delay_max": 3.0,
  "template_threshold": 0.8,
  "emergency_stop_key": "f9",
  "max_runtime_hours": 12,
  "gather_resources": true,
  "upgrade_buildings": true,
  "train_troops": true,
  "attack_monsters": false,
  "arena_battles": false
}
```

## 🛡️ Safety & Anti-Detection

### Human-Like Behavior
- Randomized delays between actions (1.5-3.0 seconds)
- Takes breaks every hour for 5 minutes
- Varies click positions slightly
- Natural mouse movement curves

### Safety Features
- Emergency stop key (F9) - stops bot immediately
- Runtime limits - won't run indefinitely
- Error recovery - handles game crashes/disconnects
- Screenshot logging - saves evidence when things go wrong

### Recommendations
1. **Start Supervised**: Watch the bot for the first hour
2. **Use Breaks**: Enable regular break intervals
3. **Don't Run 24/7**: Take longer breaks between sessions
4. **Monitor Logs**: Check the logs regularly for issues
5. **Backup Account**: Link your account to prevent loss

## 📊 Bot Output

### Console Output
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         Dark War Survival Bot                               ║
║                          Automation System v1.0                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

16:30:25 - INFO - Starting Dark War Survival Bot
16:30:25 - INFO - Emergency stop key: F9
16:30:26 - INFO - Bot initialized successfully

============================================================
CYCLE 1 - Runtime: 0.0h
============================================================
16:30:27 - INFO - Starting task: gather_resources
16:30:30 - INFO - Task completed: gather_resources in 2.8s
16:30:33 - INFO - Starting task: collect_rewards
16:30:35 - INFO - Task completed: collect_rewards in 1.9s
```

### Statistics (Every 10 Cycles)
```
============================================================
BOT STATISTICS
============================================================
RUNTIME:
  0.5 hours

CYCLES COMPLETED:
  10

TASK STATISTICS:
  gather_resources: 9 success, 1 failed
  upgrade_buildings: 3 success, 0 failed
  train_troops: 5 success, 0 failed
============================================================
```

## 🔧 Troubleshooting

### "BlueStacks window not found"
- Make sure BlueStacks is running and visible
- Try different window titles in config:
  - "BlueStacks App Player"
  - "BlueStacks"
  - "BlueStacks 5"

### "Template not found" errors
- Templates need to be exact pixel matches
- Take new screenshots if game UI changed
- Adjust `template_threshold` (0.7-0.9)
- Crop templates to small, unique areas

### Bot clicks wrong locations
- Check BlueStacks window size matches config
- Retake templates at same resolution
- Ensure game is in same state when taking templates

### Bot is too fast/slow
- Adjust `action_delay_min` and `action_delay_max`
- Increase delays for stability
- Decrease for faster execution

## 📁 File Structure

```
dark-war-automation-bot/
├── bot_control_center.py      # 🎛️ Main GUI Control Center
├── performance_optimizer.py   # ⚡ System optimization tools
├── LAUNCH_BOT_CONTROL.bat    # 🚀 Easy launcher script
├── phone_rapid_bot.py         # 📱 Phone automation engine
├── main.py                   # 💻 Command line bot entry point
├── config.py                 # ⚙️ Configuration management
├── window_manager.py         # 🪟 Window detection and control
├── template_matcher.py       # 👁️ Computer vision system
├── game_tasks.py            # 🎮 Game automation logic
├── bot_logger.py            # 📝 Logging system
├── requirements.txt         # 📦 Python dependencies
├── README.md               # 📄 This file
├── .gitignore              # 🚫 Git ignore rules
├── COMPLETE_BOT_SOLUTION.md # 📚 Complete solution guide
├── PHONE_BOT_READY.md      # 📱 Phone setup guide
├── bot_config.json         # ⚙️ Bot configuration (created)
├── speed_config.json       # ⚡ Speed optimization config (created)
├── templates/              # 🖼️ Template images (you create)
│   ├── gather_btn.png
│   ├── food_node.png
│   └── ...
└── logs/                   # 📝 Log files (created)
    └── bot_20241115_163025.log
```

## ⚡ Performance

### System Requirements
- Windows 10/11
- Python 3.7+
- 4GB+ RAM
- BlueStacks App Player

### Expected Performance
- **Startup Time**: ~5 seconds
- **Task Execution**: 2-5 seconds per task
- **Resource Usage**: ~50MB RAM, minimal CPU
- **Actions Per Hour**: 200-400 depending on configuration

## 🚨 Important Notes

This bot will:
- ✅ Control your mouse and keyboard
- ✅ Take screenshots of your screen
- ✅ Click on game elements automatically
- ✅ Run continuously until stopped
- ✅ Modify your game progress

This bot will NOT:
- ❌ Hack or modify the game files
- ❌ Access your account credentials
- ❌ Communicate with game servers directly
- ❌ Install malware or viruses
- ❌ Access files outside the bot directory

## 📞 Support

If you encounter issues:

1. Check the `logs/` directory for error messages
2. Verify all templates are properly created
3. Test with `--detect-window` and `--test-templates`
4. Adjust configuration settings
5. Run with `--verbose` to see detailed output

## 📄 License

This project is for educational purposes. Use at your own risk.

---

**Ready to automate Dark War Survival? Follow the setup guide and let the bot play for you!** 🤖