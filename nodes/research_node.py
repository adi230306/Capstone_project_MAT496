from typing import List
from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from state import ResearchState
from models.schemas import ResearchFact
from config import Config
import json

class ResearchNode:
    """Node for analyzing content from multiple perspectives."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=Config.LLM_MODEL, temperature=0.1)
    
    def __call__(self, state: ResearchState) -> Command[ResearchState]:
        """Analyze source content from multiple perspectives."""
        source_contents = state["source_contents"]
        topic = state["topic"]
        
        if not source_contents:
            return Command(update={"research_memory": {}})
        
        print(f" Analyzing content from {len(source_contents)} sources...")
        
        research_memory = {}
        
        for perspective in Config.RESEARCH_PERSPECTIVES:
            print(f"  Perspective: {perspective}")
            facts = self._analyze_perspective(topic, perspective, source_contents)
            research_memory[perspective] = facts
        
        total_facts = sum(len(facts) for facts in research_memory.values())
        print(f" Extracted {total_facts} facts across {len(Config.RESEARCH_PERSPECTIVES)} perspectives")
        
        return Command(update={"research_memory": research_memory})
    
    def _analyze_perspective(self, topic: str, perspective: str, sources: list) -> List[ResearchFact]:
        """Analyze sources from a specific perspective."""
        # Prepare source content for analysis
        source_texts = []
        for source in sources:
            for chunk in source.chunks[:3]:  # Use first 3 chunks per source
                source_texts.append(f"Source: {source.title}\nURL: {source.url}\nContent: {chunk}")
        
        context = "\n\n".join(source_texts)
        
        prompt = f"""
        Analyze the following sources about '{topic}' from the perspective of: {perspective}
        
        SOURCES:
        {context}
        
        Extract 3-5 key facts, insights, and information relevant to {perspective}.
        
        For each fact, provide:
        - The factual information
        - Source URL it came from  
        - Confidence level (0.0 to 1.0)
        - Relevant tags
        
        Return ONLY a JSON array of objects with these fields: fact, perspective, source_url, confidence, tags
        """
        
        messages = [
            SystemMessage(content="You are a research assistant. Extract factual information from sources and return valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Try to parse JSON response
            content = response.content.strip()
            
            # Handle cases where response might have markdown code blocks
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.startswith('```'):
                content = content[3:]  # Remove ```
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            
            facts_data = json.loads(content)
            
            facts = []
            for fact_data in facts_data:
                # Ensure all required fields are present
                if 'fact' in fact_data and 'source_url' in fact_data:
                    facts.append(ResearchFact(
                        fact=fact_data['fact'],
                        perspective=perspective,
                        source_url=fact_data['source_url'],
                        confidence=fact_data.get('confidence', 0.8),
                        tags=fact_data.get('tags', [])
                    ))
            
            return facts
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for {perspective}: {e}")
            print(f"Response was: {response.content}")
            return []
        except Exception as e:
            print(f"Error in research analysis for {perspective}: {e}")
            return []