import os
from typing import List, Dict, Any
from src.utils.agents.scout_agent import ScoutAgent
from src.utils.agents.builder_agent import BuilderAgent
from src.utils.agents.inspector_agent import InspectorAgent
from src.utils.agents.messenger_agent import MessengerAgent

class CaptainAgent:
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        self.scout = ScoutAgent()
        self.builder = BuilderAgent(model=model)
        self.inspector = InspectorAgent(model=model)
        self.messenger = MessengerAgent(model=model)

    def process_video(self, video_path: str, question: str = "Hãy mô tả nội dung chính của video này.") -> Dict[str, Any]:
        """
        Orchestrates the VISTA Video Scene Graph Generation and Reasoning Pipeline:
        1. ScoutAgent extracts keyframes and applies entity masking (SAM/OpenCV).
        2. BuilderAgent generates frame-level relations and links identical entities.
        3. InspectorAgent validates and finalizes the scene graph.
        4. MessengerAgent grounds the question and performs graph reasoning to get the answer.
        """
        print("CaptainAgent: Starting video analysis workflow...")

        # Phase 1: Perception (Scout)
        print("CaptainAgent: Launching ScoutAgent for Frame Extraction, Selection, and Masking...")
        scout_result = self.scout.run(video_path)

        # Phase 2: Representation (Builder)
        print("CaptainAgent: Launching BuilderAgent for Entity Generation & Relation Detection...")
        builder_result = self.builder.run(
            keyframes=scout_result["keyframes"],
            masked_keyframes=scout_result["masked_keyframes"]
        )

        # Phase 3: Quality Assurance (Inspector)
        print("CaptainAgent: Launching InspectorAgent for Scene Graph validation...")
        validated_graph = self.inspector.run(builder_result["scene_graph"])

        # Phase 4: Communication & Reasoning (Messenger)
        print(f"CaptainAgent: Launching MessengerAgent to reason about question: '{question}'...")
        messenger_result = self.messenger.run(question, validated_graph)

        return {
            "video_info": scout_result["video_info"],
            "keyframes": scout_result["keyframes"],
            "masked_keyframes": scout_result["masked_keyframes"],
            "selected_indices": scout_result["selected_indices"],
            "relations": builder_result["relations_per_frame"],
            "scene_graph": validated_graph,
            "answer": messenger_result["answer"]
        }

    def generate_chat_thoughts(self, question: str, answer: str) -> List[Dict[str, Any]]:
        """
        Compiles the structured coordination thoughts representing the VISTA Multi-Agent collaborative process.
        This will be returned to the frontend as the `parts` array in chat messages.
        """
        return [
            {
                "type": "thought",
                "author": "Captain Agent",
                "content": f"Đang điều phối các Agent để giải quyết câu hỏi: '{question}'.\n- Kế hoạch: Phân tích câu hỏi -> Tìm kiếm quan hệ liên quan -> Đánh giá chéo -> Messenger trả lời."
            },
            {
                "type": "thought",
                "author": "Messenger Agent",
                "content": f"Đang phân tích cấu trúc cú pháp câu hỏi: '{question}' để xác định các entity và hành động cần tìm kiếm trong scene graph."
            },
            {
                "type": "thought",
                "author": "Graph Builder Agent",
                "content": "Đang định vị các đối tượng, hành động và quan hệ không gian/thời gian trong scene graph tương ứng với câu hỏi của người dùng."
            },
            {
                "type": "thought",
                "author": "Inspector Agent",
                "content": "Đang kiểm tra tính chính xác của các mối quan hệ được trích xuất đối với ngữ cảnh câu hỏi, loại bỏ mâu thuẫn logic."
            },
            {
                "type": "thought",
                "author": "Messenger Agent",
                "content": "Đang tổng hợp thông tin, xâu chuỗi logic và diễn đạt câu trả lời mạch lạc bằng tiếng Việt."
            },
            {
                "type": "text",
                "author": "Messenger Agent",
                "content": answer
            }
        ]
