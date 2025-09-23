import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from io import BytesIO
from PIL import Image
import numpy as np
from google import genai

from src.data.prompts.image_relation_prompt import IMAGE_RELATION_PROMPT, COLOR_EXTRACTION_PROMPT


class ImageRelationAnalyzer:
    """Tool for analyzing relations between objects in video frames"""
    
    def __init__(self, api_key: str, keyframes_dir: str):
        """
        Args:
            api_key: Google Gemini API key
            keyframes_dir: Path to keyframes_output directory
        """
        self.client = genai.Client(api_key=api_key)
        self.keyframes_dir = Path(keyframes_dir)
        self.prev_objects = None
        self.known_objects_colors = {}  # Cache colors of known objects
        
    def _upload_image_array(self, img_array: np.ndarray) -> Any:
        """Upload numpy array image to Gemini"""
        img_pil = Image.fromarray(img_array)
        buffer = BytesIO()
        img_pil.save(buffer, format="JPEG")
        buffer.seek(0)
        
        return self.client.files.upload(file=buffer, config={"mime_type": "image/jpeg"})
    
    def _upload_image_file(self, image_path: str) -> Any:
        """Upload image file to Gemini"""
        with open(image_path, "rb") as f:
            return self.client.files.upload(file=f, config={"mime_type": "image/jpeg"})
    
    def _extract_colors_from_keyframe(self, video_name: str, frame_idx: int, new_objects: List[str]) -> Dict[str, str]:
        """Extract colors of new objects from original keyframe"""
        # Keyframes are stored in directories: keyframes_output/video_name/frame_XXXX.jpg
        keyframe_path = self.keyframes_dir / video_name / f"frame_{frame_idx:04d}.jpg"
        
        if not keyframe_path.exists():
            print(f"Warning: Keyframe not found {keyframe_path}")
            return {}
        
        try:
            image_file = self._upload_image_file(str(keyframe_path))
            
            prompt = COLOR_EXTRACTION_PROMPT.format(
                objects_to_analyze=json.dumps(new_objects, ensure_ascii=False)
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[image_file, prompt]
            )
            
            colors = {}
            for part in response.candidates[0].content.parts:
                if part.text:
                    try:
                        color_data = json.loads(part.text)
                        colors.update(color_data)
                    except json.JSONDecodeError:
                        print(f"Warning: Cannot parse color data: {part.text}")
            
            return colors
            
        except Exception as e:
            print(f"Error extracting colors: {e}")
            return {}
    
    def _detect_new_objects(self, current_relations: List[str]) -> List[str]:
        """Detect new objects without color information"""
        new_objects = []
        
        for relation in current_relations:
            # Extract object names from relation string
            parts = relation.split(" - ")
            if len(parts) >= 3:
                obj1 = parts[0].split(" (")[0]  # Get object name, remove description
                obj2 = parts[2].split(" (")[0]
                
                for obj in [obj1, obj2]:
                    if obj not in self.known_objects_colors and obj not in new_objects:
                        new_objects.append(obj)
        
        return new_objects
    
    def _update_relations_with_colors(self, relations: List[str], colors: Dict[str, str]) -> List[str]:
        """Update relations with color information from keyframe"""
        updated_relations = []
        
        for relation in relations:
            parts = relation.split(" - ")
            if len(parts) >= 3:
                obj1_part = parts[0]
                relation_part = parts[1]
                obj2_part = parts[2]
                
                # Update object 1
                obj1_name = obj1_part.split(" (")[0]
                if obj1_name in colors:
                    obj1_part = f"{obj1_name} ({colors[obj1_name]})"
                
                # Update object 2  
                obj2_name = obj2_part.split(" (")[0]
                if obj2_name in colors:
                    obj2_part = f"{obj2_name} ({colors[obj2_name]})"
                
                updated_relation = f"{obj1_part} - {relation_part} - {obj2_part}"
                updated_relations.append(updated_relation)
            else:
                updated_relations.append(relation)
        
        return updated_relations
    
    def analyze_frame(self, img_array: np.ndarray, video_name: str, frame_idx: int) -> List[str]:
        """
        Analyze one frame to find relations between objects
        
        Args:
            img_array: Numpy array of processed frame
            video_name: Video name (to find corresponding keyframe)
            frame_idx: Current frame index
            
        Returns:
            List of relation strings
        """
        try:
            # Upload processed frame
            image_file = self._upload_image_array(img_array)
            
            # Create prompt with previous frame information
            prev_objects_info = ""
            if self.prev_objects:
                prev_objects_info = json.dumps(self.prev_objects, ensure_ascii=False)
            
            prompt = IMAGE_RELATION_PROMPT.format(
                prev_objects_info=prev_objects_info
            )
            
            # Call Gemini to analyze relations
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=[image_file, prompt]
            )
            
            relations = []
            for part in response.candidates[0].content.parts:
                if part.text:
                    try:
                        data = json.loads(part.text)
                        if isinstance(data, list):
                            relations.extend(data)
                    except json.JSONDecodeError:
                        relations.append(part.text.strip())
            
            # Detect new objects needing colors
            new_objects = self._detect_new_objects(relations)
            
            # Get colors from keyframe if there are new objects
            if new_objects:
                print(f"Frame {frame_idx}: Detected new objects: {new_objects}")
                colors = self._extract_colors_from_keyframe(video_name, frame_idx, new_objects)
                
                # Update color cache
                self.known_objects_colors.update(colors)
                
                # Update relations with new colors
                relations = self._update_relations_with_colors(relations, colors)
            
            # Save current frame information for next frame
            self.prev_objects = relations
            
            return relations
            
        except Exception as e:
            print(f"Error analyzing frame {frame_idx}: {e}")
            return []
    
    def analyze_video_frames(self, processed_frames: List[np.ndarray], video_name: str) -> Dict[str, List[str]]:
        """
        Analyze all frames of a video
        
        Args:
            processed_frames: List of processed frames 
            video_name: Video name
            
        Returns:
            Dict with frame_name as key and list of relations as value
        """
        all_frame_relations = {}
        
        # Reset state for new video
        self.prev_objects = None
        self.known_objects_colors = {}
        
        for i, frame in enumerate(processed_frames):
            relations = self.analyze_frame(frame, video_name, i)
            all_frame_relations[f"frame_{i}"] = relations
            
            print(f"Frame {i} - {len(relations)} relations found")
        
        return all_frame_relations


def create_image_relation_tool(api_key: str, keyframes_dir: str):
    """Factory function to create ImageRelationAnalyzer tool"""
    return ImageRelationAnalyzer(api_key=api_key, keyframes_dir=keyframes_dir)