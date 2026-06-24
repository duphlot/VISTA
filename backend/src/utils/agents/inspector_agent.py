import os
import json
from typing import List
from google import genai
from dotenv import load_dotenv
from src.data.prompts.inspector_prompt import Inspector_PROMPT

load_dotenv()

class InspectorAgent:
    def __init__(self, model: str = "gemini-2.0-flash"):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def run(self, scene_graph: List[str]) -> List[str]:
        """
        Runs Inspector Agent:
        1. Formats the scene graph and queries LLM to check format/validity
        2. Filters out low-confidence, invalid, or noisy relations
        """
        if not scene_graph:
            return []

        # Construct prompt
        graph_text = json.dumps(scene_graph, ensure_ascii=False, indent=2)
        prompt = f"{Inspector_PROMPT}\n\nScene Graph cần kiểm tra:\n{graph_text}"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt]
                )

                # Parse the response text as JSON
                text = response.text.strip() if response.text else ""

                # Clean markdown code blocks if present
                if text.startswith("```json"):
                    text = text.split("```json")[1].split("```")[0].strip()
                elif text.startswith("```"):
                    text = text.split("```")[1].split("```")[0].strip()

                validated_graph = json.loads(text)
                if isinstance(validated_graph, list):
                    print(f"InspectorAgent: Verified and finalized {len(validated_graph)} valid scene graph relations.")
                    return validated_graph
                else:
                    print("InspectorAgent: Checked output was not a list, returning original graph.")
                    return scene_graph

            except Exception as e:
                print(f"InspectorAgent: Validation attempt {attempt+1} failed ({e})")
                if attempt == max_retries - 1:
                    print("InspectorAgent: All verification attempts failed, returning original graph as fallback.")
                    return scene_graph

        return scene_graph
