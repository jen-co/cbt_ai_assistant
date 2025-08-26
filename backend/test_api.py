#!/usr/bin/env python3
"""
Test script for the CBT Assistant API

This script demonstrates how to use the API endpoints.
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = "http://localhost:5000"


def test_analysis(question: str, use_context: bool):
    """Test the analysis endpoint with optional context flag"""
    print(f"\nTesting /analyse with use_context={use_context}: {question[:80]}...")

    try:
        payload = {
            "question": question,
            "use_context": use_context,
        }

        response = requests.post(
            f"{API_BASE_URL}/analyse",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("Analysis successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Analysis failed: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Main test function"""
    print("CBT Assistant API Test")
    print("=" * 50)

    # Test questions
    test_questions = [
        "I am feeling very anxious and concerned about how my daughter is adjusting to her new daycare. I am worried that her behaviour is a sign that there is something wrong with her. I am angry with myself for not at least changing the start date til after holiday as now I am worried it has unsettled her before our holiday and its going to make her difficult on our holiday and this ruin our holiday.",
        "I feel like I'm a complete failure because I didn't get the promotion at work. Everyone else seems to be moving forward in their careers while I'm stuck in the same position.",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*50}")
        print(f"Test {i} (use_context=True):")
        test_analysis(question, use_context=True)
        time.sleep(1)

        print(f"Test {i} (use_context=False):")
        test_analysis(question, use_context=False)
        time.sleep(2)  # Small delay between requests


    print(f"\n{'='*50}")
    print("Testing completed!")


if __name__ == "__main__":
    main() 