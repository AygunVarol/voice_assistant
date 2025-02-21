# Voice Assistant

## This is a voice assistant that continuously listens for “wake words” to perform commands (e.g., turning on lights, playing music). The project will focus on reducing accidental triggers by refining speech-recognition models and introducing an adjustable “sensitivity” setting. It will also include a visible or audible notification whenever the device is actively processing a command.

## Architecture Overview

```
The voice assistant project will be structured using a modular Python architecture with the following key components:
1) main.py serves as the entry point, initializing the core components and managing the application lifecycle.
2) speech_listener.py implements continuous audio monitoring using PyAudio, handling wake word detection through a dedicated thread.
3) command_processor.py contains the logic for processing recognized commands, implementing command patterns for different actions (lights, music, etc.), and manages the sensitivity settings.
4) wake_word_detector.py uses a pre-trained speech recognition model (likely using TensorFlow or PyTorch) to detect wake words with adjustable sensitivity thresholds.
5) notification_manager.py handles visual and audio feedback when commands are being processed.
The application uses SQLite as a lightweight database (managed through SQLAlchemy ORM) in database_manager.py to store user preferences, sensitivity settings, and command history.
The database connection is configured in config.py, which also stores other application settings.
Data flows from the audio input through the wake word detector, then to the command processor, which queries the database for user preferences before executing actions.
The notification system runs parallel to these operations, providing real-time feedback.
The architecture follows a service-oriented pattern, with clear separation of concerns between audio processing, command handling, and user feedback components.
```

## Folder Structure

```
voice_assistant/
  - main.py
  - config/
    - config.py
  - modules/
    - speech_listener.py
    - command_processor.py
    - wake_word_detector.py
    - notification_manager.py
    - database_manager.py
  - models/
    - user_preferences.py
    - command_history.py
  - utils/
    - audio_utils.py
    - db_utils.py
```
