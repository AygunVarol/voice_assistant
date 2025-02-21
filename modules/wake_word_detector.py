import os
import numpy as np
import tensorflow as tf
from threading import Lock
from typing import Optional, Tuple
from tensorflow.keras import layers, models
from utils.audio_utils import preprocess_audio
from config.config import WakeWordConfig

class WakeWordDetector:
    def __init__(self):
        self.config = WakeWordConfig()
        self.model = self._load_model()
        self.sensitivity = self.config.DEFAULT_SENSITIVITY
        self.lock = Lock()
        self._threshold = self._calculate_threshold()

    def _load_model(self) -> models.Model:
        """Loads or creates the wake word detection model"""
        model_path = os.path.join(self.config.MODEL_DIR, "wake_word_model.h5")
        
        if os.path.exists(model_path):
            return models.load_model(model_path)
        else:
            # Create simple wake word detection model
            model = models.Sequential([
                layers.Input(shape=(self.config.AUDIO_FEATURES,)),
                layers.Dense(256, activation='relu'),
                layers.Dropout(0.3),
                layers.Dense(128, activation='relu'),
                layers.Dropout(0.2),
                layers.Dense(64, activation='relu'),
                layers.Dense(1, activation='sigmoid')
            ])
            model.compile(optimizer='adam',
                        loss='binary_crossentropy',
                        metrics=['accuracy'])
            return model

    def _calculate_threshold(self) -> float:
        """Calculate detection threshold based on sensitivity"""
        base_threshold = 0.5
        sensitivity_factor = (self.sensitivity - 5) / 10.0
        return base_threshold + (sensitivity_factor * 0.3)

    def set_sensitivity(self, level: int) -> None:
        """Set wake word detection sensitivity (1-10)"""
        with self.lock:
            self.sensitivity = max(1, min(10, level))
            self._threshold = self._calculate_threshold()

    def detect_wake_word(self, audio_data: np.ndarray) -> Tuple[bool, float]:
        """
        Detect wake word in audio data
        Returns: (detection_result, confidence_score)
        """
        with self.lock:
            # Preprocess audio data
            features = preprocess_audio(audio_data, 
                                     sample_rate=self.config.SAMPLE_RATE,
                                     n_features=self.config.AUDIO_FEATURES)
            
            # Get model prediction
            prediction = self.model.predict(np.expand_dims(features, axis=0),
                                         verbose=0)[0][0]
            
            # Compare against threshold
            is_wake_word = prediction >= self._threshold
            
            return is_wake_word, float(prediction)

    def update_model(self, training_data: np.ndarray, 
                    labels: np.ndarray) -> None:
        """Update wake word model with new training data"""
        with self.lock:
            self.model.fit(training_data, labels,
                         epochs=self.config.TRAINING_EPOCHS,
                         batch_size=self.config.BATCH_SIZE,
                         verbose=0)
            
            # Save updated model
            model_path = os.path.join(self.config.MODEL_DIR, 
                                    "wake_word_model.h5")
            self.model.save(model_path)

    def get_current_sensitivity(self) -> int:
        """Get current sensitivity level"""
        with self.lock:
            return self.sensitivity

    def get_detection_threshold(self) -> float:
        """Get current detection threshold"""
        with self.lock:
            return self._threshold
