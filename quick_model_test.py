"""
Quick LLM Model Comparison for Dark War Survival
Tests speed and basic strategic intelligence with shorter timeouts
"""

import requests
import time
import json
import re

def quick_test_model(model_name, timeout=30):
    """Quick test with short timeout."""

    print(f"\nTesting {model_name} (timeout: {timeout}s)...")

    # Super simple strategic test
    prompt = """Quick Dark War decision:

Storage full: 535M/535M
Food production: 200k/hour being wasted
Options: A) Upgrade Warehouse B) Spend resources C) Stop production

Answer: {"choice": "A", "speed_reason": "brief reason"}"""

    try:
        start_time = time.time()

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 100,  # Short response
                    "temperature": 0.5
                }
            },
            timeout=timeout
        )

        response_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip()

            # Extract JSON if wrapped in markdown
            json_text = response_text
            if "```" in response_text:
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)

            # Try to parse JSON
            json_valid = False
            choice_correct = False
            try:
                parsed_json = json.loads(json_text)
                json_valid = True
                choice_correct = parsed_json.get("choice") == "A"
            except:
                pass

            # Speed scoring
            if response_time < 5:
                speed_score = "EXCELLENT"
            elif response_time < 15:
                speed_score = "GOOD"
            elif response_time < 30:
                speed_score = "ACCEPTABLE"
            else:
                speed_score = "SLOW"

            return {
                "success": True,
                "response_time": response_time,
                "speed_score": speed_score,
                "json_valid": json_valid,
                "choice_correct": choice_correct,
                "response_length": len(response_text),
                "response_text": response_text[:150] + "..." if len(response_text) > 150 else response_text
            }

        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "TIMEOUT", "response_time": timeout}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """Run quick comparison test."""

    models = [
        ("gemma3:latest", 30),      # Current model - known to be slow
        ("deepseek-r1:32b", 45),    # Larger model - expect slower
        ("llama3.1:70b", 60)        # Largest model - expect very slow
    ]

    print("QUICK LLM PERFORMANCE COMPARISON")
    print("="*60)
    print("Testing strategic intelligence speed and accuracy")
    print()

    results = {}

    for model_name, timeout in models:
        result = quick_test_model(model_name, timeout)
        results[model_name] = result

        if result["success"]:
            print(f"  Response Time: {result['response_time']:.1f}s ({result['speed_score']})")
            print(f"  JSON Valid: {result['json_valid']}")
            print(f"  Correct Choice: {result['choice_correct']}")
            print(f"  Response: {result['response_text']}")
        else:
            print(f"  FAILED: {result['error']}")
            if "response_time" in result:
                print(f"  Timeout after: {result['response_time']:.1f}s")

        print()

    # Generate quick recommendation
    print("="*60)
    print("QUICK RECOMMENDATION:")
    print("="*60)

    working_models = {k: v for k, v in results.items() if v.get("success")}

    if working_models:
        # Find fastest working model
        fastest = min(working_models.items(),
                     key=lambda x: x[1]["response_time"])

        # Find most accurate
        accurate_models = {k: v for k, v in working_models.items()
                         if v.get("json_valid") and v.get("choice_correct")}

        print(f"Fastest Model: {fastest[0]} ({fastest[1]['response_time']:.1f}s)")

        if accurate_models:
            best_accurate = min(accurate_models.items(),
                              key=lambda x: x[1]["response_time"])
            print(f"Best Accurate: {best_accurate[0]} ({best_accurate[1]['response_time']:.1f}s)")

        # Real-time gaming recommendation
        gaming_suitable = {k: v for k, v in working_models.items()
                          if v["response_time"] < 10}  # Under 10s for gaming

        if gaming_suitable:
            gaming_best = min(gaming_suitable.items(),
                            key=lambda x: x[1]["response_time"])
            print(f"\nFor Real-time Gaming: {gaming_best[0]} ({gaming_best[1]['response_time']:.1f}s)")
            print("Recommendation: Use this model for bot automation")
        else:
            print(f"\nFor Real-time Gaming: NONE SUITABLE (all too slow)")
            print("Recommendation: Consider lighter models or reduce LLM usage")

    else:
        print("ERROR: No models working properly")

    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"quick_llm_results_{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump({
                "test_type": "quick_performance_comparison",
                "timestamp": timestamp,
                "results": results
            }, f, indent=2)
        print(f"\nResults saved to: {filename}")
    except Exception as e:
        print(f"Failed to save results: {e}")

if __name__ == "__main__":
    main()
    input("\nPress Enter to close...")