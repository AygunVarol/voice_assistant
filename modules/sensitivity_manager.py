from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging
from contextlib import contextmanager
from typing import Optional

from ..config.database import get_db_connection
from .models import SensitivitySettings

class SensitivityManager:
    def __init__(self):
        self._db_connection = get_db_connection()
        self._session_maker = sessionmaker(bind=self._db_connection)
        self._current_sensitivity = self._load_sensitivity()
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def _session_scope(self):
        session = self._session_maker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()

    def _load_sensitivity(self) -> float:
        with self._session_scope() as session:
            settings = session.query(SensitivitySettings).first()
            if not settings:
                # Create default settings if none exist
                default_sensitivity = 0.5
                settings = SensitivitySettings(sensitivity_level=default_sensitivity)
                session.add(settings)
                session.commit()
            return settings.sensitivity_level

    def get_current_sensitivity(self) -> float:
        return self._current_sensitivity

    def update_sensitivity(self, new_level: float) -> bool:
        if not 0.0 <= new_level <= 1.0:
            self.logger.error(f"Invalid sensitivity level: {new_level}")
            return False

        try:
            with self._session_scope() as session:
                settings = session.query(SensitivitySettings).first()
                if settings:
                    settings.sensitivity_level = new_level
                else:
                    settings = SensitivitySettings(sensitivity_level=new_level)
                    session.add(settings)
                
                self._current_sensitivity = new_level
                return True
        except Exception as e:
            self.logger.error(f"Failed to update sensitivity: {str(e)}")
            return False

    def adjust_threshold(self, ambient_noise_level: float) -> float:
        """
        Adjusts detection threshold based on ambient noise and sensitivity settings
        Returns the adjusted threshold value
        """
        base_threshold = 0.5
        noise_factor = min(1.0, max(0.0, ambient_noise_level / 100.0))
        sensitivity_factor = self._current_sensitivity
        
        # Calculate adjusted threshold
        adjusted_threshold = base_threshold * (1 + noise_factor) * (2 - sensitivity_factor)
        return min(1.0, max(0.1, adjusted_threshold))

    def get_wake_word_threshold(self) -> float:
        """
        Returns the current wake word detection threshold
        """
        return max(0.2, min(0.8, 1.0 - self._current_sensitivity))

    def calibrate_sensitivity(self, false_trigger_rate: float) -> None:
        """
        Auto-calibrates sensitivity based on false trigger rate
        """
        if false_trigger_rate > 0.2:  # Too many false triggers
            new_sensitivity = max(0.1, self._current_sensitivity - 0.1)
        elif false_trigger_rate < 0.05:  # Too few triggers
            new_sensitivity = min(0.9, self._current_sensitivity + 0.1)
        else:
            return

        self.update_sensitivity(new_sensitivity)
