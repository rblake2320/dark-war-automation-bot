# Dark War Survival - Complete OCR Detection Reference

This document provides comprehensive details about what the OCR system needs to detect in Dark War Survival game for building management automation.

## Game Overview
Dark War Survival is a mobile strategy game where players build and upgrade various buildings in their base. The automation bot uses OCR (Optical Character Recognition) to scan the game screen and automatically detect which buildings are maxed out to avoid wasting resources.

## Building Types & Max Levels

### Resource Production Buildings
- **Farm**: Produces food
  - Max Level: 25
  - Visual: Green crop fields
  - Text appears: "Farm", "Farm Lv.X", "Farm Level X/25"

- **Lumber Mill**: Produces wood
  - Max Level: 25
  - Visual: Brown wooden structure with logs
  - Text appears: "Lumber Mill", "Mill", "Lumber", "Lv.X/25"

- **Quarry**: Produces stone
  - Max Level: 25
  - Visual: Gray stone pit with rocks
  - Text appears: "Quarry", "Stone Quarry", "Lv.X/25"

- **Iron Mine**: Produces iron
  - Max Level: 25
  - Visual: Dark mine entrance with tools
  - Text appears: "Iron Mine", "Mine", "Lv.X/25"

### Storage Buildings
- **Warehouse**: Stores all resources
  - Max Level: 25
  - Visual: Large brown storage building
  - Text appears: "Warehouse", "Storage", "Lv.X/25"

### Defense Buildings
- **Tower** / **Watch Tower**: Defensive structure
  - Max Level: 25
  - Visual: Tall stone tower with battlements
  - Text appears: "Tower", "Watch Tower", "Watchtower", "Defense Tower", "Lv.X/25"

- **Wall**: Defensive barrier
  - Max Level: 25
  - Visual: Stone wall segments
  - Text appears: "Wall", "City Wall", "Lv.X/25"

- **Gate**: Main entrance
  - Max Level: 25
  - Visual: Large wooden/stone gate
  - Text appears: "Gate", "Main Gate", "City Gate", "Lv.X/25"

### Military Buildings
- **Barracks**: Trains infantry units
  - Max Level: 25
  - Visual: Military building with flags
  - Text appears: "Barracks", "Training Barracks", "Lv.X/25"

- **Stable**: Trains cavalry units
  - Max Level: 25
  - Visual: Horse stable building
  - Text appears: "Stable", "War Stable", "Lv.X/25"

- **Workshop**: Produces siege equipment
  - Max Level: 25
  - Visual: Building with mechanical tools
  - Text appears: "Workshop", "Siege Workshop", "Lv.X/25"

### Special Buildings
- **Hunter's Hut** / **Hunter Hut**: Hunting building
  - Max Level: 25
  - Visual: Small wooden hut with hunting equipment
  - Text appears: "Hunter's Hut", "Hunter Hut", "Hunters Hut", "HuntersHut", "Lv.X/25"

- **Kitchen**: Food preparation
  - Max Level: 25
  - Visual: Building with cooking equipment
  - Text appears: "Kitchen", "Mess Hall", "Lv.X/25"

- **Dorm** / **Dormitory**: Housing for troops
  - Max Level: 10 (Lower than others!)
  - Visual: Residential building
  - Text appears: "Dorm", "Dormitory", "Barracks Dorm", "Lv.X/10"

- **Academy**: Research building
  - Max Level: 25
  - Visual: Academic building with scrolls/books
  - Text appears: "Academy", "Research Academy", "Lv.X/25"

- **Hospital**: Heals wounded troops
  - Max Level: 25
  - Visual: Medical building with red cross
  - Text appears: "Hospital", "Field Hospital", "Lv.X/25"

- **Hero Hall**: Manages heroes
  - Max Level: 25
  - Visual: Grand hall building
  - Text appears: "Hero Hall", "Heroes Hall", "Hall", "Lv.X/25"

- **Gathering Ground**: Resource collection point
  - Max Level: 20 (Lower than others!)
  - Visual: Open area with gathering workers
  - Text appears: "Gathering Ground", "Gathering", "Ground", "Lv.X/20"

## OCR Text Patterns to Detect

### Level Display Formats
The game displays building levels in several formats:

1. **Standard Format**: "Lv.12/25" or "Lv 12/25"
2. **Full Word**: "Level 12/25" or "Level: 12/25"
3. **Short Form**: "12/25" (just numbers)
4. **Maxed Indicators**: "MAX", "MAXED", "Lv.25/25"
5. **Percentage**: "100%" (for maxed buildings)

### Text Variations to Handle
- **Spacing**: "Lv.12 / 25", "Lv. 12/25", "Lv12/25"
- **Capitalization**: "LV.12/25", "lv.12/25", "Level 12/25"
- **Abbreviations**: "Lvl.12/25", "L.12/25"
- **Concatenation**: "HuntersHutLv.12" (OCR sometimes runs words together)

