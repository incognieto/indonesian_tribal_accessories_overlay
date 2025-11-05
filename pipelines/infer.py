"""
Inference pipeline for face detection and accessory overlay.
Combines Haar cascades, ORB+BoVW+SVM validation, NMS, and overlay placement.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from .features import FeaturePipeline
from .geometry import compute_eye_angle, sort_eyes_left_right
from .overlay import AccessoryOverlay
from .train import SVMTrainer
from .utils import logger, nms


class FaceDetector:
    """Hybrid Haar + SVM face detector."""
    
    def __init__(
        self,
        cascade_dir: Path,
        feature_pipeline: FeaturePipeline,
        svm_trainer: SVMTrainer,
        config: Optional[Dict] = None
    ):
        """
        Initialize face detector.
        
        Args:
            cascade_dir: Directory containing Haar cascade XML files
            feature_pipeline: Trained feature extraction pipeline
            svm_trainer: Trained SVM classifier
            config: Configuration dict for Haar parameters
        """
        self.cascade_dir = Path(cascade_dir)
        self.feature_pipeline = feature_pipeline
        self.svm_trainer = svm_trainer
        self.config = config or {}
        
        # Load Haar cascades
        self._load_cascades()
    
    def _load_cascades(self) -> None:
        """Load all available Haar cascades."""
        self.cascades = {}
        
        cascade_files = {
            #'face_default': 'bad_face_cascade.xml', # Example of a bad cascade for testing
            'face_default': 'my_custom_face_cascade.xml',  # Custom trained cascade (mengganti haarcascade_frontalface_default.xml)
            # 'face_default': 'haarcascade_frontalface_default.xml', # Original cascade
            'face_alt': 'haarcascade_frontalface_alt.xml',
            'face_alt2': 'haarcascade_frontalface_alt2.xml',
            'face_alt_tree': 'haarcascade_frontalface_alt_tree.xml',
            'profile': 'haarcascade_profileface.xml',
            'eye': 'haarcascade_eye.xml',
            'eye_glass': 'haarcascade_eye_tree_eyeglasses.xml',
            'nose': 'haarcascade_mcs_nose.xml',
            'mouth': 'haarcascade_mcs_mouth.xml',
            'smile': 'haarcascade_smile.xml',
        }
        
        for name, filename in cascade_files.items():
            path = self.cascade_dir / filename
            if path.exists():
                cascade = cv2.CascadeClassifier(str(path))
                if not cascade.empty():
                    self.cascades[name] = cascade
                    logger.info(f"Loaded cascade: {name}")
                else:
                    logger.warning(f"Failed to load cascade: {path}")
            else:
                logger.debug(f"Cascade not found: {path}")
        
        if not self.cascades:
            raise ValueError(f"No Haar cascades loaded from {self.cascade_dir}")
    
    def detect_faces_haar(
        self,
        image: np.ndarray,
        cascade_name: str = 'face_default'
    ) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using Haar cascade.
        
        Args:
            image: Grayscale image
            cascade_name: Name of cascade to use
        
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        if cascade_name not in self.cascades:
            logger.warning(f"Cascade '{cascade_name}' not available, using default")
            cascade_name = 'face_default'
        
        cascade = self.cascades[cascade_name]
        
        # Get parameters from config
        haar_config = self.config.get('haar', {}).get('face', {})
        scale_factor = haar_config.get('scaleFactor', 1.1)
        min_neighbors = haar_config.get('minNeighbors', 5)
        min_size = tuple(haar_config.get('minSize', [30, 30]))
        
        faces = cascade.detectMultiScale(
            image,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size
        )
        
        return [tuple(f) for f in faces]
    
    def detect_features(
        self,
        image: np.ndarray,
        face_box: Tuple[int, int, int, int]
    ) -> Dict[str, List]:
        """
        Detect facial features (eyes, nose) within face region.
        
        Args:
            image: Grayscale image
            face_box: Face bounding box (x, y, w, h)
        
        Returns:
            Dict with 'eyes', 'nose', 'mouth' detections
        """
        fx, fy, fw, fh = face_box
        face_roi = image[fy:fy+fh, fx:fx+fw]
        
        features = {
            'eyes': [],
            'nose': [],
            'mouth': []
        }
        
        # Detect eyes
        if 'eye' in self.cascades:
            eye_config = self.config.get('haar', {}).get('eye', {})
            eyes = self.cascades['eye'].detectMultiScale(
                face_roi,
                scaleFactor=eye_config.get('scaleFactor', 1.05),
                minNeighbors=eye_config.get('minNeighbors', 6),
                minSize=tuple(eye_config.get('minSize', [20, 20]))
            )
            # Convert to global coordinates
            features['eyes'] = [(fx + ex, fy + ey, ew, eh) for ex, ey, ew, eh in eyes]
        
        # Detect nose
        if 'nose' in self.cascades:
            nose_config = self.config.get('haar', {}).get('nose', {})
            noses = self.cascades['nose'].detectMultiScale(
                face_roi,
                scaleFactor=nose_config.get('scaleFactor', 1.1),
                minNeighbors=nose_config.get('minNeighbors', 4),
                minSize=tuple(nose_config.get('minSize', [15, 15]))
            )
            features['nose'] = [(fx + nx, fy + ny, nw, nh) for nx, ny, nw, nh in noses]
        
        # Detect mouth
        if 'mouth' in self.cascades:
            mouths = self.cascades['mouth'].detectMultiScale(
                face_roi,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(20, 20)
            )
            features['mouth'] = [(fx + mx, fy + my, mw, mh) for mx, my, mw, mh in mouths]
        
        return features
    
    def validate_face_svm(
        self,
        image: np.ndarray,
        face_box: Tuple[int, int, int, int]
    ) -> Tuple[bool, float]:
        """
        Validate face detection using SVM.
        
        Args:
            image: Input image (BGR or grayscale)
            face_box: Face bounding box (x, y, w, h)
        
        Returns:
            (is_valid, confidence_score) tuple
        """
        x, y, w, h = face_box
        
        # Extract ROI
        if len(image.shape) == 3:
            roi = image[y:y+h, x:x+w]
        else:
            roi = image[y:y+h, x:x+w]
        
        # Extract features
        features = self.feature_pipeline.extract_features_single(roi)
        features = self.feature_pipeline.transform_scaler(features.reshape(1, -1))
        
        # Predict
        prediction = self.svm_trainer.predict(features)[0]
        score = self.svm_trainer.decision_function(features)[0]
        
        return bool(prediction == 1), float(score)
    
    def detect(
        self,
        image: np.ndarray,
        use_svm: bool = True,
        svm_threshold: float = 0.0,
        use_nms: bool = True,
        nms_threshold: float = 0.3
    ) -> Tuple[List[Tuple[int, int, int, int]], List[float], List[Dict]]:
        """
        Detect faces in image with optional SVM validation.
        
        Args:
            image: Input image (BGR)
            use_svm: Whether to validate with SVM
            svm_threshold: Decision function threshold for SVM
            use_nms: Whether to apply NMS
            nms_threshold: IoU threshold for NMS
        
        Returns:
            (faces, scores, features_list) tuple
            - faces: List of bounding boxes
            - scores: List of confidence scores
            - features_list: List of detected features per face
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect with multiple Haar cascades
        all_faces = []
        
        for cascade_name in ['face_default', 'face_alt', 'face_alt2', 'face_alt_tree']:
            if cascade_name in self.cascades:
                faces = self.detect_faces_haar(gray, cascade_name)
                all_faces.extend(faces)
        
        if not all_faces:
            return [], [], []
        
        # Validate with SVM if enabled
        if use_svm:
            validated_faces = []
            validated_scores = []
            
            for face in all_faces:
                is_valid, score = self.validate_face_svm(image, face)
                if is_valid and score >= svm_threshold:
                    validated_faces.append(face)
                    validated_scores.append(score)
            
            all_faces = validated_faces
            scores = validated_scores
        else:
            # Use face size as score
            scores = [w * h for x, y, w, h in all_faces]
        
        if not all_faces:
            return [], [], []
        
        # Apply NMS
        if use_nms:
            keep_indices = nms(all_faces, scores, iou_threshold=nms_threshold)
            all_faces = [all_faces[i] for i in keep_indices]
            scores = [scores[i] for i in keep_indices]
        
        # Detect features for each face
        features_list = []
        for face in all_faces:
            features = self.detect_features(gray, face)
            features_list.append(features)
        
        return all_faces, scores, features_list


