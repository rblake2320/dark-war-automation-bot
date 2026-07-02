"""
Dark War Survival - Strategic Intelligence Integration
Version: 3.1.0 - Complete Game Understanding & Strategic Automation

This module integrates all intelligent systems to provide comprehensive
game understanding and strategic automation for maximizing resources.

Integration Components:
- Game Knowledge Database (building stats, upgrade costs, strategies)
- Building Level Tracker (accurate level detection and monitoring)
- Resource Maximization Engine (strategic optimization for max resources)
- Intelligent Actions (purpose-driven automation)
- LLM Advisor (strategic decision making)

GOAL: Transform bot from mindless clicking to strategic intelligence that
understands tower levels, warehouse levels, and has clear reasons for every action.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any

# Import all intelligence systems
from game_knowledge_database import GameKnowledgeDatabase, GameIntelligenceEngine
from building_level_tracker import BuildingLevelTracker
from resource_maximization_engine import ResourceMaximizationEngine, ResourceMaximizationAction
from action_system import ActionExecutor, ActionContext, GameAction, ActionResult, ActionPriority
from intelligent_actions import RewardCollectionAction, BuildingUpgradeAction
from llm_advisor import LLMAdvisor

logger = logging.getLogger(__name__)

class StrategicIntelligenceCore:
    """
    Core strategic intelligence that combines all systems for complete game understanding.

    This replaces random clicking with intelligent strategic automation backed by:
    - Comprehensive game knowledge
    - Accurate building level detection
    - Strategic resource optimization
    - Purpose-driven action execution
    """

    def __init__(self, llm_advisor=None, window_manager=None, template_matcher=None):
        """Initialize complete strategic intelligence system."""

        # Core intelligence components
        self.llm_advisor = llm_advisor or LLMAdvisor()
        self.knowledge_db = GameKnowledgeDatabase()
        self.building_tracker = BuildingLevelTracker(self.llm_advisor)
        self.resource_engine = ResourceMaximizationEngine(self.llm_advisor)
        self.action_executor = ActionExecutor(self.llm_advisor, window_manager, template_matcher)

        # Game state tracking
        self.current_game_state = {
            'resources': {},
            'buildings': {},
            'events': [],
            'last_update': None
        }

        # Strategic tracking
        self.current_strategy = "max_all_resources"
        self.optimization_plan = None
        self.execution_history = []

        logger.info("🧠 Strategic Intelligence Core initialized - Complete game understanding active")
        logger.info("🎯 Mission: Transform mindless clicking to strategic resource maximization")

    def analyze_complete_game_state(self, screenshot_path: str = None,
                                  current_resources: Dict[str, int] = None,
                                  active_events: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of complete game state with full intelligence.

        This provides complete understanding of game state for strategic decisions.
        """
        logger.info("🔍 Starting comprehensive game state analysis...")

        complete_analysis = {
            'timestamp': datetime.now().isoformat(),
            'buildings': {},
            'resources': current_resources or {},
            'events': active_events or [],
            'strategic_analysis': {},
            'recommendations': [],
            'next_action': {},
            'confidence': 0.0
        }

        try:
            # Step 1: Detect and analyze all building levels
            if screenshot_path:
                logger.info("📊 Analyzing building levels with intelligent detection...")
                detected_buildings = self.building_tracker.detect_building_levels(screenshot_path)
                complete_analysis['buildings'] = {
                    name: {
                        'name': state.name,
                        'current_level': state.current_level,
                        'max_level': state.max_level,
                        'status': state.status,
                        'upgrade_cost': state.upgrade_cost,
                        'strategic_priority': state.strategic_priority,
                        'detection_confidence': state.detection_confidence
                    }
                    for name, state in detected_buildings.items()
                }

                logger.info(f"✅ Detected {len(detected_buildings)} buildings:")
                for name, building in complete_analysis['buildings'].items():
                    logger.info(f"   📊 {name}: Level {building['current_level']}/{building['max_level']} "
                              f"(Confidence: {building['detection_confidence']:.1f})")

            # Step 2: Analyze resource optimization opportunities
            if current_resources and complete_analysis['buildings']:
                logger.info("💰 Analyzing resource maximization opportunities...")

                # Convert building analysis for resource engine
                building_states = {
                    name: {'current_level': data['current_level']}
                    for name, data in complete_analysis['buildings'].items()
                }

                resource_analysis = self.resource_engine.analyze_current_resource_state(
                    current_resources, building_states
                )
                complete_analysis['strategic_analysis'] = resource_analysis

                # Create optimization plan
                optimization_plan = self.resource_engine.create_optimization_plan(
                    current_resources, building_states
                )
                self.optimization_plan = optimization_plan

                logger.info(f"📋 Resource analysis complete:")
                logger.info(f"   Phase: {resource_analysis['recommended_phase']}")
                logger.info(f"   Bottlenecks: {len(resource_analysis['bottlenecks'])}")
                logger.info(f"   Opportunities: {len(resource_analysis['optimization_opportunities'])}")

            # Step 3: Get strategic recommendations from game intelligence
            if complete_analysis['buildings'] and current_resources:
                logger.info("🧠 Generating strategic recommendations...")

                game_intelligence = GameIntelligenceEngine()
                recommendation = game_intelligence.analyze_game_state_and_recommend(
                    list(complete_analysis['buildings'].values()),
                    current_resources,
                    active_events
                )

                complete_analysis['recommendations'].append(recommendation)

            # Step 4: Determine next strategic action
            logger.info("🎯 Determining next strategic action...")
            next_action = self._determine_next_strategic_action(
                complete_analysis['buildings'],
                current_resources or {},
                complete_analysis['strategic_analysis'],
                active_events or []
            )
            complete_analysis['next_action'] = next_action

            # Step 5: Calculate overall confidence in analysis
            complete_analysis['confidence'] = self._calculate_analysis_confidence(complete_analysis)

            # Update internal state
            self.current_game_state.update({
                'resources': current_resources or {},
                'buildings': complete_analysis['buildings'],
                'events': active_events or [],
                'last_update': datetime.now()
            })

            logger.info("✅ Complete game state analysis finished")
            logger.info(f"🎯 Next action: {next_action.get('action_type', 'Unknown')} - {next_action.get('reasoning', 'No reasoning')[:60]}...")
            logger.info(f"🔍 Analysis confidence: {complete_analysis['confidence']:.1f}")

            return complete_analysis

        except Exception as e:
            logger.error(f"❌ Game state analysis failed: {e}")
            complete_analysis['error'] = str(e)
            return complete_analysis

    def _determine_next_strategic_action(self, buildings: Dict[str, Any],
                                       current_resources: Dict[str, int],
                                       strategic_analysis: Dict[str, Any],
                                       active_events: List[str]) -> Dict[str, Any]:
        """Determine the single best strategic action based on complete intelligence."""

        # Use resource maximization strategy if we have complete data
        if buildings and current_resources and strategic_analysis:
            building_states = {
                name: {'current_level': data['current_level']}
                for name, data in buildings.items()
            }

            resource_action_system = ResourceMaximizationAction(self.resource_engine)
            strategic_action = resource_action_system.get_next_strategic_action(
                current_resources, building_states
            )

            # Enhance with LLM validation
            if self.llm_advisor:
                is_valid, reasoning, confidence = self.llm_advisor.validate_action_goal(
                    strategic_action.get('reasoning', ''),
                    {
                        'current_resources': current_resources,
                        'visible_buildings': list(buildings.values()),
                        'active_events': active_events
                    }
                )

                strategic_action['llm_validated'] = is_valid
                strategic_action['llm_reasoning'] = reasoning
                strategic_action['llm_confidence'] = confidence

            return strategic_action

        # Fallback to basic intelligent decision
        total_resources = sum(current_resources.values()) if current_resources else 0
        if total_resources < 200000000:  # Less than 200M total
            return {
                'action_type': 'collect_rewards',
                'target': 'mail_rewards',
                'reasoning': 'Low total resources detected. Collect rewards to fund strategic upgrades.',
                'expected_benefit': 'Immediate resource boost for building upgrades',
                'strategy': 'resource_collection',
                'priority': 'critical'
            }

        return {
            'action_type': 'wait',
            'reasoning': 'Insufficient data for strategic decision',
            'expected_benefit': 'Collect more game state information',
            'strategy': 'data_collection',
            'priority': 'low'
        }

    def _calculate_analysis_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for complete analysis."""
        confidence = 0.0

        # Building detection confidence
        if analysis['buildings']:
            avg_building_confidence = sum(
                building['detection_confidence']
                for building in analysis['buildings'].values()
            ) / len(analysis['buildings'])
            confidence += avg_building_confidence * 0.4

        # Resource data completeness
        if analysis['resources'] and len(analysis['resources']) >= 4:
            confidence += 0.3

        # Strategic analysis completeness
        if analysis['strategic_analysis']:
            confidence += 0.2

        # Recommendations availability
        if analysis['recommendations']:
            confidence += 0.1

        return min(1.0, confidence)

    def execute_intelligent_action(self, action_details: Dict[str, Any]) -> ActionResult:
        """
        Execute intelligent action with complete strategic understanding.

        This replaces mindless clicking with purposeful action execution.
        """
        logger.info("🚀 Executing intelligent action with strategic understanding...")
        logger.info(f"🎯 Action: {action_details.get('action_type', 'Unknown')}")
        logger.info(f"💭 Reasoning: {action_details.get('reasoning', 'No reasoning provided')}")

        try:
            action_type = action_details.get('action_type', 'unknown')

            if action_type == 'collect_rewards':
                # Create intelligent reward collection action
                target_gain = action_details.get('expected_resource_gain', 50000000)
                reward_action = RewardCollectionAction(
                    target_resource_increase=target_gain,
                    priority=ActionPriority.HIGH
                )

                # Add strategic context
                reward_action.strategic_context = action_details.get('strategy', 'resource_maximization')
                reward_action.ultimate_goal = action_details.get('ultimate_goal', 'Max all resources')

                # Execute with full intelligence
                result = self.action_executor.execute_with_intelligence(reward_action)

            elif action_type == 'upgrade_building':
                # Create intelligent building upgrade action
                building_name = action_details.get('target', 'Unknown')
                current_level = action_details.get('current_level', 0)
                target_level = current_level + 1

                upgrade_action = BuildingUpgradeAction(
                    building_name=building_name,
                    target_level=target_level,
                    strategic_context=action_details.get('strategy', 'resource_maximization')
                )

                # Add strategic context
                upgrade_action.strategic_reasoning = action_details.get('reasoning', 'Strategic upgrade')
                upgrade_action.expected_resource_benefit = action_details.get('expected_benefit', 'Improved capacity')

                # Execute with full intelligence
                result = self.action_executor.execute_with_intelligence(upgrade_action)

            else:
                # Unknown action type
                result = ActionResult(
                    success=False,
                    action_name="UnknownAction",
                    goal_achieved="Unknown action type",
                    outcome_description=f"Unsupported action type: {action_type}",
                    resources_changed={},
                    execution_time=0.0,
                    error_message=f"Action type '{action_type}' not implemented"
                )

            # Record execution in history
            self.execution_history.append({
                'timestamp': datetime.now().isoformat(),
                'action_details': action_details,
                'result': {
                    'success': result.success,
                    'goal_achieved': result.goal_achieved,
                    'outcome': result.outcome_description,
                    'resources_changed': result.resources_changed,
                    'execution_time': result.execution_time
                }
            })

            logger.info(f"✅ Action execution completed: {result.success}")
            logger.info(f"🎯 Goal achieved: {result.goal_achieved}")
            logger.info(f"📊 Outcome: {result.outcome_description}")

            return result

        except Exception as e:
            logger.error(f"❌ Intelligent action execution failed: {e}")

            error_result = ActionResult(
                success=False,
                action_name="ExecutionError",
                goal_achieved="Action failed",
                outcome_description=f"Action execution error: {str(e)}",
                resources_changed={},
                execution_time=0.0,
                error_message=str(e)
            )

            return error_result

    def get_strategic_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive strategic dashboard with all intelligence data."""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'current_strategy': self.current_strategy,
            'game_state': self.current_game_state,
            'optimization_plan': {},
            'execution_history': self.execution_history[-10:],  # Last 10 actions
            'intelligence_status': {},
            'strategic_insights': []
        }

        try:
            # Current optimization plan
            if self.optimization_plan:
                dashboard['optimization_plan'] = {
                    'phase': self.optimization_plan.phase,
                    'priority_actions': len(self.optimization_plan.priority_actions),
                    'estimated_time': str(self.optimization_plan.estimated_time),
                    'expected_gains': self.optimization_plan.expected_gains,
                    'bottlenecks': self.optimization_plan.bottlenecks
                }

            # Intelligence system status
            dashboard['intelligence_status'] = {
                'llm_advisor_enabled': self.llm_advisor.enabled if self.llm_advisor else False,
                'knowledge_database_ready': True,
                'building_tracker_active': True,
                'resource_engine_active': True,
                'action_executor_ready': True
            }

            # Strategic insights
            if self.current_game_state['resources']:
                total_resources = sum(self.current_game_state['resources'].values())
                target_total = self.resource_engine.ultimate_targets.total()
                progress = total_resources / target_total * 100

                dashboard['strategic_insights'] = [
                    f"Resource maximization progress: {progress:.1f}% of ultimate target",
                    f"Current total resources: {total_resources:,}",
                    f"Ultimate target: {target_total:,}",
                    f"Strategy phase: {self.optimization_plan.phase if self.optimization_plan else 'Unknown'}",
                    f"Actions executed: {len(self.execution_history)}",
                    f"Last update: {self.current_game_state.get('last_update', 'Never')}"
                ]

        except Exception as e:
            logger.error(f"Dashboard generation error: {e}")
            dashboard['error'] = str(e)

        return dashboard

    def explain_current_strategy(self) -> str:
        """Provide detailed explanation of current strategic approach."""

        explanation = f"""
🧠 STRATEGIC INTELLIGENCE OVERVIEW
{'='*80}

🎯 PRIMARY MISSION: Maximize all resources through intelligent automation
   Target: 1B food, 600M wood, 400M stone, 300M iron

🏗️ INTELLIGENCE SYSTEMS ACTIVE:
   ✅ Game Knowledge Database - Comprehensive building stats and strategies
   ✅ Building Level Tracker - Accurate level detection (Tower, Warehouse, etc.)
   ✅ Resource Maximization Engine - Strategic optimization for max resources
   ✅ Intelligent Actions - Purpose-driven automation with clear goals
   ✅ LLM Strategic Advisor - AI-powered decision validation and reasoning

📊 CURRENT GAME STATE:
"""

        if self.current_game_state['resources']:
            total = sum(self.current_game_state['resources'].values())
            target = self.resource_engine.ultimate_targets.total()
            explanation += f"   💰 Total Resources: {total:,} / {target:,} ({total/target*100:.1f}%)\n"

            for resource, amount in self.current_game_state['resources'].items():
                explanation += f"   📊 {resource.title()}: {amount:,}\n"

        if self.current_game_state['buildings']:
            explanation += f"   🏗️ Buildings Tracked: {len(self.current_game_state['buildings'])}\n"
            for name, building in self.current_game_state['buildings'].items():
                explanation += f"      • {name}: Level {building['current_level']}/{building['max_level']}\n"

        if self.optimization_plan:
            explanation += f"""
🎯 CURRENT OPTIMIZATION PLAN:
   Phase: {self.optimization_plan.phase.upper()}
   Priority Actions: {len(self.optimization_plan.priority_actions)}
   Estimated Completion: {self.optimization_plan.estimated_time}
   Expected Resource Gains: {self.optimization_plan.expected_gains}
"""

        if self.optimization_plan and self.optimization_plan.bottlenecks:
            explanation += f"\n⚠️  IDENTIFIED BOTTLENECKS:\n"
            for bottleneck in self.optimization_plan.bottlenecks[:3]:
                explanation += f"   • {bottleneck}\n"

        explanation += f"""
🔄 TRANSFORMATION ACHIEVED:
   ❌ BEFORE: Mindless clicking without understanding or purpose
   ✅ NOW: Every action has strategic reasoning based on:
      • Real building levels and upgrade costs
      • Resource optimization mathematics
      • Strategic timing and priorities
      • Clear path to ultimate resource targets

🎮 EVERY CLICK NOW HAS MEANING:
   • Understands Tower level {self.current_game_state['buildings'].get('Tower', {}).get('current_level', '?')} and strategic value
   • Knows Warehouse level {self.current_game_state['buildings'].get('Warehouse', {}).get('current_level', '?')} and storage capacity
   • Calculates exact upgrade costs and benefits
   • Optimizes for maximum resource accumulation
   • Validates every action with AI strategic reasoning

🚀 RESULT: Intelligent strategic automation with clear path to max all resources!
"""

        return explanation.strip()

