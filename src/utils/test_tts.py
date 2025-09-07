import pyttsx3
import time
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def text_to_speech(text, voice_id=None):
    logging.info(f"Starting TTS for text: {text}")
    engine = pyttsx3.init()
    if voice_id:
        engine.setProperty('voice', voice_id)
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    logging.info("Finished TTS for text")

if __name__ == '__main__':
    sentences = [
        "Hello, this is sentence one.",
        "Now speaking sentence two.",
        "Finally, this is sentence three."
    ]

    for sentence in sentences:
        text_to_speech(sentence)
        time.sleep(2)  # Pause 1 second between sentences
