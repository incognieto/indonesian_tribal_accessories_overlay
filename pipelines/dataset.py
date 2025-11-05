"""
Dataset management for face detection training.
Handles loading, splitting, auto-ROI extraction, and IoU-based labeling.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np
from sklearn.model_selection import train_test_split

from .utils import logger, collect_image_paths, compute_iou, ensure_dir


class DatasetManager:
    """Manages dataset loading, splitting, and ROI extraction."""
    
    def __init__(
        self,
        pos_dir: Path,
        neg_dir: Path,
        cascade_face_path: Path,
        test_size: float = 0.15,
        val_size: float = 0.15,
        random_state: int = 42
    ):
        """
        Initialize dataset manager.
        
        Args:
            pos_dir: Directory with positive samples (faces)
            neg_dir: Directory with negative samples (non-faces)
            cascade_face_path: Path to Haar cascade for face detection
            test_size: Fraction for test split
            val_size: Fraction for validation split
            random_state: Random seed for reproducibility
        """
        self.pos_dir = Path(pos_dir)
        self.neg_dir = Path(neg_dir)
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        
        # Load Haar cascade for auto-ROI extraction
        self.face_cascade = cv2.CascadeClassifier(str(cascade_face_path))
        if self.face_cascade.empty():
            raise ValueError(f"Failed to load cascade: {cascade_face_path}")
        
        self.data: List[Tuple[Path, int]] = []  # (path, label)
        self.splits: Dict[str, List[Tuple[Path, int]]] = {}
    
    def load_data(self) -> None:
        """Load positive and negative samples."""
        logger.info("Loading dataset...")
        
        # Load positive samples
        pos_paths = collect_image_paths(self.pos_dir)
        logger.info(f"Found {len(pos_paths)} positive samples in {self.pos_dir}")
        
        # Load negative samples
        neg_paths = collect_image_paths(self.neg_dir)
        logger.info(f"Found {len(neg_paths)} negative samples in {self.neg_dir}")
        
        # Create dataset: (path, label)
        self.data = [(p, 1) for p in pos_paths] + [(p, 0) for p in neg_paths]
        
        logger.info(f"Total samples: {len(self.data)}")
    
    def create_splits(self) -> None:
        """Create train/val/test splits with stratification."""
        if not self.data:
            raise ValueError("No data loaded. Call load_data() first.")
        
        paths, labels = zip(*self.data)
        
        # First split: train+val vs test
        train_val_paths, test_paths, train_val_labels, test_labels = train_test_split(
            paths, labels,
            test_size=self.test_size,
            stratify=labels,
            random_state=self.random_state
        )
        
        # Second split: train vs val
        val_size_adjusted = self.val_size / (1 - self.test_size)
        train_paths, val_paths, train_labels, val_labels = train_test_split(
            train_val_paths, train_val_labels,
            test_size=val_size_adjusted,
            stratify=train_val_labels,
            random_state=self.random_state
        )
        
        # Store splits
        self.splits = {
            'train': list(zip(train_paths, train_labels)),
            'val': list(zip(val_paths, val_labels)),
            'test': list(zip(test_paths, test_labels))
        }
        
        logger.info(f"Split sizes - Train: {len(self.splits['train'])}, "
                   f"Val: {len(self.splits['val'])}, Test: {len(self.splits['test'])}")
        
        # Log class distribution
        for split_name, split_data in self.splits.items():
            labels_split = [label for _, label in split_data]
            pos_count = sum(labels_split)
            neg_count = len(labels_split) - pos_count
            logger.info(f"{split_name.capitalize()}: {pos_count} pos, {neg_count} neg")
    
    def save_splits(self, output_path: Path) -> None:
        """Save splits to JSON file for reproducibility."""
        if not self.splits:
            raise ValueError("No splits created. Call create_splits() first.")
        
        splits_json = {
            split_name: [
                {'path': str(path), 'label': label}
                for path, label in split_data
            ]
            for split_name, split_data in self.splits.items()
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(splits_json, f, indent=2)
        
        logger.info(f"Saved splits to {output_path}")
    
    def load_splits(self, splits_path: Path) -> None:
        """Load splits from JSON file."""
        with open(splits_path, 'r') as f:
            splits_json = json.load(f)
        
        self.splits = {
            split_name: [
                (Path(item['path']), item['label'])
                for item in split_data
            ]
            for split_name, split_data in splits_json.items()
        }
        
        logger.info(f"Loaded splits from {splits_path}")
    
    def extract_roi_from_image(
        self,
        img_path: Path,
        target_size: Tuple[int, int] = (128, 128),
        iou_threshold: float = 0.5
    ) -> Tuple[np.ndarray, bool]:
        """
        Extract ROI from image using Haar cascade.
        
        For positive images: extract face ROI if detected
        For negative images: extract random crops or use full image
        
        Args:
            img_path: Path to image
            target_size: Target size for ROI (width, height)
            iou_threshold: IoU threshold for positive validation
        
        Returns:
            (roi_image, is_valid) tuple
        """
        img = cv2.imread(str(img_path))
        if img is None:
            logger.warning(f"Failed to load image: {img_path}")
            return None, False
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) > 0:
            # Use largest face
            faces_sorted = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            x, y, w, h = faces_sorted[0]
            
            # Extract ROI
            roi = gray[y:y+h, x:x+w]
            
            # Resize to target size
            roi_resized = cv2.resize(roi, target_size)
            
            return roi_resized, True
        else:
            # No face detected
            # For negatives, this is expected; for positives, it's a failure
            # Use center crop as fallback
            h, w = gray.shape
            crop_size = min(h, w)
            y_start = (h - crop_size) // 2
            x_start = (w - crop_size) // 2
            
            roi = gray[y_start:y_start+crop_size, x_start:x_start+crop_size]
            roi_resized = cv2.resize(roi, target_size)
            
            return roi_resized, False
    
    def get_split_data(self, split: str = 'train') -> List[Tuple[Path, int]]:
        """Get data for a specific split."""
        if split not in self.splits:
            raise ValueError(f"Split '{split}' not found. Available: {list(self.splits.keys())}")
        return self.splits[split]


def create_dataset_from_full_images(
    images_dir: Path,
    output_pos_dir: Path,
    output_neg_dir: Path,
    cascade_face_path: Path,
    neg_samples_per_image: int = 3,
    roi_size: Tuple[int, int] = (128, 128)
) -> None:
    """
    Create positive and negative ROI dataset from full images.
    
    Uses Haar cascade to detect faces (positive ROIs) and extract
    random non-face regions (negative ROIs).
    
    Args:
        images_dir: Directory with full images
        output_pos_dir: Output directory for positive ROIs
        output_neg_dir: Output directory for negative ROIs
        cascade_face_path: Path to Haar cascade
        neg_samples_per_image: Number of negative samples per image
        roi_size: Size of extracted ROIs
    """
    logger.info(f"Creating dataset from {images_dir}")
    
    ensure_dir(output_pos_dir)
    ensure_dir(output_neg_dir)
    
    # Load cascade
    face_cascade = cv2.CascadeClassifier(str(cascade_face_path))
    if face_cascade.empty():
        raise ValueError(f"Failed to load cascade: {cascade_face_path}")
    
    image_paths = collect_image_paths(images_dir)
    logger.info(f"Found {len(image_paths)} images")
    
    pos_count = 0
    neg_count = 0
    
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Save positive samples (faces)
        for i, (fx, fy, fw, fh) in enumerate(faces):
            face_roi = gray[fy:fy+fh, fx:fx+fw]
            face_resized = cv2.resize(face_roi, roi_size)
            
            output_path = output_pos_dir / f"{img_path.stem}_face_{i}.png"
            cv2.imwrite(str(output_path), face_resized)
            pos_count += 1
        
        # Generate negative samples (non-face regions)
        for i in range(neg_samples_per_image):
            # Random crop
            crop_w, crop_h = roi_size[0] * 2, roi_size[1] * 2  # Larger initial crop
            
            if w < crop_w or h < crop_h:
                continue
            
            max_attempts = 10
            for _ in range(max_attempts):
                x = np.random.randint(0, w - crop_w)
                y = np.random.randint(0, h - crop_h)
                
                # Check if overlaps with any face (IoU threshold)
                crop_box = (x, y, crop_w, crop_h)
                overlaps = any(
                    compute_iou(crop_box, face) > 0.3
                    for face in faces
                )
                
                if not overlaps:
                    # Valid negative sample
                    neg_roi = gray[y:y+crop_h, x:x+crop_w]
                    neg_resized = cv2.resize(neg_roi, roi_size)
                    
                    output_path = output_neg_dir / f"{img_path.stem}_neg_{i}.png"
                    cv2.imwrite(str(output_path), neg_resized)
                    neg_count += 1
                    break
    
    logger.info(f"Created {pos_count} positive and {neg_count} negative samples")
