import pyaudio
import threading
import queue
import numpy as np
from typing import Optional, Callable

from ..utils.audio_utils import AudioUtils
from ..modules.wake_word_detector import WakeWordDetector
from ..config.config import Config

class SpeechListener:
    def __init__(self, 
                 wake_word_callback: Callable,
                 config: Config,
                 audio_utils: AudioUtils,
                 wake_word_detector: WakeWordDetector):
        
        self.wake_word_callback = wake_word_callback
        self.config = config
        self.audio_utils = audio_utils
        self.wake_word_detector = wake_word_detector
        
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.listen_thread: Optional[threading.Thread] = None

    def start_listening(self):
        """Start audio stream and processing thread"""
        if self.is_listening:
            return

        self.is_listening = True
        
        # Open audio stream
        self.stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=self.config.AUDIO_CHANNELS,
            rate=self.config.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.config.CHUNK_SIZE,
            stream_callback=self._audio_callback
        )

        # Start processing thread
        self.listen_thread = threading.Thread(target=self._process_audio)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def stop_listening(self):
        """Stop audio stream and processing"""
        if not self.is_listening:
            return

        self.is_listening = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.listen_thread:
            self.listen_thread.join()
            
        # Clear queue
        while not self.audio_queue.empty():
            self.audio_queue.get()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream to add data to queue"""
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)

    def _process_audio(self):
        """Process audio data from queue and detect wake word"""
        while self.is_listening:
            try:
                # Get audio chunk from queue
                audio_data = self.audio_queue.get(timeout=1.0)
                
                # Process audio through wake word detector
                if self.wake_word_detector.detect(audio_data):
                    # Wake word detected - trigger callback
                    self.wake_word_callback()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
                continue

    def __del__(self):
        """Cleanup on deletion"""
        self.stop_listening()
        if self.audio:
            self.audio.terminate()
