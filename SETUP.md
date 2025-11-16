# 🚀 Dark War Survival Bot - Complete Setup Guide

## 🎯 Quick Start (For Beginners)

### Method 1: Automatic Installation (Recommended)

1. **Download the repository**
2. **Run the installer**:
   ```bash
   python install.py
   ```
3. **Launch the Bot Control Center**:
   ```bash
   # Double-click this file:
   LAUNCH_BOT_CONTROL.bat
   ```
4. **Start automating!**

### Method 2: Manual Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run performance optimizer**:
   ```bash
   python performance_optimizer.py
   ```

3. **Launch control center**:
   ```bash
   python bot_control_center.py
   ```

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11
- **Python**: 3.7+ (Download from [python.org](https://python.org))
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space

### Game Requirements
Choose **ONE** of these options:

#### Option A: Phone Mirroring (Recommended)
- **Phone**: Android/iPhone with Dark War Survival
- **Mirroring Software**:
  - [Vysor](https://vysor.io/) (Free)
  - [scrcpy](https://github.com/Genymobile/scrcpy) (Free, Open Source)
  - [ApowerMirror](https://www.apowermirror.com/) (Free/Paid)
  - Windows built-in "Your Phone" app

#### Option B: BlueStacks Emulator
- **BlueStacks**: [Download BlueStacks 5](https://www.bluestacks.com/)
- **Game**: Dark War Survival installed in BlueStacks

## 🎮 Game Setup

### For Phone Mirroring

1. **Install mirroring software** (Vysor recommended)
2. **Connect your phone** via USB or WiFi
3. **Enable Developer Options** on phone:
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times
   - Go back to Settings → Developer Options
   - Enable "USB Debugging"
4. **Start mirroring** - your phone screen should appear on PC
5. **Open Dark War Survival** on your phone
6. **Note the window title** (usually "Dark War" or similar)

### For BlueStacks

1. **Install BlueStacks 5**
2. **Download Dark War Survival** from Google Play Store
3. **Launch the game** and complete tutorial
4. **Set BlueStacks to windowed mode** (not fullscreen)
5. **Note the window title** ("BlueStacks App Player")

## 🎛️ Bot Control Center Setup

### First Launch

1. **Run the Control Center**:
   ```bash
   python bot_control_center.py
   ```

2. **Select your mode**:
   - Choose "Phone Mirroring" if using phone
   - Choose "BlueStacks" if using emulator

3. **Select target window**:
   - Click "Refresh" to scan for windows
   - Select your game window from dropdown
   - Click "Test Click" to verify it works

4. **Adjust speed settings**:
   - **Beginner**: Click Speed 0.5s, Cycle Speed 2.0s, Actions 3
   - **Intermediate**: Click Speed 0.1s, Cycle Speed 1.0s, Actions 5
   - **Advanced**: Click Speed 0.01s, Cycle Speed 0.05s, Actions 10

### Settings Configuration

**Tab 2: Settings**
- ✅ Enable "Auto-focus target window"
- ✅ Enable "Minimize other windows" (for performance)
- Configure phone click areas (for phone mode)
- Set performance tools preferences

## ⚡ Performance Optimization

### Automatic Optimization

Run the performance optimizer for best results:

```bash
python performance_optimizer.py
```

This will:
- ✅ Close unnecessary windows
- ✅ Set high priority for bot process
- ✅ Disable Windows animations
- ✅ Optimize PyAutoGUI settings
- ✅ Create aggressive speed configuration

### Manual Optimization Tips

1. **Close other applications** while running bot
2. **Set power mode to High Performance**
3. **Disable antivirus scanning** for bot folder
4. **Use dedicated monitor** for the game
5. **Ensure stable internet connection**

## 🎯 Usage Modes

### Phone Mode Features

**Smart Click Areas**:
- 📧 **Mail/Rewards** (highest priority)
- ⚔️ **Heroes** (character management)
- 🌍 **World** (exploration features)
- 🎪 **Events** (limited-time activities)
- 👑 **VIP** (premium benefits)
- 🏰 **Center** (base buildings)

**Advantages**:
- Direct phone control
- Access to all mobile features
- Faster response times
- Advanced base support (millions of resources)

### BlueStacks Mode Features

**Automated Tasks**:
- 🌾 Resource gathering (food, wood, stone)
- 🏗️ Building upgrades
- ⚔️ Troop training
- 🎁 Reward collection
- 🏥 Troop healing
- 👹 Monster attacks (optional)

**Advantages**:
- Stable emulator environment
- Template-based recognition
- Proven automation methods

## 🛡️ Safety Features

### Built-in Protections

- **Emergency Stop**: F9 key stops bot instantly
- **Runtime Limits**: Configurable maximum runtime
- **Error Recovery**: Handles disconnections and errors
- **Human-like Timing**: Random delays between actions
- **Window Loss Recovery**: Re-finds target window automatically

### Usage Recommendations

1. **Start Supervised**: Watch the bot for first 30 minutes
2. **Use Conservative Settings**: Start with slower speeds
3. **Take Breaks**: Don't run 24/7, take regular breaks
4. **Monitor Performance**: Check logs and activity regularly
5. **Backup Account**: Link to Google/Facebook

## 📊 Expected Performance

### Phone Mode Performance
- **Speed**: 200+ clicks per minute
- **Efficiency**: 5-8 actions per cycle
- **Resource Usage**: Minimal CPU/RAM
- **Response Time**: 0.1-0.5 seconds per action

### BlueStacks Mode Performance
- **Speed**: 100+ clicks per minute
- **Efficiency**: 3-5 actions per cycle
- **Resource Usage**: Moderate CPU/RAM
- **Response Time**: 0.5-2.0 seconds per action

## 🔧 Troubleshooting

### Common Issues

**"Window not found"**
- ✅ Verify game is open and visible
- ✅ Check window title matches expected format
- ✅ Try "Refresh" button in control center
- ✅ Restart the game application

**"Bot not clicking anything"**
- ✅ Test click first with "Test Click" button
- ✅ Verify target window is selected
- ✅ Check if game screen is visible
- ✅ Try different speed settings

**"Very slow performance"**
- ✅ Run `performance_optimizer.py`
- ✅ Close other applications
- ✅ Reduce speed settings temporarily
- ✅ Check for Windows updates

**"Template matching fails" (BlueStacks)**
- ✅ Update templates with `create_templates.py`
- ✅ Check game resolution settings
- ✅ Verify BlueStacks window size
- ✅ Adjust template threshold in config

### Getting Help

1. **Check Activity Log**: Tab 3 in Control Center
2. **Review Config**: Check `bot_config.json`
3. **Run Diagnostics**: Use test scripts in repository
4. **Read Documentation**: See `/docs/` folder
5. **Check Issues**: GitHub repository issues page

## 📁 File Organization

### Core Files
- `bot_control_center.py` - Main GUI interface
- `performance_optimizer.py` - Speed optimization
- `phone_rapid_bot.py` - Phone automation
- `main.py` - Command line interface

### Configuration
- `bot_config.json` - Main bot configuration
- `speed_config.json` - Performance settings
- `requirements.txt` - Python dependencies

### Documentation
- `README.md` - Overview and features
- `SETUP.md` - This setup guide
- `COMPLETE_BOT_SOLUTION.md` - Advanced guide
- `PHONE_BOT_READY.md` - Phone-specific setup

## 🎉 Next Steps

Once setup is complete:

1. **Test basic functionality** with conservative settings
2. **Gradually increase speed** as you get comfortable
3. **Explore advanced features** in Settings tab
4. **Monitor and adjust** based on performance
5. **Enjoy automated gameplay!**

## 📞 Support

- **Documentation**: Read all `.md` files in repository
- **GitHub Issues**: Report bugs and feature requests
- **Performance**: Use built-in optimization tools
- **Configuration**: Customize `bot_config.json`

---

**🚀 Ready to automate Dark War Survival? Follow this guide and start dominating!**