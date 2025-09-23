from typing import List
from pydantic import BaseModel
from google import genai
from pathlib import Path
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
# --- Config LLM Client ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Pydantic Schemas ---
class GraphReasoningInput(BaseModel):
    question: str
    graph_text: str
    top_k: int = 200

class GraphReasoningOutput(BaseModel):
    answer: str

# --- Agent Class ---
class GraphReasoningAgent:
    def __init__(self, model="gemini-2.0-flash"):
        self.model = model

    def _retrieve_relevant_relations(self, question: str, graph_text: str, top_k: int) -> str:
        relations = graph_text.strip().splitlines()
        question_tokens = set(question.lower().split())
        scored = []
        for rel in relations:
            score = sum(token in rel.lower() for token in question_tokens)
            if score > 0:
                scored.append((score, rel))
        scored.sort(reverse=True, key=lambda x: x[0])
        top_relations = [rel for _, rel in scored[:top_k]]
        if not top_relations:
            top_relations = relations[:top_k]
        return "\n".join(top_relations)

    def run(self, data: GraphReasoningInput) -> GraphReasoningOutput:
        relevant_graph = self._retrieve_relevant_relations(
            data.question, data.graph_text, data.top_k
        )

        prompt = f"""
Bạn là một hệ thống reasoning dựa trên scene graph.
Dưới đây là các quan hệ trong graph có thể liên quan đến câu hỏi:

{relevant_graph}

Câu hỏi: {data.question}

Hãy trả lời câu hỏi một cách logic, rõ ràng, dựa trên thông tin có trong graph.
Chỉ trả về câu trả lời, không thêm giải thích.
"""
        response = client.models.generate_content(
            model=self.model,
            contents=[prompt]
        )
        # Lấy text đầu tiên
        answer = ""
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.text:
                    answer += part.text.strip()
        return GraphReasoningOutput(answer=answer)
