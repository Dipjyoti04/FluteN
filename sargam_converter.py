"""
Sargam Note Converter - Maps frequencies to Indian classical music sargam notation
"""
import numpy as np
from typing import List, Tuple, Optional

class SargamConverter:
    def __init__(self, base_frequency: float = 261.63):  # C4 as default Sa
        """
        Initialize the sargam converter with a base frequency for Sa
        
        Args:
            base_frequency: The frequency of Sa (default is C4 = 261.63 Hz)
        """
        self.base_frequency = base_frequency
        
        # Sargam note ratios relative to Sa (just intonation)
        self.sargam_ratios = {
            'Sa': 1.0,      # Shadja
            'Re': 9/8,      # Rishabh (Shuddha)
            'Ga': 5/4,      # Gandhar (Shuddha)
            'Ma': 4/3,      # Madhyam (Shuddha)
            'Pa': 3/2,      # Pancham
            'Dha': 5/3,     # Dhaivat (Shuddha)
            'Ni': 15/8,     # Nishad (Shuddha)
        }
        
        # Alternative ratios for komal (flat) notes
        self.komal_ratios = {
            'Re': 16/15,    # Komal Rishabh
            'Ga': 6/5,      # Komal Gandhar
            'Dha': 8/5,     # Komal Dhaivat
            'Ni': 9/5,      # Komal Nishad
        }
        
        # Generate frequency mappings
        self._generate_frequency_mappings()
    
    def _generate_frequency_mappings(self):
        """Generate frequency mappings for multiple octaves"""
        self.note_frequencies = {}
        
        # Generate for 3 octaves (lower, middle, upper)
        for octave in range(-1, 2):
            octave_multiplier = 2 ** octave
            
            # Shuddha notes
            for note, ratio in self.sargam_ratios.items():
                freq = self.base_frequency * ratio * octave_multiplier
                octave_suffix = self._get_octave_suffix(octave)
                self.note_frequencies[f"{note}{octave_suffix}"] = freq
            
            # Komal notes
            for note, ratio in self.komal_ratios.items():
                freq = self.base_frequency * ratio * octave_multiplier
                octave_suffix = self._get_octave_suffix(octave)
                self.note_frequencies[f"{note}♭{octave_suffix}"] = freq
    
    def _get_octave_suffix(self, octave: int) -> str:
        """Get octave suffix for notation"""
        if octave == -1:
            return "₋"  # Lower octave
        elif octave == 0:
            return ""   # Middle octave
        elif octave == 1:
            return "₊"  # Upper octave
        return ""
    
    def frequency_to_sargam(self, frequency: float, tolerance: float = 50.0) -> Optional[str]:
        """
        Convert a frequency to the closest sargam note
        
        Args:
            frequency: Input frequency in Hz
            tolerance: Maximum deviation in Hz to consider a match
            
        Returns:
            Closest sargam note or None if no match within tolerance
        """
        if frequency <= 0:
            return None
            
        closest_note = None
        min_difference = float('inf')
        
        for note, note_freq in self.note_frequencies.items():
            difference = abs(frequency - note_freq)
            if difference < min_difference and difference <= tolerance:
                min_difference = difference
                closest_note = note
        
        return closest_note
    
    def frequencies_to_sargam_sequence(self, frequencies: List[float], 
                                     tolerance: float = 50.0) -> List[Optional[str]]:
        """
        Convert a sequence of frequencies to sargam notes
        
        Args:
            frequencies: List of frequencies in Hz
            tolerance: Maximum deviation in Hz to consider a match
            
        Returns:
            List of sargam notes (None for unmatched frequencies)
        """
        return [self.frequency_to_sargam(freq, tolerance) for freq in frequencies]
    
    def set_base_frequency(self, frequency: float):
        """Update the base frequency (Sa) and regenerate mappings"""
        self.base_frequency = frequency
        self._generate_frequency_mappings()
    
    def get_note_info(self) -> dict:
        """Get information about all available notes and their frequencies"""
        return dict(sorted(self.note_frequencies.items(), key=lambda x: x[1]))
