#!/usr/bin/env python3
"""
Test script for the CBTLLMService
"""

import sys
from pathlib import Path

# Add the parent directory to the Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from backend.config import Config
from backend.cbt_llm_service import CBTLLMService


def main():
    """Test the CBTLLMService directly"""
    try:
        config = Config()
        service = CBTLLMService(config)
        
        test_question = "I am feeling very anxious and concerned about how my daughter is adjusting to her new daycare. I am worried that her behaviour is a sign that there is something wrong with her. I am angry with myself for not at least changing the start date til after holiday as now I am worried it has unsettled her before our holiday and its going to make her difficult on our holiday and this ruin our holiday."
        
        print("Testing CBTLLMService (RAG mode)...")
        analysis_result, source_content = service.analyse_question(test_question, use_context=True)
        print("Analysis result:")
        print(analysis_result)
        print("\nSource content:")
        print(source_content)
        
        print("\nTesting CBTLLMService (simple mode)...")
        analysis_simple, source_simple = service.analyse_question(test_question, use_context=False)
        print("Simple Analysis result:")
        print(analysis_simple)
        print("\nSource content (should be empty):")
        print(source_simple)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()