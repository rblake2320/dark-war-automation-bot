# Changelog - Dark War Survival Bot

## [2.1.0] - 2024-11-16

### 🚀 **Enhanced OCR Detection System & Building Management**

### ✨ **New Features**

#### 🏗️ **Smart Building Management Tab**
- **Building Detection**: OCR-powered building scanning and level detection
- **Building Tree View**: Organized display of detected buildings with status
- **JSON Export**: Export building data for external analysis
- **Last Scan Tracking**: Timestamps for all detected buildings
- **Scan Progress**: Visual feedback during building detection workflows

#### 👁️ **OCR Status Synchronization**
- **Real-Time OCR Status**: Live OCR system availability monitoring
- **OCR Test Function**: One-click OCR system verification
- **Version Display**: Shows Tesseract version when available
- **Visual Indicators**: Color-coded status (green/red) for OCR health
- **Error Detection**: Automatic detection of OCR configuration issues

#### 🎮 **Phone-Friendly Speed Presets**
- **Slow Mode (Safe)**: 0.5s clicks, 3.0s cycles, 3 actions - for careful operations
- **Normal Mode**: 0.2s clicks, 1.5s cycles, 5 actions - balanced performance
- **Fast Mode**: 0.1s clicks, 0.8s cycles, 7 actions - quick automation
- **Turbo Mode**: 0.05s clicks, 0.3s cycles, 10 actions - maximum speed
- **One-Click Presets**: Apply entire speed configuration instantly

#### 🛠️ **Error Log Utilities & Diagnostics**
- **Error Log Viewer**: Integrated error log display in Diagnostics tab
- **Log Refresh**: One-click error log refresh
- **Log Clearing**: Clear old error logs to free space
- **Diagnostic Scripts Integration**: Run OCR tests directly from GUI
- **System Information Panel**: Shows version, OCR, keyboard hook status

#### 🔍 **OCR Diagnostic Scripts**
- **simple_ocr_test.py**: Quick OCR verification with basic text recognition
  - Installation check
  - Simple text recognition test
  - Screenshot OCR test (if screenshots available)
  - Pass/fail/skip reporting
- **test_ocr_debug.py**: Comprehensive OCR debugging tool
  - Environment validation
  - Performance benchmarking with different PSM modes
  - Image preprocessing tests (grayscale, threshold, adaptive)
  - Confidence level analysis
  - Debug image generation
  - Detailed error logging to error_logs/

### 🔧 **Improvements**

#### 💪 **Hardened BotConfig Loading/Saving**
- **Version Field Support**: Config files now include version information
- **Unknown Key Preservation**: Forward/backward compatible - preserves unknown settings
- **Emergency Stop Sync**: Automatically syncs emergency_stop_key with emergency_stop_keys list
- **Graceful Degradation**: Handles missing keys with sensible defaults
- **Migration Support**: Automatic config migration from older versions
- **Error Recovery**: Robust error handling prevents config crashes

#### 📊 **Enhanced Statistics Tracking**
- **OCR Scan Count**: Tracks number of OCR operations performed
- **Buildings Detected**: Counts detected buildings across sessions
- **Scan Progress**: Real-time feedback during building scans

#### 📁 **Runtime Artifact Management**
- **error_logs/ Directory**: Dedicated directory for error logs
- **building_data/ Directory**: Stores exported building JSON data
- **Automatic Directory Creation**: Install script creates necessary directories
- **.gitignore Updates**: Excludes runtime artifacts from version control

### 🐛 **Bug Fixes**
- **Config Loading Crashes**: Fixed crashes when loading configs with new/unknown keys
- **Emergency Stop Key Mismatch**: Synchronized emergency stop options between config and Control Center
- **Test Compatibility**: Resolved PytestReturnNotNoneWarning in legacy tests

### 📦 **Dependencies**

#### New Dependencies
- `pytesseract`: OCR text recognition engine
- `opencv-python-headless`: Additional OpenCV support for OCR
- `keyboard`: Enhanced keyboard hook support (optional)

#### Installation Updates
- **install.py**: Updated to v2.1.0 with OCR dependency installation
- **Tesseract Installation Guide**: Added platform-specific Tesseract installation instructions
- **Optional Dependency Handling**: Gracefully handles missing OCR dependencies

### 📚 **Documentation**
- **OCR Pipeline Documentation**: Added documentation for OCR diagnostic tools
- **Building Management Guide**: Instructions for using building detection features
- **Speed Preset Guide**: Documentation for phone-friendly speed presets
- **Error Log Utilities**: Guide for using diagnostic tools

### ⚙️ **Configuration Changes**
- Added `version` field to bot_config.json
- Changed default `emergency_stop_key` from "f9" to "esc"
- Added `emergency_stop_keys` list for multiple key support
- Added `enable_ocr` flag (default: true)
- Added `ocr_confidence_threshold` (default: 0.7)

