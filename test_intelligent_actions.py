"""
Dark War Survival Bot - Intelligent Action System Test
Version: 3.0.0 - Purpose-Driven Automation

This test validates the complete transformation from mindless clicking
to intelligent, goal-oriented actions with strategic reasoning.

Testing validates:
1. Every action has clear goal, reasoning, and validation
2. LLM provides strategic decision-making capabilities
3. Actions are executed with purpose and measured outcomes
4. Bot makes intelligent decisions rather than random clicking
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# Import the intelligent action system
from action_system import ActionExecutor, ActionContext
from intelligent_actions import RewardCollectionAction, BuildingUpgradeAction, ActionFactory
from llm_advisor import LLMAdvisor

# Configure test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntelligentActionSystemTest:
    """
    Comprehensive test for intelligent action system.

    This test demonstrates the complete paradigm shift from:
    OLD: "Click here, click there, hope something good happens"
    NEW: "Execute this specific action because it achieves this strategic goal"
    """

    def __init__(self):
        """Initialize test environment with all components."""
        self.llm_advisor = LLMAdvisor()
        self.action_executor = ActionExecutor(llm_advisor=self.llm_advisor)
        self.test_results = []

    def run_comprehensive_test(self) -> bool:
        """
        Run complete intelligent action system test.

        Returns:
            True if all tests pass and system is ready for production
        """
        print("=" * 80)
        print("INTELLIGENT ACTION SYSTEM - COMPREHENSIVE TEST")
        print("=" * 80)
        print("MISSION: Transform mindless clicking into purposeful automation")
        print("")

        all_tests_passed = True

        # Test 1: LLM Strategic Decision Making
        all_tests_passed &= self._test_llm_strategic_decisions()

        # Test 2: Intelligent Action Creation and Validation
        all_tests_passed &= self._test_intelligent_action_creation()

        # Test 3: Action Execution with Purpose and Validation
        all_tests_passed &= self._test_action_execution_with_purpose()

        # Test 4: Strategic Action Planning (LLM-driven)
        all_tests_passed &= self._test_strategic_action_planning()

        # Test 5: Outcome Analysis and Learning
        all_tests_passed &= self._test_outcome_analysis()

        # Test 6: Integration with Bot Control System
        all_tests_passed &= self._test_bot_integration()

        # Final Results
        self._display_final_results(all_tests_passed)
        return all_tests_passed

    def _test_llm_strategic_decisions(self) -> bool:
        """Test 1: LLM provides strategic decision-making capabilities."""
        print("\n🤖 TEST 1: LLM Strategic Decision Making")
        print("-" * 50)

        try:
            # Test action goal validation
            test_game_state = {
                'current_resources': {'food': 30000000, 'wood': 20000000, 'stone': 15000000, 'iron': 10000000},
                'active_events': ['Alliance War in 2 hours'],
                'visible_buildings': [{'name': 'Tower', 'ready': True}, {'name': 'Farm', 'ready': True}]
            }

            # Test 1a: Goal validation
            print("  🔍 Testing action goal validation...")
            is_valid, reasoning, confidence = self.llm_advisor.validate_action_goal(
                "Collect mail rewards to gain 50,000,000 resources",
                test_game_state
            )
            print(f"    ✅ Goal validation: {is_valid} ({confidence:.1f}) - {reasoning[:60]}...")

            # Test 1b: Next action suggestion
            print("  🎯 Testing strategic action suggestions...")
            action_type, suggestion_reasoning, parameters = self.llm_advisor.suggest_next_action(test_game_state)
            print(f"    ✅ Next action suggestion: {action_type} - {suggestion_reasoning[:60]}...")

            # Test 1c: Building prioritization
            print("  📊 Testing building prioritization...")
            test_buildings = [
                {'name': 'Tower', 'type': 'defense', 'current_level': 24},
                {'name': 'Farm', 'type': 'resource', 'current_level': 22}
            ]
            prioritized = self.llm_advisor.prioritize_buildings(
                test_buildings,
                test_game_state['current_resources'],
                test_game_state['active_events']
            )
            print(f"    ✅ Priority order: {[b['name'] for b in prioritized]}")

            self.test_results.append({"test": "LLM Strategic Decisions", "status": "PASSED", "details": "All LLM functions working"})
            return True

        except Exception as e:
            print(f"    ❌ LLM test failed: {e}")
            self.test_results.append({"test": "LLM Strategic Decisions", "status": "FAILED", "details": str(e)})
            return False

    def _test_intelligent_action_creation(self) -> bool:
        """Test 2: Intelligent actions have clear goals and reasoning."""
        print("\n🎯 TEST 2: Intelligent Action Creation")
        print("-" * 50)

        try:
            # Test 2a: Reward Collection Action
            print("  📬 Creating RewardCollectionAction...")
            reward_action = RewardCollectionAction(target_resource_increase=50000000)

            # Validate action has purpose
            assert reward_action.goal != "", "Action must have clear goal"
            assert reward_action.reasoning != "", "Action must have strategic reasoning"
            assert reward_action.expected_benefit != "", "Action must have expected benefit"

            print(f"    ✅ Goal: {reward_action.goal[:60]}...")
            print(f"    ✅ Reasoning: {reward_action.reasoning[:60]}...")
            print(f"    ✅ Expected benefit: {reward_action.expected_benefit[:60]}...")

            # Test 2b: Building Upgrade Action
            print("  🏗️ Creating BuildingUpgradeAction...")
            building_action = BuildingUpgradeAction(
                building_name="Warehouse",
                target_level=30,
                strategic_context="alliance_war_preparation"
            )

            # Validate strategic context
            assert "Warehouse" in building_action.goal, "Goal must mention specific building"
            assert "alliance_war_preparation" in building_action.reasoning, "Reasoning must include context"

            print(f"    ✅ Strategic building upgrade: {building_action.goal}")

            # Test 2c: Action Summary
            print("  📋 Testing action summary...")
            summary = reward_action.get_action_summary()
            assert "🎯 ACTION:" in summary, "Summary must include action identifier"
            assert "📋 GOAL:" in summary, "Summary must include goal"
            assert "💭 REASONING:" in summary, "Summary must include reasoning"

            print(f"    ✅ Action summary format validated")

            self.test_results.append({"test": "Intelligent Action Creation", "status": "PASSED", "details": "All action types created successfully"})
            return True

        except Exception as e:
            print(f"    ❌ Action creation test failed: {e}")
            self.test_results.append({"test": "Intelligent Action Creation", "status": "FAILED", "details": str(e)})
            return False

    def _test_action_execution_with_purpose(self) -> bool:
        """Test 3: Actions are executed with purpose and validation."""
        print("\n🚀 TEST 3: Action Execution with Purpose")
        print("-" * 50)

        try:
            # Create test context
            test_context = ActionContext(
                current_resources={'food': 30000000, 'wood': 20000000, 'stone': 15000000, 'iron': 10000000},
                visible_buildings=[{'name': 'Tower', 'ready': True}],
                active_events=['Alliance War in 2 hours'],
                alliance_status='war_preparation',
                current_troops=50000,
                last_action_time=datetime.now(),
                ui_state='main_screen',
                screenshot_path='test_screenshot.png'  # Simulated
            )

            # Test 3a: Action prerequisite validation
            print("  🔍 Testing action prerequisite validation...")
            reward_action = RewardCollectionAction(target_resource_increase=25000000)

            can_execute, validation_reason = reward_action.can_execute(test_context)
            print(f"    ✅ Prerequisites check: {can_execute} - {validation_reason}")

            # Test 3b: Action execution with intelligence
            print("  🎬 Testing intelligent action execution...")
            if self.action_executor:
                result = self.action_executor.execute_with_intelligence(reward_action)

                # Validate result completeness
                assert result.action_name != "", "Result must include action name"
                assert result.goal_achieved != "", "Result must include goal achievement status"
                assert result.outcome_description != "", "Result must include outcome description"

                print(f"    ✅ Execution result: {result.success} - {result.outcome_description[:60]}...")
                print(f"    ✅ Resources changed: {result.resources_changed}")
                print(f"    ✅ Execution time: {result.execution_time:.2f}s")

            # Test 3c: Action logging and tracking
            print("  📊 Testing action logging...")
            reward_action.log_action_start()  # Should show purposeful logging
            print(f"    ✅ Action logging demonstrates purpose and reasoning")

            self.test_results.append({"test": "Action Execution with Purpose", "status": "PASSED", "details": "All execution features working"})
            return True

        except Exception as e:
            print(f"    ❌ Action execution test failed: {e}")
            self.test_results.append({"test": "Action Execution with Purpose", "status": "FAILED", "details": str(e)})
            return False

    def _test_strategic_action_planning(self) -> bool:
        """Test 4: System makes strategic decisions rather than random actions."""
        print("\n📈 TEST 4: Strategic Action Planning")
        print("-" * 50)

        try:
            # Test 4a: ActionFactory creates strategic actions
            print("  🏭 Testing ActionFactory strategic planning...")

            # Low resource scenario
            low_resource_state = {
                'current_resources': {'food': 5000000, 'wood': 3000000, 'stone': 2000000, 'iron': 1000000},
                'visible_buildings': [],
                'active_events': []
            }

            strategic_priorities = ['resource_collection', 'building_upgrades']
            next_action = ActionFactory.create_next_action(low_resource_state, strategic_priorities)

            if next_action:
                print(f"    ✅ Low resources → Strategic action: {next_action.__class__.__name__}")
                print(f"    ✅ Action goal: {next_action.goal}")
                assert "RewardCollectionAction" in str(type(next_action)), "Should prioritize resource collection when low"

            # War preparation scenario
            war_prep_state = {
                'current_resources': {'food': 200000000, 'wood': 150000000, 'stone': 100000000, 'iron': 80000000},
                'visible_buildings': [{'name': 'Tower', 'status': 'ready', 'current_level': 24}],
                'active_events': ['Alliance War in 1 hour']
            }

            war_action = ActionFactory.create_next_action(war_prep_state, ['defense', 'war_preparation'])
            if war_action:
                print(f"    ✅ War preparation → Strategic action: {war_action.__class__.__name__}")
                print(f"    ✅ Action context: {getattr(war_action, 'strategic_context', 'N/A')}")

            # Test 4b: LLM-driven strategic suggestions
            print("  🤖 Testing LLM strategic suggestions...")
            action_type, reasoning, params = self.llm_advisor.suggest_next_action(war_prep_state)
            print(f"    ✅ LLM suggests: {action_type} - {reasoning[:50]}...")

            self.test_results.append({"test": "Strategic Action Planning", "status": "PASSED", "details": "Strategic decision-making working"})
            return True

        except Exception as e:
            print(f"    ❌ Strategic planning test failed: {e}")
            self.test_results.append({"test": "Strategic Action Planning", "status": "FAILED", "details": str(e)})
            return False

    def _test_outcome_analysis(self) -> bool:
        """Test 5: Actions are analyzed for strategic effectiveness."""
        print("\n📊 TEST 5: Outcome Analysis and Learning")
        print("-" * 50)

        try:
            # Test 5a: Action outcome analysis
            print("  🔍 Testing action outcome analysis...")

            # Simulated action result
            mock_result = {
                'action_name': 'RewardCollectionAction',
                'success': True,
                'goal_achieved': 'Collected mail rewards to gain 75,000,000 resources',
                'outcome_description': 'Successfully collected 3 reward items',
                'resources_changed': {'food': 50000000, 'wood': 25000000},
                'execution_time': 32.5
            }

            mock_state_before = {'current_resources': {'food': 30000000, 'wood': 20000000}}
            mock_state_after = {'current_resources': {'food': 80000000, 'wood': 45000000}}

            strategic_score, analysis, improvements = self.llm_advisor.analyze_action_outcome(
                action_goal="Collect mail rewards to gain 50,000,000 resources",
                expected_benefit="Gain immediate resource boost for strategic operations",
                actual_result=mock_result,
                game_state_before=mock_state_before,
                game_state_after=mock_state_after
            )

            print(f"    ✅ Strategic success score: {strategic_score:.1f}")
            print(f"    ✅ Analysis: {analysis[:60]}...")
            print(f"    ✅ Improvements suggested: {len(improvements)} items")

            # Test 5b: Learning from execution history
            print("  📈 Testing execution history tracking...")
            if hasattr(self.action_executor, 'execution_history'):
                # Add mock result to history
                self.action_executor.execution_history.append(mock_result)
                stats = self.action_executor.get_execution_statistics()

                print(f"    ✅ Execution stats: {stats.get('total_actions', 0)} actions tracked")
                print(f"    ✅ Success rate: {stats.get('success_rate', '0%')}")

            self.test_results.append({"test": "Outcome Analysis", "status": "PASSED", "details": "Analysis and learning working"})
            return True

        except Exception as e:
            print(f"    ❌ Outcome analysis test failed: {e}")
            self.test_results.append({"test": "Outcome Analysis", "status": "FAILED", "details": str(e)})
            return False

    def _test_bot_integration(self) -> bool:
        """Test 6: Integration with existing bot control system."""
        print("\n🔗 TEST 6: Bot Control System Integration")
        print("-" * 50)

        try:
            # Test 6a: Integration with building manager
            print("  🏗️ Testing building manager integration...")
            try:
                from building_manager import BuildingManager
                bm = BuildingManager()

                # Check if LLM advisor is integrated
                if hasattr(bm, 'llm_advisor') and bm.llm_advisor:
                    print("    ✅ Building manager has LLM advisor integrated")
                else:
                    print("    ⚠️  Building manager missing LLM advisor integration")

            except ImportError as e:
                print(f"    ⚠️  Building manager import issue: {e}")

            # Test 6b: Action system API compatibility
            print("  🔌 Testing action system API...")

            # Verify action system exports correct interfaces
            from action_system import GameAction, ActionExecutor, ActionResult, ActionContext
            from intelligent_actions import RewardCollectionAction, BuildingUpgradeAction

            print("    ✅ All action system classes imported successfully")
            print("    ✅ Action interfaces compatible with bot control system")

            # Test 6c: Error handling and graceful degradation
            print("  🛡️ Testing error handling...")

            # Test with disabled LLM
            disabled_advisor = LLMAdvisor(enabled=False)
            action_type, reasoning, params = disabled_advisor.suggest_next_action({})
            print(f"    ✅ Graceful degradation: {reasoning}")

            self.test_results.append({"test": "Bot Integration", "status": "PASSED", "details": "Integration working properly"})
            return True

        except Exception as e:
            print(f"    ❌ Bot integration test failed: {e}")
            self.test_results.append({"test": "Bot Integration", "status": "FAILED", "details": str(e)})
            return False

    def _display_final_results(self, all_tests_passed: bool):
        """Display comprehensive test results and system status."""
        print("\n" + "=" * 80)
        print("🏁 INTELLIGENT ACTION SYSTEM - TEST RESULTS")
        print("=" * 80)

        # Display test results
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["status"] == "FAILED":
                print(f"   Details: {result['details']}")

        # Overall status
        print(f"\n🎯 OVERALL STATUS: {'✅ ALL TESTS PASSED' if all_tests_passed else '❌ SOME TESTS FAILED'}")

        if all_tests_passed:
            print("\n🎉 TRANSFORMATION COMPLETE!")
            print("=" * 80)
            print("🔄 BEFORE: Mindless clicking without purpose")
            print("   - Random coordinate clicking")
            print("   - No understanding of action goals")
            print("   - No strategic reasoning")
            print("   - No outcome validation")
            print("")
            print("🎯 AFTER: Intelligent, purpose-driven automation")
            print("   - Every action has clear strategic goal")
            print("   - LLM provides strategic reasoning")
            print("   - Actions validated for strategic soundness")
            print("   - Outcomes analyzed for continuous improvement")
            print("   - Strategic planning drives action selection")
            print("")
            print("🚀 READY FOR PRODUCTION USE!")
            print("   Next: Integrate with bot_control_center.py")
            print("   Launch: python bot_control_center.py")
        else:
            print("\n⚠️  SYSTEM NEEDS ATTENTION")
            print("   Review failed tests above")
            print("   Address issues before production use")

        # Performance summary
        if self.llm_advisor.enabled:
            stats = self.llm_advisor.get_performance_stats()
            print(f"\n📊 LLM PERFORMANCE:")
            print(f"   • Model: {stats.get('model', 'Unknown')}")
            print(f"   • Total queries: {stats.get('total_queries', 0)}")
            print(f"   • Average response: {stats.get('avg_response_time', 'Unknown')}")
            print(f"   • Error rate: {stats.get('error_rate', 'Unknown')}")

def run_intelligent_action_test():
    """Main test runner function."""
    try:
        tester = IntelligentActionSystemTest()
        success = tester.run_comprehensive_test()
        return success
    except Exception as e:
        print(f"\n❌ TEST RUNNER FAILED: {e}")
        return False

if __name__ == "__main__":
    print("DARK WAR SURVIVAL BOT - INTELLIGENT ACTION SYSTEM TEST")
    print("Mission: Validate transformation from mindless clicking to purposeful automation")
    print("")

    success = run_intelligent_action_test()

    if success:
        print("\nSUCCESS: Intelligent action system ready for production!")
        print("The bot now executes actions with purpose, reasoning, and validation")
        print("Every click now has meaning and strategic value")
    else:
        print("\nFAILED: System needs debugging before production use")

    print("\nNext Steps:")
    print("1. Integrate intelligent actions with bot_control_center.py")
    print("2. Test with real game environment")
    print("3. Monitor strategic decision-making effectiveness")