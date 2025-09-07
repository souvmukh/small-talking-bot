# src/test_stt.py
""" Test script for standalone Speech-to-Text (STT) functionality using Vosk model. """
import os, time
from speech_manager.audio_input import SpeechToText
from speech_manager.audio_output import TexttoSpeech    
from utils.logger import log
import pyttsx3

# --- CONFIGURATION ---
MODEL_DIR = "C:\\_c_github\\talker\\models"
MODEL_NAME = "vosk-model-small-en-us-0.15"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)


def main():
    """
    Main function to run the standalone STT test.
    """
    # First, check if the model path actually exists.
    if not os.path.exists(MODEL_PATH):
        log.error(f"Model path does not exist: {MODEL_PATH}")
        log.error("Please download the Vosk model and place it in the correct directory.")
        return

    try:
        # Initialize the speech-to-text engine.
        stt_engine = SpeechToText(model_path=MODEL_PATH)
        #tts = TexttoSpeech()  # using default voice
        log.info("Starting STT test. Press Ctrl+C to exit.")
        
        # Loop forever, listening and printing the result.
        i = 0
        while True:
            text = stt_engine.listen()
            pyttsx3.init()
            tts = TexttoSpeech()
            tts.text_to_speech(text)
            
            if text:
                print(f"--> You said {i}: {text}\n")
                time.sleep(5)  # Pause before next listen
                i += 1
    except KeyboardInterrupt:
        log.info("\nTest stopped by user.")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()