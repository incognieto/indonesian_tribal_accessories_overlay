"""
SVM training pipeline with hyperparameter tuning and evaluation.
Supports LinearSVC and RBF SVM with cross-validation and comprehensive metrics.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, average_precision_score,
    precision_recall_curve, roc_curve
)
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVC, SVC
from tqdm import tqdm

from .dataset import DatasetManager
from .features import FeaturePipeline
from .utils import logger, plot_confusion_matrix, plot_pr_curve, plot_roc_curve


class SVMTrainer:
    """SVM trainer with hyperparameter tuning."""
    
    def __init__(
        self,
        svm_type: str = 'linear',
        random_state: int = 42,
        n_jobs: int = -1
    ):
        """
        Initialize SVM trainer.
        
        Args:
            svm_type: 'linear' or 'rbf'
            random_state: Random seed
            n_jobs: Number of parallel jobs (-1 = all cores)
        """
        self.svm_type = svm_type
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.model = None
        self.best_params = None
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        param_grid: Dict[str, List[Any]] = None,
        cv: int = 5,
        verbose: bool = True
    ) -> None:
        """
        Train SVM with hyperparameter search.
        
        Args:
            X_train: Training features
            y_train: Training labels
            param_grid: Hyperparameter grid for search
            cv: Number of CV folds
            verbose: Show progress
        """
        logger.info(f"Training {self.svm_type.upper()} SVM...")
        logger.info(f"Training set: {X_train.shape[0]} samples, {X_train.shape[1]} features")
        
        # Create base model
        if self.svm_type == 'linear':
            base_model = LinearSVC(
                random_state=self.random_state,
                max_iter=2000,
                dual=False  # Recommended when n_samples > n_features
            )
            
            # Default param grid for LinearSVC
            if param_grid is None:
                param_grid = {
                    'C': [0.01, 0.1, 1.0, 10.0, 100.0]
                }
        
        elif self.svm_type == 'rbf':
            base_model = SVC(
                kernel='rbf',
                random_state=self.random_state,
                probability=True,  # Enable probability estimates
                cache_size=500
            )
            
            # Default param grid for RBF SVM
            if param_grid is None:
                param_grid = {
                    'C': [0.1, 1.0, 10.0, 100.0],
                    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1]
                }
        
        else:
            raise ValueError(f"Unknown SVM type: {self.svm_type}")
        
        # Grid search with cross-validation
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=cv,
            scoring='f1',
            n_jobs=self.n_jobs,
            verbose=2 if verbose else 0
        )
        
        grid_search.fit(X_train, y_train)
        
        # Store best model and parameters
        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        
        logger.info(f"Best parameters: {self.best_params}")
        logger.info(f"Best CV F1 score: {grid_search.best_score_:.4f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        if self.model is None:
            raise ValueError("Model not trained")
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.
        
        For LinearSVC, use decision_function as proxy.
        For SVC with probability=True, use predict_proba.
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        if hasattr(self.model, 'predict_proba'):
            # SVC with probability
            proba = self.model.predict_proba(X)
            return proba[:, 1]  # Probability of positive class
        else:
            # LinearSVC: use decision function
            scores = self.model.decision_function(X)
            # Normalize to [0, 1] range (sigmoid-like)
            from scipy.special import expit
            return expit(scores)
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Get decision function scores."""
        if self.model is None:
            raise ValueError("Model not trained")
        return self.model.decision_function(X)
    
    def save(self, path: Path) -> None:
        """Save trained model."""
        if self.model is None:
            raise ValueError("No model to save")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"Saved model to {path}")
        
        # Save metadata
        meta_path = path.parent / f"{path.stem}_meta.json"
        meta = {
            'svm_type': self.svm_type,
            'best_params': self.best_params
        }
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
    
    def load(self, path: Path) -> None:
        """Load trained model."""
        self.model = joblib.load(path)
        logger.info(f"Loaded model from {path}")
        
        # Load metadata if exists
        meta_path = path.parent / f"{path.stem}_meta.json"
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            self.svm_type = meta.get('svm_type', 'linear')
            self.best_params = meta.get('best_params', {})


