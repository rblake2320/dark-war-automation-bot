"""
Configuration settings for Dark War Survival Bot
"""

import json
import os
from dataclasses import dataclass, asdict
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

    @classmethod
    def load_from_file(cls, filepath: str) -> 'BotConfig':
        """Load configuration from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                return cls(**data)
        return cls()

    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2)

# Default configuration
DEFAULT_CONFIG_PATH = "bot_config.json"

def get_config() -> BotConfig:
    """Get the bot configuration"""
    return BotConfig.load_from_file(DEFAULT_CONFIG_PATH)

def save_config(config: BotConfig):
    """Save the bot configuration"""
    config.save_to_file(DEFAULT_CONFIG_PATH)