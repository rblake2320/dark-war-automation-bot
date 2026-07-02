"""
Configuration settings for Dark War Survival Bot
"""

import json
import os
from dataclasses import dataclass, asdict, field, fields
from typing import Dict, Any

@dataclass
class BotConfig:
    # Window settings
    window_title: str = "BlueStacks App Player"
    window_width: int = 1280
    window_height: int = 720

    # Bot behavior
    action_delay_min: float = 1.5
    action_delay_max: float = 3.0
    template_threshold: float = 0.8
    max_retries: int = 3

    # Safety settings
    emergency_stop_key: str = "f9"
    max_runtime_hours: int = 12
    break_interval_minutes: int = 60
    break_duration_minutes: int = 5

    # Features to enable
    gather_resources: bool = True
    upgrade_buildings: bool = True
    train_troops: bool = True
    collect_rewards: bool = True
    heal_troops: bool = True
    attack_monsters: bool = False
    arena_battles: bool = False

    # Logging
    log_level: str = "INFO"
    save_screenshots: bool = True
    extra_settings: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'BotConfig':
        """Load configuration from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                field_names = {f.name for f in fields(cls)}
                parsed_data: Dict[str, Any] = {}
                extra_settings: Dict[str, Any] = {}

                for key, value in data.items():
                    if key in field_names and key != "extra_settings":
                        parsed_data[key] = value
                    elif key == "emergency_stop_keys" and "emergency_stop_key" in field_names:
                        if isinstance(value, list) and value:
                            parsed_data["emergency_stop_key"] = value[0]
                    else:
                        extra_settings[key] = value

                if extra_settings and "extra_settings" in field_names:
                    parsed_data["extra_settings"] = extra_settings

                return cls(**parsed_data)
        return cls()

    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        data = asdict(self)
        extra_settings = data.pop("extra_settings", {}) or {}

        # Preserve multi-key emergency stop configuration if present
        emergency_stop_key = data.get("emergency_stop_key")
        if emergency_stop_key and "emergency_stop_keys" not in extra_settings:
            extra_settings["emergency_stop_keys"] = [emergency_stop_key]

        merged_config = {**extra_settings, **data}

        with open(filepath, 'w') as f:
            json.dump(merged_config, f, indent=2)

# Default configuration
DEFAULT_CONFIG_PATH = "bot_config.json"

def get_config() -> BotConfig:
    """Get the bot configuration"""
    return BotConfig.load_from_file(DEFAULT_CONFIG_PATH)

def save_config(config: BotConfig):
    """Save the bot configuration"""
    config.save_to_file(DEFAULT_CONFIG_PATH)