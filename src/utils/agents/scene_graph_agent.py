from typing import List, Dict
from pydantic import BaseModel
from google import genai
from pathlib import Path
import time
from src.data.prompts.graph_builder_prompt import GRAPH_BUILDER_PROMPT

client = genai.Client(api_key="GEMINI_API_KEY")


# --- Pydantic Schemas ---
class SceneGraphInput(BaseModel):
    frames_dict: Dict[str, List[str]]  # {"frame_0": ["người1 - đứng cạnh - ghế1", ...], ...}


class SceneGraphOutput(BaseModel):
    combined_relations: List[str]


# --- Agent Class ---
class SameEntityAgent:
    def __init__(self, model="gemini-2.0-flash", group_size=10):
        self.model = model
        self.group_size = group_size

    def _get_same_entity_between_frames(self, frame_names, frames_dict) -> List[str]:
        prompt = "Bạn là AI giúp xác định cùng một object qua nhiều frame trong video.\n"
        for fn in frame_names:
            prompt += f"{fn}:\n"
            prompt += "\n".join(frames_dict[fn]) + "\n"

        prompt += "\n" + GRAPH_BUILDER_PROMPT
        response = client.models.generate_content(
            model=self.model,
            contents=[prompt]
        )

        same_entity_rels = []
        for part in response.candidates[0].content.parts:
            if part.text:
                for line in part.text.strip().split("\n"):
                    if line.strip():
                        same_entity_rels.append(line.strip())
        return same_entity_rels

    def run(self, data: SceneGraphInput) -> SceneGraphOutput:
        frame_names = sorted(data.frames_dict.keys())
        all_same_entity_rels = []

        for i in range(0, len(frame_names), self.group_size):
            group = frame_names[i:i+self.group_size]
            same_entity_rels = self._get_same_entity_between_frames(group, data.frames_dict)
            all_same_entity_rels.extend(same_entity_rels)

        combined_rels = []
        for frame_name, rels in data.frames_dict.items():
            for r in rels:
                combined_rels.append(f"{r} (frame: {frame_name})")
        combined_rels.extend(all_same_entity_rels)

        return SceneGraphOutput(combined_relations=combined_rels)