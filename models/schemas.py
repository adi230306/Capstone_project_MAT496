from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SearchResult(BaseModel):
    """Schema for search results."""
    url: str
    title: str
    content: str
    relevance_score: float = Field(ge=0, le=1)

class SourceContent(BaseModel):
    """Schema for parsed source content."""
    url: str
    title: str
    content: str
    chunks: List[str]
    metadata: Dict[str, Any]

class ResearchFact(BaseModel):
    """Schema for individual research facts."""
    fact: str
    perspective: str
    source_url: str
    confidence: float = Field(ge=0, le=1)
    tags: List[str] = []

class ArticleOutline(BaseModel):
    """Schema for article outline."""
    title: str
    sections: List[Dict[str, Any]]
    summary: str

class SectionDraft(BaseModel):
    """Schema for section drafts."""
    section_title: str
    content: str
    sources: List[str]
    key_points: List[str]