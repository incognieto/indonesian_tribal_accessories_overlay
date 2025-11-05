"""
Utility functions for the CV Accessory Overlay system.
Handles I/O, timing, logging, visualization, and configuration.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON configuration file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], path: Path) -> None:
    """Save dictionary to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_image(path: Path, grayscale: bool = False) -> np.ndarray:
    """Load image from file."""
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to load image: {path}")
    return img


def load_image_rgba(path: Path) -> np.ndarray:
    """Load image with alpha channel (RGBA)."""
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Failed to load image: {path}")
    
    # Convert to RGBA if needed
    if img.shape[2] == 3:
        # Add full opacity alpha channel
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    elif img.shape[2] == 4:
        # Already RGBA, ensure proper channel order
        pass
    
    return img


def save_image(img: np.ndarray, path: Path) -> None:
    """Save image to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), img)
    logger.info(f"Saved image to {path}")


def collect_image_paths(directory: Path, extensions: List[str] = None) -> List[Path]:
    """Collect all image paths from directory."""
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    paths = []
    for ext in extensions:
        paths.extend(directory.glob(f'*{ext}'))
        paths.extend(directory.glob(f'*{ext.upper()}'))
    
    return sorted(paths)


def visualize_detections(
    img: np.ndarray,
    boxes: List[Tuple[int, int, int, int]],
    labels: Optional[List[str]] = None,
    scores: Optional[List[float]] = None,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """Draw bounding boxes on image."""
    vis_img = img.copy()
    
    for i, (x, y, w, h) in enumerate(boxes):
        cv2.rectangle(vis_img, (x, y), (x + w, y + h), color, thickness)
        
        if labels or scores:
            label_text = ""
            if labels:
                label_text += labels[i]
            if scores:
                label_text += f" {scores[i]:.2f}"
            
            cv2.putText(
                vis_img, label_text, (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
            )
    
    return vis_img


def show_image(img: np.ndarray, title: str = "Image", wait: bool = True) -> None:
    """Display image using OpenCV window."""
    cv2.imshow(title, img)
    if wait:
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def plot_confusion_matrix(cm: np.ndarray, save_path: Optional[Path] = None) -> None:
    """Plot confusion matrix."""
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.colorbar()
    
    # Add text annotations
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"Saved confusion matrix to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_pr_curve(
    precision: np.ndarray,
    recall: np.ndarray,
    ap: float,
    save_path: Optional[Path] = None
) -> None:
    """Plot Precision-Recall curve."""
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, 'b-', linewidth=2, label=f'AP = {ap:.3f}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"Saved PR curve to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_roc_curve(
    fpr: np.ndarray,
    tpr: np.ndarray,
    auc: float,
    save_path: Optional[Path] = None
) -> None:
    """Plot ROC curve."""
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, 'b-', linewidth=2, label=f'AUC = {auc:.3f}')
    plt.plot([0, 1], [0, 1], 'r--', linewidth=1, label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"Saved ROC curve to {save_path}")
    else:
        plt.show()
    
    plt.close()


class Timer:
    """Simple timer context manager."""
    
    def __init__(self, name: str = "Operation", verbose: bool = True):
        self.name = name
        self.verbose = verbose
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.time() - self.start_time
        if self.verbose:
            logger.info(f"{self.name} took {self.elapsed:.3f}s")


def compute_iou(box1: Tuple[int, int, int, int], 
                box2: Tuple[int, int, int, int]) -> float:
    """Compute IoU between two boxes (x, y, w, h)."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    
    # Compute intersection
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    
    # Compute union
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area
    
    if union_area == 0:
        return 0.0
    
    return inter_area / union_area


def nms(
    boxes: List[Tuple[int, int, int, int]],
    scores: List[float],
    iou_threshold: float = 0.3
) -> List[int]:
    """
    Non-Maximum Suppression.
    
    Args:
        boxes: List of boxes (x, y, w, h)
        scores: List of confidence scores
        iou_threshold: IoU threshold for suppression
    
    Returns:
        List of indices to keep
    """
    if len(boxes) == 0:
        return []
    
    # Convert to numpy arrays
    boxes_arr = np.array(boxes)
    scores_arr = np.array(scores)
    
    # Sort by scores (descending)
    indices = np.argsort(scores_arr)[::-1]
    
    keep = []
    while len(indices) > 0:
        # Pick box with highest score
        current = indices[0]
        keep.append(current)
        
        if len(indices) == 1:
            break
        
        # Compute IoU with remaining boxes
        ious = np.array([
            compute_iou(boxes[current], boxes[idx])
            for idx in indices[1:]
        ])
        
        # Keep boxes with IoU below threshold
        indices = indices[1:][ious < iou_threshold]
    
    return keep


def set_seed(seed: int = 42) -> None:
    """Set random seed for reproducibility."""
    np.random.seed(seed)
    logger.info(f"Set random seed to {seed}")


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path
