"""
Music Transcriber - Main class that combines audio processing and sargam conversion
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt

from audio_processor import AudioProcessor
from sargam_converter import SargamConverter

class MusicTranscriber:
    def __init__(self, base_frequency: float = 261.63):
        """
        Initialize the music transcriber
        
        Args:
            base_frequency: Base frequency for Sa (default C4)
        """
        self.audio_processor = AudioProcessor()
        self.sargam_converter = SargamConverter(base_frequency)
        self.last_transcription = None
    
    def transcribe_audio_file(self, file_path: str, 
                            tolerance: float = 50.0,
                            min_note_duration: float = 0.1) -> Dict:
        """
        Transcribe an audio file to sargam notation
        
        Args:
            file_path: Path to audio file
            tolerance: Frequency tolerance for note matching
            min_note_duration: Minimum duration for a note to be considered
            
        Returns:
            Dictionary containing transcription results
        """
        print(f"Transcribing: {os.path.basename(file_path)}")
        
        # Load audio
        audio_data, duration = self.audio_processor.load_audio(file_path)
        
        # Extract pitch contour
        times, frequencies = self.audio_processor.extract_pitch_contour(audio_data)
        
        # Smooth frequencies
        smoothed_frequencies = self.audio_processor.smooth_frequencies(frequencies)
        
        # Convert to sargam notes
        sargam_notes = self.sargam_converter.frequencies_to_sargam_sequence(
            smoothed_frequencies, tolerance
        )
        
        # Detect note onsets
        onset_times = self.audio_processor.detect_note_onsets(audio_data)
        
        # Create note segments
        note_segments = self._create_note_segments(
            times, sargam_notes, onset_times, min_note_duration
        )
        
        # Create transcription result
        transcription = {
            'file_path': file_path,
            'duration': duration,
            'base_frequency': self.sargam_converter.base_frequency,
            'timestamp': datetime.now().isoformat(),
            'note_segments': note_segments,
            'raw_data': {
                'times': times.tolist(),
                'frequencies': smoothed_frequencies.tolist(),
                'sargam_sequence': sargam_notes
            }
        }
        
        self.last_transcription = transcription
        return transcription
    
    def _create_note_segments(self, times: np.ndarray, sargam_notes: List[Optional[str]], 
                            onset_times: np.ndarray, min_duration: float) -> List[Dict]:
        """
        Create note segments from continuous sargam sequence
        
        Args:
            times: Time array
            sargam_notes: Sargam note sequence
            onset_times: Detected onset times
            min_duration: Minimum note duration
            
        Returns:
            List of note segments with start time, end time, and note
        """
        segments = []
        current_note = None
        start_time = 0
        
        for i, (time, note) in enumerate(zip(times, sargam_notes)):
            if note != current_note:
                # End previous note if it exists and meets minimum duration
                if current_note is not None and (time - start_time) >= min_duration:
                    segments.append({
                        'note': current_note,
                        'start_time': start_time,
                        'end_time': time,
                        'duration': time - start_time
                    })
                
                # Start new note
                if note is not None:
                    current_note = note
                    start_time = time
                else:
                    current_note = None
        
        # Handle the last note
        if current_note is not None and len(times) > 0:
            end_time = times[-1]
            if (end_time - start_time) >= min_duration:
                segments.append({
                    'note': current_note,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time
                })
        
        return segments
    
    def format_transcription_text(self, transcription: Dict, notes_only: bool = False) -> str:
        """
        Format transcription as readable text
        
        Args:
            transcription: Transcription dictionary
            notes_only: If True, return only the sargam notes sequence
            
        Returns:
            Formatted text representation
        """
        segments = transcription['note_segments']
        
        if not segments:
            return "No clear notes detected in the audio."
        
        # Create compact notation
        compact_notes = [seg['note'] for seg in segments]
        
        if notes_only:
            return " ".join(compact_notes)
        
        text_lines = []
        text_lines.append(f"🎵 Sargam Transcription")
        text_lines.append(f"File: {os.path.basename(transcription['file_path'])}")
        text_lines.append(f"Duration: {transcription['duration']:.2f} seconds")
        text_lines.append(f"Base Sa: {transcription['base_frequency']:.2f} Hz")
        text_lines.append("-" * 50)
        
        # Create timeline representation
        text_lines.append("Timeline:")
        for segment in segments:
            start = segment['start_time']
            duration = segment['duration']
            note = segment['note']
            text_lines.append(f"{start:6.2f}s - {start+duration:6.2f}s: {note:>4} ({duration:.2f}s)")
        
        text_lines.append("-" * 50)
        
        text_lines.append("Compact Notation:")
        text_lines.append(" ".join(compact_notes))
        
        return "\n".join(text_lines)
    
    def save_transcription(self, transcription: Dict, output_path: str):
        """
        Save transcription to JSON file
        
        Args:
            transcription: Transcription dictionary
            output_path: Output file path
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcription, f, indent=2, ensure_ascii=False)
        
        print(f"Transcription saved to: {output_path}")
    
    def save_transcription_text(self, transcription: Dict, output_path: str, notes_only: bool = False):
        """
        Save transcription as readable text file
        
        Args:
            transcription: Transcription dictionary
            output_path: Output text file path
            notes_only: If True, save only the sargam notes sequence
        """
        text_content = self.format_transcription_text(transcription, notes_only)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"Text transcription saved to: {output_path}")
    
    def plot_transcription(self, transcription: Dict, output_path: Optional[str] = None):
        """
        Create a visualization of the transcription
        
        Args:
            transcription: Transcription dictionary
            output_path: Optional path to save the plot
        """
        raw_data = transcription['raw_data']
        times = np.array(raw_data['times'])
        frequencies = np.array(raw_data['frequencies'])
        segments = transcription['note_segments']
        
        plt.figure(figsize=(15, 8))
        
        # Plot frequency contour
        plt.subplot(2, 1, 1)
        plt.plot(times, frequencies, 'b-', alpha=0.7, linewidth=1)
        plt.ylabel('Frequency (Hz)')
        plt.title('Pitch Contour')
        plt.grid(True, alpha=0.3)
        
        # Highlight note segments
        for segment in segments:
            start = segment['start_time']
            end = segment['end_time']
            plt.axvspan(start, end, alpha=0.3, color='orange')
            
            # Add note labels
            mid_time = (start + end) / 2
            if mid_time < times[-1]:
                plt.text(mid_time, plt.ylim()[1] * 0.9, segment['note'], 
                        ha='center', va='center', fontweight='bold')
        
        # Plot sargam timeline
        plt.subplot(2, 1, 2)
        note_y_positions = {}
        unique_notes = list(set(seg['note'] for seg in segments))
        for i, note in enumerate(sorted(unique_notes)):
            note_y_positions[note] = i
        
        for segment in segments:
            start = segment['start_time']
            end = segment['end_time']
            note = segment['note']
            y_pos = note_y_positions[note]
            
            plt.barh(y_pos, end - start, left=start, height=0.8, 
                    alpha=0.7, edgecolor='black')
            plt.text((start + end) / 2, y_pos, note, 
                    ha='center', va='center', fontweight='bold')
        
        plt.yticks(range(len(unique_notes)), sorted(unique_notes))
        plt.xlabel('Time (seconds)')
        plt.ylabel('Sargam Notes')
        plt.title('Sargam Timeline')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to: {output_path}")
        else:
            plt.show()
    
    def set_base_frequency_from_audio(self, file_path: str, 
                                    reference_note: str = 'Sa') -> float:
        """
        Auto-detect base frequency from a reference audio file
        
        Args:
            file_path: Path to reference audio file
            reference_note: The sargam note this audio represents
            
        Returns:
            Detected base frequency
        """
        audio_data, _ = self.audio_processor.load_audio(file_path)
        frequencies = self.audio_processor.extract_fundamental_frequencies(audio_data)
        
        # Take the median frequency as the reference
        valid_frequencies = [f for f in frequencies if f > 0]
        if valid_frequencies:
            detected_freq = np.median(valid_frequencies)
            
            # Adjust based on reference note
            if reference_note != 'Sa':
                ratio = self.sargam_converter.sargam_ratios.get(reference_note, 1.0)
                detected_freq = detected_freq / ratio
            
            self.sargam_converter.set_base_frequency(detected_freq)
            print(f"Base frequency set to: {detected_freq:.2f} Hz")
            return detected_freq
        
        return self.sargam_converter.base_frequency
