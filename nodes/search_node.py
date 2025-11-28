from typing import List
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from state import ResearchState
from tools.search_tool import SearchTool
from config import Config

class SearchNode:
    """Node for performing web searches."""
    
    def __init__(self):
        self.search_tool = SearchTool(Config.SEARCH_PROVIDER)
    
    def __call__(self, state: ResearchState) -> Command[ResearchState]:
        """Execute search for the given topic."""
        topic = state["topic"]
        
        print(f" Searching for: {topic}")
        
        # Generate search query based on topic
        search_query = self._generate_search_query(topic)
        
        # Perform search
        search_results = self.search_tool.search(search_query, Config.MAX_SEARCH_RESULTS)
        
        if not search_results:
            return Command(
                update={
                    "error": "No search results found",
                    "search_results": [],
                    "search_query": search_query
                }
            )
        
        print(f"Found {len(search_results)} search results")
        
        return Command(
            update={
                "search_results": search_results,
                "search_query": search_query,
                "error": None
            }
        )
    
    def _generate_search_query(self, topic: str) -> str:
        """Generate optimized search query from topic."""
        # Focus search on the topic itself, not the article title
        return f"{topic} recent developments 2024 research"