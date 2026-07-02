"""
Dark War Survival Bot - Intelligent Action System
Version: 3.0.0 - Goal-Oriented Automation

This module transforms mindless clicking into intelligent, purposeful actions.
Every action has a goal, reasoning, expected outcome, and validation.

Key Components:
- GameAction: Base class for all intelligent actions
- ActionResult: Standardized result reporting
- ActionExecutor: Executes actions with validation and error recovery
- GameStateTracker: Monitors game state changes for outcome validation
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of actions the bot can perform"""
    COLLECT_REWARDS = "collect_rewards"
    UPGRADE_BUILDING = "upgrade_building"
    TRAIN_TROOPS = "train_troops"
    GATHER_RESOURCES = "gather_resources"
    MANAGE_ALLIANCE = "manage_alliance"
    STRATEGIC_PLANNING = "strategic_planning"
    UI_NAVIGATION = "ui_navigation"

class ActionPriority(Enum):
    """Priority levels for action execution"""
    CRITICAL = 5    # Must do immediately (emergency situations)
    HIGH = 4        # Important strategic actions
    MEDIUM = 3      # Normal optimization actions
    LOW = 2         # Nice-to-have improvements
    BACKGROUND = 1  # Maintenance tasks

@dataclass
class ActionContext:
    """Context information available when executing actions"""
    current_resources: Dict[str, int]
    visible_buildings: List[Dict]
    active_events: List[str]
    alliance_status: str
    current_troops: int
    last_action_time: datetime
    ui_state: str  # "main_screen", "building_menu", "upgrade_dialog", etc.
    screenshot_path: Optional[str] = None

@dataclass
class ActionResult:
    """Standardized result from action execution"""
    success: bool
    action_name: str
    goal_achieved: str
    outcome_description: str
    resources_changed: Dict[str, int]
    execution_time: float
    error_message: Optional[str] = None
    validation_notes: List[str] = None
    suggested_next_action: Optional[str] = None
    confidence_score: float = 0.0

    def __post_init__(self):
        if self.validation_notes is None:
            self.validation_notes = []

class GameAction(ABC):
    """
    Base class for all intelligent actions in Dark War Survival.

    Every action must have:
    - Clear goal and purpose
    - Reasoning for why it should be executed
    - Expected outcomes and benefits
    - Validation criteria for success/failure
    """

    def __init__(self,
                 goal: str,
                 reasoning: str,
                 expected_benefit: str,
                 priority: ActionPriority = ActionPriority.MEDIUM,
                 estimated_duration: float = 5.0):
        """
        Initialize action with purpose and understanding.

        Args:
            goal: What this action is trying to achieve (e.g., "Increase food storage capacity")
            reasoning: Why this action serves the goal (e.g., "Warehouse upgrade needed for alliance war prep")
            expected_benefit: What benefit this provides (e.g., "+20% storage, enables 60M food collection")
            priority: How important this action is
            estimated_duration: How long this action should take (seconds)
        """
        self.goal = goal
        self.reasoning = reasoning
        self.expected_benefit = expected_benefit
        self.priority = priority
        self.estimated_duration = estimated_duration

        # Execution tracking
        self.created_at = datetime.now()
        self.execution_attempts = 0
        self.last_attempt_time: Optional[datetime] = None

        # Dependencies and requirements
        self.prerequisites: List[str] = []
        self.resource_requirements: Dict[str, int] = {}
        self.ui_state_required: str = "main_screen"

    @abstractmethod
    def can_execute(self, context: ActionContext) -> Tuple[bool, str]:
        """
        Check if action can be executed in current context.

        Args:
            context: Current game state and context

        Returns:
            Tuple of (can_execute, reason)

        Example:
            return True, "All requirements met"
            return False, "Insufficient food: need 45M, have 30M"
        """
        pass

    @abstractmethod
    def execute_core_logic(self, context: ActionContext) -> ActionResult:
        """
        Execute the core action logic.

        This is where the actual clicking/UI interaction happens.
        Should be focused on execution, not validation.

        Args:
            context: Current game state and context

        Returns:
            ActionResult with execution outcome
        """
        pass

    @abstractmethod
    def validate_outcome(self, context_before: ActionContext,
                        context_after: ActionContext) -> Tuple[bool, str, float]:
        """
        Validate that action achieved expected outcome.

        Args:
            context_before: Game state before action
            context_after: Game state after action

        Returns:
            Tuple of (success, validation_message, confidence_score)

        Example:
            return True, "Warehouse level increased 24→25, -45M food", 0.95
            return False, "Building level unchanged, upgrade may have failed", 0.2
        """
        pass

    def get_action_summary(self) -> str:
        """Get human-readable summary of action purpose and plan"""
        return f"""
🎯 ACTION: {self.__class__.__name__}
📋 GOAL: {self.goal}
💭 REASONING: {self.reasoning}
✨ EXPECTED BENEFIT: {self.expected_benefit}
⭐ PRIORITY: {self.priority.name}
⏱️ ESTIMATED TIME: {self.estimated_duration}s
        """.strip()

    def log_action_start(self):
        """Log action start with full context"""
        logger.info("="*60)
        logger.info("🚀 STARTING INTELLIGENT ACTION")
        logger.info("="*60)
        logger.info(self.get_action_summary())
        logger.info("="*60)

    def log_action_end(self, result: ActionResult):
        """Log action completion with results"""
        logger.info("="*60)
        logger.info("🏁 ACTION COMPLETED")
        logger.info("="*60)
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        logger.info(f"STATUS: {status}")
        logger.info(f"GOAL ACHIEVED: {result.goal_achieved}")
        logger.info(f"OUTCOME: {result.outcome_description}")
        logger.info(f"EXECUTION TIME: {result.execution_time:.2f}s")

        if result.resources_changed:
            logger.info(f"RESOURCE CHANGES: {result.resources_changed}")

        if result.validation_notes:
            logger.info("VALIDATION NOTES:")
            for note in result.validation_notes:
                logger.info(f"  • {note}")

        if result.error_message:
            logger.error(f"ERROR: {result.error_message}")

        if result.suggested_next_action:
            logger.info(f"SUGGESTED NEXT: {result.suggested_next_action}")

        logger.info("="*60)

