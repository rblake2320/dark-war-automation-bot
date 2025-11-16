# 📚 Dark War Survival Bot - Documentation Index

## 🚀 Quick Start Guides

### For Beginners
1. **[SETUP.md](../SETUP.md)** - Complete setup guide with step-by-step instructions
2. **[README.md](../README.md)** - Main project overview and feature list
3. **[install.py](../install.py)** - Automatic installation script

### For Advanced Users
1. **Command Line Usage** - `python main.py --help`
2. **Configuration Guide** - Edit `bot_config.json`
3. **Performance Tuning** - `python performance_optimizer.py`

## 📱 Phone Mode Documentation

### Setup and Configuration
- **Phone Mirroring Setup**: Requirements and software options
- **Window Detection**: Finding your "Dark War" window
- **Click Area Configuration**: Mail, Heroes, World, Events, VIP, Center
- **Advanced Base Support**: Optimized for millions of resources

### Features
- **Smart Click Areas**: Automated prioritized clicking
- **Fast Performance**: 200+ clicks per minute
- **Direct Control**: No emulator overhead
- **Advanced Content**: Endgame features support

## 💻 BlueStacks Mode Documentation

### Setup and Configuration
- **BlueStacks Installation**: Download and setup guide
- **Template Creation**: UI element recognition setup
- **Window Management**: Auto-detection and focus
- **Building Automation**: Resource and troop management

### Features
- **Computer Vision**: Template matching system
- **Building Upgrades**: Intelligent upgrade logic
- **Resource Collection**: Automated gathering
- **Multi-building Support**: Handle multiple structures

## 🎛️ Control Center Guide

### Interface Overview
- **Tab 1: Bot Control** - Main automation controls
- **Tab 2: Settings** - Configuration options
- **Tab 3: Activity Log** - Real-time monitoring

### Controls and Features
- **Mode Switching**: Phone ↔ BlueStacks seamlessly
- **Speed Controls**: Click speed, cycle speed, actions per cycle
- **Window Management**: Auto-detect and select target windows
- **Emergency Controls**: Instant stop functionality
- **Real-time Stats**: Cycles, clicks, runtime, errors

### Speed Settings Guide
| Mode | Click Speed | Cycle Speed | Actions/Cycle | Use Case |
|------|-------------|-------------|---------------|----------|
| Safe | 0.5s | 2.0s | 3 | First time users |
| Balanced | 0.1s | 1.0s | 5 | Regular usage |
| Speed Demon | 0.01s | 0.05s | 10 | Maximum performance |

## ⚡ Performance Optimization

### Automatic Optimization
- **Performance Optimizer**: `python performance_optimizer.py`
- **System Tweaks**: Windows animations, process priority
- **Speed Configuration**: Aggressive timing settings
- **Window Management**: Minimize conflicts

### Manual Optimization
- **Close Applications**: Reduce system load
- **Power Settings**: High performance mode
- **Antivirus**: Exclude bot folder from scanning
- **Monitor Setup**: Dedicated display for game

### Performance Metrics
- **Before Optimization**: 10-15 actions/minute
- **After Optimization**: 600+ actions/minute
- **Speed Improvement**: Up to 40x faster
- **Resource Usage**: Minimal CPU/RAM impact

## 🛡️ Safety and Security

### Built-in Safety Features
- **Emergency Stop**: F9 key for instant shutdown
- **Runtime Limits**: Configurable maximum run time
- **Error Recovery**: Automatic handling of common issues
- **Human-like Behavior**: Randomized timing and patterns

### Anti-Detection Measures
- **Natural Delays**: Random timing between actions
- **Break Intervals**: Scheduled pauses
- **Click Variation**: Slightly different click positions
- **Mouse Movement**: Natural cursor paths

### Usage Recommendations
- **Supervised Start**: Watch first 30 minutes
- **Conservative Settings**: Begin with slower speeds
- **Regular Breaks**: Don't run continuously
- **Account Safety**: Link to backup services

## 🔧 Configuration Files

### bot_config.json
```json
{
  "window_title": "BlueStacks App Player",
  "phone_window_title": "Dark War",
  "action_delay_min": 0.1,
  "action_delay_max": 0.5,
  "template_threshold": 0.8,
  "emergency_stop_key": "f9",
  "max_runtime_hours": 12,
  "enable_logging": true
}
```

### speed_config.json
```json
{
  "click_delay": 0.01,
  "cycle_delay": 0.05,
  "actions_per_cycle": 10,
  "aggressive_mode": true
}
```

## 🐛 Troubleshooting Guide