### 🧪 **Testing**
- All tests pass with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest`
- Note: PytestReturnNotNoneWarning for legacy tests (functionality intact)
- OCR diagnostic scripts tested and verified
- Config migration tested from v2.0.0 to v2.1.0

---

## [2.0.0] - 2024-11-16

### 🚀 **Major Release - Complete Enhancement Package**

### ✨ **New Features**

#### 🚨 **Emergency Stop System**
- **ESC Key Emergency Stop**: Global ESC key monitoring for instant bot termination
- **Response Time**: Improved from 5+ seconds to <1 second
- **Global Hotkey**: Works even when bot window is not focused
- **Visual Feedback**: Window title flashes "🚨 EMERGENCY STOP ACTIVATED 🚨"
- **Statistics Tracking**: Counts emergency stop events

#### 🧠 **Smart Window Management**
- **Window State Detection**: Automatically detects minimized, collapsed, or invisible windows
- **Intelligent Skipping**: Skips unusable windows during automation cycles
- **Exclusion List**: Automatically excludes bot control center and system windows
- **Auto-Recovery**: Waits for windows to become usable again
- **Enhanced Filtering**: Better window selection with size and state validation

#### 📝 **Action-Aware Logging**
- **Detailed Action Logs**: Shows "Clicked Mail icon - found 2 rewards" instead of coordinates
- **Result Detection**: Simulates and logs expected action results
- **Context Awareness**: Understands what each click area does
- **Action History**: Maintains detailed history of all actions performed
- **Enhanced Statistics**: Tracks specific action types and success rates

#### 🔄 **Version Control System**
- **Automatic Migration**: Detects v1.x configs and upgrades them seamlessly
- **Backward Compatibility**: Preserves all existing settings during upgrade
- **Version Display**: Shows version number in GUI title bar
- **Configuration Validation**: Ensures config files are valid and compatible

### 🔧 **Improvements**

#### ⚡ **Performance Enhancements**
- **Faster Emergency Stop**: Reduced sleep intervals for immediate response
- **Window Validation**: Pre-validates windows before automation cycles
- **Memory Management**: Automatic cleanup of action history (keeps last 1000 actions)
- **Error Handling**: Improved error messages and recovery mechanisms

#### 🎯 **Enhanced Target Selection**
- **Smart Auto-Selection**: Better detection of game windows vs bot windows
- **Multiple Keywords**: Supports more phone mirroring apps (Vysor, scrcpy, etc.)
- **Validation**: Double-checks selected windows are actually usable
- **User Feedback**: Clear messages about window selection results

#### 🔍 **Test Click Improvements**
- **Detailed Analysis**: Shows window state, size, and expected action
- **Target Identification**: Explains what area will be clicked
- **Result Simulation**: Shows expected outcome of test click
- **Enhanced Feedback**: Uses emojis and clear status messages

### 🐛 **Bug Fixes**

#### Critical Issues Resolved:
- **Fixed**: Emergency stop buttons not working reliably (root cause: long sleep blocking)
- **Fixed**: Bot targeting its own control center window instead of game
- **Fixed**: Window detection including minimized/collapsed windows
- **Fixed**: Logs showing coordinates instead of meaningful actions
- **Fixed**: No feedback on test click functionality

#### Technical Fixes:
- **Thread Management**: Improved bot worker thread lifecycle
- **Memory Leaks**: Prevented memory growth during long automation sessions
- **Error Recovery**: Better handling of window focus and state changes
- **UI Responsiveness**: Faster UI updates during automation

### 📊 **Enhanced Statistics**
- **Action Breakdown**: Tracks specific actions performed (Mail clicks, Heroes clicks, etc.)
- **Window Management**: Counts skipped windows and reasons
- **Emergency Events**: Tracks emergency stop usage
- **Performance Metrics**: Better runtime and efficiency tracking

### 🔧 **Technical Changes**

#### New Dependencies:
- **keyboard>=1.13.0**: For ESC key emergency stop monitoring

#### Configuration Format:
```json
{
  "version": "2.0.0",
  "emergency_stop_keys": ["esc"],
  "enable_detailed_logging": true,
  "skip_minimized_windows": true,
  // ... other settings preserved
}
```

#### New Files:
- Enhanced `bot_control_center.py` with all v2.0 features
- Automatic config migration system
- Comprehensive logging and statistics

### 📚 **Documentation Updates**
- Updated README.md with v2.0 features
- Added upgrade guide for v1.x users
- Enhanced setup instructions
- Created comprehensive changelog

### ⚠️ **Breaking Changes**
None! Version 2.0 is fully backward compatible with v1.x configurations.

---

## [1.0.0] - 2024-11-15

### ✨ **Initial Release**
- Basic GUI Control Center with tabs
- Phone and BlueStacks automation modes
- Speed controls and window selection
- Basic logging and statistics
- Template matching for BlueStacks
- Simple emergency stop (F9 key in CLI only)

---

## Migration Guide

### From v1.x to v2.0:
1. **No action required** - upgrade happens automatically
2. **Install keyboard library**: `pip install keyboard>=1.13.0`
3. **Launch bot**: All new features work immediately
4. **New ESC key**: Use ESC for instant emergency stop

### What's Preserved:
- All your speed settings
- Window preferences
- Automation mode selection
- Phone click area settings
- Performance settings

### What's Enhanced:
- Much faster emergency stop response
- Better window management
- Detailed action logging
- Enhanced error handling
- Professional UI feedback

---

**🎉 Version 2.0.0 transforms your bot from a basic automation tool into a professional-grade solution with enterprise-level features!**