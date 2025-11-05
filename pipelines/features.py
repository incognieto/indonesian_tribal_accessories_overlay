"""
Feature extraction using ORB and Bag-of-Visual-Words (BoVW).
Implements ORB keypoint detection, descriptor extraction, k-means codebook, and BoVW encoding.
"""

from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import joblib
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from .utils import logger


class ORBFeatureExtractor:
    """ORB-based feature extractor with BoVW encoding."""
    
    def __init__(
        self,
        n_features: int = 500,
        scale_factor: float = 1.2,
        n_levels: int = 8,
        edge_threshold: int = 31,
        first_level: int = 0,
        wta_k: int = 2,
        patch_size: int = 31
    ):
        """
        Initialize ORB feature extractor.
        
        Args:
            n_features: Maximum number of ORB keypoints to detect
            scale_factor: Pyramid decimation ratio
            n_levels: Number of pyramid levels
            edge_threshold: Size of border to ignore
            first_level: Level of pyramid to put source image
            wta_k: Number of points producing each element in descriptor
            patch_size: Size of patch used for descriptor
        """
        self.orb = cv2.ORB_create(
            nfeatures=n_features,
            scaleFactor=scale_factor,
            nlevels=n_levels,
            edgeThreshold=edge_threshold,
            firstLevel=first_level,
            WTA_K=wta_k,
            patchSize=patch_size
        )
        self.n_features = n_features
    
    def extract_keypoints_descriptors(
        self,
        image: np.ndarray
    ) -> Tuple[List, Optional[np.ndarray]]:
        """
        Extract ORB keypoints and descriptors from image.
        
        Args:
            image: Grayscale image
        
        Returns:
            (keypoints, descriptors) tuple
            descriptors is None if no keypoints found
        """
        keypoints, descriptors = self.orb.detectAndCompute(image, None)
        
        if descriptors is None:
            # No keypoints found
            return keypoints, None
        
        return keypoints, descriptors
    
    def extract_descriptors_only(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract only descriptors (skip keypoints)."""
        _, descriptors = self.orb.detectAndCompute(image, None)
        return descriptors


class BoVWEncoder:
    """Bag-of-Visual-Words encoder using k-means clustering."""
    
    def __init__(
        self,
        n_clusters: int = 256,
        random_state: int = 42,
        batch_size: int = 1000,
        max_iter: int = 100
    ):
        """
        Initialize BoVW encoder.
        
        Args:
            n_clusters: Number of visual words (k for k-means)
            random_state: Random seed
            batch_size: Batch size for MiniBatchKMeans
            max_iter: Maximum iterations for k-means
        """
        self.n_clusters = n_clusters
        self.kmeans = MiniBatchKMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            batch_size=batch_size,
            max_iter=max_iter,
            verbose=0
        )
        self.is_fitted = False
    
    def fit(self, descriptors: np.ndarray) -> None:
        """
        Fit k-means codebook on descriptors.
        
        Args:
            descriptors: Array of shape (n_descriptors, descriptor_dim)
        """
        if descriptors.shape[0] == 0:
            raise ValueError("No descriptors provided for fitting")
        
        logger.info(f"Fitting k-means with {descriptors.shape[0]} descriptors...")
        self.kmeans.fit(descriptors)
        self.is_fitted = True
        logger.info(f"Codebook created with {self.n_clusters} visual words")
    
    def transform(self, descriptors: Optional[np.ndarray]) -> np.ndarray:
        """
        Transform descriptors to BoVW histogram.
        
        Args:
            descriptors: Array of shape (n_descriptors, descriptor_dim)
                        Can be None if no keypoints detected
        
        Returns:
            BoVW histogram of shape (n_clusters,)
        """
        if not self.is_fitted:
            raise ValueError("Encoder not fitted. Call fit() first.")
        
        # Handle case where no descriptors extracted
        if descriptors is None or descriptors.shape[0] == 0:
            # Return uniform small histogram as fallback
            return np.ones(self.n_clusters, dtype=np.float32) / self.n_clusters
        
        # Assign descriptors to clusters
        labels = self.kmeans.predict(descriptors)
        
        # Build histogram
        histogram = np.bincount(labels, minlength=self.n_clusters).astype(np.float32)
        
        # L1 normalization
        hist_sum = histogram.sum()
        if hist_sum > 0:
            histogram /= hist_sum
        
        return histogram
    
    def fit_transform(self, descriptors: np.ndarray) -> np.ndarray:
        """Fit codebook and transform descriptors."""
        self.fit(descriptors)
        return self.transform(descriptors)
    
    def save(self, path: Path) -> None:
        """Save codebook to file."""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted encoder")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.kmeans, path)
        logger.info(f"Saved codebook to {path}")
    
    def load(self, path: Path) -> None:
        """Load codebook from file."""
        self.kmeans = joblib.load(path)
        self.n_clusters = self.kmeans.n_clusters
        self.is_fitted = True
        logger.info(f"Loaded codebook from {path}")


class FeaturePipeline:
    """Complete feature extraction pipeline: ORB + BoVW."""
    
    def __init__(
        self,
        orb_n_features: int = 500,
        bovw_n_clusters: int = 256,
        target_size: Tuple[int, int] = (128, 128),
        use_scaler: bool = True
    ):
        """
        Initialize feature pipeline.
        
        Args:
            orb_n_features: Number of ORB keypoints
            bovw_n_clusters: Number of visual words
            target_size: Target image size (width, height)
            use_scaler: Whether to use StandardScaler
        """
        self.orb_extractor = ORBFeatureExtractor(n_features=orb_n_features)
        self.bovw_encoder = BoVWEncoder(n_clusters=bovw_n_clusters)
        self.target_size = target_size
        self.use_scaler = use_scaler
        self.scaler = StandardScaler() if use_scaler else None
        self.scaler_fitted = False
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image: convert to grayscale and resize."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Resize to target size
        if gray.shape[:2] != self.target_size[::-1]:  # (h, w) vs (w, h)
            gray = cv2.resize(gray, self.target_size)
        
        return gray
    
    def extract_features_single(self, image: np.ndarray) -> np.ndarray:
        """
        Extract BoVW features from single image.
        
        Args:
            image: Input image (BGR or grayscale)
        
        Returns:
            BoVW feature vector
        """
        # Preprocess
        gray = self.preprocess_image(image)
        
        # Extract ORB descriptors
        descriptors = self.orb_extractor.extract_descriptors_only(gray)
        
        # Encode to BoVW
        bovw_features = self.bovw_encoder.transform(descriptors)
        
        return bovw_features
    
    def extract_features_batch(
        self,
        images: List[np.ndarray],
        verbose: bool = True
    ) -> np.ndarray:
        """
        Extract BoVW features from batch of images.
        
        Args:
            images: List of images
            verbose: Show progress bar
        
        Returns:
            Feature matrix of shape (n_images, n_clusters)
        """
        features_list = []
        
        iterator = tqdm(images, desc="Extracting features") if verbose else images
        
        for img in iterator:
            features = self.extract_features_single(img)
            features_list.append(features)
        
        return np.array(features_list)
    
    def build_codebook(
        self,
        images: List[np.ndarray],
        max_descriptors: int = 200000,
        verbose: bool = True
    ) -> None:
        """
        Build BoVW codebook from training images.
        
        Args:
            images: List of training images
            max_descriptors: Maximum descriptors to use for k-means
            verbose: Show progress
        """
        logger.info(f"Building codebook from {len(images)} images...")
        
        # Collect descriptors from all images
        all_descriptors = []
        
        iterator = tqdm(images, desc="Collecting descriptors") if verbose else images
        
        for img in iterator:
            gray = self.preprocess_image(img)
            descriptors = self.orb_extractor.extract_descriptors_only(gray)
            
            if descriptors is not None:
                all_descriptors.append(descriptors)
        
        # Concatenate all descriptors
        if not all_descriptors:
            raise ValueError("No descriptors extracted from any image")
        
        all_descriptors = np.vstack(all_descriptors)
        logger.info(f"Collected {all_descriptors.shape[0]} descriptors")
        
        # Subsample if too many
        if all_descriptors.shape[0] > max_descriptors:
            logger.info(f"Subsampling to {max_descriptors} descriptors")
            indices = np.random.choice(
                all_descriptors.shape[0],
                max_descriptors,
                replace=False
            )
            all_descriptors = all_descriptors[indices]
        
        # Fit BoVW encoder
        self.bovw_encoder.fit(all_descriptors)
    
    def fit_scaler(self, features: np.ndarray) -> None:
        """Fit StandardScaler on features."""
        if self.scaler is None:
            return
        
        self.scaler.fit(features)
        self.scaler_fitted = True
        logger.info("Fitted StandardScaler")
    
    def transform_scaler(self, features: np.ndarray) -> np.ndarray:
        """Transform features using fitted scaler."""
        if self.scaler is None:
            return features
        
        if not self.scaler_fitted:
            raise ValueError("Scaler not fitted")
        
        return self.scaler.transform(features)
    
    def save(self, output_dir: Path) -> None:
        """Save pipeline components."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save BoVW encoder
        self.bovw_encoder.save(output_dir / 'codebook.pkl')
        
        # Save scaler if used
        if self.scaler is not None and self.scaler_fitted:
            joblib.dump(self.scaler, output_dir / 'scaler.pkl')
            logger.info(f"Saved scaler to {output_dir / 'scaler.pkl'}")
        
        # Save config
        config = {
            'orb_n_features': self.orb_extractor.n_features,
            'bovw_n_clusters': self.bovw_encoder.n_clusters,
            'target_size': self.target_size,
            'use_scaler': self.use_scaler
        }
        
        import json
        with open(output_dir / 'feature_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved feature pipeline to {output_dir}")
    
    def load(self, input_dir: Path) -> None:
        """Load pipeline components."""
        # Load BoVW encoder
        self.bovw_encoder.load(input_dir / 'codebook.pkl')
        
        # Load scaler if exists
        scaler_path = input_dir / 'scaler.pkl'
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            self.scaler_fitted = True
            logger.info(f"Loaded scaler from {scaler_path}")
        
        # Load config
        config_path = input_dir / 'feature_config.json'
        if config_path.exists():
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update parameters
            self.orb_extractor.n_features = config['orb_n_features']
            self.target_size = tuple(config['target_size'])
            self.use_scaler = config['use_scaler']
        
        logger.info(f"Loaded feature pipeline from {input_dir}")
