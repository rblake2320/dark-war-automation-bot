# Dark War Survival - Game Views & Coordinate System Reference

**CRITICAL CONTEXT FOR FUTURE SESSIONS**

## Game View System Overview

Dark War Survival has **TWO DISTINCT VIEW MODES** with different coordinate systems and content:

### 🏠 **Shelter View (Base View)**
**What it shows:**
- Your city/base buildings and structures
- Building levels and upgrade status
- Buildings like Hunter's Hut, Kitchen, Tower, Farm, etc.
- This is where **building automation should focus**

**Characteristics:**
- Screen shows your base layout in isometric view
- Buildings are stationary in this view
- Building names and levels are visible
- **This is the PRIMARY view for OCR building detection**

**Coordinate System:**
- Buildings have fixed positions relative to base layout
- Coordinates are stable when zoomed/centered on base
- Can move view by click-and-drag but buildings stay in relative positions

### 🌍 **World View (Map View)**
**What it shows:**
- World map with other players, resources, monsters
- Exploration targets and resource nodes
- Alliance territories and world events
- NOT relevant for building automation

**Characteristics:**
- Shows large world map
- Player can scroll/pan around the world
- No building information visible
- Used for exploration, gathering, attacks

**Coordinate System:**
- World coordinates are completely different
- Constantly changing as player pans around map
- **NOT suitable for building detection**

---

## Critical Implications for OCR Coordinate System

### ⚠️ **IMPORTANT CONSIDERATIONS:**

1. **View Mode Detection Required:**
   - OCR system MUST detect which view mode is active
   - Building scanning should ONLY work in Shelter View
   - Coordinates logged in World View would be meaningless

2. **Coordinate Stability:**
   - **Shelter View**: Coordinates are reliable for building detection
   - **World View**: Coordinates change constantly, not usable
   - Click-and-drag in Shelter View can shift coordinates

3. **User Workflow:**
   - User should be instructed to be in **Shelter View** for coordinate logging
   - System should validate view mode before scanning
   - Warning if attempting to scan in World View

4. **OCR Text Differences:**
   - **Shelter View**: Building names, levels (Hunter's Hut Lv.12/25)
   - **World View**: Player names, alliance names, resource amounts

---

## Implementation Requirements for Coordinate System

### View Detection Strategy

**Text-Based Detection:**
```python
def detect_game_view(ocr_text):
    shelter_keywords = ["hunter", "kitchen", "tower", "farm", "level", "lv.", "upgrade"]
    world_keywords = ["gather", "attack", "alliance", "monster", "resource node"]

    shelter_count = sum(1 for keyword in shelter_keywords if keyword in ocr_text.lower())
    world_count = sum(1 for keyword in world_keywords if keyword in ocr_text.lower())

    if shelter_count > world_count:
        return "shelter"
    elif world_count > shelter_count:
        return "world"
    else:
        return "unknown"
```

**UI Element Detection:**
- Look for specific UI elements that indicate view mode
- Shelter View: Building upgrade buttons, building names
- World View: Alliance territory markers, resource nodes

### Coordinate Logging Workflow

**Enhanced Workflow:**
1. **Validate View Mode**: Ensure user is in Shelter View
2. **Stabilize View**: User should center on their base
3. **Log Coordinates**: Click buildings to store positions
4. **Validate Coordinates**: Test that coordinates point to correct buildings
5. **Store View Context**: Save which view mode coordinates were captured in

### Error Prevention

**Safeguards to Implement:**
```python
def validate_coordinate_context(self):
    """Ensure coordinates are valid for current view"""
    # Take screenshot
    # Run quick OCR
    # Detect view mode
    # Warn if in wrong view
    # Suggest switching to Shelter View
```

---

## User Instructions for Coordinate Logging

### Setup Process:

1. **Enter Shelter View:**
   - Ensure you're viewing your base/city (not world map)
   - Center the view on your base buildings
   - Make sure building names and levels are clearly visible

2. **Stabilize Screen:**
   - Don't scroll or move the view during coordinate logging
   - Zoom to a level where building names are readable
   - Ensure good lighting/contrast

3. **Log Building Coordinates:**
   - Click directly on building name/level text (not building graphic)
   - One click per building type
   - Follow the UI prompts for building selection

4. **Validation:**
   - System will test coordinates by extracting small regions
   - Verify OCR can read building names at logged positions
   - Recapture any coordinates that fail validation

### Troubleshooting:

**If Coordinates Don't Work:**
- Check if you're in the correct view mode (Shelter vs World)
- Verify you haven't scrolled/moved the view since logging
- Ensure building text is visible at the coordinate position
- Recalibrate coordinates if window size changed

---

## Technical Implementation Notes

### Coordinate Storage Format

**Enhanced JSON Format:**
```json
{
  "version": "2.0",
  "view_mode": "shelter",
  "view_context": {
    "base_centered": true,
    "zoom_level": "medium",
    "screen_stable": true
  },
  "window_info": {
    "title": "Dark War",
    "width": 1280,
    "height": 720
  },
  "buildings": {
    "hunter_hut_1": {
      "name": "Hunter's Hut",
      "building_type": "hunter",
      "absolute": {"x": 450, "y": 320},
      "relative": {"x": 0.35, "y": 0.44},
      "roi_size": {"width": 150, "height": 80},
      "view_mode_captured": "shelter",
      "validation_status": "verified",
      "timestamp": "2025-11-16T20:30:00"
    }
  }
}
```

### View Mode Validation

**Pre-Scan Checks:**
```python
def validate_scan_conditions(self, screenshot):
    """Validate that scanning conditions are optimal"""
    # Quick OCR to detect view mode
    view_mode = self.detect_game_view(screenshot)

    if view_mode != "shelter":
        return {
            "valid": False,
            "error": f"Wrong view mode: {view_mode}",
            "suggestion": "Switch to Shelter View to see your base buildings"
        }

    return {"valid": True}
```

---

## Session Continuity Information

### For Future Claude Sessions:

**Key Points to Remember:**
1. Dark War Survival has Shelter View (buildings) and World View (map)
2. OCR building detection ONLY works in Shelter View
3. Coordinates must be captured while in Shelter View with stable screen
4. World View coordinates are meaningless for building detection
5. System needs view mode validation before scanning

**Files Created:**
- `coordinate_logger.py` - Mouse click coordinate capture system
- `DARK_WAR_GAME_VIEWS_REFERENCE.md` - This documentation file
- Enhanced `requirements.txt` with pynput dependency

**Implementation Status:**
- ✅ Coordinate logging framework complete
- ⚠️ Need to add view mode detection
- ⚠️ Need to integrate with bot_control_center.py
- ⚠️ Need to enhance building_manager.py for coordinate-based scanning

**Critical Next Steps:**
1. Add view mode detection to coordinate system
2. Implement coordinate setup UI in bot control center
3. Add coordinate-based ROI scanning to building manager
4. Test system with both Shelter and World views to ensure proper behavior

This context is essential for any future development of the coordinate-based building detection system.