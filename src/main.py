# main.py

import os
from utils.logger import log
from speech_manager.audio_input import SpeechToText
from speech_manager.audio_filter import AudioFilterConfig
from core.text_processing import LLMProcessor, LLMConfig
from speech_manager.audio_output import TextToSpeech, TTSConfig

# --- Application Configuration ---

# Path to the Vosk STT model
# Assumes a 'models' directory in the project root
MODEL_DIR = "C:\\_c_github\\talker\\models"
MODEL_NAME = "vosk-model-en-us-0.22"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)


def main():
    """
    The main entry point for the voice assistant application.

    This function initializes all the core components and runs the
    main loop for continuous interaction.
    """
    log.info("Starting Offline Voice Assistant...")

    # 1. --- Initialization ---
    # Create instances of our core components, injecting their dependencies.
    try:
        if not os.path.exists(MODEL_PATH):
            log.error(f"Vosk model not found at {MODEL_PATH}.")
            log.error(
                "Please download the model and place it in the correct directory."
            )
            return
        audio_filter = AudioFilterConfig(
            low_cutoff_hz=250.0, high_cutoff_hz=3500.0, order=5
        )

        stt_engine = SpeechToText(model_path=MODEL_PATH, filter_config=audio_filter)

        # Use the Pydantic models to create validated configs
        llm_config = LLMConfig(model_name="phi3:mini")
        llm_processor = LLMProcessor(config=llm_config)

        tts_config = TTSConfig(rate=165)  # Slightly slower for clarity
        tts_engine = TextToSpeech(config=tts_config)

    except Exception as e:
        log.error(f"Failed to initialize a core component: {e}")
        return

    # 2. --- Main Application Loop ---
    # This loop continuously listens, processes, and responds.
    log.info("Initialization complete. Assistant is ready.")
    tts_engine.speak("Hello! I'm online and ready to help.")

    try:
        while True:
            # a. Listen for user input
            user_text = stt_engine.listen()

            if not user_text:
                log.warning("No input received or STT failed. Listening again.")
                continue

            # b. Add a simple exit command
            if user_text.lower().strip() == "goodbye":
                log.info("Exit command received. Shutting down.")
                tts_engine.speak("Goodbye!")
                break

            # c. Process the text and get a response
            llm_response = llm_processor.generate_response(user_text)

            # d. Speak the response
            tts_engine.speak(llm_response)

    except KeyboardInterrupt:
        log.info("Application interrupted by user (Ctrl+C). Shutting down.")
    except Exception as e:
        log.critical(f"A critical error occurred in the main loop: {e}", exc_info=True)
    finally:
        log.info("Application has shut down.")


if __name__ == "__main__":
    main()
