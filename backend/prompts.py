"""
CBT Assistant Prompts

This module contains all the prompts used by the CBT Assistant for cognitive distortion analysis.
"""

import json
import os
from pathlib import Path

def load_cognitive_distortions(json_path: Path) -> dict:
    """
    Load cognitive distortions data from JSON file
    
    Returns:
        dict: Cognitive distortions data
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Cognitive distortions JSON file not found at {json_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in cognitive_distortions.json: {e}")

def get_cbt_rag_prompt(json_cognitive_distortions_path: Path) -> str:
    """
    Get the RAG CBT analysis prompt for identifying cognitive distortions
    
    Returns:
        str: The formatted prompt for cognitive distortion analysis
    """
    # Load cognitive distortions data
    distortions_data = load_cognitive_distortions(json_cognitive_distortions_path)
    
    # Convert JSON to string and escape curly braces to prevent template variable conflicts
    json_str = json.dumps(distortions_data, indent=2).replace('{', '{{').replace('}', '}}')
    
    return f"""

Issue: {{question}}

You are a Cognitive Behavioral Therapist. You are assisting me with helping to identify negative thinking patterns or cognitive destortions that usually prevent me from seeing situations as they really are. 

The following is a JSON object containing common cognitive distortions and their descriptions:

{json_str}

The context below are some of my past journal entries. I would like to get a sense of distortions that are present in the context.

Your task is to:

1. From the list of common cognitive distortions in the json object above identify those that are present in the context, providing an explanation of how the cognitve distortion relates to the context.

2. Identify situations or events that are similar between the context and the issue that seem to trigger these cognitive distortions as well as overall themes. Do not provide advice, simply state similarites between the context and the issue. 

Context: {{context}}

Your response should all be directed in second person format, directed at me.

{{format_instructions}}

""" 


def get_cbt_simple_prompt(json_cognitive_distortions_path: Path) -> str:
    """
    Get a simpler CBT analysis prompt (no external context) for identifying cognitive distortions in a single issue.
    
    Returns:
        str: The formatted prompt for simple cognitive distortion analysis
    """
    distortions_data = load_cognitive_distortions(json_cognitive_distortions_path)
    json_str = json.dumps(distortions_data, indent=2).replace('{', '{{').replace('}', '}}')
    
    return f"""
You are a Cognitive Behavioral Therapist. You are assisting me with helping to identify negative thinking patterns or cognitive distortions that usually prevent me from seeing situations as they really are.

The following is a JSON object containing common cognitive distortions and their descriptions as well as questions to help challenge the cognitive distortions:

{json_str}

Your task is to:

1. From the list of common cognitive distortions in the json object above, identify the cognitive distortions present in my issue, providing an explanation of how each cognitive distortion relates to my issue.

2. Based on each cognitive distortion identified, help me challenge the cognitive distortions by asking the questions from each category provided above. Adjust the questions to be relevant to my issue.

Issue: {{question}}

Your response should be directed in second person format, directed at me.

{{format_instructions}}

"""


