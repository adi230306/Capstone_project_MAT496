from typing import List
from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from state import ResearchState
from config import Config

class SynthesisNode:
    """Node for synthesizing draft sections into final article."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=Config.LLM_MODEL, temperature=0.2)
    
    def __call__(self, state: ResearchState) -> Command[ResearchState]:
        """Synthesize all sections into final article."""
        draft_sections = state["draft_sections"]
        outline = state["outline"]
        
        if not draft_sections or not outline:
            return Command(update={"final_article": "No content available."})
        
        print(" Synthesizing final article...")
        
        section_contents = []
        for section in outline.sections:
            section_title = section["title"]
            if section_title in draft_sections:
                draft = draft_sections[section_title]
                section_contents.append(f"## {section_title}\n\n{draft.content}")
        
        all_content = "\n\n".join(section_contents)
        
        final_article = self._synthesize_article(
            outline.title,  # Use the title from outline (could be custom or generated)
            outline.summary,
            all_content
        )
        
        print("✅ Final article synthesized")
        
        return Command(update={"final_article": final_article})
    
    def _synthesize_article(self, title: str, summary: str, content: str) -> str:
        """Synthesize cohesive final article."""
        prompt = f"""
        Transform the following draft sections into a polished, cohesive Wikipedia-style article.
        
        TITLE: {title}
        SUMMARY: {summary}
        
        DRAFT CONTENT:
        {content}
        
        Instructions:
        1. Start with the title as a level 1 heading: # {title}
        2. Add the summary as an introductory paragraph
        3. Maintain Wikipedia-style: neutral, factual, comprehensive
        4. Ensure smooth transitions between sections
        5. Improve flow and readability
        6. Maintain consistent tone and style
        7. Keep all essential information and citations
        8. Format with proper Markdown headings
        9. Ensure the article is self-contained and informative
        
        Return the complete, polished article.
        """
        
        messages = [
            SystemMessage(content="You are a senior editor. Create polished, professional articles from draft content."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"Error in synthesis: {e}")
            return f"# {title}\n\n{summary}\n\n{content}"