from pydantic import BaseModel, Field
from typing import List, Optional

class CognitiveDistortion(BaseModel):
    name: str = Field(description="Name of the cognitive distortion")
    explanation: str = Field(description="Explanation of how cognitive distortion relates in this instance")
    questions: Optional[List[str]] = Field(description="Questions to challenge the cognitive distortion")

class CogDistortionAnalysis(BaseModel):
    cognitive_distortions_issue: List[CognitiveDistortion] = Field(description="Cognitive distortions identified in the issue")
    
class CogDistortionComparison(BaseModel):
    cognitive_distortions_context: List[CognitiveDistortion] = Field(description="Cognitive distortions identified in the context")
    comparison: str = Field(description="A summary of situations or events that are similar between the context and the issue that seem to trigger these cognitive distortions as well as overall themes")

class AnalysisRequest(BaseModel):
    question: str = Field(description="The user's question or issue to analyse")
    use_context: Optional[bool] = Field(default=False, description="Whether to use retrieval context (RAG). True=rags, False=simple LLM")

class AnalysisResponse(BaseModel):
    result: object
    source_content: Optional[str] = Field(description="Concatenated content from source documents used in the analysis")
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str 