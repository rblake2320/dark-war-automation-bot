"""
Dark War Survival - Resource Maximization Engine
Version: 3.1.0 - Strategic Resource Optimization

This module implements intelligent strategies for maximizing all resources
through optimal building upgrades, resource management, and strategic timing.

CORE GOAL: Max out Food, Wood, Stone, and Iron through intelligent automation
"""

import json
import logging
import math
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from game_knowledge_database import GameKnowledgeDatabase
from building_level_tracker import BuildingLevelTracker

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Resource types in Dark War Survival."""
    FOOD = "food"
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"

@dataclass
class ResourceTarget:
    """Target resource amounts for maximization strategy."""
    food: int = 1000000000      # 1B food (absolute max goal)
    wood: int = 600000000       # 600M wood
    stone: int = 400000000      # 400M stone
    iron: int = 300000000       # 300M iron

    def total(self) -> int:
        """Total target resources."""
        return self.food + self.wood + self.stone + self.iron

@dataclass
class ResourceOptimizationPlan:
    """Comprehensive plan for resource maximization."""
    phase: str  # "storage_expansion", "production_boost", "optimization", "maintenance"
    priority_actions: List[Dict[str, Any]]
    estimated_time: timedelta
    expected_gains: Dict[str, int]
    bottlenecks: List[str]
    success_criteria: Dict[str, int]

class ResourceMaximizationEngine:
    """
    Intelligent engine for maximizing all resources through strategic automation.

    This replaces random clicking with systematic resource optimization strategies.
    """

    def __init__(self, llm_advisor=None):
        """Initialize resource maximization engine."""
        self.llm_advisor = llm_advisor
        self.knowledge_db = GameKnowledgeDatabase()
        self.building_tracker = BuildingLevelTracker(llm_advisor)

        # Resource targets and thresholds
        self.ultimate_targets = ResourceTarget()
        self.intermediate_targets = [
            ResourceTarget(100000000, 60000000, 40000000, 30000000),   # 100M food milestone
            ResourceTarget(250000000, 150000000, 100000000, 75000000), # 250M food milestone
            ResourceTarget(500000000, 300000000, 200000000, 150000000), # 500M food milestone
            ResourceTarget(1000000000, 600000000, 400000000, 300000000) # Ultimate goal
        ]

        # Strategy phases
        self.current_phase = "assessment"
        self.optimization_history: List[Dict] = []

        logger.info("Resource Maximization Engine initialized - ready to max all resources")

    def analyze_current_resource_state(self, current_resources: Dict[str, int],
                                     building_states: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis of current resource state and optimization potential.

        Returns detailed analysis with bottlenecks, opportunities, and strategic recommendations.
        """
        analysis = {
            'current_totals': current_resources,
            'target_progress': {},
            'storage_analysis': {},
            'production_analysis': {},
            'bottlenecks': [],
            'optimization_opportunities': [],
            'recommended_phase': 'assessment'
        }

        try:
            # Calculate progress toward targets
            total_current = sum(current_resources.values())
            total_target = self.ultimate_targets.total()

            for target in self.intermediate_targets:
                target_total = target.total()
                if total_current < target_total:
                    analysis['target_progress']['next_milestone'] = {
                        'target': target,
                        'current_progress': total_current / target_total,
                        'remaining': target_total - total_current
                    }
                    break

            # Storage capacity analysis
            storage_capacity = self._analyze_storage_capacity(building_states)
            analysis['storage_analysis'] = storage_capacity

            # Production rate analysis
            production_rates = self._analyze_production_rates(building_states)
            analysis['production_analysis'] = production_rates

            # Identify bottlenecks
            bottlenecks = self._identify_resource_bottlenecks(
                current_resources, storage_capacity, production_rates
            )
            analysis['bottlenecks'] = bottlenecks

            # Find optimization opportunities
            opportunities = self._find_optimization_opportunities(
                current_resources, building_states, bottlenecks
            )
            analysis['optimization_opportunities'] = opportunities

            # Determine recommended phase
            analysis['recommended_phase'] = self._determine_optimization_phase(
                current_resources, storage_capacity, production_rates, bottlenecks
            )

            logger.info(f"📊 Resource analysis complete - Phase: {analysis['recommended_phase']}")
            logger.info(f"💰 Total resources: {total_current:,} / {total_target:,} "
                       f"({total_current/total_target*100:.1f}%)")

            return analysis

        except Exception as e:
            logger.error(f"Resource analysis failed: {e}")
            return analysis

    def _analyze_storage_capacity(self, building_states: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current storage capacity vs needs."""
        storage_analysis = {
            'current_capacity': {'food': 0, 'wood': 0, 'stone': 0, 'iron': 0},
            'max_potential_capacity': {'food': 0, 'wood': 0, 'stone': 0, 'iron': 0},
            'storage_efficiency': 0.0,
            'upgrade_potential': []
        }

        storage_buildings = ['Warehouse', 'Granary']  # Main storage buildings

        for building_name in storage_buildings:
            if building_name in building_states:
                building_state = building_states[building_name]
                current_level = building_state.get('current_level', 0)

                # Get storage stats for current level
                current_stats = self.knowledge_db.get_building_stats(building_name, current_level)
                max_stats = self.knowledge_db.get_building_stats(building_name, 30)  # Max level

                if current_stats and max_stats:
                    # Add to current capacity (storage buildings affect all resources)
                    for resource in ['food', 'wood', 'stone', 'iron']:
                        storage_analysis['current_capacity'][resource] += current_stats.storage_capacity
                        storage_analysis['max_potential_capacity'][resource] += max_stats.storage_capacity

                    # Calculate upgrade potential
                    if current_level < 30:
                        potential_gain = max_stats.storage_capacity - current_stats.storage_capacity
                        storage_analysis['upgrade_potential'].append({
                            'building': building_name,
                            'current_level': current_level,
                            'potential_gain': potential_gain,
                            'upgrade_cost': current_stats.upgrade_cost
                        })

        # Calculate overall storage efficiency
        total_current = sum(storage_analysis['current_capacity'].values())
        total_max = sum(storage_analysis['max_potential_capacity'].values())

        if total_max > 0:
            storage_analysis['storage_efficiency'] = total_current / total_max

        return storage_analysis

    def _analyze_production_rates(self, building_states: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current resource production rates."""
        production_analysis = {
            'current_rates': {'food': 0, 'wood': 0, 'stone': 0, 'iron': 0},
            'max_potential_rates': {'food': 0, 'wood': 0, 'stone': 0, 'iron': 0},
            'production_efficiency': {},
            'upgrade_potential': []
        }

        # Map buildings to resources they produce
        production_buildings = {
            'Farm': 'food',
            'Sawmill': 'wood',
            'Quarry': 'stone',
            'Iron Mine': 'iron'
        }

        for building_name, resource_type in production_buildings.items():
            if building_name in building_states:
                building_state = building_states[building_name]
                current_level = building_state.get('current_level', 0)

                # Get production stats
                current_stats = self.knowledge_db.get_building_stats(building_name, current_level)
                max_stats = self.knowledge_db.get_building_stats(building_name, 30)

                if current_stats and max_stats:
                    production_analysis['current_rates'][resource_type] = current_stats.production_rate
                    production_analysis['max_potential_rates'][resource_type] = max_stats.production_rate

                    # Calculate efficiency for this building
                    if max_stats.production_rate > 0:
                        efficiency = current_stats.production_rate / max_stats.production_rate
                        production_analysis['production_efficiency'][building_name] = efficiency

                    # Calculate upgrade potential
                    if current_level < 30:
                        potential_gain = max_stats.production_rate - current_stats.production_rate
                        production_analysis['upgrade_potential'].append({
                            'building': building_name,
                            'resource_type': resource_type,
                            'current_level': current_level,
                            'potential_gain': potential_gain,
                            'upgrade_cost': current_stats.upgrade_cost
                        })

        return production_analysis

    def _identify_resource_bottlenecks(self, current_resources: Dict[str, int],
                                     storage_analysis: Dict[str, Any],
                                     production_analysis: Dict[str, Any]) -> List[str]:
        """Identify what's limiting resource maximization."""
        bottlenecks = []

        # Check storage bottlenecks
        for resource, amount in current_resources.items():
            capacity = storage_analysis['current_capacity'].get(resource, 0)
            if capacity > 0 and amount > capacity * 0.8:  # 80% full
                bottlenecks.append(f"{resource} storage capacity limiting accumulation")

        # Check production bottlenecks
        total_production = sum(production_analysis['current_rates'].values())
        total_storage = sum(storage_analysis['current_capacity'].values())

        if total_production * 24 > total_storage * 0.5:  # Production fills storage too fast
            bottlenecks.append("Storage capacity cannot keep up with production rates")

        # Check individual resource production efficiency
        for building, efficiency in production_analysis['production_efficiency'].items():
            if efficiency < 0.5:  # Less than 50% of max potential
                resource_type = {
                    'Farm': 'food', 'Sawmill': 'wood',
                    'Quarry': 'stone', 'Iron Mine': 'iron'
                }.get(building, 'unknown')
                bottlenecks.append(f"{building} producing only {efficiency*100:.0f}% of potential {resource_type}")

        # Check resource balance
        resource_values = list(current_resources.values())
        if max(resource_values) > min(resource_values) * 3:  # Imbalanced resources
            bottlenecks.append("Resource types are severely imbalanced")

        return bottlenecks

    def _find_optimization_opportunities(self, current_resources: Dict[str, int],
                                       building_states: Dict[str, Any],
                                       bottlenecks: List[str]) -> List[Dict[str, Any]]:
        """Find specific opportunities for resource optimization."""
        opportunities = []

        # Storage expansion opportunities
        storage_upgrades = []
        for building in ['Warehouse', 'Granary']:
            if building in building_states:
                current_level = building_states[building].get('current_level', 0)
                if current_level < 30:
                    stats = self.knowledge_db.get_building_stats(building, current_level)
                    if stats and self._can_afford_upgrade(stats.upgrade_cost, current_resources):
                        storage_upgrades.append({
                            'type': 'storage_expansion',
                            'building': building,
                            'current_level': current_level,
                            'benefit': f"Increase storage capacity by {stats.storage_capacity:,}",
                            'cost': stats.upgrade_cost,
                            'priority': 'critical' if building == 'Warehouse' else 'high'
                        })

        if storage_upgrades:
            opportunities.extend(storage_upgrades)

        # Production optimization opportunities
        production_upgrades = []
        for building in ['Farm', 'Sawmill', 'Quarry', 'Iron Mine']:
            if building in building_states:
                current_level = building_states[building].get('current_level', 0)
                if current_level < 30:
                    stats = self.knowledge_db.get_building_stats(building, current_level)
                    if stats and self._can_afford_upgrade(stats.upgrade_cost, current_resources):
                        resource_type = {
                            'Farm': 'food', 'Sawmill': 'wood',
                            'Quarry': 'stone', 'Iron Mine': 'iron'
                        }[building]

                        production_upgrades.append({
                            'type': 'production_boost',
                            'building': building,
                            'resource_type': resource_type,
                            'current_level': current_level,
                            'benefit': f"Increase {resource_type} production by {stats.production_rate:,}/hour",
                            'cost': stats.upgrade_cost,
                            'priority': 'medium'
                        })

        if production_upgrades:
            opportunities.extend(production_upgrades)

        # Resource collection opportunities
        total_resources = sum(current_resources.values())
        if total_resources < self.intermediate_targets[0].total():
            opportunities.append({
                'type': 'resource_collection',
                'target': 'mail_rewards',
                'benefit': 'Immediate resource boost for upgrades',
                'priority': 'high'
            })

        return opportunities

    def _determine_optimization_phase(self, current_resources: Dict[str, int],
                                    storage_analysis: Dict[str, Any],
                                    production_analysis: Dict[str, Any],
                                    bottlenecks: List[str]) -> str:
        """Determine what phase of optimization we should be in."""

        total_resources = sum(current_resources.values())
        storage_efficiency = storage_analysis.get('storage_efficiency', 0)

        # Phase 1: Storage Expansion (if storage is limiting factor)
        if storage_efficiency < 0.7 or any('storage' in bottleneck.lower() for bottleneck in bottlenecks):
            return "storage_expansion"

        # Phase 2: Production Boost (if production is limiting factor)
        avg_production_efficiency = sum(production_analysis['production_efficiency'].values()) / max(1, len(production_analysis['production_efficiency']))
        if avg_production_efficiency < 0.7:
            return "production_boost"

        # Phase 3: Resource Collection (if resources are too low)
        if total_resources < self.intermediate_targets[0].total():
            return "resource_collection"

        # Phase 4: Balanced Optimization (general improvement)
        if total_resources < self.ultimate_targets.total() * 0.8:
            return "balanced_optimization"

        # Phase 5: Maintenance (near max resources)
        return "maintenance"

    def _can_afford_upgrade(self, upgrade_cost: Dict[str, int], current_resources: Dict[str, int]) -> bool:
        """Check if we can afford an upgrade."""
        for resource, cost in upgrade_cost.items():
            if current_resources.get(resource, 0) < cost:
                return False
        return True

    def create_optimization_plan(self, current_resources: Dict[str, int],
                               building_states: Dict[str, Any]) -> ResourceOptimizationPlan:
        """
        Create comprehensive optimization plan for maximizing all resources.

        This provides step-by-step actions with strategic reasoning.
        """
        # Analyze current state
        analysis = self.analyze_current_resource_state(current_resources, building_states)

        # Determine phase and priorities
        phase = analysis['recommended_phase']
        opportunities = analysis['optimization_opportunities']
        bottlenecks = analysis['bottlenecks']

        # Create priority action list
        priority_actions = self._create_priority_action_list(phase, opportunities, bottlenecks)

        # Calculate estimated time and gains
        estimated_time, expected_gains = self._calculate_plan_estimates(priority_actions)

        # Define success criteria for this phase
        success_criteria = self._define_success_criteria(phase, current_resources)

        plan = ResourceOptimizationPlan(
            phase=phase,
            priority_actions=priority_actions,
            estimated_time=estimated_time,
            expected_gains=expected_gains,
            bottlenecks=bottlenecks,
            success_criteria=success_criteria
        )

        logger.info(f"📋 Optimization plan created for phase: {phase}")
        logger.info(f"🎯 Priority actions: {len(priority_actions)} steps")
        logger.info(f"⏱️ Estimated time: {estimated_time}")
        logger.info(f"💰 Expected gains: {expected_gains}")

        return plan

    def _create_priority_action_list(self, phase: str, opportunities: List[Dict],
                                   bottlenecks: List[str]) -> List[Dict[str, Any]]:
        """Create prioritized list of actions based on phase and opportunities."""
        actions = []

        if phase == "storage_expansion":
            # Prioritize storage building upgrades
            storage_opportunities = [op for op in opportunities if op.get('type') == 'storage_expansion']
            storage_opportunities.sort(key=lambda x: x.get('priority', 'low') == 'critical', reverse=True)

            for opportunity in storage_opportunities[:3]:  # Top 3 storage upgrades
                actions.append({
                    'action_type': 'upgrade_building',
                    'building': opportunity['building'],
                    'reasoning': f"Storage expansion critical for resource maximization: {opportunity['benefit']}",
                    'expected_benefit': opportunity['benefit'],
                    'cost': opportunity['cost'],
                    'priority': opportunity['priority']
                })

        elif phase == "production_boost":
            # Prioritize production building upgrades
            production_opportunities = [op for op in opportunities if op.get('type') == 'production_boost']
            # Sort by resource importance: food > wood > stone > iron
            resource_priority = {'food': 4, 'wood': 3, 'stone': 2, 'iron': 1}
            production_opportunities.sort(
                key=lambda x: resource_priority.get(x.get('resource_type', ''), 0),
                reverse=True
            )

            for opportunity in production_opportunities[:4]:  # Top 4 production upgrades
                actions.append({
                    'action_type': 'upgrade_building',
                    'building': opportunity['building'],
                    'reasoning': f"Boost {opportunity['resource_type']} production for faster accumulation: {opportunity['benefit']}",
                    'expected_benefit': opportunity['benefit'],
                    'cost': opportunity['cost'],
                    'priority': 'high'
                })

        elif phase == "resource_collection":
            # Prioritize resource collection
            actions.append({
                'action_type': 'collect_rewards',
                'target': 'mail_rewards',
                'reasoning': 'Collect immediate resources to fund strategic building upgrades',
                'expected_benefit': 'Immediate resource boost of 50-100M total resources',
                'priority': 'critical'
            })

        elif phase == "balanced_optimization":
            # Mix of storage, production, and collection
            all_opportunities = sorted(opportunities, key=lambda x: {
                'critical': 3, 'high': 2, 'medium': 1, 'low': 0
            }.get(x.get('priority', 'low'), 0), reverse=True)

            for opportunity in all_opportunities[:5]:  # Top 5 opportunities
                if opportunity.get('type') in ['storage_expansion', 'production_boost']:
                    actions.append({
                        'action_type': 'upgrade_building',
                        'building': opportunity['building'],
                        'reasoning': f"Balanced optimization: {opportunity['benefit']}",
                        'expected_benefit': opportunity['benefit'],
                        'cost': opportunity.get('cost', {}),
                        'priority': opportunity.get('priority', 'medium')
                    })
                elif opportunity.get('type') == 'resource_collection':
                    actions.append({
                        'action_type': 'collect_rewards',
                        'target': opportunity['target'],
                        'reasoning': opportunity['benefit'],
                        'expected_benefit': opportunity['benefit'],
                        'priority': opportunity.get('priority', 'medium')
                    })

        return actions

    def _calculate_plan_estimates(self, priority_actions: List[Dict]) -> Tuple[timedelta, Dict[str, int]]:
        """Calculate estimated time and resource gains for plan."""
        estimated_minutes = 0
        expected_gains = {'food': 0, 'wood': 0, 'stone': 0, 'iron': 0}

        for action in priority_actions:
            if action.get('action_type') == 'upgrade_building':
                # Building upgrades take time based on level
                estimated_minutes += 45  # ~45 minutes per building upgrade (including execution)

                # Production buildings add ongoing gains
                building = action.get('building', '')
                if building in ['Farm', 'Sawmill', 'Quarry', 'Iron Mine']:
                    resource_map = {'Farm': 'food', 'Sawmill': 'wood', 'Quarry': 'stone', 'Iron Mine': 'iron'}
                    resource = resource_map.get(building, 'food')
                    expected_gains[resource] += 50000 * 24  # Estimate 50k/hour increase * 24 hours

            elif action.get('action_type') == 'collect_rewards':
                estimated_minutes += 5  # 5 minutes for reward collection
                # Add immediate resource gains
                for resource in expected_gains.keys():
                    expected_gains[resource] += 20000000  # 20M per resource type from rewards

        return timedelta(minutes=estimated_minutes), expected_gains

    def _define_success_criteria(self, phase: str, current_resources: Dict[str, int]) -> Dict[str, int]:
        """Define success criteria for current optimization phase."""
        total_current = sum(current_resources.values())

        if phase == "storage_expansion":
            return {
                'storage_capacity_increase': 200000000,  # 200M total storage increase
                'warehouse_level': 30,  # Max warehouse level
                'granary_level': 30     # Max granary level
            }

        elif phase == "production_boost":
            return {
                'food_production_rate': 200000,    # 200k food/hour
                'wood_production_rate': 150000,    # 150k wood/hour
                'stone_production_rate': 100000,   # 100k stone/hour
                'iron_production_rate': 80000      # 80k iron/hour
            }

        elif phase == "resource_collection":
            next_milestone = total_current * 1.5  # 50% increase
            return {
                'total_resources': int(next_milestone),
                'immediate_resource_gain': 100000000  # 100M immediate gain
            }

        elif phase == "balanced_optimization":
            return {
                'total_resources': int(total_current * 1.3),  # 30% increase
                'all_key_buildings_level': 25  # All key buildings at least level 25
            }

        return {'total_resources': self.ultimate_targets.total()}

    def execute_next_optimization_step(self, optimization_plan: ResourceOptimizationPlan,
                                     current_resources: Dict[str, int]) -> Dict[str, Any]:
        """
        Execute the next step in the optimization plan.

        Returns specific action to take with detailed reasoning.
        """
        if not optimization_plan.priority_actions:
            return {
                'action_type': 'wait',
                'reasoning': 'No optimization actions available',
                'success': True
            }

        # Get next priority action
        next_action = optimization_plan.priority_actions[0]

        # Validate we can still afford it (resources may have changed)
        if next_action.get('action_type') == 'upgrade_building':
            cost = next_action.get('cost', {})
            if not self._can_afford_upgrade(cost, current_resources):
                # Skip this action for now
                return {
                    'action_type': 'collect_resources',
                    'target': 'mail_rewards',
                    'reasoning': f"Insufficient resources for {next_action['building']} upgrade. Collecting resources first.",
                    'expected_benefit': 'Accumulate resources to fund planned upgrades'
                }

        # Return the action with strategic context
        return {
            'action_type': next_action['action_type'],
            'target': next_action.get('building') or next_action.get('target'),
            'reasoning': next_action['reasoning'],
            'expected_benefit': next_action['expected_benefit'],
            'phase': optimization_plan.phase,
            'priority': next_action.get('priority', 'medium'),
            'cost': next_action.get('cost', {}),
            'plan_progress': f"Step 1 of {len(optimization_plan.priority_actions)} in {optimization_plan.phase} phase"
        }

# Integration with intelligent actions
class ResourceMaximizationAction:
    """Intelligent action that follows resource maximization strategy."""

    def __init__(self, resource_engine: ResourceMaximizationEngine):
        self.resource_engine = resource_engine

    def get_next_strategic_action(self, current_resources: Dict[str, int],
                                building_states: Dict[str, Any]) -> Dict[str, Any]:
        """Get next action based on resource maximization strategy."""

        # Create optimization plan
        plan = self.resource_engine.create_optimization_plan(current_resources, building_states)

        # Execute next step
        next_action = self.resource_engine.execute_next_optimization_step(plan, current_resources)

        # Add strategic context
        next_action['strategy'] = 'resource_maximization'
        next_action['ultimate_goal'] = 'Max all resources: 1B food, 600M wood, 400M stone, 300M iron'

        return next_action

# Example usage and testing
if __name__ == "__main__":
    print("Dark War Survival - Resource Maximization Engine")
    print("=" * 60)

    # Initialize engine
    engine = ResourceMaximizationEngine()

    # Example current state
    current_resources = {
        'food': 150000000,    # 150M food
        'wood': 80000000,     # 80M wood
        'stone': 50000000,    # 50M stone
        'iron': 30000000      # 30M iron
    }

    building_states = {
        'Warehouse': {'current_level': 25},
        'Granary': {'current_level': 22},
        'Farm': {'current_level': 20},
        'Sawmill': {'current_level': 18},
        'Quarry': {'current_level': 16},
        'Iron Mine': {'current_level': 15},
        'Tower': {'current_level': 20}
    }

    print(f"💰 Current Resources: {sum(current_resources.values()):,} total")
    print(f"🎯 Ultimate Target: {engine.ultimate_targets.total():,} total")
    print(f"📊 Progress: {sum(current_resources.values())/engine.ultimate_targets.total()*100:.1f}%")

    # Analyze current state
    analysis = engine.analyze_current_resource_state(current_resources, building_states)

    print(f"\n📈 RESOURCE STATE ANALYSIS:")
    print(f"   Phase: {analysis['recommended_phase']}")
    print(f"   Bottlenecks: {len(analysis['bottlenecks'])}")
    for bottleneck in analysis['bottlenecks'][:3]:  # Show top 3
        print(f"      - {bottleneck}")
    print(f"   Opportunities: {len(analysis['optimization_opportunities'])}")

    # Create optimization plan
    plan = engine.create_optimization_plan(current_resources, building_states)

    print(f"\n🎯 OPTIMIZATION PLAN:")
    print(f"   Phase: {plan.phase}")
    print(f"   Priority Actions: {len(plan.priority_actions)}")
    for i, action in enumerate(plan.priority_actions[:3]):  # Show top 3
        print(f"      {i+1}. {action['action_type']}: {action.get('building', action.get('target'))}")
        print(f"         Reasoning: {action['reasoning']}")
    print(f"   Estimated Time: {plan.estimated_time}")
    print(f"   Expected Gains: {plan.expected_gains}")

    # Get next action
    action_system = ResourceMaximizationAction(engine)
    next_action = action_system.get_next_strategic_action(current_resources, building_states)

    print(f"\n🚀 NEXT STRATEGIC ACTION:")
    print(f"   Action: {next_action['action_type']}")
    print(f"   Target: {next_action.get('target', 'N/A')}")
    print(f"   Reasoning: {next_action['reasoning']}")
    print(f"   Expected Benefit: {next_action['expected_benefit']}")
    print(f"   Strategy: {next_action['strategy']}")
    print(f"   Ultimate Goal: {next_action['ultimate_goal']}")

    print("\n✅ Resource Maximization Engine Ready!")
    print("🎯 Strategic resource optimization with clear path to max all resources")
    print("📊 Every action optimized for Food/Wood/Stone/Iron maximization")