"""
CBT Assistant Backend Package

A Cognitive Behavioral Therapy assistant that uses RAG (Retrieval-Augmented Generation)
to analyse user questions and identify cognitive distortions.
"""

from .app import create_app, run_app
from .cbt_llm_service import CBTLLMService
from .models import AnalysisRequest, AnalysisResponse, ErrorResponse, CogDistortionAnalysis
from .config import Config
from .prompts import get_cbt_rag_prompt

__version__ = "1.0.0"
__author__ = "Jennifer Cohen"

__all__ = [
    "create_app",
    "run_app", 
    "CBTLLMService",
    "AnalysisRequest",
    "AnalysisResponse", 
    "ErrorResponse",
    "CogDistortionAnalysis",
    "Config",
    "get_cbt_rag_prompt"
] 