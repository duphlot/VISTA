import cv2
import numpy as np
import os
from typing import List, Tuple, Dict, Any
from src.utils.basetools.preprocess_video import VideoPreprocessor

class ScoutAgent:
    def __init__(self, frame_interval: int = 1, similarity_threshold: float = 0.8):
        self.preprocessor = VideoPreprocessor(
            frame_interval=frame_interval, 
            similarity_threshold=similarity_threshold
        )
        self.sam_processor = None
        
        # Try loading PanopticSAMProcessor, fallback to OpenCV if missing dependencies or checkpoint
        try:
            from src.utils.basetools.mask import PanopticSAMProcessor
            # Check if sam checkpoint exists before initializing
            checkpoint_path = "sam_vit_h_4b8939.pth"
            if os.path.exists(checkpoint_path):
                self.sam_processor = PanopticSAMProcessor(sam_checkpoint=checkpoint_path)
                print("ScoutAgent initialized SAM Processor successfully.")
            else:
                print("ScoutAgent: SAM checkpoint not found, using OpenCV contour-based masking fallback.")
        except Exception as e:
            print(f"ScoutAgent: Could not load SAM Processor ({e}), using OpenCV contour-based masking fallback.")

    def _generate_opencv_masks(self, frame: np.ndarray) -> np.ndarray:
        """Lightweight fallback mask generator using Canny edges and contours"""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        # Apply blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        mask_frame = frame.copy()
        
        # Sort contours by area to draw larger ones first
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        for i, contour in enumerate(sorted_contours[:15]): # Limit to top 15 regions
            if cv2.contourArea(contour) > 200:
                # Generate a unique pseudo-random color for each object region
                np.random.seed(i)
                color = tuple(map(int, np.random.randint(50, 255, size=3)))
                # Draw the filled contour overlay with transparency
                overlay = mask_frame.copy()
                cv2.drawContours(overlay, [contour], -1, color, -1) # Filled
                cv2.drawContours(mask_frame, [contour], -1, color, 2) # Boundary
                # Apply transparency
                cv2.addWeighted(overlay, 0.3, mask_frame, 0.7, 0, mask_frame)
                
        return mask_frame

    def run(self, video_path: str) -> Dict[str, Any]:
        """
        Runs Scout Agent:
        1. Extract video metadata
        2. Extract raw frames
        3. Perform frame selection (redundancy removal)
        4. Generate entity masked frames
        """
        video_info = self.preprocessor.get_video_info(video_path)
        
        # Extract frames
        raw_frames = self.preprocessor.extract_frames(video_path, max_frames=video_info['frame_count'])
        
        # Frame selection
        filtered_frames, selected_indices = self.preprocessor.remove_redundant_frames(raw_frames)
        
        # Entity Masking
        masked_frames = []
        for frame in filtered_frames:
            if self.sam_processor is not None:
                try:
                    # SAM process_frame returns (visualization_image, refined_masks)
                    masked_img, _ = self.sam_processor.process_frame(frame)
                    masked_frames.append(masked_img)
                except Exception as e:
                    print(f"Error in SAM masking: {e}. Falling back to OpenCV.")
                    masked_frames.append(self._generate_opencv_masks(frame))
            else:
                masked_frames.append(self._generate_opencv_masks(frame))
                
        return {
            "video_info": video_info,
            "keyframes": filtered_frames,
            "selected_indices": selected_indices,
            "masked_keyframes": masked_frames
        }
