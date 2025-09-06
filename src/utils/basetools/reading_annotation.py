import json
from typing import Dict, List

class CLEVRERObjectHandler:
    """Handle CLEVRER annotation data for object detection and tracking"""
    
    def __init__(self, annotation_file: str):
        """
        Initialize with annotation file
        
        Args:
            annotation_file: Path to the JSON annotation file
        """
        with open(annotation_file, "r") as f:
            self.data = json.load(f)

        self.objects = self.data["object_property"]       # metadata object
        self.trajectories = self.data["motion_trajectory"] # motion per frame

    def get_objects(self) -> List[Dict]:
        """Get all static object properties"""
        return self.objects

    def get_objects_in_frame(self, frame_id: int) -> List[Dict]:
        """
        Get all objects present in a specific frame with their properties and positions
        
        Args:
            frame_id: Frame number to query
            
        Returns:
            List of objects with merged property and motion data
        """
        frame_info = next((f for f in self.trajectories if f["frame_id"] == frame_id), None)
        if frame_info is None:
            return []
        
        result = []
        for obj in frame_info["objects"]:
            obj_info = next(o for o in self.objects if o["object_id"] == obj["object_id"])
            merged = {**obj_info, **obj}  # merge property + motion info
            result.append(merged)
        return result