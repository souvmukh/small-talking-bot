# audio_input.py
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from utils.logger import log

class SpeechToText:
    """
    Handles capturing audio from the microphone and transcribing it to text using Vosk.
    
    This class follows the Single Responsibility Principle, as its only purpose
    is to manage the speech-to-text conversion process.
    """

    def __init__(self, model_path: str, device_id: int = None):
        """
        Initializes the SpeechToText engine.

        Args:
            model_path (str): Path to the Vosk model directory.
            device_id (int, optional): The ID of the audio input device. 
                                       Defaults to the system's default device.
        """
        log.info("Initializing Speech-to-Text engine...")
        try:
            # Load the Vosk model. Models can be downloaded from the Vosk website.
            # A smaller model is recommended for devices like Raspberry Pi.
            self.model = Model(model_path)
            self.device_info = sd.query_devices(device_id, 'input')
            self.samplerate = int(self.device_info['default_samplerate'])
            # A queue to hold audio chunks from the microphone callback.
            self.q = queue.Queue()
            log.info("Vosk model loaded successfully.")
        except Exception as e:
            log.error(f"Failed to load Vosk model from {model_path}. "
                      f"Please ensure the model is downloaded and the path is correct. Error: {e}")
            raise

    def _audio_callback(self, indata, frames, time, status):
        """
        This callback function is called by sounddevice for each audio chunk.
        """
        if status:
            log.warning(f"Audio input status: {status}")
        # Add the audio chunk (as a bytes object) to the queue.
        self.q.put(bytes(indata))

    def listen(self) -> str:
        """
        Listens for a single utterance from the microphone and returns the transcribed text.

        This method activates the microphone, waits for the user to speak, and stops
        once a complete phrase is detected.

        Returns:
            str: The transcribed text from the user's speech.
        """
        try:
            # Create a recognizer instance using the loaded model.
            recognizer = KaldiRecognizer(self.model, self.samplerate)
            log.info("STT: Listening... Say something!")

            # Use a context manager to ensure the audio stream is properly closed.
            with sd.RawInputStream(samplerate=self.samplerate,
                                   blocksize=8000,
                                   device=self.device_info['index'],
                                   dtype='int16',
                                   channels=1,
                                   callback=self._audio_callback):

                while True:
                    # Get an audio chunk from the queue. This blocks until a chunk is available.
                    data = self.q.get()
                    
                    # Feed the audio data to the recognizer.
                    if recognizer.AcceptWaveform(data):
                        # recognizer.AcceptWaveform returns True when it thinks a phrase is complete.
                        result_json = recognizer.Result()
                        result_dict = json.loads(result_json)
                        text = result_dict.get('text', '')
                        log.info(f"STT: Recognized: '{text}'")
                        if text: # If text was recognized, stop listening.
                            return text
                    # else: # Uncomment to see partial results as you speak
                    #     partial_result = recognizer.PartialResult()
                    #     log.debug(f"Partial: {partial_result}")

        except Exception as e:
            log.error(f"STT: An error occurred during listening: {e}")
            return ""