class InferencePipeline:
    """Complete inference pipeline with accessory overlay."""
    
    def __init__(
        self,
        detector: FaceDetector,
        overlay_system: AccessoryOverlay,
        accessories: Dict[str, np.ndarray]
    ):
        """
        Initialize inference pipeline.
        
        Args:
            detector: Face detector
            overlay_system: Accessory overlay system
            accessories: Dict of loaded accessory images
        """
        self.detector = detector
        self.overlay_system = overlay_system
        self.accessories = accessories
    
    def process_image(
        self,
        image: np.ndarray,
        enabled_accessories: List[str] = None,
        use_svm: bool = True,
        visualize_boxes: bool = False
    ) -> np.ndarray:
        """
        Process single image: detect faces and overlay accessories.
        
        Args:
            image: Input image (BGR)
            enabled_accessories: List of enabled accessory types
            use_svm: Whether to validate with SVM
            visualize_boxes: Whether to draw detection boxes
        
        Returns:
            Processed image with overlays
        """
        result = image.copy()
        
        # Detect faces
        faces, scores, features_list = self.detector.detect(
            image,
            use_svm=use_svm
        )
        
        logger.debug(f"Detected {len(faces)} faces")
        
        # Process each face
        for i, (face, features) in enumerate(zip(faces, features_list)):
            # Compute rotation angle from eyes
            rotation_angle = 0.0
            eyes = features.get('eyes', [])
            
            if len(eyes) >= 2:
                left_eye, right_eye = sort_eyes_left_right(eyes)
                if left_eye and right_eye:
                    rotation_angle = compute_eye_angle(left_eye, right_eye)
            
            # Overlay accessories
            result = self.overlay_system.overlay_all(
                result,
                face,
                self.accessories,
                eyes=eyes,
                nose_box=features.get('nose', [None])[0] if features.get('nose') else None,
                rotation_angle=rotation_angle,
                enabled=enabled_accessories
            )
            
            # Visualize detection box if requested
            if visualize_boxes:
                fx, fy, fw, fh = face
                cv2.rectangle(result, (fx, fy), (fx + fw, fy + fh), (0, 255, 0), 2)
                cv2.putText(
                    result, f"Face {i+1}",
                    (fx, fy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
                )
        
        return result
    
    def process_video(
        self,
        input_path: Path,
        output_path: Path,
        enabled_accessories: List[str] = None,
        use_svm: bool = True,
        max_frames: Optional[int] = None
    ) -> None:
        """
        Process video file.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            enabled_accessories: List of enabled accessory types
            use_svm: Whether to validate with SVM
            max_frames: Maximum frames to process (for testing)
        """
        logger.info(f"Processing video: {input_path}")
        
        # Open video
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {input_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if max_frames:
            total_frames = min(total_frames, max_frames)
        
        logger.info(f"Video: {width}x{height} @ {fps} FPS, {total_frames} frames")
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret or (max_frames and frame_count >= max_frames):
                break
            
            # Process frame
            processed = self.process_image(frame, enabled_accessories, use_svm)
            
            # Write frame
            out.write(processed)
            
            frame_count += 1
            if frame_count % 30 == 0:
                logger.info(f"Processed {frame_count}/{total_frames} frames")
        
        # Release resources
        cap.release()
        out.release()
        
        logger.info(f"Saved processed video to {output_path}")
    
    def process_webcam(
        self,
        camera_id: int = 0,
        enabled_accessories: List[str] = None,
        use_svm: bool = True,
        show_fps: bool = True,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
        mirror: bool = True
    ) -> None:
        """
        Process webcam feed in real-time.
        
        Args:
            camera_id: Camera device ID
            enabled_accessories: List of enabled accessory types
            use_svm: Whether to validate with SVM
            show_fps: Whether to display FPS
            width: Camera frame width (lower = faster, e.g., 320, 640, 1280)
            height: Camera frame height (lower = faster, e.g., 240, 480, 720)
            fps: Target FPS (camera-dependent)
            mirror: Flip frame horizontally (mirror mode, default True)
        """
        logger.info(f"Opening webcam (camera {camera_id})...")
        
        # Open webcam
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            raise ValueError(f"Failed to open camera {camera_id}")
        
        # Set resolution and FPS
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        
        # Get actual settings (camera may not support requested values)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        logger.info(f"Camera resolution: {actual_width}x{actual_height} @ {actual_fps} FPS")
        logger.info(f"Using SVM: {use_svm}")
        if not use_svm:
            logger.info("TIP: Haar-only mode for maximum FPS!")
        
        # FPS tracking
        import time
        prev_time = time.time()
        
        # Current enabled accessories (can be toggled)
        current_enabled = enabled_accessories.copy() if enabled_accessories else ['hat', 'ear', 'piercing', 'tattoo']
        
        logger.info("Press 'q' to quit, 'h' to toggle hat, 'e' to toggle earrings, 'p' to toggle piercing, 't' to toggle tattoo")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Mirror/flip frame horizontally if enabled
            if mirror:
                frame = cv2.flip(frame, 1)
            
            # Process frame
            processed = self.process_image(frame, current_enabled, use_svm)
            
            # Calculate FPS
            if show_fps:
                curr_time = time.time()
                fps = 1 / (curr_time - prev_time)
                prev_time = curr_time
                
                cv2.putText(
                    processed, f"FPS: {fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
                )
            
            # Show enabled accessories
            status_text = f"Enabled: {', '.join(current_enabled)}"
            cv2.putText(
                processed, status_text,
                (10, processed.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
            
            # Display
            cv2.imshow('CV Accessory Overlay', processed)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('h'):
                if 'hat' in current_enabled:
                    current_enabled.remove('hat')
                else:
                    current_enabled.append('hat')
                logger.info(f"Toggled hat: {'ON' if 'hat' in current_enabled else 'OFF'}")
            elif key == ord('e'):
                if 'ear' in current_enabled:
                    current_enabled.remove('ear')
                else:
                    current_enabled.append('ear')
                logger.info(f"Toggled earrings: {'ON' if 'ear' in current_enabled else 'OFF'}")
            elif key == ord('p'):
                if 'piercing' in current_enabled:
                    current_enabled.remove('piercing')
                else:
                    current_enabled.append('piercing')
                logger.info(f"Toggled piercing: {'ON' if 'piercing' in current_enabled else 'OFF'}")
            elif key == ord('t'):
                if 'tattoo' in current_enabled:
                    current_enabled.remove('tattoo')
                else:
                    current_enabled.append('tattoo')
                logger.info(f"Toggled tattoo: {'ON' if 'tattoo' in current_enabled else 'OFF'}")
        
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        
        logger.info("Webcam processing stopped")
