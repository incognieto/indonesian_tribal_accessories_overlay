"""
Geometry utilities for pose estimation and landmark heuristics.
Handles ear position estimation, eye angle calculation, and facial landmark positioning.
"""

import math
from typing import List, Optional, Tuple

import cv2
import numpy as np


def compute_eye_angle(
    left_eye: Tuple[int, int, int, int],
    right_eye: Tuple[int, int, int, int]
) -> float:
    """
    Compute rotation angle based on two eyes.
    
    Args:
        left_eye: (x, y, w, h) of left eye
        right_eye: (x, y, w, h) of right eye
    
    Returns:
        Angle in degrees (positive = clockwise tilt)
    """
    # Get centers
    lx, ly, lw, lh = left_eye
    rx, ry, rw, rh = right_eye
    
    left_center = (lx + lw // 2, ly + lh // 2)
    right_center = (rx + rw // 2, ry + rh // 2)
    
    # Compute angle
    dx = right_center[0] - left_center[0]
    dy = right_center[1] - left_center[1]
    
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg


def estimate_ear_positions(
    face_box: Tuple[int, int, int, int],
    eyes: Optional[List[Tuple[int, int, int, int]]] = None
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Estimate left and right ear positions based on face bbox and eyes.
    
    Strategy:
    - Ears are typically at ~±0.45 * face_width from face center
    - Vertical position is between eye level and bottom third of face
    
    Args:
        face_box: (x, y, w, h) of face
        eyes: Optional list of detected eyes for refinement
    
    Returns:
        (left_ear_pos, right_ear_pos) as (x, y) tuples
    """
    fx, fy, fw, fh = face_box
    face_cx = fx + fw // 2
    face_cy = fy + fh // 2
    
    # Default ear positions
    ear_x_offset = int(0.45 * fw)
    ear_y_offset = int(0.65 * fh)  # Lower part of face
    
    # Refine Y position based on eyes if available
    if eyes and len(eyes) >= 1:
        # Use average eye Y position
        avg_eye_y = sum(ey + eh // 2 for ex, ey, ew, eh in eyes) / len(eyes)
        # Place ears slightly below eyes
        ear_y = int(avg_eye_y + 0.3 * fh)
    else:
        ear_y = fy + ear_y_offset
    
    left_ear_pos = (face_cx - ear_x_offset, ear_y)
    right_ear_pos = (face_cx + ear_x_offset, ear_y)
    
    return left_ear_pos, right_ear_pos


def estimate_nose_position(
    face_box: Tuple[int, int, int, int],
    eyes: Optional[List[Tuple[int, int, int, int]]] = None,
    nose_box: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[int, int]:
    """
    Estimate nose tip position for piercing placement.
    
    Args:
        face_box: (x, y, w, h) of face
        eyes: Optional detected eyes for refinement
        nose_box: Optional detected nose box
    
    Returns:
        (x, y) position for nose piercing
    """
    fx, fy, fw, fh = face_box
    face_cx = fx + fw // 2
    
    # If nose detected, use it
    if nose_box:
        nx, ny, nw, nh = nose_box
        return (nx + nw // 2, ny + int(0.7 * nh))
    
    # Otherwise use heuristic: between eyes and mouth
    if eyes and len(eyes) >= 1:
        avg_eye_y = sum(ey + eh // 2 for ex, ey, ew, eh in eyes) / len(eyes)
        nose_y = int(avg_eye_y + 0.35 * fh)
    else:
        nose_y = fy + int(0.58 * fh)
    
    return (face_cx, nose_y)


def estimate_cheek_position(
    face_box: Tuple[int, int, int, int],
    side: str = 'right'
) -> Tuple[int, int]:
    """
    Estimate cheek position for tattoo placement.
    
    Args:
        face_box: (x, y, w, h) of face
        side: 'left' or 'right'
    
    Returns:
        (x, y) position for cheek tattoo
    """
    fx, fy, fw, fh = face_box
    face_cx = fx + fw // 2
    
    # Cheek position: offset from center, lower half of face
    x_offset = int(0.35 * fw)
    y_offset = int(0.65 * fh)
    
    if side == 'left':
        x = face_cx - x_offset
    else:  # right
        x = face_cx + x_offset
    
    y = fy + y_offset
    
    return (x, y)


def rotate_image(
    image: np.ndarray,
    angle: float,
    center: Optional[Tuple[int, int]] = None
) -> np.ndarray:
    """
    Rotate image around center point.
    
    Args:
        image: Input image (can be RGBA)
        angle: Rotation angle in degrees (positive = clockwise)
        center: Rotation center (default: image center)
    
    Returns:
        Rotated image
    """
    h, w = image.shape[:2]
    
    if center is None:
        center = (w // 2, h // 2)
    
    # Get rotation matrix
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)  # Negate for correct direction
    
    # Rotate image
    if image.shape[2] == 4:  # RGBA
        # Rotate BGR and alpha separately, then combine
        bgr = image[:, :, :3]
        alpha = image[:, :, 3]
        
        rotated_bgr = cv2.warpAffine(bgr, M, (w, h), flags=cv2.INTER_LINEAR)
        rotated_alpha = cv2.warpAffine(alpha, M, (w, h), flags=cv2.INTER_LINEAR)
        
        rotated = np.dstack([rotated_bgr, rotated_alpha])
    else:
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR)
    
    return rotated


def resize_image(
    image: np.ndarray,
    scale: float,
    interpolation: int = cv2.INTER_LINEAR
) -> np.ndarray:
    """
    Resize image by scale factor.
    
    Args:
        image: Input image
        scale: Scale factor
        interpolation: OpenCV interpolation method
    
    Returns:
        Resized image
    """
    if scale == 1.0:
        return image
    
    h, w = image.shape[:2]
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    if new_w <= 0 or new_h <= 0:
        raise ValueError(f"Invalid scale {scale} for image size {w}x{h}")
    
    return cv2.resize(image, (new_w, new_h), interpolation=interpolation)


def is_point_in_bounds(
    point: Tuple[int, int],
    img_shape: Tuple[int, int]
) -> bool:
    """
    Check if point is within image bounds.
    
    Args:
        point: (x, y) coordinates
        img_shape: (height, width) of image
    
    Returns:
        True if point is within bounds
    """
    x, y = point
    h, w = img_shape[:2]
    return 0 <= x < w and 0 <= y < h


def clip_bbox_to_bounds(
    bbox: Tuple[int, int, int, int],
    img_shape: Tuple[int, int]
) -> Tuple[int, int, int, int]:
    """
    Clip bounding box to image bounds.
    
    Args:
        bbox: (x, y, w, h)
        img_shape: (height, width) of image
    
    Returns:
        Clipped (x, y, w, h)
    """
    x, y, w, h = bbox
    img_h, img_w = img_shape[:2]
    
    # Clip coordinates
    x = max(0, min(x, img_w - 1))
    y = max(0, min(y, img_h - 1))
    
    # Adjust width and height
    w = min(w, img_w - x)
    h = min(h, img_h - y)
    
    return (x, y, w, h)


def get_bbox_roi(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    clip: bool = True
) -> np.ndarray:
    """
    Extract ROI from image using bounding box.
    
    Args:
        image: Input image
        bbox: (x, y, w, h)
        clip: Whether to clip bbox to image bounds
    
    Returns:
        ROI image
    """
    x, y, w, h = bbox
    
    if clip:
        x, y, w, h = clip_bbox_to_bounds(bbox, image.shape)
    
    if w <= 0 or h <= 0:
        raise ValueError(f"Invalid bbox dimensions: {bbox}")
    
    return image[y:y+h, x:x+w]


def sort_eyes_left_right(
    eyes: List[Tuple[int, int, int, int]]
) -> Tuple[Optional[Tuple], Optional[Tuple]]:
    """
    Sort detected eyes into left and right based on x-coordinate.
    
    Args:
        eyes: List of eye bboxes (x, y, w, h)
    
    Returns:
        (left_eye, right_eye) tuple, either can be None
    """
    if len(eyes) == 0:
        return None, None
    elif len(eyes) == 1:
        # Assume it's one eye, can't determine which
        return eyes[0], None
    else:
        # Sort by x-coordinate
        sorted_eyes = sorted(eyes, key=lambda e: e[0])
        return sorted_eyes[0], sorted_eyes[-1]


def compute_face_orientation(
    face_box: Tuple[int, int, int, int],
    profile_boxes: List[Tuple[int, int, int, int]] = None
) -> str:
    """
    Estimate face orientation (frontal, left_profile, right_profile).
    
    Args:
        face_box: Main face detection (x, y, w, h)
        profile_boxes: Optional profile face detections
    
    Returns:
        'frontal', 'left_profile', or 'right_profile'
    """
    if not profile_boxes:
        return 'frontal'
    
    # If profile detected overlapping with face, determine orientation
    fx, fy, fw, fh = face_box
    face_center_x = fx + fw // 2
    
    for px, py, pw, ph in profile_boxes:
        profile_center_x = px + pw // 2
        
        # Check if profile is within face region
        if abs(profile_center_x - face_center_x) < fw * 0.3:
            # Determine left or right based on relative position
            if profile_center_x < face_center_x:
                return 'left_profile'
            else:
                return 'right_profile'
    
    return 'frontal'


def get_actual_bounds_from_alpha(
    image_rgba: np.ndarray,
    alpha_threshold: int = 10
) -> Tuple[int, int, int, int]:
    """
    Get actual bounding box of non-transparent content in RGBA image.
    
    Args:
        image_rgba: RGBA image with alpha channel
        alpha_threshold: Minimum alpha value to consider as non-transparent
    
    Returns:
        Tuple (x_min, y_min, width, height) of actual content bounds
    """
    if image_rgba.shape[2] != 4:
        # No alpha channel, return full size
        h, w = image_rgba.shape[:2]
        return (0, 0, w, h)
    
    alpha = image_rgba[:, :, 3]
    
    # Find rows and columns with alpha > threshold
    rows = np.any(alpha > alpha_threshold, axis=1)
    cols = np.any(alpha > alpha_threshold, axis=0)
    
    # Check if there's any non-transparent content
    if not np.any(rows) or not np.any(cols):
        h, w = image_rgba.shape[:2]
        return (0, 0, w, h)
    
    y_indices = np.where(rows)[0]
    x_indices = np.where(cols)[0]
    
    y_min, y_max = y_indices[0], y_indices[-1]
    x_min, x_max = x_indices[0], x_indices[-1]
    
    width = x_max - x_min + 1
    height = y_max - y_min + 1
    
    return (x_min, y_min, width, height)


def get_hat_bottom_width(
    hat_img: np.ndarray,
    alpha_threshold: int = 10,
    bottom_ratio: float = 0.1
) -> int:
    """
    Calculate the actual width of the hat at its bottom edge.
    This is crucial for matching the hat width with the forehead width.
    
    Args:
        hat_img: RGBA image of the hat
        alpha_threshold: Minimum alpha value to consider as visible
        bottom_ratio: Ratio of bottom portion to measure (0.1 = bottom 10%)
    
    Returns:
        Width of the hat at bottom edge in pixels
    """
    if hat_img.shape[2] != 4:
        return hat_img.shape[1]
    
    alpha = hat_img[:, :, 3]
    
    # Find the actual content bounds
    rows = np.any(alpha > alpha_threshold, axis=1)
    if not np.any(rows):
        return hat_img.shape[1]
    
    y_indices = np.where(rows)[0]
    y_max = y_indices[-1]
    
    # Measure width at bottom portion
    bottom_height = max(1, int(hat_img.shape[0] * bottom_ratio))
    bottom_start = max(0, y_max - bottom_height)
    
    # Get maximum width in the bottom portion
    max_width = 0
    for y in range(bottom_start, y_max + 1):
        row_alpha = alpha[y, :]
        cols = np.where(row_alpha > alpha_threshold)[0]
        if len(cols) > 0:
            row_width = cols[-1] - cols[0] + 1
            max_width = max(max_width, row_width)
    
    return max_width if max_width > 0 else hat_img.shape[1]
