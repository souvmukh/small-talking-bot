# core/audio_output.py

import pyttsx3
from pydantic import BaseModel, Field
from utils.logger import log

# ----------------------------
# 1. Pydantic Configuration Model (No changes here)
# ----------------------------
class TTSConfig(BaseModel):
    rate: int = Field(default=175, gt=50, lt=300) 
    volume: float = Field(default=1.0, ge=0.0, le=1.0)
    voice_id: str = Field(
        default="HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-GB_HAZEL_11.0"
    )

# ----------------------------
# 2. Main TTS Class (Updated Logic)
# ----------------------------
class TextToSpeech:
    """
    Handles converting text into spoken audio using pyttsx3.
    
    This updated version creates a new engine instance for each call to speak(),
    which avoids issues with the pyttsx3 event loop terminating after the
    first use.
    """
    
    def __init__(self, config: TTSConfig):
        """
        Initializes the TextToSpeech handler with a validated configuration.
        Note: The engine itself is now initialized within the speak() method.
        
        Args:
            config (TTSConfig): A Pydantic model with TTS settings.
        """
        self.config = config
        log.info("TTS: Text-to-Speech handler configured.")
        # We no longer initialize the engine here.

    def speak(self, text: str):
        """
        Speaks the given text aloud by creating a temporary engine instance.

        This method is blocking; it will not return until the speech is complete.

        Args:
            text (str): The text to be spoken.
        """
        if not text or not text.strip():
            log.warning("TTS: Received empty text. Nothing to speak.")
            return

        log.info(f"TTS: Speaking: '{text}'")
        try:
            # Initialize the engine right before we need it.
            engine = pyttsx3.init()
            
            # Apply settings from our stored config
            engine.setProperty('rate', self.config.rate)
            engine.setProperty('volume', self.config.volume)
            engine.setProperty('voice', self.config.voice_id)
            log.info(
                f"TTS: Engine initialized. Rate: {self.config.rate}, Volume: {self.config.volume}, Voice: {self.config.voice_id}"
            )
            # Queue the text and run the event loop
            engine.say(text)
            engine.runAndWait()
            
            # The engine instance is automatically garbage collected after this method exits.
            
        except Exception as e:
            log.error(f"TTS: An error occurred during speech synthesis: {e}")