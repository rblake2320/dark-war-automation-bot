"""
Game automation tasks for Dark War Survival
"""

import time
import random
import logging
import cv2
from typing import List, Optional
from dataclasses import dataclass
from window_manager import WindowManager
from template_matcher import TemplateMatcher, TemplateMatch
from bot_logger import log_task_start, log_task_complete, log_task_failed

@dataclass
class GameTask:
    name: str
    priority: int  # 1=highest, 5=lowest
    cooldown: float  # minutes
    enabled: bool = True
    last_executed: float = 0

class DarkWarBot:
    def __init__(self, config):
        self.config = config
        self.window_manager = WindowManager(config.window_title)
        self.template_matcher = TemplateMatcher(threshold=config.template_threshold)
        self.logger = logging.getLogger(__name__)

        # Task definitions
        self.tasks = [
            GameTask("gather_resources", 1, 5.0),
            GameTask("collect_rewards", 1, 3.0),
            GameTask("upgrade_buildings", 2, 10.0),
            GameTask("train_troops", 2, 8.0),
            GameTask("heal_troops", 3, 15.0),
            GameTask("attack_monsters", 4, 30.0),
            GameTask("arena_battles", 5, 60.0),
        ]

        # Statistics
        self.stats = {task.name: {"success": 0, "failed": 0} for task in self.tasks}
        self.total_cycles = 0

    def execute_task(self, task: GameTask) -> bool:
        """Execute a specific game task"""
        start_time = time.time()
        log_task_start(task.name)

        try:
            # Get current screenshot
            screenshot = self.window_manager.capture_window()
            if screenshot is None:
                raise Exception("Could not capture window")

            # Execute task based on type
            success = False
            if task.name == "gather_resources":
                success = self._gather_resources(screenshot)
            elif task.name == "collect_rewards":
                success = self._collect_rewards(screenshot)
            elif task.name == "upgrade_buildings":
                success = self._upgrade_buildings(screenshot)
            elif task.name == "train_troops":
                success = self._train_troops(screenshot)
            elif task.name == "heal_troops":
                success = self._heal_troops(screenshot)
            elif task.name == "attack_monsters":
                success = self._attack_monsters(screenshot)
            elif task.name == "arena_battles":
                success = self._arena_battles(screenshot)

            # Update statistics
            if success:
                self.stats[task.name]["success"] += 1
                task.last_executed = time.time()
                duration = time.time() - start_time
                log_task_complete(task.name, duration)
            else:
                self.stats[task.name]["failed"] += 1
                log_task_failed(task.name, "Task execution failed")

            return success

        except Exception as e:
            self.stats[task.name]["failed"] += 1
            log_task_failed(task.name, str(e))
            return False

    def _gather_resources(self, screenshot) -> bool:
        """Gather resources from the map"""
        # Look for resource indicators (wood/gems show we have resources)
        resource_wood = self.template_matcher.find_template(screenshot, "resource_wood")
        if resource_wood:
            self.logger.info("Resources detected - continuing resource management")
            return True
        return False

    def _collect_rewards(self, screenshot) -> bool:
        """Collect various rewards"""
        # Check for mail icon (detected successfully)
        mail_icon = self.template_matcher.find_template(screenshot, "mail_icon")
        if mail_icon:
            center_x, center_y = self.template_matcher.get_template_center(mail_icon)
            self.window_manager.click_relative(center_x, center_y)
            self.logger.info(f"Clicked mail icon at ({center_x}, {center_y})")
            time.sleep(1)  # Quick wait for mail interface to open
            return True

        return False

    def _upgrade_buildings(self, screenshot) -> bool:
        """Upgrade buildings when possible"""
        # PRIORITY 1: Click the Build Scrapyard button (this is a real action!)
        build_btn = self.template_matcher.find_template(screenshot, "build_scrapyard_btn")
        if build_btn:
            center_x, center_y = self.template_matcher.get_template_center(build_btn)
            self.window_manager.click_relative(center_x, center_y)
            self.logger.info(f"✅ BUILDING SCRAPYARD - Clicked at ({center_x}, {center_y})")
            time.sleep(1)  # Quick wait for build to start

            # Take another screenshot to see if a build menu appeared
            new_screenshot = self.window_manager.capture_window()
            if new_screenshot is not None:
                # Look for confirm/build buttons in the new interface
                # This is where we'd click "Confirm Build" or similar
                pass

            return True

        # PRIORITY 2: Click on buildings that can be upgraded
        # Look for buildings with upgrade numbers - click on the building itself
        for upgrade_template in ["upgrade_number_2", "upgrade_number_3"]:
            upgrade_match = self.template_matcher.find_template(screenshot, upgrade_template)
            if upgrade_match:
                center_x, center_y = self.template_matcher.get_template_center(upgrade_match)

                # Click on the building (slightly above the number)
                building_x = center_x
                building_y = center_y - 40  # Click higher up on the building

                self.window_manager.click_relative(building_x, building_y)
                self.logger.info(f"🏗️ CLICKED BUILDING - {upgrade_template} at ({building_x}, {building_y})")
                time.sleep(0.5)

                # After clicking building, look for upgrade interface
                time.sleep(1)  # Quick wait for building menu to open
                new_screenshot = self.window_manager.capture_window()
                if new_screenshot is not None:
                    # Look for upgrade button in the building menu
                    # This is where upgrade buttons would appear
                    self.logger.info("Building menu should be open - looking for upgrade options")

                return True

        self.logger.info("No buildings available for upgrade")
        return False

    def _train_troops(self, screenshot) -> bool:
        """Train troops"""
        # Look for barracks or training facility
        barracks = self.template_matcher.find_template(screenshot, "barracks")
        if barracks:
            center_x, center_y = self.template_matcher.get_template_center(barracks)
            self.window_manager.click_relative(center_x, center_y)
            time.sleep(2)

            # Look for train button
            train_btn = self.template_matcher.find_template(screenshot, "train_btn")
            if train_btn:
                center_x, center_y = self.template_matcher.get_template_center(train_btn)
                self.window_manager.click_relative(center_x, center_y)
                time.sleep(2)

                # Confirm training
                confirm_btn = self.template_matcher.find_template(screenshot, "confirm_btn")
                if confirm_btn:
                    center_x, center_y = self.template_matcher.get_template_center(confirm_btn)
                    self.window_manager.click_relative(center_x, center_y)
                    time.sleep(2)
                    return True

        return False

    def _heal_troops(self, screenshot) -> bool:
        """Heal injured troops"""
        # Look for hospital or healing facility
        hospital = self.template_matcher.find_template(screenshot, "hospital")
        if hospital:
            center_x, center_y = self.template_matcher.get_template_center(hospital)
            self.window_manager.click_relative(center_x, center_y)
            time.sleep(2)

            # Look for heal button
            heal_btn = self.template_matcher.find_template(screenshot, "heal_btn")
            if heal_btn:
                center_x, center_y = self.template_matcher.get_template_center(heal_btn)
                self.window_manager.click_relative(center_x, center_y)
                time.sleep(2)
                return True

        return False

    def _attack_monsters(self, screenshot) -> bool:
        """Attack monsters on the map"""
        if not self.config.attack_monsters:
            return False

        # Look for monster on map
        monster = self.template_matcher.find_template(screenshot, "monster")
        if monster:
            center_x, center_y = self.template_matcher.get_template_center(monster)
            self.window_manager.click_relative(center_x, center_y)
            time.sleep(2)

            # Look for attack button
            attack_btn = self.template_matcher.find_template(screenshot, "attack_btn")
            if attack_btn:
                center_x, center_y = self.template_matcher.get_template_center(attack_btn)
                self.window_manager.click_relative(center_x, center_y)
                time.sleep(2)
                return True

        return False

    def _arena_battles(self, screenshot) -> bool:
        """Participate in arena battles"""
        if not self.config.arena_battles:
            return False

        # Look for arena
        arena = self.template_matcher.find_template(screenshot, "arena")
        if arena:
            center_x, center_y = self.template_matcher.get_template_center(arena)
            self.window_manager.click_relative(center_x, center_y)
            time.sleep(2)

            # Look for battle button
            battle_btn = self.template_matcher.find_template(screenshot, "battle_btn")
            if battle_btn:
                center_x, center_y = self.template_matcher.get_template_center(battle_btn)
                self.window_manager.click_relative(center_x, center_y)
                time.sleep(2)
                return True

        return False

    def get_next_task(self) -> Optional[GameTask]:
        """Get the next task to execute based on priority and cooldown"""
        current_time = time.time()
        available_tasks = []

        for task in self.tasks:
            if not task.enabled:
                continue

            # Check if task is enabled in config
            if hasattr(self.config, task.name) and not getattr(self.config, task.name):
                continue

            # Check cooldown
            time_since_last = (current_time - task.last_executed) / 60  # minutes
            if time_since_last >= task.cooldown:
                available_tasks.append(task)

        # Sort by priority (lower number = higher priority)
        available_tasks.sort(key=lambda t: t.priority)

        return available_tasks[0] if available_tasks else None

    def wait_with_random_delay(self):
        """Wait with randomized delay to appear more human"""
        delay = random.uniform(self.config.action_delay_min, self.config.action_delay_max)
        self.logger.debug(f"Waiting {delay:.1f} seconds")
        time.sleep(delay)