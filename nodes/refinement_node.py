from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from state import ResearchState
from config import Config

class RefinementNode:
    """Node for final refinement and quality check."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=Config.LLM_MODEL, temperature=0.1)
    
    def __call__(self, state: ResearchState) -> Command[ResearchState]:
        """Perform final refinement and quality check."""
        final_article = state["final_article"]
        research_memory = state["research_memory"]
        
        if not final_article or len(final_article.strip()) < 100:
            return Command(update={})  # No changes
        
        print("✨ Refining final article...")
        
        refined_article = self._refine_article(final_article, research_memory)
        
        # Generate citations section
        citations = self._generate_citations(research_memory)
        
        final_output = f"{refined_article}\n\n## References\n\n{citations}"
        
        print(" Article refinement complete")
        
        return Command(update={"final_article": final_output})
    
    def _refine_article(self, article: str, research_memory: dict) -> str:
        """Refine article for quality and accuracy."""
        prompt = f"""
        Review and refine the following article for:
        
        1. Factual accuracy and consistency
        2. Readability and flow
        3. Grammar and spelling
        4. Logical structure
        5. Completeness of information
        
        ARTICLE:
        {article}
        
        Provide the refined version with minimal changes, focusing on quality improvements.
        """
        
        messages = [
            SystemMessage(content="You are a quality assurance editor. Improve articles while preserving content."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"Error in refinement: {e}")
            return article
    
    def _generate_citations(self, research_memory: dict) -> str:
        """Generate citations section from research memory."""
        all_sources = set()
        
        for perspective, facts in research_memory.items():
            for fact in facts:
                all_sources.add(fact.source_url)
        
        if not all_sources:
            return "No sources cited."
        
        citations = []
        for i, source in enumerate(sorted(all_sources), 1):
            citations.append(f"{i}. {source}")
        
        return "\n".join(citations)