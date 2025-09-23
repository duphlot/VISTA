import os
import re
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List

from src.utils.basetools.image_relation_tool import create_image_relation_tool


class VideoAnalysisTool:
    """Tool wrapper for agent to analyze video relations"""
    
    def __init__(self, processed_frames_dir: str, keyframes_dir: str, gemini_api_key: str):
        self.processed_frames_dir = Path(processed_frames_dir)
        self.keyframes_dir = Path(keyframes_dir)
        self.image_relation_tool = create_image_relation_tool(
            api_key=gemini_api_key,
            keyframes_dir=keyframes_dir
        )
    
    def _extract_video_id(self, message: str) -> str:
        """Extract video ID from user message"""
        # Find numbers with at least 8 digits (usually video IDs)
        numbers = re.findall(r'\d{8,}', message)
        return numbers[0] if numbers else None
    
    def _load_frames(self, video_name: str) -> List[np.ndarray]:
        """Load all frames from processed_frames directory"""
        frames_dir = self.processed_frames_dir / video_name
        
        if not frames_dir.exists():
            raise FileNotFoundError(f"Không tìm thấy thư mục frames: {frames_dir}")
        
        frame_files = sorted([f for f in frames_dir.glob("*.jpg") if f.is_file()])
        
        if not frame_files:
            raise FileNotFoundError(f"Không tìm thấy frame nào trong {frames_dir}")
        
        processed_frames = []
        for frame_file in frame_files:
            img = cv2.imread(str(frame_file))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            processed_frames.append(img_rgb)
        
        return processed_frames
    
    def analyze_video_relations(self, user_message: str) -> str:
        """
        Analyze object relations in video based on user message
        
        Args:
            user_message: Message from user containing video analysis request
            
        Returns:
            Formatted analysis results string
        """
        try:
            # Extract video ID
            video_name = self._extract_video_id(user_message)
            if not video_name:
                return "❌ Không tìm thấy ID video trong yêu cầu. Vui lòng cung cấp ID video (ví dụ: 3557498300)."
            
            # Load frames
            try:
                processed_frames = self._load_frames(video_name)
            except FileNotFoundError as e:
                return f"❌ {str(e)}"
            
            # Analyze using image relation tool
            all_relations = self.image_relation_tool.analyze_video_frames(processed_frames, video_name)
            
            # Format results
            return self._format_results(video_name, all_relations, len(processed_frames))
            
        except Exception as e:
            return f"❌ Lỗi trong quá trình phân tích: {str(e)}"
    
    def _format_results(self, video_name: str, all_relations: Dict[str, List[str]], total_frames: int) -> str:
        """Format analysis results into markdown string"""
        result_lines = [
            f"# 📹 Kết quả phân tích video {video_name}",
            f"**Tổng số frames:** {total_frames}",
            ""
        ]
        
        relation_count = 0
        for frame_name, relations in all_relations.items():
            frame_num = frame_name.replace("frame_", "")
            result_lines.append(f"## 🎬 Frame {frame_num}")
            
            if relations:
                for relation in relations:
                    result_lines.append(f"- {relation}")
                    relation_count += 1
            else:
                result_lines.append("- *Không phát hiện quan hệ nào*")
            
            result_lines.append("")
        
        result_lines.insert(2, f"**Tổng số quan hệ phát hiện:** {relation_count}")
        result_lines.insert(3, "")
        
        return "\n".join(result_lines)


def create_video_analysis_tool(processed_frames_dir: str, keyframes_dir: str, gemini_api_key: str):
    """Factory function to create VideoAnalysisTool"""
    return VideoAnalysisTool(processed_frames_dir, keyframes_dir, gemini_api_key)