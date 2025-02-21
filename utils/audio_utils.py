import pyaudio
import wave
import numpy as np
from typing import Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AudioUtils:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.DEFAULT_CHUNK = 1024
        self.DEFAULT_FORMAT = pyaudio.paFloat32
        self.DEFAULT_CHANNELS = 1
        self.DEFAULT_RATE = 16000
        
    def open_stream(self, 
                   chunk: int = None,
                   audio_format: int = None, 
                   channels: int = None,
                   rate: int = None) -> pyaudio.Stream:
        """Opens an audio stream with specified or default parameters"""
        chunk = chunk or self.DEFAULT_CHUNK
        audio_format = audio_format or self.DEFAULT_FORMAT
        channels = channels or self.DEFAULT_CHANNELS
        rate = rate or self.DEFAULT_RATE
        
        try:
            stream = self.audio.open(
                format=audio_format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk
            )
            return stream
        except Exception as e:
            logger.error(f"Error opening audio stream: {str(e)}")
            raise

    def record_audio(self, 
                    duration: float,
                    chunk: int = None,
                    audio_format: int = None,
                    channels: int = None, 
                    rate: int = None) -> Tuple[bytes, pyaudio.Stream]:
        """Records audio for specified duration and returns the frames"""
        chunk = chunk or self.DEFAULT_CHUNK
        audio_format = audio_format or self.DEFAULT_FORMAT
        channels = channels or self.DEFAULT_CHANNELS
        rate = rate or self.DEFAULT_RATE
        
        stream = self.open_stream(chunk, audio_format, channels, rate)
        frames = []
        
        for _ in range(0, int(rate / chunk * duration)):
            try:
                data = stream.read(chunk)
                frames.append(data)
            except Exception as e:
                logger.error(f"Error recording audio: {str(e)}")
                stream.stop_stream()
                stream.close()
                raise
                
        return b''.join(frames), stream

    def save_audio(self,
                  frames: bytes,
                  filename: str,
                  channels: int = None,
                  rate: int = None,
                  audio_format: int = None) -> None:
        """Saves recorded audio frames to a WAV file"""
        channels = channels or self.DEFAULT_CHANNELS
        rate = rate or self.DEFAULT_RATE
        audio_format = audio_format or self.DEFAULT_FORMAT
        
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(self.audio.get_sample_size(audio_format))
            wf.setframerate(rate)
            wf.writeframes(frames)
            wf.close()
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            raise

    def calculate_audio_energy(self, audio_data: bytes) -> float:
        """Calculates the energy level of audio data"""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            return np.sqrt(np.mean(np.square(audio_array)))
        except Exception as e:
            logger.error(f"Error calculating audio energy: {str(e)}")
            raise

    def apply_noise_reduction(self, audio_data: bytes, noise_threshold: float = 0.1) -> bytes:
        """Applies basic noise reduction to audio data"""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            audio_array[abs(audio_array) < noise_threshold] = 0
            return audio_array.tobytes()
        except Exception as e:
            logger.error(f"Error applying noise reduction: {str(e)}")
            raise

    def close(self) -> None:
        """Closes the PyAudio instance"""
        try:
            self.audio.terminate()
        except Exception as e:
            logger.error(f"Error closing audio: {str(e)}")
            raise
