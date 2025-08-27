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


def test_get_cognitive_distortions():
    """Test GET /cognitive-distortions"""
    print("\nTesting GET /cognitive-distortions ...")
    try:
        resp = requests.get(f"{API_BASE_URL}/cognitive-distortions", timeout=15)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Retrieved {len(data) if hasattr(data, '__len__') else 'data'} entries")
            return True
        else:
            print(f"Request failed: {resp.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_process_images():
    """Test POST /process-images (will fail if no images are present; that is acceptable for visibility)"""
    print("\nTesting POST /process-images ...")
    try:
        resp = requests.post(f"{API_BASE_URL}/process-images", timeout=120)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Processed text length: {data.get('text_length')}")
            return True
        else:
            print(f"Request returned non-200 (expected if no images are present): {resp.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_save_text(sample_text: str):
    """Test POST /save-text"""
    print("\nTesting POST /save-text ...")
    try:
        resp = requests.post(
            f"{API_BASE_URL}/save-text",
            json={"text": sample_text},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Saved text length: {data.get('text_length')}")
            return True
        else:
            print(f"Request failed: {resp.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_save_entry(sample_entry: dict):
    """Test POST /save-entry"""
    print("\nTesting POST /save-entry ...")
    try:
        resp = requests.post(
            f"{API_BASE_URL}/save-entry",
            json=sample_entry,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Entry saved successfully. Total entries: {data.get('entry_count')}")
            return True
        else:
            print(f"Request failed: {resp.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main test function"""
    print("CBT Assistant API Test")
    print("=" * 50)

    # Quick GET check
    test_get_cognitive_distortions()

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

    # Optional OCR/text flow samples (may fail if not set up; still useful for feedback)
    test_process_images()
    test_save_text("Sample extracted or edited text.")

    # Test save entry (matches frontend schema)
    sample_entry = {
        "situationThoughts": "Work presentation: I'm worried I'll forget what to say.",
        "cognitiveDistortions": ["Catastrophising", "Mind reading"],
        "challengeAnswers": {
            "Catastrophising": [
                "It's unlikely everything will go wrong.",
                "I have a plan and slides if I forget."
            ],
            "Mind reading": [
                "I can't know what others think.",
                "Focus on delivering clearly."
            ]
        }
    }
    test_save_entry(sample_entry)

    print(f"\n{'='*50}")
    print("Testing completed!")


if __name__ == "__main__":
    main() 