### Screen Layout Context
- **Building Names**: Usually appear above or below the building graphic
- **Level Text**: Appears near building name, often in yellow or white text
- **UI Overlays**: Game may have popup windows with building upgrade info
- **Background**: Buildings are on grass/dirt terrain background
- **Lighting**: Game has day/night cycle affecting text visibility

## Common OCR Challenges

### Text Quality Issues
- **Small Text**: Building names/levels can be small on screen
- **Font Style**: Game uses stylized fantasy fonts
- **Color Contrast**: Text may have low contrast with background
- **Shadows/Effects**: Text often has drop shadows or glow effects

### Game UI Interference
- **Overlapping Elements**: Troops, heroes, or effects may cover building text
- **Animation**: Buildings may have animated elements
- **Popups**: Tutorial or upgrade windows may cover buildings
- **Zoom Level**: Player may zoom in/out affecting text size

### OCR Noise Patterns
- **Partial Text**: "Hunt...Hut" (text cut off)
- **Merged Text**: "FarmLv12Mill" (multiple buildings merged)
- **Special Characters**: "Lv․12/25" (wrong punctuation)
- **Numbers**: "1v.12/25" (1 instead of L), "Lv.I2/25" (I instead of 1)

## Detection Strategy

### Primary Detection Method
1. **Scan for building names** in the extracted text
2. **Look for level patterns** near building names
3. **Parse level numbers** to determine if maxed
4. **Validate results** against known max levels

### Building Name Matching
```
Building Variations to Match:
- Hunter: ["hunter", "huntershut", "hunters", "hut"]
- Tower: ["tower", "watchtower", "watch", "defense"]
- Kitchen: ["kitchen", "mess", "hall"]
- Farm: ["farm", "crops"]
- Mill: ["mill", "lumber", "wood"]
- Quarry: ["quarry", "stone"]
- Mine: ["mine", "iron"]
- Warehouse: ["warehouse", "storage"]
- Barracks: ["barracks", "training"]
- Academy: ["academy", "research"]
- Hospital: ["hospital", "medical"]
- Hero Hall: ["hero", "hall", "heroes"]
- Gathering: ["gathering", "ground", "collection"]
- Dorm: ["dorm", "dormitory", "housing"]
```

### Level Pattern Matching
```regex
Primary Patterns:
- r'lv\.?\s*(\d+)\s*/\s*(\d+)'     # "Lv.12/25", "Lv 12/25"
- r'level\s*:?\s*(\d+)\s*/\s*(\d+)' # "Level: 12/25"
- r'(\d+)\s*/\s*(\d+)'             # "12/25"
- r'(\d+)\/(\d+)'                  # "12/25" (no spaces)
- r'max'                           # "MAX", "MAXED"
- r'(\d+)\s*%'                     # "100%"
```

## Success Criteria

### What OCR Should Successfully Detect
1. **Building Name**: Correctly identify the building type
2. **Current Level**: Extract the current building level
3. **Max Level**: Know the maximum possible level for that building
4. **Maxed Status**: Determine if current level equals max level
5. **Confidence**: Provide confidence score for detection accuracy

### Expected Results Format
```json
{
  "hunter": {
    "current_level": 12,
    "max_level": 25,
    "is_maxed": false,
    "confidence": 0.85,
    "detection_method": "numeric",
    "raw_text": "Hunter's Hut Lv.12/25",
    "area": "detected"
  },
  "dorm": {
    "current_level": 10,
    "max_level": 10,
    "is_maxed": true,
    "confidence": 0.90,
    "detection_method": "numeric",
    "raw_text": "Dorm Lv.10/10",
    "area": "detected"
  }
}
```

## Testing & Validation

### Test Cases
1. **Perfect Text**: "Hunter's Hut Lv.25/25" → Should detect as maxed
2. **Noisy Text**: "Hunt...ut Lv2□/25" → Should still detect level 25/25
3. **Merged Text**: "FarmLv12MillLv25" → Should detect both buildings
4. **Missing Levels**: "Kitchen" → Should detect building but no level
5. **False Positives**: Random numbers "12/25" → Should not match without building name

### Validation Rules
- **Level Range**: Current level should be 1-25 (1-20 for Gathering, 1-10 for Dorm)
- **Ratio Check**: Max level should be >= current level
- **Name Validation**: Building name must match known registry
- **Confidence Threshold**: Only mark as maxed if confidence > 85%

## Integration with Bot

### How OCR Results Are Used
1. **Scan Screenshot**: Capture current game screen
2. **Extract Text**: Use Tesseract OCR to read all text
3. **Parse Buildings**: Find building names and levels
4. **Update Database**: Store building states and maxed status
5. **Skip Logic**: Automation will skip clicking on maxed buildings
6. **Statistics**: Track how many buildings are maxed, time saved

### Performance Metrics
- **Detection Rate**: % of visible buildings correctly identified
- **Accuracy Rate**: % of level readings that are correct
- **False Positive Rate**: % of non-building text incorrectly detected
- **Processing Speed**: Time to complete full screen scan
- **Memory Usage**: RAM usage during OCR processing

This reference should provide complete context for any AI system working with Dark War Survival OCR detection.