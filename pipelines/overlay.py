"""
Overlay system for placing accessories on detected faces.
Handles alpha blending and proper positioning of hat, earrings, piercing, and tattoo.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

import cv2
import numpy as np

from .geometry import (
    rotate_image, resize_image, clip_bbox_to_bounds,
    estimate_ear_positions, estimate_nose_position, estimate_cheek_position,
    get_hat_bottom_width, get_actual_bounds_from_alpha
)
from .utils import logger, load_json, load_image_rgba


class AccessoryOverlay:
    """Manages accessory overlays on face images."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize accessory overlay system.
        
        Args:
            config_path: Path to overlay configuration JSON
        """
        if config_path and config_path.exists():
            self.config = load_json(config_path)
        else:
            # Default configuration
            self.config = self._default_config()
        
        # Cache for loaded accessories
        self.accessories_cache = {}
    
    @staticmethod
    def _default_config() -> Dict:
        """Return default overlay configuration."""
        return {
            "hat": {
                "scale_factor": 1.2,
                "y_offset_factor": -0.25,
                "rotation_enabled": True,
                "anchor": "bottom_center"
            },
            "earring_left": {
                "x_offset_factor": -0.45,
                "y_offset_factor": 0.65,
                "scale_factor": 0.15,
                "anchor": "top_center"
            },
            "earring_right": {
                "x_offset_factor": 0.45,
                "y_offset_factor": 0.65,
                "scale_factor": 0.15,
                "anchor": "top_center"
            },
            "piercing_nose": {
                "x_offset_factor": 0.05,
                "y_offset_factor": 0.58,
                "scale_factor": 0.08,
                "anchor": "center"
            },
            "tattoo_face": {
                "x_offset_factor": 0.35,
                "y_offset_factor": 0.65,
                "scale_factor": 0.2,
                "opacity": 0.8,
                "anchor": "center"
            }
        }
    
    def load_accessory(
        self,
        accessory_type: str,
        path: Path
    ) -> np.ndarray:
        """
        Load accessory image (RGBA).
        
        Args:
            accessory_type: Type of accessory (e.g., 'hat', 'earring_left')
            path: Path to PNG file with alpha channel
        
        Returns:
            RGBA image
        """
        if accessory_type in self.accessories_cache:
            return self.accessories_cache[accessory_type]
        
        img = load_image_rgba(path)
        self.accessories_cache[accessory_type] = img
        logger.info(f"Loaded {accessory_type} from {path}")
        
        return img
    
    def alpha_blend(
        self,
        background: np.ndarray,
        overlay: np.ndarray,
        position: Tuple[int, int],
        anchor: str = 'center',
        opacity: float = 1.0
    ) -> np.ndarray:
        """
        Blend overlay onto background using alpha channel.
        
        Args:
            background: Background image (BGR)
            overlay: Overlay image (BGRA)
            position: (x, y) position for overlay
            anchor: 'center', 'top_center', 'bottom_center'
            opacity: Opacity multiplier (0.0 to 1.0)
        
        Returns:
            Blended image
        """
        result = background.copy()
        
        # Ensure overlay has alpha channel
        if overlay.shape[2] != 4:
            logger.warning("Overlay missing alpha channel, adding full opacity")
            overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2BGRA)
        
        # Extract dimensions
        bg_h, bg_w = background.shape[:2]
        ov_h, ov_w = overlay.shape[:2]
        
        # Compute top-left position based on anchor
        x, y = position
        
        if anchor == 'center':
            x_tl = x - ov_w // 2
            y_tl = y - ov_h // 2
        elif anchor == 'top_center':
            x_tl = x - ov_w // 2
            y_tl = y
        elif anchor == 'bottom_center':
            x_tl = x - ov_w // 2
            y_tl = y - ov_h
        else:
            # Default to top-left
            x_tl = x
            y_tl = y
        
        # Compute overlay region in background
        x1_bg = max(0, x_tl)
        y1_bg = max(0, y_tl)
        x2_bg = min(bg_w, x_tl + ov_w)
        y2_bg = min(bg_h, y_tl + ov_h)
        
        # Check if overlay is completely outside bounds
        if x2_bg <= x1_bg or y2_bg <= y1_bg:
            logger.debug("Overlay completely out of bounds, skipping")
            return result
        
        # Compute corresponding region in overlay
        x1_ov = x1_bg - x_tl
        y1_ov = y1_bg - y_tl
        x2_ov = x1_ov + (x2_bg - x1_bg)
        y2_ov = y1_ov + (y2_bg - y1_bg)
        
        # Extract regions
        bg_region = result[y1_bg:y2_bg, x1_bg:x2_bg]
        ov_region = overlay[y1_ov:y2_ov, x1_ov:x2_ov]
        
        # Extract alpha channel and apply opacity
        alpha = ov_region[:, :, 3].astype(float) / 255.0 * opacity
        alpha = alpha[:, :, np.newaxis]
        
        # Extract BGR channels
        ov_bgr = ov_region[:, :, :3]
        
        # Blend
        blended = (alpha * ov_bgr + (1 - alpha) * bg_region).astype(np.uint8)
        
        # Place back into result
        result[y1_bg:y2_bg, x1_bg:x2_bg] = blended
        
        return result
    
    def overlay_hat(
        self,
        image: np.ndarray,
        face_box: Tuple[int, int, int, int],
        hat_img: np.ndarray,
        eyes: Optional[list] = None,
        rotation_angle: float = 0.0
    ) -> np.ndarray:
        """
        Overlay hat on face.
        
        Args:
            image: Background image
            face_box: Face bounding box (x, y, w, h)
            hat_img: Hat image (RGBA)
            eyes: List of detected eyes for rotation
            rotation_angle: Manual rotation angle (degrees)
        
        Returns:
            Image with hat overlay
        """
        fx, fy, fw, fh = face_box
        config = self.config.get('hat', {})
        
        # Get the actual width of the hat at its bottom edge
        # This is where the hat should match the forehead width
        hat_bottom_width_px = get_hat_bottom_width(hat_img)
        
        # Compute target hat width based on face width
        scale_factor = config.get('scale_factor', 1.2)
        target_hat_bottom_width = int(fw * scale_factor)
        
        # Calculate resize ratio based on matching bottom widths
        # Instead of using canvas width, we use actual hat bottom width
        resize_ratio = target_hat_bottom_width / hat_bottom_width_px
        
        # Resize hat proportionally based on bottom width matching
        hat_width = int(hat_img.shape[1] * resize_ratio)
        hat_height = int(hat_img.shape[0] * resize_ratio)
        hat_resized = cv2.resize(hat_img, (hat_width, hat_height))
        
        # Rotate if enabled
        if config.get('rotation_enabled', True) and rotation_angle != 0:
            hat_resized = rotate_image(hat_resized, rotation_angle)
        
        # Compute position
        y_offset_factor = config.get('y_offset_factor', -0.25)
        face_cx = fx + fw // 2
        hat_y = fy + int(fh * y_offset_factor)
        
        position = (face_cx, hat_y)
        anchor = config.get('anchor', 'bottom_center')
        
        # Blend
        result = self.alpha_blend(image, hat_resized, position, anchor=anchor)
        
        return result
    
    def overlay_earrings(
        self,
        image: np.ndarray,
        face_box: Tuple[int, int, int, int],
        earring_left_img: Optional[np.ndarray] = None,
        earring_right_img: Optional[np.ndarray] = None,
        eyes: Optional[list] = None
    ) -> np.ndarray:
        """
        Overlay earrings on face.
        
        Args:
            image: Background image
            face_box: Face bounding box
            earring_left_img: Left earring image (RGBA)
            earring_right_img: Right earring image (RGBA)
            eyes: List of detected eyes for refinement
        
        Returns:
            Image with earring overlays
        """
        result = image.copy()
        
        # Estimate ear positions
        left_ear_pos, right_ear_pos = estimate_ear_positions(face_box, eyes)
        
        # Overlay left earring
        if earring_left_img is not None:
            config = self.config.get('earring_left', {})
            scale_factor = config.get('scale_factor', 0.15)
            
            # Resize earring
            fx, fy, fw, fh = face_box
            earring_size = int(fw * scale_factor)
            aspect_ratio = earring_left_img.shape[0] / earring_left_img.shape[1]
            earring_h = int(earring_size * aspect_ratio)
            
            earring_resized = cv2.resize(earring_left_img, (earring_size, earring_h))
            
            anchor = config.get('anchor', 'top_center')
            result = self.alpha_blend(result, earring_resized, left_ear_pos, anchor=anchor)
        
        # Overlay right earring
        if earring_right_img is not None:
            config = self.config.get('earring_right', {})
            scale_factor = config.get('scale_factor', 0.15)
            
            fx, fy, fw, fh = face_box
            earring_size = int(fw * scale_factor)
            aspect_ratio = earring_right_img.shape[0] / earring_right_img.shape[1]
            earring_h = int(earring_size * aspect_ratio)
            
            earring_resized = cv2.resize(earring_right_img, (earring_size, earring_h))
            
            anchor = config.get('anchor', 'top_center')
            result = self.alpha_blend(result, earring_resized, right_ear_pos, anchor=anchor)
        
        return result
    
    def overlay_nose_piercing(
        self,
        image: np.ndarray,
        face_box: Tuple[int, int, int, int],
        piercing_img: np.ndarray,
        eyes: Optional[list] = None,
        nose_box: Optional[Tuple[int, int, int, int]] = None
    ) -> np.ndarray:
        """
        Overlay nose piercing on face.
        
        Args:
            image: Background image
            face_box: Face bounding box
            piercing_img: Piercing image (RGBA)
            eyes: List of detected eyes
            nose_box: Optional detected nose box
        
        Returns:
            Image with piercing overlay
        """
        config = self.config.get('piercing_nose', {})
        
        # Estimate nose position
        nose_pos = estimate_nose_position(face_box, eyes, nose_box)
        
        # Resize piercing
        fx, fy, fw, fh = face_box
        scale_factor = config.get('scale_factor', 0.08)
        piercing_size = int(fw * scale_factor)
        
        piercing_resized = cv2.resize(piercing_img, (piercing_size, piercing_size))
        
        # Blend
        anchor = config.get('anchor', 'center')
        result = self.alpha_blend(image, piercing_resized, nose_pos, anchor=anchor)
        
        return result
    
    def overlay_face_tattoo(
        self,
        image: np.ndarray,
        face_box: Tuple[int, int, int, int],
        tattoo_img: np.ndarray,
        side: str = 'right'
    ) -> np.ndarray:
        """
        Overlay face tattoo (e.g., on cheek).
        
        Args:
            image: Background image
            face_box: Face bounding box
            tattoo_img: Tattoo image (RGBA)
            side: 'left' or 'right' cheek
        
        Returns:
            Image with tattoo overlay
        """
        config = self.config.get('tattoo_face', {})
        
        # Estimate cheek position
        tattoo_pos = estimate_cheek_position(face_box, side)
        
        # Resize tattoo
        fx, fy, fw, fh = face_box
        scale_factor = config.get('scale_factor', 0.2)
        tattoo_size = int(fw * scale_factor)
        
        aspect_ratio = tattoo_img.shape[0] / tattoo_img.shape[1]
        tattoo_h = int(tattoo_size * aspect_ratio)
        
        tattoo_resized = cv2.resize(tattoo_img, (tattoo_size, tattoo_h))
        
        # Blend with opacity
        anchor = config.get('anchor', 'center')
        opacity = config.get('opacity', 0.8)
        result = self.alpha_blend(image, tattoo_resized, tattoo_pos, anchor=anchor, opacity=opacity)
        
        return result
    
    def overlay_all(
        self,
        image: np.ndarray,
        face_box: Tuple[int, int, int, int],
        accessories: Dict[str, np.ndarray],
        eyes: Optional[list] = None,
        nose_box: Optional[Tuple[int, int, int, int]] = None,
        rotation_angle: float = 0.0,
        enabled: list = None
    ) -> np.ndarray:
        """
        Overlay all accessories on face.
        
        Args:
            image: Background image
            face_box: Face bounding box
            accessories: Dict mapping accessory type to image
            eyes: Detected eyes
            nose_box: Detected nose box
            rotation_angle: Face rotation angle
            enabled: List of enabled accessory types
        
        Returns:
            Image with all overlays
        """
        result = image.copy()
        
        if enabled is None:
            enabled = list(accessories.keys())
        
        # Overlay in order: tattoo, piercing, earrings, hat
        # (back to front)
        
        # 1. Face tattoo
        if 'tattoo_face' in accessories and 'tattoo' in enabled:
            result = self.overlay_face_tattoo(
                result, face_box, accessories['tattoo_face']
            )
        
        # 2. Nose piercing
        if 'piercing_nose' in accessories and 'piercing' in enabled:
            result = self.overlay_nose_piercing(
                result, face_box, accessories['piercing_nose'],
                eyes=eyes, nose_box=nose_box
            )
        
        # 3. Earrings
        if 'ear' in enabled:
            earring_left = accessories.get('earring_left')
            earring_right = accessories.get('earring_right')
            
            result = self.overlay_earrings(
                result, face_box,
                earring_left_img=earring_left,
                earring_right_img=earring_right,
                eyes=eyes
            )
        
        # 4. Hat
        if 'hat' in accessories and 'hat' in enabled:
            result = self.overlay_hat(
                result, face_box, accessories['hat'],
                eyes=eyes, rotation_angle=rotation_angle
            )
        
        return result


def create_sample_accessories(output_dir: Path) -> None:
    """
    Create sample accessory PNG files with transparency.
    
    Args:
        output_dir: Output directory for accessory images
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Hat (simple triangle/trapezoid)
    hat = np.zeros((200, 300, 4), dtype=np.uint8)
    # Draw filled polygon for hat
    pts = np.array([[150, 20], [50, 100], [250, 100], [150, 20]], np.int32)
    cv2.fillPoly(hat, [pts], (50, 50, 200, 255))  # Red hat
    # Brim
    cv2.rectangle(hat, (30, 100), (270, 130), (40, 40, 180, 255), -1)
    cv2.imwrite(str(output_dir / 'hat.png'), hat)
    
    # Earring (simple circle/loop)
    earring = np.zeros((100, 60, 4), dtype=np.uint8)
    cv2.circle(earring, (30, 50), 20, (0, 215, 255, 255), 3)  # Gold color
    cv2.circle(earring, (30, 20), 5, (0, 215, 255, 255), -1)  # Hook
    cv2.imwrite(str(output_dir / 'earring_left.png'), earring)
    cv2.imwrite(str(output_dir / 'earring_right.png'), earring)
    
    # Nose piercing (small stud)
    piercing = np.zeros((40, 40, 4), dtype=np.uint8)
    cv2.circle(piercing, (20, 20), 8, (192, 192, 192, 255), -1)  # Silver
    cv2.circle(piercing, (20, 20), 4, (255, 255, 255, 255), -1)  # Highlight
    cv2.imwrite(str(output_dir / 'piercing_nose.png'), piercing)
    
    # Face tattoo (simple pattern)
    tattoo = np.zeros((80, 80, 4), dtype=np.uint8)
    # Draw decorative pattern
    cv2.circle(tattoo, (40, 40), 30, (0, 0, 0, 200), 2)
    cv2.circle(tattoo, (40, 40), 20, (0, 0, 0, 180), 2)
    cv2.line(tattoo, (40, 10), (40, 70), (0, 0, 0, 180), 2)
    cv2.imwrite(str(output_dir / 'tattoo_face.png'), tattoo)
    
    # Skin tattoo (larger pattern)
    tattoo_skin = np.zeros((150, 150, 4), dtype=np.uint8)
    cv2.putText(tattoo_skin, "CV", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0, 180), 5)
    cv2.imwrite(str(output_dir / 'tattoo_skin.png'), tattoo_skin)
    
    logger.info(f"Created sample accessories in {output_dir}")