### Common Issues and Solutions

#### Window Detection Problems
- **Issue**: "Window not found"
- **Solution**:
  1. Verify game is open and visible
  2. Check window title matches config
  3. Use "Refresh" button in control center
  4. Restart game application

#### Performance Issues
- **Issue**: "Very slow performance"
- **Solution**:
  1. Run `performance_optimizer.py`
  2. Close other applications
  3. Reduce speed settings
  4. Check system resources

#### Click Detection Problems
- **Issue**: "Bot not clicking anything"
- **Solution**:
  1. Use "Test Click" button first
  2. Verify target window selected
  3. Check game screen visibility
  4. Adjust speed settings

#### Template Matching (BlueStacks)
- **Issue**: "Template not found"
- **Solution**:
  1. Update templates with screenshot tool
  2. Check game resolution settings
  3. Verify window size consistency
  4. Adjust template threshold

### Diagnostic Tools
- **Window Detection**: `python find_phone_window.py`
- **Template Testing**: `python create_templates.py`
- **Performance Check**: `python performance_optimizer.py`
- **Config Validation**: Check `bot_config.json` syntax

## 📊 API Reference

### Core Classes

#### BotControlCenter
- **Purpose**: Main GUI interface
- **Location**: `bot_control_center.py`
- **Key Methods**:
  - `start_bot()` - Begin automation
  - `stop_bot()` - End automation
  - `emergency_stop()` - Instant shutdown

#### WindowManager
- **Purpose**: Window detection and control
- **Location**: `window_manager.py`
- **Key Methods**:
  - `find_window()` - Locate target window
  - `focus_window()` - Bring window to front
  - `get_window_rect()` - Get window dimensions

#### TemplateMatcherr
- **Purpose**: Computer vision system
- **Location**: `template_matcher.py`
- **Key Methods**:
  - `find_template()` - Locate UI elements
  - `click_template()` - Click found elements
  - `update_templates()` - Refresh recognition data

### Configuration Classes

#### BotConfig
- **Purpose**: Settings management
- **Location**: `config.py`
- **Key Properties**:
  - `window_title` - Target window name
  - `action_delay_min/max` - Timing controls
  - `template_threshold` - Recognition sensitivity

## 🚀 Development Guide

### Project Structure
```
dark-war-automation-bot/
├── Core Bot Files/
│   ├── bot_control_center.py    # Main GUI
│   ├── performance_optimizer.py # Speed tools
│   ├── phone_rapid_bot.py       # Phone engine
│   └── main.py                  # CLI interface
├── Configuration/
│   ├── config.py                # Settings management
│   ├── bot_config.json          # User settings
│   └── speed_config.json        # Performance settings
├── Automation Engine/
│   ├── window_manager.py        # Window control
│   ├── template_matcher.py      # Computer vision
│   ├── game_tasks.py           # Game logic
│   └── bot_logger.py           # Logging system
└── Documentation/
    ├── README.md               # Main overview
    ├── SETUP.md               # Setup guide
    └── docs/INDEX.md          # This file
```

### Contributing
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** with proper documentation
4. **Test thoroughly** on both phone and BlueStacks modes
5. **Submit pull request** with detailed description

### Testing
- **Unit Tests**: Individual component testing
- **Integration Tests**: Full workflow testing
- **Performance Tests**: Speed and efficiency validation
- **Safety Tests**: Emergency stop and error handling

## 📄 License and Legal

### Open Source License
- **Type**: MIT License
- **Commercial Use**: Permitted
- **Modification**: Permitted
- **Distribution**: Permitted

### Disclaimer
- **Educational Purpose**: For learning automation concepts
- **User Responsibility**: Follow game terms of service
- **No Warranty**: Use at your own risk
- **Account Safety**: Not responsible for account issues

### Game Compliance
- **Terms of Service**: Review Dark War Survival TOS
- **Fair Play**: Use responsibly and ethically
- **Detection Risk**: Automation may be detectable
- **Account Protection**: Link accounts to prevent loss

---

## 📞 Support and Community

### Getting Help
1. **Read Documentation**: Start with README.md and SETUP.md
2. **Check Troubleshooting**: Common issues and solutions above
3. **GitHub Issues**: Report bugs and request features
4. **Configuration**: Customize settings for your needs

### Contribution
- **Bug Reports**: Detailed issue descriptions
- **Feature Requests**: Enhancement suggestions
- **Code Contributions**: Pull requests welcome
- **Documentation**: Help improve guides

---

**🎮 Happy Automating! Master Dark War Survival with the ultimate bot solution!**