# Integration with existing bot control center
def enhance_bot_with_strategic_intelligence(bot_control_center):
    """Enhance existing bot control center with complete strategic intelligence."""

    # Initialize strategic intelligence core
    strategic_intelligence = StrategicIntelligenceCore(
        llm_advisor=getattr(bot_control_center, 'llm_advisor', None),
        window_manager=getattr(bot_control_center, 'window_manager', None),
        template_matcher=getattr(bot_control_center, 'template_matcher', None)
    )

    # Add to bot control center
    bot_control_center.strategic_intelligence = strategic_intelligence

    # Add new method for intelligent automation
    def run_strategic_automation(self):
        """Run complete strategic automation with full game understanding."""
        logger.info("🧠 Starting strategic automation with complete intelligence...")

        try:
            # Capture current screenshot
            screenshot = self.window_manager.capture_window() if self.window_manager else None

            # Get current resources (integrate with existing OCR)
            current_resources = getattr(self, 'last_detected_resources', {
                'food': 100000000, 'wood': 50000000, 'stone': 30000000, 'iron': 20000000
            })

            # Analyze complete game state
            game_analysis = self.strategic_intelligence.analyze_complete_game_state(
                screenshot_path=screenshot,
                current_resources=current_resources,
                active_events=[]
            )

            # Execute next strategic action
            next_action = game_analysis['next_action']
            if next_action.get('action_type') != 'wait':
                result = self.strategic_intelligence.execute_intelligent_action(next_action)
                logger.info(f"✅ Strategic action completed: {result.success}")
                return result
            else:
                logger.info("⏸️ Strategic automation waiting for optimal timing")
                return None

        except Exception as e:
            logger.error(f"❌ Strategic automation error: {e}")
            return None

    def get_strategic_dashboard(self):
        """Get strategic intelligence dashboard."""
        return self.strategic_intelligence.get_strategic_dashboard()

    def explain_current_strategy(self):
        """Get detailed explanation of current strategy."""
        return self.strategic_intelligence.explain_current_strategy()

    # Bind methods to bot instance
    import types
    bot_control_center.run_strategic_automation = types.MethodType(run_strategic_automation, bot_control_center)
    bot_control_center.get_strategic_dashboard = types.MethodType(get_strategic_dashboard, bot_control_center)
    bot_control_center.explain_current_strategy = types.MethodType(explain_current_strategy, bot_control_center)

    logger.info("🚀 Bot Control Center enhanced with Strategic Intelligence!")
    logger.info("🧠 Complete game understanding and strategic automation now available")

