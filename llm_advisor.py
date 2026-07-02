"""
Dark War Survival Bot - LLM Strategic Advisor
Version: 1.0.0
Date: November 16, 2025

This module provides AI-powered strategic decision making and OCR error correction
for the Dark War Survival automation bot using Ollama local LLMs.
"""

import ollama
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAdvisor:
    """
    Strategic decision-making assistant for Dark War Survival bot.

    Features:
    - OCR error correction and text interpretation
    - Dynamic building prioritization based on game state
    - Strategic recommendations for resource allocation
    - Event-aware task scheduling
    - Alliance and competitive intelligence
    """

    def __init__(self, model="gemma3:latest", timeout=10, enabled=True):
        """
        Initialize the LLM Advisor.

        Args:
            model: Ollama model to use (default: gemma3:latest for speed)
            timeout: Timeout for LLM responses in seconds
            enabled: Whether LLM features are enabled (for easy toggle)
        """
        self.model = model
        self.timeout = timeout
        self.enabled = enabled
        self.conversation_history = []
        self.last_strategy_update = 0
        self.strategy_cache = {}

        # Performance tracking
        self.stats = {
            'ocr_corrections': 0,
            'strategic_queries': 0,
            'total_response_time': 0,
            'errors': 0,
            'cache_hits': 0
        }

        # Test connection on initialization
        if self.enabled:
            self._test_connection()

    def _test_connection(self) -> bool:
        """Test connection to Ollama server."""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': 'ping'}],
                stream=False
            )
            logger.info(f"LLM Advisor initialized with model: {self.model}")
            return True
        except Exception as e:
            logger.warning(f"LLM connection failed: {e}. Disabling LLM features.")
            self.enabled = False
            return False

    def _query_llm(self, prompt: str, system_context: str = "") -> Optional[str]:
        """
        Query the LLM with error handling and timeout.

        Args:
            prompt: User prompt
            system_context: Optional system context for the query

        Returns:
            LLM response or None if failed
        """
        if not self.enabled:
            return None

        try:
            start_time = time.time()

            messages = []
            if system_context:
                messages.append({'role': 'system', 'content': system_context})
            messages.append({'role': 'user', 'content': prompt})

            response = ollama.chat(
                model=self.model,
                messages=messages,
                stream=False
            )

            response_time = time.time() - start_time
            self.stats['total_response_time'] += response_time

            logger.debug(f"LLM query completed in {response_time:.2f}s")

            return response['message']['content']

        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            self.stats['errors'] += 1
            return None

    def correct_ocr_text(self, ocr_text: str, context: str = "", confidence: float = 0.0) -> Tuple[str, float]:
        """
        Correct garbled OCR text using LLM understanding.

        Args:
            ocr_text: Raw OCR output that may contain errors
            context: Additional context (e.g., "building detection", "resource count")
            confidence: Original OCR confidence (0.0-1.0)

        Returns:
            Tuple of (corrected_text, new_confidence)
        """
        if not self.enabled or confidence > 0.85:
            # Skip LLM if confidence is already high
            return ocr_text, confidence

        self.stats['ocr_corrections'] += 1

        system_context = """You are an OCR error correction assistant for the Dark War Survival mobile game.
        Your job is to interpret garbled text and return the most likely correct reading.

        Common game elements:
        - Buildings: Tower, Farm, Warehouse, Barracks, Kitchen, Hunter's Hut, Mill, etc.
        - Levels: "Lv.25", "Level 15/25", "29/30", etc.
        - Resources: Food, Wood, Stone, Iron (with numbers like "45M", "1.2B")
        - UI text: "Upgrade", "Collect", "Build", "Research", etc.

        Rules:
        1. If text is clearly readable, return it unchanged
        2. Fix common OCR errors (0→O, 1→l, 5→S, etc.)
        3. If completely garbled, return "UNKNOWN"
        4. Always preserve numbers and building names when possible"""

        prompt = f"""
        OCR extracted text: "{ocr_text}"
        Context: {context}
        Original confidence: {confidence:.2f}

        What is the most likely correct interpretation of this text?
        Respond with ONLY the corrected text, no explanation.
        """

        corrected = self._query_llm(prompt, system_context)

        if corrected and corrected.strip().upper() != "UNKNOWN":
            # LLM provided a correction
            new_confidence = min(0.9, confidence + 0.3)  # Boost confidence but not to 100%
            logger.info(f"OCR corrected: '{ocr_text}' → '{corrected.strip()}' (confidence: {new_confidence:.2f})")
            return corrected.strip(), new_confidence
        else:
            # LLM couldn't help or failed
            return ocr_text, confidence

    def prioritize_buildings(self, buildings: List[Dict], resources: Dict,
                           game_events: List[str] = None, alliance_status: str = "peaceful") -> List[Dict]:
        """
        Get dynamic building priorities based on current game state.

        Args:
            buildings: List of buildings ready to upgrade
            resources: Current resource levels
            game_events: List of active/upcoming events
            alliance_status: Current alliance situation

        Returns:
            Buildings sorted by recommended priority
        """
        if not self.enabled or not buildings:
            return buildings  # Return unchanged if LLM disabled

        self.stats['strategic_queries'] += 1

        # Check cache first (strategy valid for 10 minutes)
        cache_key = f"priority_{len(buildings)}_{alliance_status}_{hash(str(sorted(resources.items())))}"
        if cache_key in self.strategy_cache:
            cached_result, cache_time = self.strategy_cache[cache_key]
            if time.time() - cache_time < 600:  # 10 minutes
                self.stats['cache_hits'] += 1
                logger.debug("Using cached building priorities")
                return self._apply_priority_order(buildings, cached_result)

        system_context = """You are a strategic advisor for Dark War Survival mobile game.
        Analyze the current game state and recommend building upgrade priorities.

        Consider these factors:
        1. Defense buildings (Tower, Wall) before alliance wars
        2. Resource buildings (Farm, Mill) during peaceful times
        3. Military buildings (Barracks) when preparing for battles
        4. Cost-efficiency (cheaper upgrades when resources are low)
        5. Resource production vs consumption balance

        Respond with ONLY a JSON array of building priorities:
        ["building_name_1", "building_name_2", "building_name_3"]"""

        events_text = ", ".join(game_events) if game_events else "None active"

        buildings_summary = []
        for building in buildings:
            buildings_summary.append({
                'name': building.get('name', 'Unknown'),
                'type': building.get('type', 'Unknown'),
                'current_level': building.get('current_level', '?'),
                'upgrade_cost': building.get('upgrade_cost', 'Unknown')
            })

        prompt = f"""
        GAME STATE ANALYSIS:

        Buildings ready to upgrade:
        {json.dumps(buildings_summary, indent=2)}

        Current resources:
        {json.dumps(resources, indent=2)}

        Active/upcoming events: {events_text}
        Alliance status: {alliance_status}
        Current time: {datetime.now().strftime('%A %H:%M')}

        Rank these buildings by upgrade priority (most important first).
        Consider resource costs, strategic value, and timing.

        Respond with JSON array of building names in priority order:
        """

        llm_response = self._query_llm(prompt, system_context)

        if llm_response:
            try:
                # Parse LLM priority order
                priority_order = json.loads(llm_response.strip())

                # Cache the result
                self.strategy_cache[cache_key] = (priority_order, time.time())

                logger.info(f"LLM building priority: {priority_order}")
                return self._apply_priority_order(buildings, priority_order)

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse LLM building priorities: {e}")

        # Fallback to original order
        return buildings

    def _apply_priority_order(self, buildings: List[Dict], priority_order: List[str]) -> List[Dict]:
        """Apply LLM priority order to buildings list."""
        prioritized = []
        remaining = buildings.copy()

        # Add buildings in priority order
        for priority_name in priority_order:
            for building in remaining[:]:
                if building.get('name', '').lower().startswith(priority_name.lower()[:5]):
                    prioritized.append(building)
                    remaining.remove(building)
                    break

        # Add any remaining buildings
        prioritized.extend(remaining)

        return prioritized

    def get_strategic_tips(self, game_state: Dict) -> str:
        """
        Get high-level strategic recommendations for the next hour.

        Args:
            game_state: Current game state including resources, buildings, events

        Returns:
            Strategic recommendations as formatted text
        """
        if not self.enabled:
            return "LLM advisor disabled. Using default automation strategies."

        # Only generate new tips every 10 minutes
        if time.time() - self.last_strategy_update < 600:
            return self.strategy_cache.get('last_tips', 'Continue current automation strategy.')

        self.stats['strategic_queries'] += 1

        system_context = """You are a strategic advisor for Dark War Survival.
        Provide concise, actionable advice for the next hour of gameplay.
        Focus on automation priorities and resource management.

        Keep advice to 3 bullet points, each 1-2 sentences maximum."""

        prompt = f"""
        Current game state summary:
        {json.dumps(game_state, indent=2, default=str)}

        Provide 3 strategic tips for the next hour of automated gameplay.
        Consider resource levels, building states, and any events.

        Format as:
        • Tip 1 (1-2 sentences)
        • Tip 2 (1-2 sentences)
        • Tip 3 (1-2 sentences)
        """

        tips = self._query_llm(prompt, system_context)

        if tips:
            self.last_strategy_update = time.time()
            self.strategy_cache['last_tips'] = tips
            logger.info("Generated new strategic tips")
            return tips
        else:
            return "Continue current automation strategy. Monitor resource levels and building progress."

    def analyze_game_event(self, event_text: str, current_strategy: str) -> Dict[str, Any]:
        """
        Analyze a game event or notification and suggest strategy adjustments.

        Args:
            event_text: Text of the game notification/event
            current_strategy: Current automation strategy

        Returns:
            Dictionary with analysis and recommended actions
        """
        if not self.enabled:
            return {'analysis': 'LLM disabled', 'action': 'continue', 'priority': 'normal'}

        system_context = """You are analyzing Dark War Survival game events.
        Determine if the event requires strategy changes and what actions to take.

        Event types:
        - Alliance wars: Prioritize defense buildings and shields
        - Resource events: Focus on gathering and production
        - Battle events: Prepare troops and defenses
        - Building events: Accelerate construction

        Respond with JSON only:
        {
            "event_type": "war|resource|battle|building|other",
            "urgency": "low|medium|high|critical",
            "recommended_action": "brief description",
            "strategy_change": "continue|adjust|major_change"
        }"""

        prompt = f"""
        Game event detected: "{event_text}"
        Current automation strategy: {current_strategy}

        Analyze this event and recommend actions:
        """

        analysis = self._query_llm(prompt, system_context)

        if analysis:
            try:
                result = json.loads(analysis.strip())
                logger.info(f"Event analysis: {result.get('event_type')} - {result.get('urgency')} urgency")
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse event analysis")

        # Fallback
        return {
            'event_type': 'other',
            'urgency': 'low',
            'recommended_action': 'Monitor situation',
            'strategy_change': 'continue'
        }

    def should_upgrade_now(self, building: Dict, resources: Dict,
                          ongoing_tasks: List[str] = None) -> Tuple[bool, str]:
        """
        Decide whether to upgrade a specific building right now.

        Args:
            building: Building information including cost and benefits
            resources: Current resource levels
            ongoing_tasks: List of other tasks in progress

        Returns:
            Tuple of (should_upgrade, reasoning)
        """
        if not self.enabled:
            # Simple fallback logic
            upgrade_cost = building.get('upgrade_cost', {})
            for resource, cost in upgrade_cost.items():
                if resources.get(resource, 0) < cost:
                    return False, f"Insufficient {resource}"
            return True, "Resources available"

        system_context = """You are a resource allocation advisor for Dark War Survival.
        Analyze whether to spend resources on an upgrade right now vs waiting.

        Consider:
        1. Resource availability and regeneration
        2. Other pending tasks that need resources
        3. Strategic timing (save for more important upgrades)
        4. Opportunity cost

        Respond with JSON only:
        {
            "decision": true/false,
            "reasoning": "brief explanation",
            "wait_time": "immediate|1hour|4hours|12hours|wait_for_event"
        }"""

        ongoing_text = ", ".join(ongoing_tasks) if ongoing_tasks else "None"

        prompt = f"""
        UPGRADE DECISION:

        Building: {building.get('name')} Level {building.get('current_level', '?')}
        Upgrade cost: {json.dumps(building.get('upgrade_cost', {}), indent=2)}
        Upgrade benefits: {building.get('upgrade_benefit', 'Unknown')}

        Current resources: {json.dumps(resources, indent=2)}
        Ongoing tasks: {ongoing_text}

        Should I upgrade this building RIGHT NOW?
        """

        decision = self._query_llm(prompt, system_context)

        if decision:
            try:
                result = json.loads(decision.strip())
                should_upgrade = result.get('decision', True)
                reasoning = result.get('reasoning', 'LLM recommendation')

                logger.debug(f"Upgrade decision for {building.get('name')}: {should_upgrade} - {reasoning}")
                return should_upgrade, reasoning

            except json.JSONDecodeError:
                logger.warning("Failed to parse upgrade decision")

        # Fallback: upgrade if resources available
        return True, "Resources available (fallback decision)"

    def validate_action_goal(self, action_goal: str, current_game_state: Dict[str, Any]) -> Tuple[bool, str, float]:
        """
        Validate whether an action's goal makes strategic sense in current game state.

        This provides intelligent validation for the action system, ensuring every action
        has meaningful purpose rather than being mindless clicking.

        Args:
            action_goal: The goal statement from a GameAction
            current_game_state: Current resources, buildings, events, etc.

        Returns:
            Tuple of (is_valid, reasoning, confidence_score)
        """
        if not self.enabled:
            return True, "LLM validation disabled", 0.5

        self.stats['strategic_queries'] += 1

        system_context = """You are a strategic validator for Dark War Survival actions.
        Analyze whether an action's goal makes sense given the current game state.

        Consider:
        1. Resource efficiency and availability
        2. Strategic timing and prioritization
        3. Event-driven needs (alliance wars, events)
        4. Long-term vs short-term benefits
        5. Opportunity cost of this action vs alternatives

        Respond with JSON only:
        {
            "valid": true/false,
            "reasoning": "detailed explanation of why this goal is/isn't strategic",
            "confidence": 0.0-1.0,
            "suggested_alternative": "alternative action if goal is invalid"
        }"""

        resources = current_game_state.get('current_resources', {})
        events = current_game_state.get('active_events', [])
        buildings = current_game_state.get('visible_buildings', [])

        prompt = f"""
        ACTION GOAL VALIDATION:

        Proposed action goal: "{action_goal}"

        Current game state:
        - Resources: {json.dumps(resources, indent=2)}
        - Active events: {events}
        - Ready buildings: {len(buildings)} buildings ready for upgrade
        - Time: {datetime.now().strftime('%A %H:%M')}

        Is this action goal strategically sound right now?
        Should the bot execute this action or focus on something else?
        """

        llm_response = self._query_llm(prompt, system_context)

        if llm_response:
            try:
                result = json.loads(llm_response.strip())
                is_valid = result.get('valid', True)
                reasoning = result.get('reasoning', 'LLM analysis')
                confidence = result.get('confidence', 0.5)

                logger.debug(f"Action goal validation: {is_valid} ({confidence:.1f}) - {reasoning}")
                return is_valid, reasoning, confidence

            except json.JSONDecodeError:
                logger.warning("Failed to parse action validation response")

        # Fallback: assume valid
        return True, "Validation unavailable (fallback)", 0.5

    def suggest_next_action(self, current_game_state: Dict[str, Any],
                           last_action_result: Optional[Dict] = None) -> Tuple[Optional[str], str, Dict]:
        """
        Suggest the next intelligent action based on current game state.

        This transforms the bot from random clicking to strategic action planning.

        Args:
            current_game_state: Current resources, buildings, events, etc.
            last_action_result: Result from the previous action (if any)

        Returns:
            Tuple of (action_type, reasoning, action_parameters)
        """
        if not self.enabled:
            return None, "LLM suggestions disabled", {}

        self.stats['strategic_queries'] += 1

        system_context = """You are a strategic action planner for Dark War Survival.
        Analyze the current game state and recommend the next most important action.

        Available action types:
        - "collect_rewards": Collect mail/rewards for resources
        - "upgrade_building": Upgrade a specific building
        - "gather_resources": Focus on resource gathering
        - "train_troops": Build military units
        - "wait": No action needed right now

        Consider strategic priorities:
        1. Resource collection when low on resources
        2. Defensive preparations before alliance wars
        3. Resource production optimization during peaceful times
        4. Cost-efficient upgrades when appropriate
        5. Event-specific preparations

        Respond with JSON only:
        {
            "action_type": "action_name",
            "reasoning": "why this action is most important now",
            "priority": "critical|high|medium|low",
            "parameters": {
                "target_resource_increase": 50000000,
                "building_name": "Warehouse",
                "target_level": 30
            }
        }"""

        resources = current_game_state.get('current_resources', {})
        events = current_game_state.get('active_events', [])
        buildings = current_game_state.get('visible_buildings', [])

        # Include last action context if available
        last_action_context = ""
        if last_action_result:
            last_action_context = f"""
        Last action completed:
        - Action: {last_action_result.get('action_name', 'Unknown')}
        - Success: {last_action_result.get('success', False)}
        - Goal achieved: {last_action_result.get('goal_achieved', 'Unknown')}
        - Resources changed: {last_action_result.get('resources_changed', {})}
        """

        total_resources = sum(resources.values()) if resources else 0
        ready_buildings = [b for b in buildings if 'ready' in str(b).lower()]

        prompt = f"""
        STRATEGIC ACTION PLANNING:

        Current game state:
        - Total resources: {total_resources:,}
        - Resource breakdown: {json.dumps(resources, indent=2)}
        - Active events: {events if events else 'None'}
        - Ready buildings: {len(ready_buildings)} buildings ready
        - Time: {datetime.now().strftime('%A %H:%M')}
        {last_action_context}

        What should the bot do NEXT for maximum strategic benefit?
        Focus on the single most important action right now.
        """

        llm_response = self._query_llm(prompt, system_context)

        if llm_response:
            try:
                result = json.loads(llm_response.strip())
                action_type = result.get('action_type')
                reasoning = result.get('reasoning', 'LLM strategic recommendation')
                parameters = result.get('parameters', {})

                logger.info(f"LLM suggests next action: {action_type} - {reasoning}")
                return action_type, reasoning, parameters

            except json.JSONDecodeError:
                logger.warning("Failed to parse action suggestion response")

        # Fallback: suggest reward collection if low resources, otherwise wait
        if total_resources < 100000000:  # 100M threshold
            return "collect_rewards", "Low resources detected (fallback)", {"target_resource_increase": 50000000}
        else:
            return "wait", "No urgent actions needed (fallback)", {}

    def analyze_action_outcome(self, action_goal: str, expected_benefit: str,
                              actual_result: Dict, game_state_before: Dict,
                              game_state_after: Dict) -> Tuple[float, str, List[str]]:
        """
        Analyze whether an action achieved its intended strategic purpose.

        This provides intelligent outcome analysis beyond simple success/failure.

        Args:
            action_goal: Original goal of the action
            expected_benefit: What benefit was expected
            actual_result: ActionResult from execution
            game_state_before: Game state before action
            game_state_after: Game state after action

        Returns:
            Tuple of (strategic_success_score, analysis, improvement_suggestions)
        """
        if not self.enabled:
            return 0.7, "LLM analysis disabled", []

        self.stats['strategic_queries'] += 1

        system_context = """You are an action outcome analyzer for Dark War Survival.
        Evaluate whether an action achieved its strategic purpose and provide insights.

        Consider:
        1. Did the action achieve its stated goal?
        2. Were the benefits worth the cost/time?
        3. Did this action advance overall strategy?
        4. What could be improved next time?
        5. Strategic positioning after the action

        Respond with JSON only:
        {
            "strategic_success": 0.0-1.0,
            "analysis": "detailed analysis of strategic outcome",
            "improvements": ["suggestion1", "suggestion2"],
            "next_recommended": "what to focus on next"
        }"""

        resource_changes = actual_result.get('resources_changed', {})
        execution_success = actual_result.get('success', False)

        prompt = f"""
        ACTION OUTCOME ANALYSIS:

        Action goal: "{action_goal}"
        Expected benefit: "{expected_benefit}"

        Execution result:
        - Success: {execution_success}
        - Execution time: {actual_result.get('execution_time', 0):.1f}s
        - Resource changes: {json.dumps(resource_changes, indent=2)}
        - Outcome: {actual_result.get('outcome_description', 'Unknown')}

        Game state changes:
        - Resources before: {json.dumps(game_state_before.get('current_resources', {}), indent=2)}
        - Resources after: {json.dumps(game_state_after.get('current_resources', {}), indent=2)}

        Did this action fulfill its strategic purpose?
        How well did it advance our overall game strategy?
        """

        llm_response = self._query_llm(prompt, system_context)

        if llm_response:
            try:
                result = json.loads(llm_response.strip())
                strategic_score = result.get('strategic_success', 0.7)
                analysis = result.get('analysis', 'LLM strategic analysis')
                improvements = result.get('improvements', [])

                logger.debug(f"Action strategic analysis: {strategic_score:.1f} - {analysis}")
                return strategic_score, analysis, improvements

            except json.JSONDecodeError:
                logger.warning("Failed to parse outcome analysis response")

        # Fallback analysis
        fallback_score = 0.8 if execution_success else 0.3
        return fallback_score, "Strategic analysis unavailable (fallback)", []

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get LLM advisor performance statistics."""
        total_queries = self.stats['ocr_corrections'] + self.stats['strategic_queries']
        avg_response_time = (self.stats['total_response_time'] / max(1, total_queries))

        return {
            'enabled': self.enabled,
            'model': self.model,
            'total_queries': total_queries,
            'ocr_corrections': self.stats['ocr_corrections'],
            'strategic_queries': self.stats['strategic_queries'],
            'cache_hits': self.stats['cache_hits'],
            'errors': self.stats['errors'],
            'avg_response_time': f"{avg_response_time:.2f}s",
            'cache_size': len(self.strategy_cache),
            'error_rate': f"{(self.stats['errors'] / max(1, total_queries)) * 100:.1f}%"
        }

    def clear_cache(self):
        """Clear strategy cache (useful after game updates or major changes)."""
        self.strategy_cache.clear()
        logger.info("LLM strategy cache cleared")

    def set_enabled(self, enabled: bool):
        """Enable or disable LLM features at runtime."""
        self.enabled = enabled
        if enabled:
            self._test_connection()
        logger.info(f"LLM Advisor {'enabled' if enabled else 'disabled'}")


# Example usage and testing
if __name__ == "__main__":
    # Test the LLM Advisor
    advisor = LLMAdvisor()

    # Test OCR correction
    garbled_text = "Hunt...ut Lv2□/25"
    corrected, confidence = advisor.correct_ocr_text(garbled_text, "building detection", 0.3)
    print(f"OCR Test: '{garbled_text}' → '{corrected}' (confidence: {confidence:.2f})")

    # Test building prioritization
    test_buildings = [
        {'name': 'Tower', 'type': 'defense', 'current_level': 24, 'upgrade_cost': {'food': 45000000}},
        {'name': 'Farm', 'type': 'resource', 'current_level': 22, 'upgrade_cost': {'food': 8000000}},
        {'name': 'Barracks', 'type': 'military', 'current_level': 23, 'upgrade_cost': {'food': 15000000}}
    ]

    test_resources = {'food': 50000000, 'wood': 30000000, 'stone': 25000000}

    prioritized = advisor.prioritize_buildings(test_buildings, test_resources, ['Alliance War Starting Soon'])
    print(f"Priority Test: {[b['name'] for b in prioritized]}")

    # Show performance stats
    print(f"Performance Stats: {advisor.get_performance_stats()}")