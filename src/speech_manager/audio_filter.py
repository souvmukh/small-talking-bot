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
    
    Human Frequency Range Information:
    - Human hearing range: ~20 Hz to 20,000 Hz
    - Human speech fundamental frequencies: ~85-255 Hz (males), ~165-255 Hz (females)
    - Human speech harmonics and consonants: up to ~8,000 Hz
    - Optimal speech intelligibility range: ~80-8,000 Hz
    
    The default settings filter out:
    - Sub-sonic noise: < 80 Hz (rumble, vibrations, handling noise)
    - Ultrasonic noise: > 8,000 Hz (electronic interference, high-frequency artifacts)
    
    This preserves the full range of human speech while removing non-human frequency noise.
    """
    low_cutoff_hz: float = Field(
        default=80.0, 
        ge=20.0, 
        description="Low cutoff frequency in Hz. Filters out sub-sonic noise below human speech range."
    )
    high_cutoff_hz: float = Field(
        default=8000.0, 
        le=20000.0, 
        description="High cutoff frequency in Hz. Filters out ultrasonic noise above human speech range."
    )
    order: int = Field(
        default=5, 
        ge=1, 
        le=10, 
        description="Order of the Butterworth filter. Higher order = sharper cutoff."
    )


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