import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator


class PanopticSAMProcessor:
    def __init__(self, sam_checkpoint="sam_vit_h_4b8939.pth", model_type="vit_h", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Load SAM
        sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        sam.to(device=self.device)
        self.mask_generator = SamAutomaticMaskGenerator(sam)

        # Load Detectron2 PanopticSegmentation
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file(
            "COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml"
        ))
        cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
            "COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml"
        )
        cfg.MODEL.DEVICE = self.device
        self.predictor = DefaultPredictor(cfg)
        self.cfg = cfg

    @staticmethod
    def iou(mask1, mask2):
        inter = np.logical_and(mask1, mask2).sum()
        union = np.logical_or(mask1, mask2).sum()
        return inter / union if union > 0 else 0

    def process_frame(self, frame):
        # Detectron2 prediction
        outputs = self.predictor(frame)
        panoptic_seg, segments_info = outputs["panoptic_seg"]
        panoptic_seg = panoptic_seg.cpu().numpy()

        # SAM prediction
        sam_masks = [m["segmentation"] for m in self.mask_generator.generate(frame)]

        refined_masks = []
        for seg in segments_info:
            seg_id = seg["id"]
            mask_pan = (panoptic_seg == seg_id)
            best_iou, best_sam = 0, None
            for sam_m in sam_masks:
                score = self.iou(mask_pan, sam_m)
                if score > best_iou:
                    best_iou, best_sam = score, sam_m
            mask_final = best_sam if best_iou > 0.5 else mask_pan
            refined_masks.append({
                "category_id": seg["category_id"],
                "isthing": seg["isthing"],
                "mask": mask_final
            })

        # Visualization
        v = Visualizer(frame[:, :, ::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]))
        out = v.draw_panoptic_seg_predictions(torch.tensor(panoptic_seg), segments_info)
        return out.get_image()[:, :, ::-1], refined_masks

    def process_video(self, video_path, frame_interval=30, max_frames=None):
        cap = cv2.VideoCapture(str(video_path))
        processed_frames = []
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_interval == 0:
                processed, _ = self.process_frame(frame)
                processed_frames.append(processed)

                if max_frames and len(processed_frames) >= max_frames:
                    break
            frame_idx += 1

        cap.release()
        return processed_frames

    @staticmethod
    def show_processed_frames(processed_images):
        for i, img in enumerate(processed_images):
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.title(f"Keyframe {i}")
            plt.axis("off")
            plt.show()
