import os
import requests
from typing import List, Dict, Any
from models.schemas import SearchResult

class SearchTool:
    """Tool for performing web searches."""
    
    def __init__(self, provider: str = "tavily"):
        self.provider = provider
        self.api_key = os.getenv(f"{provider.upper()}_API_KEY")
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Perform web search using the configured provider."""
        if self.provider == "tavily":
            return self._search_tavily(query, max_results)
        elif self.provider == "serpapi":
            return self._search_serpapi(query, max_results)
        else:
            raise ValueError(f"Unsupported search provider: {self.provider}")
    
    def _search_tavily(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using Tavily API."""
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result in data.get("results", []):
                results.append(SearchResult(
                    url=result["url"],
                    title=result["title"],
                    content=result["content"],
                    relevance_score=result.get("score", 0.5)
                ))
            
            return results
            
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
