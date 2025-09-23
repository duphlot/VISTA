import subprocess
import numpy as np
from typing import List, Tuple, Dict, Any
from PIL import Image
import torch
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import torchvision.transforms as transforms
import cv2
import clip

class VideoPreprocessor:
    """Extract keyframes from videos with CLIP embedding and improved redundancy removal"""

    def __init__(self, frame_interval: int = 5, similarity_threshold: float = 0.9, max_recent: int = 5):
        """
        Args:
            frame_interval: Extract every N frames
            similarity_threshold: Cosine similarity threshold for removing redundant frames
            max_recent: Number of recent selected frames to compare for redundancy
        """
        self.frame_interval = frame_interval
        self.similarity_threshold = similarity_threshold
        self.max_recent = max_recent
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)

    def extract_frames(self, video_path: str, max_frames: int = 100) -> List[np.ndarray]:
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-f", "image2pipe",
            "-pix_fmt", "rgb24",
            "-vsync", "0",
            "-vcodec", "rawvideo", "-"
        ]

        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)

        frames = []
        frame_count = 0
        extracted_count = 0

        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height", "-of", "csv=p=0", video_path],
            capture_output=True, text=True
        )
        w, h = map(int, probe.stdout.strip().split(","))

        while extracted_count < max_frames:
            raw_frame = pipe.stdout.read(w * h * 3)
            if not raw_frame:
                break
            frame = np.frombuffer(raw_frame, np.uint8).reshape((h, w, 3))

            if frame_count % max(1, self.frame_interval) == 0:
                frames.append(frame)
                extracted_count += 1

            frame_count += 1
            # print(frame_count)

        pipe.stdout.close()
        pipe.wait()

        # print(frames)
        return frames

    def get_clip_embedding(self, frame: np.ndarray) -> np.ndarray:
        pil_image = Image.fromarray(frame)
        image_input = self.clip_preprocess(pil_image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_input)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy().flatten()

    def remove_redundant_frames(self, frames: List[np.ndarray], min_frame_gap: int = 20) -> Tuple[List[np.ndarray], List[int]]:
        """
        Remove redundant frames based on CLIP embeddings with temporal spacing.

        Args:
            frames: list of frames (np.ndarray)
            min_frame_gap: minimum number of frames between kept frames (temporal spacing)

        Returns:
            filtered_frames: list of selected frames
            selected_indices: indices of selected frames
        """
        if not frames:
            return [], []

        embeddings = [self.get_clip_embedding(f) for f in frames]
        embeddings = np.array(embeddings)

        selected_frames = [frames[0]]
        selected_indices = [0]
        recent_embeddings = [embeddings[0:1]]

        for i in range(1, len(frames)):
            current_emb = embeddings[i:i+1]
            similarities = [cosine_similarity(current_emb, e)[0][0] for e in recent_embeddings]

            time_since_last_kept = i - selected_indices[-1]

            # Keep frame if similarity low OR enough frames passed since last kept
            if all(s < self.similarity_threshold for s in similarities) or time_since_last_kept >= min_frame_gap:
                selected_frames.append(frames[i])
                selected_indices.append(i)
                recent_embeddings.append(current_emb)
                if len(recent_embeddings) > self.max_recent:
                    recent_embeddings.pop(0)

        return selected_frames, selected_indices


    def extract_keyframes_with_redundancy_removal(self, video_path: str, max_frames: int = 100) -> Tuple[List[np.ndarray], List[int]]:
        raw_frames = self.extract_frames(video_path, max_frames)
        if not raw_frames:
            return [], []
        filtered_frames, selected_indices = self.remove_redundant_frames(raw_frames)
        return filtered_frames, selected_indices

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        return {'fps': fps, 'frame_count': frame_count, 'duration': duration, 'width': width, 'height': height}
