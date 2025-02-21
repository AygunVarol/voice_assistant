# Voice Assistant

## This is a voice assistant that continuously listens for “wake words” to perform commands (e.g., turning on lights, playing music). The project will focus on reducing accidental triggers by refining speech-recognition models and introducing an adjustable “sensitivity” setting. It will also include a visible or audible notification whenever the device is actively processing a command.

## Architecture Overview

```
The voice assistant project will be structured using a modular Python architecture with the following key components: 1) main.py serves as the entry point, initializing the core application and coordinating between modules. 2) speech_listener.py implements continuous audio monitoring using PyAudio, handling wake word detection through a trained model (likely using libraries like Porcupine or Snowboy). 3) command_processor.py contains the logic for parsing and executing voice commands, implementing command patterns for different actions (lights, music, etc.). 4) sensitivity_manager.py handles the adjustable sensitivity settings, storing configurations in a SQLite database using SQLAlchemy ORM. 5) notification_handler.py manages visual and audio feedback using system-specific APIs. The application uses a SQLite database (config.db) to store user preferences, sensitivity settings, and command history, accessed through SQLAlchemy models defined in models.py. The data flow begins with speech_listener.py continuously monitoring audio input, which, upon wake word detection, triggers the command_processor.py. The command processor then executes the appropriate action while notification_handler.py provides feedback. All components interact through a well-defined event system, with the sensitivity_manager.py module continuously adjusting detection thresholds based on stored preferences. The database connection is managed through a connection pool to ensure efficient resource usage, with database operations wrapped in transactions to maintain data integrity.
```

## Folder Structure

```
voice_assistant/
  - main.py
  - config/
    - database.py
  - modules/
    - speech_listener.py
    - command_processor.py
    - sensitivity_manager.py
    - notification_handler.py
    - models.py
  - data/
    - config.db
```
