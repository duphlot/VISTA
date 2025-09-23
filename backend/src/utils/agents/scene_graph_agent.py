from typing import List, Dict
from pydantic import BaseModel
from google import genai
from pathlib import Path
import time
import os
from dotenv import load_dotenv
from src.data.prompts.graph_builder_prompt import GRAPH_BUILDER_PROMPT

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)


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
        
        # Retry mechanism for API calls
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=[prompt]
                )
                break  # Success, exit retry loop
            except Exception as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    if attempt < max_retries - 1:  # Not the last attempt
                        print(f"🔄 [RETRY] Scene graph API unavailable, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        print("❌ [ERROR] Scene graph API unavailable after all retries")
                        return []
                else:
                    raise e  # Re-raise non-503 errors

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