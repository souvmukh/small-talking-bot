# core/audio_input.py
import json
import queue
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer


from speech_manager.audio_filter import AudioFilter, AudioFilterConfig
from utils.logger import log


# --- NEW: Helper function for frequency analysis ---
def log_dominant_frequency(audio_chunk: np.ndarray, samplerate: int, prefix: str):
    """
    Analyzes an audio chunk using FFT and logs its dominant frequency.

    Args:
        audio_chunk (np.ndarray): The audio data to analyze.
        samplerate (int): The sample rate of the audio.
        prefix (str): A label for the log message (e.g., "Raw Audio").
    """
    try:
        # Ensure there's enough data and it's not just silence
        if audio_chunk.size < 2 or np.max(np.abs(audio_chunk)) < 100:
            return

        n_samples = len(audio_chunk)

        # Perform the Fast Fourier Transform
        fft_output = np.fft.fft(audio_chunk)
        # Calculate the corresponding frequencies for the FFT bins
        fft_freq = np.fft.fftfreq(n_samples, d=1 / samplerate)

        # We only care about positive frequencies
        positive_freq_mask = fft_freq > 0
        freqs = fft_freq[positive_freq_mask]
        magnitudes = np.abs(fft_output[positive_freq_mask])

        if magnitudes.size == 0:
            return

        # Find the frequency with the highest magnitude
        dominant_freq_index = np.argmax(magnitudes)
        dominant_frequency = freqs[dominant_freq_index]

        # Use DEBUG level for detailed diagnostics
        log.debug(f"{prefix} - Dominant Frequency: {dominant_frequency:.2f} Hz")

    except Exception as e:
        log.warning(f"Could not analyze frequency for '{prefix}': {e}")


# ------------------------------------------------------------------


class SpeechToText:
    """
    Handles capturing audio and transcribing it to text using Vosk.
    This version delegates noise filtering to a dedicated AudioFilter class.
    """

    def __init__(
        self,
        model_path: str,
        device_id: int = None,
        filter_config: AudioFilterConfig = AudioFilterConfig(),
    ):
        # ... __init__ method remains unchanged ...
        log.info("Initializing Speech-to-Text engine...")
        try:
            self.model = Model(model_path)
            self.device_info = sd.query_devices(device_id, "input")
            self.samplerate = int(self.device_info["default_samplerate"])
            self.q = queue.Queue()
            self.filter = AudioFilter(config=filter_config, samplerate=self.samplerate)
            log.info("Vosk model and audio filter handler initialized successfully.")
        except Exception as e:
            log.error(f"Failed during initialization. Error: {e}")
            raise

    def _audio_callback(self, indata, frames, time, status):
        # ... _audio_callback method remains unchanged ...
        if status:
            log.warning(f"Audio input status: {status}")
        self.q.put(bytes(indata))

    def listen(self) -> str:
        try:
            recognizer = KaldiRecognizer(self.model, self.samplerate)
            log.info("Listening... Say something!")

            with sd.RawInputStream(
                samplerate=self.samplerate,
                blocksize=8000,
                device=self.device_info["index"],
                dtype="int16",
                channels=1,
                callback=self._audio_callback,
            ):
                while True:
                    raw_data = self.q.get()

                    audio_samples = np.frombuffer(raw_data, dtype=np.int16)

                    # --- ADDED: Log frequency of raw audio ---
                    log_dominant_frequency(audio_samples, self.samplerate, "Raw Audio")

                    filtered_samples = self.filter.process(audio_samples)

                    # --- ADDED: Log frequency of filtered audio ---
                    log_dominant_frequency(
                        filtered_samples, self.samplerate, "Filtered Audio"
                    )

                    filtered_data_bytes = filtered_samples.astype(np.int16).tobytes()

                    if recognizer.AcceptWaveform(filtered_data_bytes):
                        result_dict = json.loads(recognizer.Result())
                        text = result_dict.get("text", "")
                        log.info(f"Recognized: '{text}'")
                        if text:
                            return text

        except Exception as e:
            log.error(f"An error occurred during listening: {e}")
            return ""
