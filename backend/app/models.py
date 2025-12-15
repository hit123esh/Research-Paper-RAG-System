"""
Pydantic models for request/response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class UploadResponse(BaseModel):
    """Response model for PDF upload."""
    paper1_id: str
    paper2_id: Optional[str] = None
    mode: str = Field(..., description="'single' or 'comparison'")
    message: str = "PDF(s) uploaded and processed successfully"


class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    paper_id: str
    question: str = Field(..., min_length=1, max_length=1000)
    explanation_level: str = Field(default="technical", pattern="^(simple|technical)$")
    paper2_id: Optional[str] = None  # For comparison questions


class QuestionResponse(BaseModel):
    """Response model for question answers."""
    answer: str
    sources: List[str] = Field(default_factory=list)
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    is_relevant: bool = True


class ComparisonRequest(BaseModel):
    """Request model for paper comparison."""
    paper1_id: str
    paper2_id: str
    aspects: Optional[List[str]] = Field(
        default_factory=lambda: ["methodology", "dataset", "results", "limitations"]
    )


class ComparisonResponse(BaseModel):
    """Response model for paper comparison."""
    comparison: Dict[str, Any]
    paper1_name: str
    paper2_name: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None

