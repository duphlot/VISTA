import time
from typing import List, Dict, Any
from src.utils.agents.image_relation_agent import ImageRelationAgent, ImageRelationInput
from src.utils.agents.scene_graph_agent import SameEntityAgent, SceneGraphInput

class BuilderAgent:
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.image_relation_agent = ImageRelationAgent(model=model)
        self.same_entity_agent = SameEntityAgent(model=model)

    def run(self, keyframes: List[Any], masked_keyframes: List[Any]) -> Dict[str, Any]:
        """
        Runs Builder Agent:
        1. Query VLM (ImageRelationAgent) for each frame to generate entity relations (using masked & original frames)
        2. Combine relations and link same entities (SameEntityAgent) across frames
        """
        all_frame_relations = {}
        
        # 1. Generate relations for each frame
        for i, frame in enumerate(masked_keyframes):
            input_data = ImageRelationInput(
                mask_frame=frame,
                original_img=keyframes[i],
                prev_objects=self.image_relation_agent.prev_objects
            )
            result = self.image_relation_agent.run(input_data)
            all_frame_relations[f"frame_{i}"] = result.relations
            
            # Wait 1 second between frames to avoid rate limits
            if i < len(masked_keyframes) - 1:
                print(f"BuilderAgent: Waiting 1 second before processing frame {i+1}...")
                time.sleep(1)
                
        # 2. Link same entities across frames to construct the video scene graph
        print("BuilderAgent: Linking entities across frames to build scene graph...")
        scene_graph_input = SceneGraphInput(frames_dict=all_frame_relations)
        linked_result = self.same_entity_agent.run(scene_graph_input)
        linked_scene_graph = linked_result.combined_relations
        
        return {
            "relations_per_frame": all_frame_relations,
            "scene_graph": linked_scene_graph
        }
