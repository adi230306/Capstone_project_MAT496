from typing import List, Dict, Any
from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from state import ResearchState
from models.schemas import ArticleOutline
from config import Config
import json

class OutlineNode:
    """Node for generating article outline."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=Config.LLM_MODEL, temperature=0.2)
    
    def __call__(self, state: ResearchState) -> Command[ResearchState]:
        """Generate article outline based on research."""
        research_memory = state["research_memory"]
        topic = state["topic"]
        
        if not research_memory:
            return Command(update={"outline": None})
        
        print("📝 Generating article outline...")
        
        # Prepare research summary
        research_summary = self._prepare_research_summary(research_memory)
        
        outline = self._generate_outline(topic, research_summary)
        
        print(f"✅ Outline generated with {len(outline.sections)} sections")
        
        return Command(update={"outline": outline})
    
    def _prepare_research_summary(self, research_memory: dict) -> str:
        """Prepare summary of research findings."""
        summary = []
        for perspective, facts in research_memory.items():
            if facts:
                summary.append(f"## {perspective.replace('_', ' ').title()}")
                for fact in facts[:3]:  # Top 3 facts per perspective
                    summary.append(f"- {fact.fact} (Source: {fact.source_url})")
                summary.append("")
        
        return "\n".join(summary)
    
    def _generate_outline(self, topic: str, research_summary: str) -> ArticleOutline:
        """Generate structured article outline."""
        prompt = f"""
        Create a comprehensive Wikipedia-style outline for an article about: {topic}
        
        RESEARCH FINDINGS:
        {research_summary}
        
        Requirements:
        1. Create a logical, hierarchical structure
        2. Include introduction and conclusion
        3. Cover all major aspects found in research
        4. Use clear, descriptive section headings
        5. Include 2-3 subsections for main sections
        6. Provide a brief summary of what the article will cover
        
        Return as JSON with: title, sections (list with title, subsections), summary
        """
        
        messages = [
            SystemMessage(content="You are an expert technical writer. Create clear, logical article outlines."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            outline_data = json.loads(response.content)
            return ArticleOutline(**outline_data)
            
        except Exception as e:
            print(f"Error generating outline: {e}")
            # Return a basic outline as fallback
            return ArticleOutline(
                title=f"Comprehensive Analysis of {topic}",
                sections=[
                    {"title": "Introduction", "subsections": []},
                    {"title": "Background and Context", "subsections": ["Historical Development", "Key Concepts"]},
                    {"title": "Current State", "subsections": ["Recent Developments", "Current Applications"]},
                    {"title": "Future Implications", "subsections": []},
                    {"title": "Conclusion", "subsections": []}
                ],
                summary=f"A comprehensive analysis of {topic} covering key aspects and implications."
            )