class Evaluator:
    """Model evaluation with comprehensive metrics."""
    
    def __init__(self, trainer: SVMTrainer):
        """
        Initialize evaluator.
        
        Args:
            trainer: Trained SVM trainer
        """
        self.trainer = trainer
        self.metrics = {}
    
    def evaluate(
        self,
        X: np.ndarray,
        y_true: np.ndarray,
        split_name: str = 'test'
    ) -> Dict[str, float]:
        """
        Evaluate model on dataset.
        
        Args:
            X: Features
            y_true: True labels
            split_name: Name of dataset split
        
        Returns:
            Dictionary of metrics
        """
        logger.info(f"Evaluating on {split_name} set ({X.shape[0]} samples)...")
        
        # Predictions
        y_pred = self.trainer.predict(X)
        y_scores = self.trainer.predict_proba(X)
        
        # Compute metrics
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_true, y_scores),
            'average_precision': average_precision_score(y_true, y_scores)
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # Log metrics
        logger.info(f"{split_name.capitalize()} Metrics:")
        for key, value in metrics.items():
            if key != 'confusion_matrix':
                logger.info(f"  {key}: {value:.4f}")
        
        logger.info(f"  Confusion Matrix:\n{cm}")
        
        self.metrics[split_name] = metrics
        
        return metrics
    
    def plot_metrics(
        self,
        X: np.ndarray,
        y_true: np.ndarray,
        output_dir: Path,
        split_name: str = 'test'
    ) -> None:
        """
        Generate and save evaluation plots.
        
        Args:
            X: Features
            y_true: True labels
            output_dir: Output directory for plots
            split_name: Name of dataset split
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Predictions
        y_pred = self.trainer.predict(X)
        y_scores = self.trainer.predict_proba(X)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        cm_path = output_dir / f'{split_name}_confusion_matrix.png'
        plot_confusion_matrix(cm, save_path=cm_path)
        
        # PR curve
        precision, recall, _ = precision_recall_curve(y_true, y_scores)
        ap = average_precision_score(y_true, y_scores)
        pr_path = output_dir / f'{split_name}_pr_curve.png'
        plot_pr_curve(precision, recall, ap, save_path=pr_path)
        
        # ROC curve
        fpr, tpr, _ = roc_curve(y_true, y_scores)
        auc = roc_auc_score(y_true, y_scores)
        roc_path = output_dir / f'{split_name}_roc_curve.png'
        plot_roc_curve(fpr, tpr, auc, save_path=roc_path)
        
        logger.info(f"Saved evaluation plots to {output_dir}")
    
    def save_report(self, output_path: Path) -> None:
        """Save evaluation report to JSON."""
        if not self.metrics:
            logger.warning("No metrics to save")
            return
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        logger.info(f"Saved evaluation report to {output_path}")


def train_pipeline(
    dataset_manager: DatasetManager,
    feature_pipeline: FeaturePipeline,
    svm_type: str = 'linear',
    param_grid: Dict[str, List[Any]] = None,
    output_dir: Path = Path('models'),
    report_dir: Path = Path('reports'),
    cv: int = 5
) -> Tuple[SVMTrainer, Evaluator]:
    """
    Complete training pipeline.
    
    Args:
        dataset_manager: Dataset manager with splits
        feature_pipeline: Feature extraction pipeline
        svm_type: 'linear' or 'rbf'
        param_grid: Hyperparameter grid
        output_dir: Output directory for models
        report_dir: Output directory for reports
        cv: Number of CV folds
    
    Returns:
        (trainer, evaluator) tuple
    """
    logger.info("=" * 60)
    logger.info("TRAINING PIPELINE")
    logger.info("=" * 60)
    
    # Load training data
    train_data = dataset_manager.get_split_data('train')
    logger.info(f"Loading {len(train_data)} training images...")
    
    train_images = []
    train_labels = []
    
    for img_path, label in tqdm(train_data, desc="Loading train images"):
        img = cv2.imread(str(img_path))
        if img is not None:
            train_images.append(img)
            train_labels.append(label)
    
    # Build codebook
    feature_pipeline.build_codebook(train_images, verbose=True)
    
    # Extract features
    logger.info("Extracting training features...")
    X_train = feature_pipeline.extract_features_batch(train_images, verbose=True)
    y_train = np.array(train_labels)
    
    # Fit scaler
    feature_pipeline.fit_scaler(X_train)
    X_train = feature_pipeline.transform_scaler(X_train)
    
    # Train SVM
    trainer = SVMTrainer(svm_type=svm_type)
    trainer.train(X_train, y_train, param_grid=param_grid, cv=cv, verbose=True)
    
    # Evaluate on validation set
    val_data = dataset_manager.get_split_data('val')
    logger.info(f"\nLoading {len(val_data)} validation images...")
    
    val_images = []
    val_labels = []
    
    for img_path, label in tqdm(val_data, desc="Loading val images"):
        img = cv2.imread(str(img_path))
        if img is not None:
            val_images.append(img)
            val_labels.append(label)
    
    X_val = feature_pipeline.extract_features_batch(val_images, verbose=True)
    X_val = feature_pipeline.transform_scaler(X_val)
    y_val = np.array(val_labels)
    
    # Evaluate
    evaluator = Evaluator(trainer)
    evaluator.evaluate(X_val, y_val, split_name='val')
    
    # Save models
    trainer.save(output_dir / f'svm_face_{svm_type}.pkl')
    feature_pipeline.save(output_dir)
    
    logger.info("\nTraining complete!")
    
    return trainer, evaluator


def evaluate_pipeline(
    dataset_manager: DatasetManager,
    feature_pipeline: FeaturePipeline,
    trainer: SVMTrainer,
    report_dir: Path = Path('reports')
) -> Evaluator:
    """
    Evaluate trained pipeline on test set.
    
    Args:
        dataset_manager: Dataset manager with splits
        feature_pipeline: Trained feature pipeline
        trainer: Trained SVM trainer
        report_dir: Output directory for reports
    
    Returns:
        Evaluator with test results
    """
    logger.info("=" * 60)
    logger.info("EVALUATION ON TEST SET")
    logger.info("=" * 60)
    
    # Load test data
    test_data = dataset_manager.get_split_data('test')
    logger.info(f"Loading {len(test_data)} test images...")
    
    test_images = []
    test_labels = []
    
    for img_path, label in tqdm(test_data, desc="Loading test images"):
        img = cv2.imread(str(img_path))
        if img is not None:
            test_images.append(img)
            test_labels.append(label)
    
    # Extract features
    X_test = feature_pipeline.extract_features_batch(test_images, verbose=True)
    X_test = feature_pipeline.transform_scaler(X_test)
    y_test = np.array(test_labels)
    
    # Evaluate
    evaluator = Evaluator(trainer)
    metrics = evaluator.evaluate(X_test, y_test, split_name='test')
    
    # Generate plots
    evaluator.plot_metrics(X_test, y_test, report_dir, split_name='test')
    
    # Save report
    evaluator.save_report(report_dir / 'test_metrics.json')
    
    return evaluator
