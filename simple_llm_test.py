"""
Quick LLM Test for Dark War Survival Strategic Intelligence
Simple test to verify LLM connection and basic performance
"""

import requests
import time
import json

def test_single_model(model_name="gemma3:latest"):
    """Quick test of a single model."""

    print(f"Testing {model_name}...")

    # Simple strategic intelligence test
    test_prompt = """Dark War Survival strategic decision:

Current: Warehouse L29 (535M storage), Food=200M, Wood=120M
Goal: Maximize resources toward 1B food target
Storage is nearly full.

What should the bot do next? Respond with JSON: {"action": "...", "reason": "...", "confidence": 0.X}"""

    try:
        start_time = time.time()

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": test_prompt,
                "stream": False,
                "options": {"num_predict": 200, "temperature": 0.7}
            },
            timeout=60
        )

        response_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip()

            print(f"\nModel: {model_name}")
            print(f"Response time: {response_time:.2f}s")
            print(f"Response length: {len(response_text)} chars")
            print(f"Response:\n{response_text}")

            # Try to parse JSON (handle markdown formatting)
            json_text = response_text
            if "```json" in response_text:
                # Extract JSON from markdown
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)

            try:
                json_response = json.loads(json_text)
                print(f"JSON parsing: SUCCESS")
                print(f"Contains action: {'action' in json_response}")
                print(f"Contains reason: {'reason' in json_response}")
                print(f"Contains confidence: {'confidence' in json_response}")

                if 'confidence' in json_response:
                    print(f"Confidence score: {json_response['confidence']}")

            except Exception as e:
                print(f"JSON parsing: FAILED - {str(e)}")
                print(f"Attempted to parse: {json_text[:100]}...")

            return {
                "success": True,
                "response_time": response_time,
                "response_text": response_text,
                "response_length": len(response_text)
            }
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Error text: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_all_models():
    """Test all available models quickly."""

    models = ["gemma3:latest", "deepseek-r1:32b", "llama3.1:70b"]

    print("QUICK LLM PERFORMANCE TEST")
    print("="*50)

    results = {}

    for model in models:
        print(f"\nTesting {model}...")
        result = test_single_model(model)
        results[model] = result

        if result.get("success"):
            print(f"[SUCCESS] {model}: {result['response_time']:.1f}s")
        else:
            print(f"[FAILED] {model}: {result.get('error', 'Unknown error')}")

    print(f"\n{'='*50}")
    print("SUMMARY:")
    print(f"{'='*50}")

    for model, result in results.items():
        if result.get("success"):
            print(f"{model}: {result['response_time']:.1f}s - [SUCCESS] Working")
        else:
            print(f"{model}: [FAILED] Failed ({result.get('error', 'Unknown')})")

if __name__ == "__main__":
    test_all_models()
    input("\nPress Enter to close...")