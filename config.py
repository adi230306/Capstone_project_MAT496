import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the AutoResearch agent."""
    LLM_MODEL = "gpt-4o"
    
    SEARCH_PROVIDER = "tavily"  
    MAX_SEARCH_RESULTS = 5
    
    RESEARCH_PERSPECTIVES = [
        "technical_fundamentals",
        "historical_context", 
        "current_applications",
        "future_implications",
        "ethical_considerations",
        "economic_impact",
        "security_concerns"
    ]
    
    MAX_ARTICLE_LENGTH = 2000
    MIN_SOURCES = 3

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")