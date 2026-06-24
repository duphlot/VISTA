from typing import List, Dict, Any
from src.utils.agents.graph_reasoning_agent import GraphReasoningAgent, GraphReasoningInput

class MessengerAgent:
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.reasoning_agent = GraphReasoningAgent(model=model)

    def run(self, question: str, scene_graph: List[str]) -> Dict[str, Any]:
        """
        Runs Messenger Agent:
        1. Grounds the user's natural language question on the scene graph
        2. Retrieves relevant graph relations and performs reasoning
        3. Formulates the final response
        """
        graph_text = "\n".join(scene_graph) if isinstance(scene_graph, list) else str(scene_graph)
        
        reasoning_input = GraphReasoningInput(
            question=question,
            graph_text=graph_text,
            top_k=200
        )
        
        result = self.reasoning_agent.run(reasoning_input)
        
        return {
            "answer": result.answer
        }
