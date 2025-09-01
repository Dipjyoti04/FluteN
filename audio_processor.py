"""
Audio Processor - Handles audio file loading and pitch detection
"""
import librosa
import numpy as np
import soundfile as sf
from typing import List, Tuple, Optional
from scipy.signal import find_peaks

class AudioProcessor:
    def __init__(self, sample_rate: int = 22050):
        """
        Initialize audio processor
        
        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate
        self.hop_length = 512
        self.frame_length = 2048
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, float]:
        """
        Load audio file and return audio data with duration
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, duration_in_seconds)
        """
        try:
            # Load audio file
            audio_data, sr = librosa.load(file_path, sr=self.sample_rate)
            duration = len(audio_data) / sr
            
            print(f"Loaded audio: {file_path}")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Sample rate: {sr} Hz")
            
            return audio_data, duration
            
        except Exception as e:
            raise Exception(f"Error loading audio file: {str(e)}")
    
    def extract_pitch_contour(self, audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract pitch contour from audio using librosa's piptrack
        
        Args:
            audio_data: Audio time series
            
        Returns:
            Tuple of (times, frequencies) arrays
        """
        # Use piptrack for pitch detection
        pitches, magnitudes = librosa.piptrack(
            y=audio_data,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            fmin=80,    # Minimum frequency (around low E2)
            fmax=2000   # Maximum frequency (covers most flute range)
        )
        
        # Extract the most prominent pitch at each time frame
        times = librosa.frames_to_time(
            np.arange(pitches.shape[1]), 
            sr=self.sample_rate, 
            hop_length=self.hop_length
        )
        
        frequencies = []
        for t in range(pitches.shape[1]):
            # Get the pitch with highest magnitude at this time frame
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            
            # Only include pitches with sufficient magnitude
            if magnitudes[index, t] > 0.1:
                frequencies.append(pitch)
            else:
                frequencies.append(0.0)  # Silence or unclear pitch
        
        return times, np.array(frequencies)
    
    def extract_fundamental_frequencies(self, audio_data: np.ndarray, 
                                      window_size: float = 0.1) -> List[float]:
        """
        Extract fundamental frequencies using YIN algorithm
        
        Args:
            audio_data: Audio time series
            window_size: Size of analysis window in seconds
            
        Returns:
            List of fundamental frequencies
        """
        # Calculate window parameters
        window_samples = int(window_size * self.sample_rate)
        hop_samples = window_samples // 2
        
        frequencies = []
        
        for start in range(0, len(audio_data) - window_samples, hop_samples):
            window = audio_data[start:start + window_samples]
            
            # Apply window function
            windowed = window * np.hanning(len(window))
            
            # Estimate fundamental frequency using autocorrelation
            f0 = self._estimate_f0_autocorr(windowed)
            frequencies.append(f0)
        
        return frequencies
    
    def _estimate_f0_autocorr(self, signal: np.ndarray) -> float:
        """
        Estimate fundamental frequency using autocorrelation
        
        Args:
            signal: Windowed audio signal
            
        Returns:
            Estimated fundamental frequency in Hz
        """
        # Compute autocorrelation
        autocorr = np.correlate(signal, signal, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find peaks in autocorrelation
        peaks, _ = find_peaks(autocorr[1:], height=0.3 * np.max(autocorr))
        
        if len(peaks) == 0:
            return 0.0
        
        # The first peak corresponds to the fundamental period
        period_samples = peaks[0] + 1
        frequency = self.sample_rate / period_samples
        
        # Filter out unrealistic frequencies
        if frequency < 80 or frequency > 2000:
            return 0.0
            
        return frequency
    
    def smooth_frequencies(self, frequencies: np.ndarray, 
                          window_size: int = 5) -> np.ndarray:
        """
        Smooth frequency contour to reduce noise
        
        Args:
            frequencies: Array of frequencies
            window_size: Size of smoothing window
            
        Returns:
            Smoothed frequency array
        """
        # Apply median filter to remove outliers
        from scipy.ndimage import median_filter
        smoothed = median_filter(frequencies, size=window_size)
        
        # Apply moving average for further smoothing
        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(smoothed, kernel, mode='same')
        
        return smoothed
    
    def detect_note_onsets(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Detect note onset times in the audio
        
        Args:
            audio_data: Audio time series
            
        Returns:
            Array of onset times in seconds
        """
        # Detect onsets using spectral flux
        onset_frames = librosa.onset.onset_detect(
            y=audio_data,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            units='frames'
        )
        
        # Convert frames to time
        onset_times = librosa.frames_to_time(
            onset_frames, 
            sr=self.sample_rate, 
            hop_length=self.hop_length
        )
        
        return onset_times
