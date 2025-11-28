from langgraph.graph import StateGraph, END
from state import ResearchState
from nodes.search_node import SearchNode
from nodes.retrieve_node import RetrieveNode
from nodes.research_node import ResearchNode
from nodes.outline_node import OutlineNode
from nodes.draft_node import DraftNode
from nodes.synthesis_node import SynthesisNode
from nodes.refinement_node import RefinementNode
import asyncio

class AutoResearchAgent:
    """Main agent class for automated research and article generation."""
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("search", SearchNode())
        workflow.add_node("retrieve", RetrieveNode())
        workflow.add_node("research", ResearchNode())
        workflow.add_node("outline", OutlineNode())
        workflow.add_node("draft", DraftNode())
        workflow.add_node("synthesize", SynthesisNode())
        workflow.add_node("refine", RefinementNode())
        
        # Define edges
        workflow.set_entry_point("search")
        workflow.add_edge("search", "retrieve")
        workflow.add_edge("retrieve", "research")
        workflow.add_edge("research", "outline")
        workflow.add_edge("outline", "draft")
        workflow.add_edge("draft", "synthesize")
        workflow.add_edge("synthesize", "refine")
        workflow.add_edge("refine", END)
        
        return workflow.compile()
    
    async def research(self, topic: str) -> dict:
        """Execute research workflow for a given topic."""
        print(f" Starting research on: {topic}")
        print("=" * 50)
        
        try:
            # Initialize state
            initial_state = ResearchState(
                topic=topic,
                search_results=[],
                source_contents=[],
                research_memory={},
                outline=None,
                draft_sections={},
                final_article="",
                error=None,
                retry_count=0
            )
            
            # Execute graph
            final_state = await self.graph.ainvoke(initial_state)
            
            print("=" * 50)
            print(" Research completed successfully!")
            
            return {
                "success": True,
                "topic": topic,
                "final_article": final_state["final_article"],
                "sources_used": len(final_state.get("source_contents", [])),
                "research_facts": sum(len(facts) for facts in final_state.get("research_memory", {}).values())
            }
            
        except Exception as e:
            print(f" Research failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic
            }

# Example usage
async def main():
    """Example usage of the AutoResearch agent."""
    
    # Initialize agent
    agent = AutoResearchAgent()
    
    # Example topics
    topics = [
        "The Impact of Quantum Computing on Cryptography",
        # "Recent Advances in Renewable Energy Storage",
        # "The Future of Artificial Intelligence in Healthcare"
    ]
    
    for topic in topics:
        result = await agent.research(topic)
        
        if result["success"]:
            print(f"\n Research Summary:")
            print(f"   Topic: {result['topic']}")
            print(f"   Sources: {result['sources_used']}")
            print(f"   Facts Extracted: {result['research_facts']}")
            print(f"\n Final Article:")
            print("=" * 50)
            print(result["final_article"])
            print("=" * 50)
        else:
            print(f"Failed: {result['error']}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())