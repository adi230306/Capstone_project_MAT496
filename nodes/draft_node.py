from typing import List, Dict
from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from state import ResearchState
from models.schemas import SectionDraft
from config import Config

class DraftNode:
    """Node for drafting article sections."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=Config.LLM_MODEL, temperature=0.3)
    
    def __call__(self, state: ResearchState) -> Command[ResearchState]:
        """Draft all article sections."""
        outline = state["outline"]
        research_memory = state["research_memory"]
        
        if not outline:
            return Command(update={"draft_sections": {}})
        
        print(f"✍️ Drafting {len(outline.sections)} sections...")
        
        draft_sections = {}
        
        for i, section in enumerate(outline.sections):
            section_title = section["title"]
            print(f" Drafting: {section_title}")
            
            relevant_facts = self._get_relevant_facts(section_title, research_memory)
            
            section_draft = self._draft_section(
                section_title, 
                relevant_facts, 
                i, 
                len(outline.sections)
            )
            
            draft_sections[section_title] = section_draft
        
        print(" All sections drafted")
        
        return Command(update={"draft_sections": draft_sections})
    
    def _get_relevant_facts(self, section_title: str, research_memory: dict) -> list:
        """Get facts relevant to the section."""
        relevant_facts = []
        
        for perspective, facts in research_memory.items():
            for fact in facts:
                if any(keyword in section_title.lower() for keyword in perspective.split('_')):
                    relevant_facts.append(fact)
        
        return relevant_facts[:10] 
    
    def _draft_section(self, section_title: str, facts: list, section_index: int, total_sections: int) -> SectionDraft:
        """Draft a single section."""
        facts_text = "\n".join([f"- {fact.fact} (Source: {fact.source_url})" for fact in facts])
        
        prompt = f"""
        Write the '{section_title}' section for a comprehensive article.
        
        This is section {section_index + 1} of {total_sections}.
        
        RELEVANT FACTS:
        {facts_text}
        
        Requirements:
        1. Write in Wikipedia-style: neutral, factual, comprehensive
        2. Use the provided facts as basis
        3. Include citations for all facts
        4. Write 200-300 words
        5. Focus on clarity and readability
        6. Connect logically to surrounding sections
        
        Provide the content, list of source URLs used, and key points.
        """
        
        messages = [
            SystemMessage(content="You are a Wikipedia editor. Write clear, factual, well-structured content."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content
            sources = list(set(fact.source_url for fact in facts))
            key_points = self._extract_key_points(content)
            
            return SectionDraft(
                section_title=section_title,
                content=content,
                sources=sources,
                key_points=key_points
            )
            
        except Exception as e:
            print(f"Error drafting section {section_title}: {e}")
            return SectionDraft(
                section_title=section_title,
                content=f"Content for {section_title} could not be generated.",
                sources=[],
                key_points=[]
            )
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from section content."""
        sentences = content.split('. ')
        return [s.strip() for s in sentences[:3] if len(s) > 20]