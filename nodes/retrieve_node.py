from langgraph.types import Command
from state import ResearchState
from tools.web_scraper import WebScraper

class RetrieveNode:
    """Node for retrieving and parsing web content."""
    
    def __init__(self):
        self.scraper = WebScraper()
    
    def __call__(self, state: ResearchState) -> Command[ResearchState]:
        """Retrieve and parse content from search results."""
        search_results = state["search_results"]
        
        if not search_results:
            return Command(update={"source_contents": []})
        
        print(f" Retrieving content from {len(search_results)} URLs...")
        
        source_contents = []
        successful_retrievals = 0
        
        for result in search_results:
            content = self.scraper.scrape_url(result.url)
            if content:
                source_contents.append(content)
                successful_retrievals += 1
                print(f" Retrieved: {result.title}")
            else:
                print(f" Failed: {result.url}")
        
        print(f" Successfully retrieved {successful_retrievals}/{len(search_results)} sources")
        
        return Command(update={"source_contents": source_contents})