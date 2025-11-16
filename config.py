"""
Configuration settings for Dark War Survival Bot
Enhanced v2.1.0 - Hardened config loading with version control
"""

import json
import os
from dataclasses import dataclass, asdict, fields
from typing import Dict, Any, Optional
import logging

__version__ = "2.1.0"

@dataclass
class BotConfig:
    # Version control
    version: str = __version__

    # Window settings
    window_title: str = "BlueStacks App Player"
    window_width: int = 1280
    window_height: int = 720

    # Bot behavior
    action_delay_min: float = 1.5
    action_delay_max: float = 3.0
    template_threshold: float = 0.8
    max_retries: int = 3

    # Safety settings - synchronized emergency stop options
    emergency_stop_key: str = "esc"  # Changed default to match Control Center
    emergency_stop_keys: list = None  # Support multiple keys
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

    # OCR settings (v2.1.0+)
    enable_ocr: bool = True
    ocr_confidence_threshold: float = 0.7

    # Extra data storage for unknown keys
    _extra_data: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize emergency_stop_keys list if None"""
        if self.emergency_stop_keys is None:
            self.emergency_stop_keys = [self.emergency_stop_key]
        if self._extra_data is None:
            self._extra_data = {}

    @classmethod
    def load_from_file(cls, filepath: str) -> 'BotConfig':
        """
        Load configuration from JSON file with hardened error handling.
        - Tolerates new keys by storing them in _extra_data
        - Preserves unknown settings for backward/forward compatibility
        - Syncs emergency-stop options automatically
        """
        if not os.path.exists(filepath):
            logging.info(f"Config file {filepath} not found, using defaults")
            return cls()

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Get known field names
            known_fields = {f.name for f in fields(cls) if not f.name.startswith('_')}

            # Separate known and unknown keys
            known_data = {}
            extra_data = {}

            for key, value in data.items():
                if key in known_fields:
                    known_data[key] = value
                else:
                    # Preserve unknown keys for forward compatibility
                    extra_data[key] = value
                    logging.debug(f"Preserving unknown config key: {key}")

            # Sync emergency stop settings
            if 'emergency_stop_key' in known_data and 'emergency_stop_keys' not in known_data:
                known_data['emergency_stop_keys'] = [known_data['emergency_stop_key']]
            elif 'emergency_stop_keys' in known_data and 'emergency_stop_key' not in known_data:
                # Use first key from list
                if known_data['emergency_stop_keys']:
                    known_data['emergency_stop_key'] = known_data['emergency_stop_keys'][0]

            # Create config with known data
            config = cls(**known_data)
            config._extra_data = extra_data

            # Migrate old version if needed
            if config.version != __version__:
                logging.info(f"Migrating config from v{config.version} to v{__version__}")
                config.version = __version__

            return config

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in config file {filepath}: {e}")
            logging.error("Using default configuration")
            return cls()
        except TypeError as e:
            # Handle case where dataclass gets unexpected kwargs
            logging.error(f"Config validation error: {e}")
            logging.error("Using default configuration")
            return cls()
        except Exception as e:
            logging.error(f"Unexpected error loading config: {e}")
            logging.error("Using default configuration")
            return cls()

    def save_to_file(self, filepath: str):
        """
        Save configuration to JSON file, preserving unknown keys.
        This ensures settings from newer versions aren't lost.
        """
        try:
            # Start with known fields
            config_dict = asdict(self)

            # Remove private fields
            config_dict = {k: v for k, v in config_dict.items() if not k.startswith('_')}

            # Add back any extra data
            if self._extra_data:
                config_dict.update(self._extra_data)

            # Ensure version is set
            config_dict['version'] = __version__

            # Write to file with pretty formatting
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2, sort_keys=True)

            logging.debug(f"Configuration saved to {filepath}")

        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")

# Default configuration
DEFAULT_CONFIG_PATH = "bot_config.json"

def get_config() -> BotConfig:
    """Get the bot configuration"""
    return BotConfig.load_from_file(DEFAULT_CONFIG_PATH)

def save_config(config: BotConfig):
    """Save the bot configuration"""
    config.save_to_file(DEFAULT_CONFIG_PATH)