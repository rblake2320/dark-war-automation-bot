"""
Test script for LLM Advisor functionality
"""
from llm_advisor import LLMAdvisor
import json

def test_llm_advisor():
    print("Testing LLM Advisor...")

    # Initialize advisor
    advisor = LLMAdvisor()

    if not advisor.enabled:
        print("ERROR: LLM Advisor could not connect to Ollama")
        return

    print("SUCCESS: LLM Advisor connected to Ollama")

    # Test OCR correction
    print("\n=== OCR Correction Test ===")
    test_ocr_cases = [
        ("Warehouse Lv.29", "building detection", 0.9),  # High confidence, should not change
        ("Hunt...ut Lv2/25", "building detection", 0.3),  # Low confidence, should correct
        ("Tow3r L15", "building detection", 0.4),  # Garbled, should correct
    ]

    for original, context, confidence in test_ocr_cases:
        corrected, new_confidence = advisor.correct_ocr_text(original, context, confidence)
        print(f"'{original}' -> '{corrected}' (confidence: {confidence:.2f} -> {new_confidence:.2f})")

    # Test building prioritization
    print("\n=== Building Priority Test ===")
    test_buildings = [
        {'name': 'Tower', 'type': 'defense', 'current_level': 24, 'upgrade_cost': {'food': 45000000}},
        {'name': 'Farm', 'type': 'resource', 'current_level': 22, 'upgrade_cost': {'food': 8000000}},
        {'name': 'Barracks', 'type': 'military', 'current_level': 23, 'upgrade_cost': {'food': 15000000}}
    ]

    test_resources = {'food': 50000000, 'wood': 30000000, 'stone': 25000000}

    print("Original order:", [b['name'] for b in test_buildings])
    prioritized = advisor.prioritize_buildings(test_buildings, test_resources, ['Alliance War Starting Soon'])
    print("LLM priority order:", [b['name'] for b in prioritized])

    # Test strategic tips
    print("\n=== Strategic Tips Test ===")
    game_state = {
        'resources': test_resources,
        'buildings_ready': len(test_buildings),
        'alliance_status': 'war_preparation',
        'events': ['Alliance War in 2 hours']
    }

    tips = advisor.get_strategic_tips(game_state)
    print("Strategic recommendations:")
    print(tips)

    # Show performance stats
    print("\n=== Performance Stats ===")
    stats = advisor.get_performance_stats()
    print(json.dumps(stats, indent=2))

    print("\nLLM Advisor test completed successfully!")

if __name__ == "__main__":
    test_llm_advisor()