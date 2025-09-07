import pyttsx3
from utils.logger import log
from pydantic import BaseModel, Field


# ----------------------------
# 1. Pydantic Configuration Model
# ----------------------------
class TTSConfig(BaseModel):
    """
    Pydantic model for validating Text-to-Speech engine settings.
    This ensures that settings like rate and volume are within valid ranges
    before being applied to the engine.
    """

    # Speech rate in words per minute
    rate: int = Field(default=175, gt=50, lt=300)
    # Volume from 0.0 (mute) to 1.0 (full)
    volume: float = Field(default=1.0, ge=0.0, le=1.0)
    voice_id: str = Field(
        default="HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-GB_HAZEL_11.0"
    )


# ----------------------------
# 2. Main TTS Class
# ----------------------------


class TextToSpeech:
    """
    Handles converting text into spoken audio using pyttsx3.

    This class focuses exclusively on the TTS functionality.
    It is initialized once and can be reused to speak multiple phrases.
    """

    def __init__(self, config: TTSConfig):

        log.info("TTS: Initializing Text-to-Speech engine...")

        try:
            self.engine = pyttsx3.init()
            self.config = config
            # Apply the validated settings from the config object
            self.engine.setProperty("rate", self.config.rate)
            self.engine.setProperty("volume", self.config.volume)
            self.engine.setProperty("voice", self.config.voice_id)
            log.info(
                f"TTS: Engine initialized. Rate: {self.config.rate}, Volume: {self.config.volume}, Voice: {self.config.voice_id}"
            )
        except Exception as e:
            log.error(
                f"TTS: Failed to initialize pyttsx3 engine. "
                "Ensure your system has the necessary TTS dependencies "
                "(e.g., eSpeak on Linux). Error: {e}"
            )
            raise

    def speak(self, text: str):
        """
        Speaks the given text aloud.

        This method is blocking; it will not return until the speech is complete.

        Args:
            text (str): The text to be spoken.
        """

        if not text or not text.strip():
            log.error("TTS: No text provided for speech conversion")
            return
        log.info(f"TTS:Speaking: '{text}'")
        try:
            log.info(f'TTS: Converting text to speech: "{text}"')
            # Add the text to the say queue
            self.engine.say(text)
            # Process the queue and wait for speech to finish
            self.engine.runAndWait()
            # self.engine.stop()
            log.info("TTS: Text-to-Speech conversion completed.")
        except Exception as e:
            log.error(f"TTS: Error during speech synthesis: {e}")
