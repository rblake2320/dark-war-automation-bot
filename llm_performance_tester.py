"""
Dark War Survival - LLM Performance Testing Framework
Version: 1.0.0 - Comprehensive Model Comparison

This tests different LLMs for strategic intelligence performance in game automation.
Measures: Speed, Accuracy, Strategic Reasoning, Game Understanding, Decision Quality
"""

import time
import json
import requests
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Any
import traceback

class LLMPerformanceTester:
    """
    Comprehensive LLM testing framework for Dark War Survival strategic intelligence.

    Tests multiple models on game-specific tasks and provides measurable performance metrics.
    """

    def __init__(self):
        """Initialize the LLM performance testing framework."""
        self.ollama_url = "http://localhost:11434/api/generate"
        self.models_to_test = [
            "gemma3:latest",      # Current model (3.3GB, fast)
            "deepseek-r1:32b",    # Balanced model (19GB)
            "llama3.1:70b"        # Large model (42GB, slow but intelligent)
        ]

        self.test_results = {}
        self.test_scenarios = self._create_test_scenarios()

        print("LLM Performance Testing Framework Initialized")
        print(f"Models to test: {self.models_to_test}")
        print(f"Test scenarios: {len(self.test_scenarios)}")
        print()

    def _create_test_scenarios(self) -> List[Dict[str, Any]]:
        """Create comprehensive test scenarios for strategic intelligence."""

        return [
            {
                "name": "Strategic Resource Planning",
                "description": "Test ability to create strategic plans for resource maximization",
                "prompt": """You are a Dark War Survival strategic intelligence system. Given this game state:

Current Resources: Food=200M, Wood=120M, Stone=80M, Iron=50M
Buildings: Warehouse L29 (535M storage), Tower L20 (125k defense), Farm L25, Sawmill L23
Goal: Maximize all resources toward 1B food, 600M wood, 400M stone, 300M iron
Constraint: Limited by storage capacity

Provide a strategic action plan with:
1. Next immediate action with clear reasoning
2. Expected outcome and benefit
3. Priority order for next 3 actions
4. Confidence score (0.0-1.0)

Format as JSON with keys: action, reasoning, expected_benefit, next_actions, confidence""",
                "expected_elements": ["action", "reasoning", "expected_benefit", "confidence"],
                "max_tokens": 500,
                "scoring_criteria": {
                    "json_validity": 0.2,
                    "strategic_soundness": 0.3,
                    "detailed_reasoning": 0.2,
                    "confidence_appropriateness": 0.15,
                    "actionable_specificity": 0.15
                }
            },

            {
                "name": "Building Level Recognition",
                "description": "Test game knowledge and building understanding",
                "prompt": """Dark War Survival building analysis task:

OCR detected: "Warehouse 29/30"
Building stats needed for strategic decision.

Question: What are the exact stats for Warehouse L29 and L30?
Provide: Storage capacity, upgrade cost (food/wood/stone/iron), strategic value

Be specific with numbers. Format as JSON: {"l29_storage": X, "l30_storage": Y, "upgrade_cost": {...}, "strategic_value": "..."}""",
                "expected_elements": ["l29_storage", "l30_storage", "upgrade_cost", "strategic_value"],
                "max_tokens": 300,
                "scoring_criteria": {
                    "accuracy": 0.4,
                    "completeness": 0.3,
                    "json_format": 0.2,
                    "strategic_insight": 0.1
                }
            },

            {
                "name": "Action Prioritization",
                "description": "Test decision-making under constraints",
                "prompt": """Strategic priority decision for Dark War Survival:

Available actions:
1. Upgrade Warehouse L29→L30 (Cost: 255M food, 127M wood, 102M stone)
2. Upgrade Farm L25→L26 (Cost: 45M food, 22M wood, 18M stone)
3. Collect daily rewards (Cost: 0, Benefit: ~50M mixed resources)
4. Train troops for defense (Cost: 20M food, Benefit: +5k power)

Current: 200M food, 120M wood, 80M stone, 50M iron
Alliance war in 4 hours.

Choose ONE action and explain why. JSON format: {"chosen_action": X, "reasoning": "...", "confidence": 0.X}""",
                "expected_elements": ["chosen_action", "reasoning", "confidence"],
                "max_tokens": 200,
                "scoring_criteria": {
                    "logical_choice": 0.4,
                    "sound_reasoning": 0.3,
                    "context_awareness": 0.2,
                    "json_format": 0.1
                }
            },

            {
                "name": "Pattern Recognition",
                "description": "Test ability to detect problematic automation patterns",
                "prompt": """Automation analysis for Dark War Survival bot:

Recent actions log:
19:31:32 - Click Heroes button (1156, 1052)
19:31:33 - Click World features (1547, 1052)
19:31:34 - Click Events panel (1557, 250)
19:31:35 - Click VIP benefits (1146, 150)
19:31:36 - Click Heroes button (1156, 1052)
19:31:37 - Click World features (1547, 1052)
19:31:38 - Click Events panel (1557, 250)

Identify the problem and suggest solution. JSON: {"problem": "...", "solution": "...", "confidence": 0.X}""",
                "expected_elements": ["problem", "solution", "confidence"],
                "max_tokens": 250,
                "scoring_criteria": {
                    "pattern_recognition": 0.4,
                    "problem_identification": 0.3,
                    "solution_quality": 0.2,
                    "json_format": 0.1
                }
            },

            {
                "name": "Rapid Response",
                "description": "Test speed of simple strategic decisions",
                "prompt": """Quick decision needed:

Game state: Warehouse full (535M/535M), Farm producing 200k/hour food
Question: What should bot do immediately?
Options: A) Upgrade Warehouse B) Spend resources C) Stop production

Answer with single letter and 10-word reason. Format: {"answer": "A", "reason": "ten words maximum explanation here"}""",
                "expected_elements": ["answer", "reason"],
                "max_tokens": 50,
                "scoring_criteria": {
                    "speed": 0.4,
                    "correctness": 0.3,
                    "brevity": 0.2,
                    "json_format": 0.1
                }
            },

            {
                "name": "Complex Strategic Analysis",
                "description": "Test deep strategic thinking and multi-variable optimization",
                "prompt": """Advanced strategic analysis for Dark War Survival:

Game State:
- Resources: 800M food, 400M wood, 300M stone, 200M iron
- Buildings: All L28-29, approaching L30 caps
- Alliance war in 2 hours
- Current power: 2.5M, Alliance requirement: 3M
- Storage: Near capacity (1.7B/1.8B total)

Multi-objective optimization needed:
1. Reach 3M power before war
2. Maintain resource growth
3. Prepare for post-war expansion
4. Avoid storage overflow

Provide comprehensive strategy with timeline. JSON format with strategy phases.""",
                "expected_elements": ["phases", "timeline", "power_strategy", "resource_management"],
                "max_tokens": 800,
                "scoring_criteria": {
                    "strategic_depth": 0.3,
                    "multi_objective_handling": 0.25,
                    "timeline_realism": 0.2,
                    "comprehensiveness": 0.15,
                    "json_structure": 0.1
                }
            }
        ]

    def test_model(self, model_name: str) -> Dict[str, Any]:
        """Test a single model on all scenarios and return comprehensive results."""

        print(f"\n{'='*80}")
        print(f"TESTING MODEL: {model_name}")
        print(f"{'='*80}")

        model_results = {
            "model": model_name,
            "test_time": datetime.now().isoformat(),
            "scenario_results": {},
            "performance_summary": {},
            "overall_score": 0.0
        }

        total_score = 0.0
        total_response_time = 0.0
        successful_tests = 0

        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\nTest {i}/{len(self.test_scenarios)}: {scenario['name']}")
            print(f"Description: {scenario['description']}")

            try:
                # Execute test
                start_time = time.time()
                response = self._query_ollama(model_name, scenario['prompt'], scenario['max_tokens'])
                response_time = time.time() - start_time

                if response:
                    # Score the response
                    score_details = self._score_response(response, scenario)
                    scenario_score = score_details['total_score']

                    print(f"Response time: {response_time:.2f}s")
                    print(f"Scenario score: {scenario_score:.3f}/1.000")
                    print(f"Response length: {len(response)} characters")

                    # Store results
                    model_results["scenario_results"][scenario['name']] = {
                        "score": scenario_score,
                        "response_time": response_time,
                        "response_length": len(response),
                        "response_text": response[:200] + "..." if len(response) > 200 else response,
                        "score_breakdown": score_details
                    }

                    total_score += scenario_score
                    total_response_time += response_time
                    successful_tests += 1

                else:
                    print(f"ERROR: No response from model")
                    model_results["scenario_results"][scenario['name']] = {
                        "score": 0.0,
                        "error": "No response from model"
                    }

            except Exception as e:
                print(f"ERROR: {str(e)}")
                model_results["scenario_results"][scenario['name']] = {
                    "score": 0.0,
                    "error": str(e)
                }

        # Calculate performance summary
        if successful_tests > 0:
            avg_score = total_score / len(self.test_scenarios)
            avg_response_time = total_response_time / successful_tests

            model_results["performance_summary"] = {
                "average_score": avg_score,
                "average_response_time": avg_response_time,
                "successful_tests": successful_tests,
                "total_tests": len(self.test_scenarios),
                "success_rate": successful_tests / len(self.test_scenarios),
                "speed_score": self._calculate_speed_score(avg_response_time),
                "accuracy_score": avg_score
            }

            # Overall score combines accuracy and speed
            speed_weight = 0.3
            accuracy_weight = 0.7
            overall_score = (avg_score * accuracy_weight +
                           model_results["performance_summary"]["speed_score"] * speed_weight)

            model_results["overall_score"] = overall_score

            print(f"\n{'-'*60}")
            print(f"MODEL SUMMARY: {model_name}")
            print(f"Average Score: {avg_score:.3f}/1.000")
            print(f"Average Response Time: {avg_response_time:.2f}s")
            print(f"Speed Score: {model_results['performance_summary']['speed_score']:.3f}/1.000")
            print(f"Overall Score: {overall_score:.3f}/1.000")
            print(f"Success Rate: {successful_tests}/{len(self.test_scenarios)}")

        return model_results

    def _query_ollama(self, model: str, prompt: str, max_tokens: int = 500) -> str:
        """Query Ollama model with timeout and error handling."""

        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }

            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=120  # 2 minute timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"Timeout querying {model}")
            return None
        except Exception as e:
            print(f"Error querying {model}: {str(e)}")
            return None

    def _score_response(self, response: str, scenario: Dict[str, Any]) -> Dict[str, float]:
        """Score a model response based on scenario criteria."""

        scores = {}
        total_score = 0.0

        try:
            # Check for JSON validity if expected
            json_response = None
            if "json" in scenario['prompt'].lower():
                try:
                    json_response = json.loads(response)
                    scores['json_validity'] = 1.0
                except:
                    scores['json_validity'] = 0.0

            # Check for expected elements
            element_score = 0.0
            for element in scenario['expected_elements']:
                if json_response and element in json_response:
                    element_score += 1.0
                elif element.lower() in response.lower():
                    element_score += 0.5

            if scenario['expected_elements']:
                scores['element_completeness'] = element_score / len(scenario['expected_elements'])

            # Length appropriateness
            response_length = len(response)
            expected_length = scenario['max_tokens'] * 4  # Rough character estimate

            if response_length < expected_length * 0.3:
                scores['length_appropriateness'] = 0.3  # Too short
            elif response_length > expected_length * 1.5:
                scores['length_appropriateness'] = 0.7  # Too long
            else:
                scores['length_appropriateness'] = 1.0  # Good length

            # Strategic keywords (game-specific)
            strategic_keywords = ['upgrade', 'storage', 'resource', 'strategy', 'benefit', 'reasoning',
                                'warehouse', 'tower', 'farm', 'priority', 'confidence', 'action']

            keyword_count = sum(1 for keyword in strategic_keywords if keyword in response.lower())
            scores['strategic_relevance'] = min(keyword_count / 5, 1.0)  # Cap at 1.0

            # Calculate total score based on scenario criteria
            criteria = scenario['scoring_criteria']
            total_score = 0.0

            for criterion, weight in criteria.items():
                if criterion in scores:
                    total_score += scores[criterion] * weight
                else:
                    # Default scoring for unknown criteria
                    if 'json' in criterion:
                        total_score += scores.get('json_validity', 0.0) * weight
                    elif 'element' in criterion or 'complete' in criterion:
                        total_score += scores.get('element_completeness', 0.0) * weight
                    elif 'strategic' in criterion:
                        total_score += scores.get('strategic_relevance', 0.0) * weight
                    else:
                        total_score += scores.get('length_appropriateness', 0.5) * weight

        except Exception as e:
            print(f"Scoring error: {str(e)}")
            total_score = 0.1  # Minimal score for any response

        scores['total_score'] = min(total_score, 1.0)  # Cap at 1.0
        return scores

    def _calculate_speed_score(self, response_time: float) -> float:
        """Calculate speed score (higher is better, normalized 0-1)."""

        # Speed scoring curve:
        # < 2s = 1.0 (excellent)
        # 2-5s = 0.8 (good)
        # 5-15s = 0.6 (acceptable)
        # 15-30s = 0.4 (slow)
        # > 30s = 0.2 (very slow)

        if response_time < 2:
            return 1.0
        elif response_time < 5:
            return 0.8
        elif response_time < 15:
            return 0.6
        elif response_time < 30:
            return 0.4
        else:
            return 0.2

    def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite on all models and generate comparison report."""

        print("DARK WAR SURVIVAL - LLM PERFORMANCE TESTING")
        print("="*80)
        print("Strategic Intelligence Model Comparison")
        print(f"Testing {len(self.models_to_test)} models on {len(self.test_scenarios)} scenarios")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        all_results = {}

        # Test each model
        for model in self.models_to_test:
            try:
                print(f"Testing model: {model}")
                model_results = self.test_model(model)
                all_results[model] = model_results

                # Brief pause between models
                time.sleep(2)

            except Exception as e:
                print(f"Failed to test {model}: {str(e)}")
                all_results[model] = {
                    "model": model,
                    "error": str(e),
                    "overall_score": 0.0
                }

        # Generate comparison report
        comparison_report = self._generate_comparison_report(all_results)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"llm_test_results_{timestamp}.json"

        try:
            with open(results_file, 'w') as f:
                json.dump({
                    "test_metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "models_tested": self.models_to_test,
                        "total_scenarios": len(self.test_scenarios)
                    },
                    "individual_results": all_results,
                    "comparison_report": comparison_report
                }, f, indent=2)

            print(f"\nResults saved to: {results_file}")

        except Exception as e:
            print(f"Failed to save results: {str(e)}")

        return {
            "individual_results": all_results,
            "comparison_report": comparison_report,
            "results_file": results_file
        }

    def _generate_comparison_report(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive comparison report."""

        print(f"\n{'='*80}")
        print("COMPREHENSIVE MODEL COMPARISON REPORT")
        print(f"{'='*80}")

        # Sort models by overall score
        valid_results = {k: v for k, v in all_results.items()
                        if 'overall_score' in v and isinstance(v['overall_score'], (int, float))}

        if not valid_results:
            print("No valid results to compare")
            return {"error": "No valid results"}

        sorted_models = sorted(valid_results.items(),
                             key=lambda x: x[1]['overall_score'],
                             reverse=True)

        print(f"\nFINAL RANKINGS:")
        print("-" * 60)

        ranking_report = []

        for rank, (model, results) in enumerate(sorted_models, 1):
            overall_score = results['overall_score']
            summary = results.get('performance_summary', {})

            avg_score = summary.get('average_score', 0)
            avg_time = summary.get('average_response_time', 0)
            speed_score = summary.get('speed_score', 0)
            success_rate = summary.get('success_rate', 0)

            print(f"{rank}. {model}")
            print(f"   Overall Score: {overall_score:.3f}/1.000")
            print(f"   Accuracy: {avg_score:.3f} | Speed Score: {speed_score:.3f}")
            print(f"   Avg Response Time: {avg_time:.1f}s")
            print(f"   Success Rate: {success_rate:.1%}")

            # Model recommendation
            if rank == 1:
                recommendation = "RECOMMENDED - Best overall performance"
            elif avg_time < 5 and overall_score > 0.6:
                recommendation = "GOOD - Fast and accurate"
            elif overall_score > 0.7:
                recommendation = "ACCURATE - High quality but slower"
            else:
                recommendation = "LIMITED - Consider alternatives"

            print(f"   Recommendation: {recommendation}")
            print()

            ranking_report.append({
                "rank": rank,
                "model": model,
                "overall_score": overall_score,
                "accuracy_score": avg_score,
                "speed_score": speed_score,
                "response_time": avg_time,
                "success_rate": success_rate,
                "recommendation": recommendation
            })

        # Best use case recommendations
        print("SPECIALIZED RECOMMENDATIONS:")
        print("-" * 40)

        fastest_model = min(valid_results.items(),
                          key=lambda x: x[1].get('performance_summary', {}).get('average_response_time', 999))

        most_accurate = max(valid_results.items(),
                          key=lambda x: x[1].get('performance_summary', {}).get('average_score', 0))

        best_overall = sorted_models[0] if sorted_models else None

        recommendations = {
            "best_overall": best_overall[0] if best_overall else "None",
            "fastest": fastest_model[0],
            "most_accurate": most_accurate[0],
            "recommendation_summary": {
                "real_time_gaming": fastest_model[0],
                "strategic_planning": most_accurate[0],
                "balanced_automation": best_overall[0] if best_overall else fastest_model[0]
            }
        }

        print(f"For Real-time Gaming: {recommendations['fastest']}")
        print(f"For Strategic Planning: {recommendations['most_accurate']}")
        print(f"For Balanced Automation: {recommendations['best_overall']}")

        return {
            "rankings": ranking_report,
            "recommendations": recommendations,
            "test_summary": {
                "models_tested": len(valid_results),
                "total_scenarios": len(self.test_scenarios),
                "best_overall_score": sorted_models[0][1]['overall_score'] if sorted_models else 0
            }
        }

def main():
    """Run the complete LLM performance test suite."""

    tester = LLMPerformanceTester()

    try:
        results = tester.run_complete_test_suite()

        print(f"\n{'='*80}")
        print("TESTING COMPLETE")
        print(f"{'='*80}")
        print(f"Results available in: {results.get('results_file', 'memory only')}")
        print("Check the comparison report above for model recommendations.")

        return results

    except KeyboardInterrupt:
        print("\nTesting interrupted by user")
        return None
    except Exception as e:
        print(f"\nTesting failed with error: {str(e)}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = main()
    input("\nPress Enter to close...")