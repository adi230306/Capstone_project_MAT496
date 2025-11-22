from typing import List, Dict, Any, Optional, TypedDict
from models.schemas import SearchResult, SourceContent, ResearchFact, ArticleOutline, SectionDraft

class ResearchState(TypedDict):
    """State definition for the AutoResearch agent."""
    
    # User input
    topic: str
    
    # Search phase
    search_results: List[SearchResult]
    search_query: Optional[str]
    
    # Retrieval phase  
    source_contents: List[SourceContent]
    
    # Research phase
    research_memory: Dict[str, List[ResearchFact]]
    
    # Outline phase
    outline: Optional[ArticleOutline]
    
    # Drafting phase
    draft_sections: Dict[str, SectionDraft]
    current_section: Optional[str]
    
    # Synthesis phase
    final_article: str
    
    # Error handling
    error: Optional[str]
    retry_count: int