class ActionExecutor:
    """
    Executes actions with validation, error recovery, and outcome tracking.

    This is the intelligent layer that wraps action execution with:
    - Pre-execution validation
    - State capture and comparison
    - Error recovery strategies
    - LLM-powered outcome analysis
    """

    def __init__(self, llm_advisor=None, window_manager=None, template_matcher=None):
        """
        Initialize action executor with required dependencies.

        Args:
            llm_advisor: LLM advisor for decision making and validation
            window_manager: Window management for clicking and screenshots
            template_matcher: Template matching for UI element detection
        """
        self.llm_advisor = llm_advisor
        self.window_manager = window_manager
        self.template_matcher = template_matcher

        # Execution tracking
        self.execution_history: List[ActionResult] = []
        self.current_context: Optional[ActionContext] = None

        # Error recovery settings
        self.max_retries = 3
        self.retry_delay = 2.0

    def capture_current_context(self) -> ActionContext:
        """
        Capture current game state for action context.

        Returns:
            ActionContext with current game state
        """
        try:
            # Take screenshot for analysis
            screenshot = None
            if self.window_manager:
                screenshot = self.window_manager.capture_window()

            # TODO: Integrate with existing building_manager and game state detection
            # For now, return basic context structure
            context = ActionContext(
                current_resources={
                    "food": 50000000,  # Placeholder - integrate with OCR
                    "wood": 30000000,
                    "stone": 25000000,
                    "iron": 20000000
                },
                visible_buildings=[],  # Placeholder - integrate with building detection
                active_events=[],
                alliance_status="active",
                current_troops=50000,
                last_action_time=datetime.now(),
                ui_state="main_screen",  # Placeholder - detect UI state
                screenshot_path=screenshot if isinstance(screenshot, str) else None
            )

            self.current_context = context
            return context

        except Exception as e:
            logger.error(f"Failed to capture context: {e}")
            # Return minimal context to avoid breaking execution
            return ActionContext(
                current_resources={},
                visible_buildings=[],
                active_events=[],
                alliance_status="unknown",
                current_troops=0,
                last_action_time=datetime.now(),
                ui_state="unknown"
            )

    def execute_with_intelligence(self, action: GameAction) -> ActionResult:
        """
        Execute action with full intelligence and validation.

        This is the main entry point that provides:
        1. Purpose logging and reasoning display
        2. Pre-execution validation
        3. Context capture and state tracking
        4. Action execution with error handling
        5. Outcome validation and analysis
        6. Error recovery and adaptation

        Args:
            action: The intelligent action to execute

        Returns:
            ActionResult with complete execution details
        """
        start_time = time.time()
        action.execution_attempts += 1
        action.last_attempt_time = datetime.now()

        # Log action start with full context
        action.log_action_start()

        try:
            # Step 1: Capture pre-execution context
            logger.info("📊 Capturing pre-execution game state...")
            context_before = self.capture_current_context()

            # Step 2: Validate action can be executed
            logger.info("🔍 Validating action prerequisites...")
            can_execute, validation_reason = action.can_execute(context_before)

            if not can_execute:
                logger.warning(f"⚠️ Action blocked: {validation_reason}")
                result = ActionResult(
                    success=False,
                    action_name=action.__class__.__name__,
                    goal_achieved="Action blocked",
                    outcome_description=f"Prerequisites not met: {validation_reason}",
                    resources_changed={},
                    execution_time=time.time() - start_time,
                    error_message=validation_reason
                )
                action.log_action_end(result)
                return result

            logger.info(f"✅ Prerequisites validated: {validation_reason}")

            # Step 3: Execute core action logic
            logger.info("🎬 Executing action logic...")
            execution_result = action.execute_core_logic(context_before)

            # Step 4: Capture post-execution context
            logger.info("📊 Capturing post-execution game state...")
            time.sleep(1)  # Allow game state to update
            context_after = self.capture_current_context()

            # Step 5: Validate outcome achieved expected results
            logger.info("🔍 Validating action outcome...")
            outcome_valid, validation_message, confidence = action.validate_outcome(
                context_before, context_after
            )

            # Step 6: Use LLM to analyze outcome if available
            if self.llm_advisor and outcome_valid:
                logger.info("🤖 LLM analyzing action outcome...")
                llm_analysis = self._get_llm_outcome_analysis(
                    action, context_before, context_after, execution_result
                )
                if llm_analysis:
                    execution_result.validation_notes.append(f"LLM Analysis: {llm_analysis}")

            # Step 7: Update result with validation
            execution_result.confidence_score = confidence
            execution_result.validation_notes.append(validation_message)
            execution_result.execution_time = time.time() - start_time

            # Step 8: Log completion and track result
            action.log_action_end(execution_result)
            self.execution_history.append(execution_result)

            return execution_result

        except Exception as e:
            logger.error(f"❌ Action execution failed: {e}")
            error_result = ActionResult(
                success=False,
                action_name=action.__class__.__name__,
                goal_achieved="Execution error",
                outcome_description=f"Action failed with error: {str(e)}",
                resources_changed={},
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
            action.log_action_end(error_result)
            self.execution_history.append(error_result)
            return error_result

    def _get_llm_outcome_analysis(self, action: GameAction,
                                 context_before: ActionContext,
                                 context_after: ActionContext,
                                 result: ActionResult) -> Optional[str]:
        """Get LLM analysis of action outcome"""
        try:
            if not self.llm_advisor:
                return None

            analysis_prompt = f"""
            Analyze the outcome of this Dark War Survival action:

            ACTION GOAL: {action.goal}
            ACTION REASONING: {action.reasoning}
            EXPECTED BENEFIT: {action.expected_benefit}

            RESOURCES BEFORE: {context_before.current_resources}
            RESOURCES AFTER: {context_after.current_resources}

            EXECUTION RESULT: {result.outcome_description}
            SUCCESS: {result.success}

            Did this action achieve its intended purpose? Was the reasoning sound?
            Provide a brief analysis (2-3 sentences).
            """

            analysis = self.llm_advisor._query_llm(analysis_prompt)
            return analysis

        except Exception as e:
            logger.warning(f"LLM outcome analysis failed: {e}")
            return None

    def execute_with_retry(self, action: GameAction) -> ActionResult:
        """
        Execute action with automatic retry on failure.

        Args:
            action: Action to execute

        Returns:
            ActionResult from final attempt
        """
        last_result = None

        for attempt in range(self.max_retries):
            logger.info(f"🔄 Execution attempt {attempt + 1}/{self.max_retries}")

            result = self.execute_with_intelligence(action)

            if result.success:
                logger.info(f"✅ Action succeeded on attempt {attempt + 1}")
                return result

            last_result = result

            if attempt < self.max_retries - 1:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed, retrying in {self.retry_delay}s...")
                logger.warning(f"   Failure reason: {result.error_message}")
                time.sleep(self.retry_delay)

        logger.error(f"❌ Action failed after {self.max_retries} attempts")
        return last_result

    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get statistics about action execution performance"""
        if not self.execution_history:
            return {"total_actions": 0}

        total_actions = len(self.execution_history)
        successful_actions = sum(1 for result in self.execution_history if result.success)

        avg_execution_time = sum(result.execution_time for result in self.execution_history) / total_actions

        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "success_rate": f"{(successful_actions / total_actions) * 100:.1f}%",
            "average_execution_time": f"{avg_execution_time:.2f}s",
            "recent_actions": [
                {
                    "name": result.action_name,
                    "success": result.success,
                    "goal": result.goal_achieved
                }
                for result in self.execution_history[-5:]  # Last 5 actions
            ]
        }

# Example usage and testing
if __name__ == "__main__":
    # This file provides the foundation for intelligent actions
    # Example actions will be implemented in separate files

    print("Action System Foundation Created!")
    print("Key Components:")
    print("✅ GameAction base class - Every action has goal, reasoning, validation")
    print("✅ ActionResult - Standardized outcome reporting")
    print("✅ ActionExecutor - Intelligent execution with validation")
    print("✅ ActionContext - Game state tracking for decisions")
    print("")
    print("Next: Implement specific actions (RewardCollectionAction, BuildingUpgradeAction, etc.)")