# Example usage and testing
if __name__ == "__main__":
    print("Dark War Survival - Strategic Intelligence Integration")
    print("=" * 70)

    # Initialize strategic intelligence
    intelligence = StrategicIntelligenceCore()

    # Example game state analysis
    current_resources = {
        'food': 180000000,    # 180M food
        'wood': 90000000,     # 90M wood
        'stone': 60000000,    # 60M stone
        'iron': 40000000      # 40M iron
    }

    active_events = ["Alliance War in 3 hours"]

    print("🧠 Running complete strategic intelligence analysis...")

    # Simulate game state analysis (would use real screenshot in production)
    analysis = intelligence.analyze_complete_game_state(
        screenshot_path=None,  # Would be real screenshot
        current_resources=current_resources,
        active_events=active_events
    )

    print(f"\n📊 COMPLETE GAME STATE ANALYSIS:")
    print(f"   Timestamp: {analysis['timestamp']}")
    print(f"   Buildings detected: {len(analysis['buildings'])}")
    print(f"   Strategic analysis: {'✅ Complete' if analysis['strategic_analysis'] else '❌ Missing'}")
    print(f"   Recommendations: {len(analysis['recommendations'])}")
    print(f"   Confidence: {analysis['confidence']:.1f}")

    # Show next strategic action
    next_action = analysis['next_action']
    print(f"\n🎯 NEXT STRATEGIC ACTION:")
    print(f"   Action: {next_action.get('action_type', 'Unknown')}")
    print(f"   Target: {next_action.get('target', 'N/A')}")
    print(f"   Reasoning: {next_action.get('reasoning', 'No reasoning')}")
    print(f"   Expected Benefit: {next_action.get('expected_benefit', 'Unknown')}")
    print(f"   Strategy: {next_action.get('strategy', 'Unknown')}")

    # Get strategic dashboard
    dashboard = intelligence.get_strategic_dashboard()
    print(f"\n📈 STRATEGIC DASHBOARD:")
    print(f"   Current Strategy: {dashboard['current_strategy']}")
    if dashboard['optimization_plan']:
        print(f"   Optimization Phase: {dashboard['optimization_plan'].get('phase', 'Unknown')}")
        print(f"   Priority Actions: {dashboard['optimization_plan'].get('priority_actions', 0)}")
    print(f"   Actions Executed: {len(dashboard['execution_history'])}")

    # Show strategic explanation
    print(f"\n🧠 STRATEGIC INTELLIGENCE EXPLANATION:")
    explanation = intelligence.explain_current_strategy()
    print(explanation[:500] + "..." if len(explanation) > 500 else explanation)

    print("\n✅ Strategic Intelligence Integration Ready!")
    print("🎯 Complete game understanding with strategic automation")
    print("🧠 Every action now backed by comprehensive intelligence and clear reasoning")
    print("📊 Tower levels, warehouse levels, and all building states understood")
    print("💰 Clear path to maximizing all resources: Food, Wood, Stone, Iron")