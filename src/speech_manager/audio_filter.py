# core/audio_filter.py
import numpy as np
from pydantic import BaseModel, Field
from utils.logger import log
from scipy import signal

# ----------------------------
# 1. Pydantic Configuration Model
# ----------------------------
class AudioFilterConfig(BaseModel):
    """
    Pydantic model to hold and validate audio filter settings.
    This configuration is self-contained within the filter module.
    """
    low_cutoff_hz: float = Field(default=200.0, ge=20.0, description="Low cutoff frequency in Hz.")
    high_cutoff_hz: float = Field(default=3000.0, le=20000.0, description="High cutoff frequency in Hz.")
    order: int = Field(default=4, ge=1, le=10, description="Order of the Butterworth filter.")


# ----------------------------
# 2. Audio Filter Class
# ----------------------------
class AudioFilter:
    """
    A class dedicated to designing and applying a band-pass filter to audio data.
    
    This class encapsulates all signal processing logic, adhering to the
    Single Responsibility Principle.
    """

    def __init__(self, config: AudioFilterConfig, samplerate: int):
        """
        Initializes the filter by designing the filter coefficients.

        Args:
            config (AudioFilterConfig): The validated Pydantic configuration for the filter.
            samplerate (int): The sample rate of the audio stream (e.g., 16000).
        """
        self.config = config
        self.samplerate = samplerate
        
        log.info(
            f"Designing a band-pass filter from {self.config.low_cutoff_hz} Hz to "
            f"{self.config.high_cutoff_hz} Hz for a sample rate of {self.samplerate} Hz."
        )
        
        # Calculate the Nyquist frequency, which is half the sample rate.
        nyquist_freq = 0.5 * self.samplerate
        
        # Normalize the cutoff frequencies to the range [0, 1].
        low = self.config.low_cutoff_hz / nyquist_freq
        high = self.config.high_cutoff_hz / nyquist_freq

        # Design the Butterworth filter once and store the coefficients.
        # 'b' and 'a' are the numerator and denominator polynomials of the filter.
        self.b, self.a = signal.butter(
            self.config.order,
            [low, high],
            btype='band'
        )
        log.info("Audio filter designed successfully.")

    def process(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
        Applies the pre-designed filter to a chunk of audio data.

        Args:
            audio_chunk (np.ndarray): A NumPy array containing the raw audio samples.

        Returns:
            np.ndarray: A NumPy array containing the filtered audio samples.
        """
        if audio_chunk.size == 0:
            return audio_chunk # Return empty array if given one
            
        # Apply the filter using `filtfilt` for zero-phase distortion.
        filtered_chunk = signal.filtfilt(self.b, self.a, audio_chunk)
        return filtered_chunk