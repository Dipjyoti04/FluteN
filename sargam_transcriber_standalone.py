#!/usr/bin/env python3
"""
Sargam Transcriber - Standalone Version
A simple app that converts audio to Indian classical music notes (Sargam).
"""
import os
import sys
import numpy as np
import soundfile as sf
import librosa
from scipy import signal
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.lang import Builder

# Set window size for desktop
if platform != 'android':
    Window.size = (400, 700)

# Kivy UI
KV = '''
<MainScreen>:
    orientation: 'vertical'
    padding: 20
    spacing: 20
    
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.9
        spacing: 20
        
        Label:
            text: 'Sargam Transcriber'
            font_size: '24sp'
            size_hint_y: 0.15
            
        Button:
            text: 'Load Audio File'
            size_hint_y: 0.15
            on_release: app.load_audio()
            
        Button:
            text: 'Record Audio'
            size_hint_y: 0.15
            on_release: app.start_recording()
            
        Button:
            text: 'Stop Recording'
            size_hint_y: 0.15
            disabled: not app.recording
            on_release: app.stop_recording()
            
        Button:
            text: 'Transcribe to Sargam'
            size_hint_y: 0.15
            disabled: not app.audio_loaded
            on_release: app.transcribe_audio()
            
        ScrollView:
            Label:
                id: output_text
                text: 'Ready to transcribe audio to sargam notes!'
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                padding: 10, 10
                
    ProgressBar:
        id: progress
        size_hint_y: 0.05
        max: 1.0
        value: 0.0
'''

class MainScreen(BoxLayout):
    pass

class SargamTranscriberApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio_data = None
        self.sample_rate = 44100
        self.recording = False
        self.audio_loaded = False
        self.recording_file = 'recording.wav'
        
    def build(self):
        self.title = 'Sargam Transcriber'
        return Builder.load_string(KV)
    
    def update_progress(self, value):
        self.root.ids.progress.value = value
    
    def update_text(self, text):
        self.root.ids.output_text.text = text
    
    def load_audio(self, path=None):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            from android.storage import app_storage_path
            
            def process_audio(uri):
                # This is a placeholder - on Android, you'd use ContentResolver
                self.update_text("Audio loading not implemented for Android in this demo")
            
            from plyer import filechooser
            filechooser.open_file(on_selection=process_audio)
        else:
            # For desktop
            from tkinter.filedialog import askopenfilename
            from tkinter import Tk
            
            root = Tk()
            root.withdraw()
            file_path = askopenfilename(
                title="Select Audio File",
                filetypes=[("Audio Files", "*.wav *.mp3 *.ogg")]
            )
            
            if file_path:
                try:
                    self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
                    self.audio_loaded = True
                    self.update_text(f"Loaded: {os.path.basename(file_path)}")
                except Exception as e:
                    self.update_text(f"Error loading file: {str(e)}")
    
    def start_recording(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
            
            from jnius import autoclass
            MediaRecorder = autoclass('android.media.MediaRecorder')
            AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
            OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
            AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
            
            self.recorder = MediaRecorder()
            self.recorder.setAudioSource(AudioSource.MIC)
            self.recorder.setOutputFormat(OutputFormat.THREE_GPP)
            self.recorder.setOutputFile(os.path.join(
                os.getenv('EXTERNAL_STORAGE'),
                'Download',
                'recording.3gp'
            ))
            self.recorder.setAudioEncoder(AudioEncoder.AMR_NB)
            self.recorder.prepare()
            self.recorder.start()
            self.recording = True
            self.update_text("Recording started...")
        else:
            import sounddevice as sd
            import soundfile as sf
            
            self.recording = True
            self.recording_frames = []
            
            def callback(indata, frames, time, status):
                if status:
                    print(status, file=sys.stderr)
                if self.recording:
                    self.recording_frames.append(indata.copy())
            
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=callback,
                dtype='float32'
            )
            self.stream.start()
            self.update_text("Recording started... (Desktop mode)")
    
    def stop_recording(self):
        if not self.recording:
            return
            
        self.recording = False
        
        if platform == 'android':
            self.recorder.stop()
            self.recorder.release()
            self.audio_loaded = True
            self.update_text("Recording saved to Download/recording.3gp")
        else:
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()
                
                if hasattr(self, 'recording_frames'):
                    self.audio_data = np.concatenate(self.recording_frames, axis=0)
                    sf.write(self.recording_file, self.audio_data, self.sample_rate)
                    self.audio_loaded = True
                    self.update_text(f"Recording saved as {self.recording_file}")
    
    def transcribe_audio(self):
        if self.audio_data is None or not self.audio_loaded:
            self.update_text("No audio loaded to transcribe!")
            return
            
        self.update_text("Transcribing audio to sargam...")
        
        try:
            # Simple pitch detection using autocorrelation
            def get_pitch(audio, sr, frame_size=2048, hop_size=512):
                # Apply window function
                window = np.hanning(frame_size)
                audio = audio[:len(audio) - (len(audio) % hop_size)]
                frames = np.lib.stride_tricks.as_strided(
                    audio,
                    shape=((len(audio) - frame_size) // hop_size + 1, frame_size),
                    strides=(audio.strides[0] * hop_size, audio.strides[0])
                )
                
                # Apply window
                frames = frames * window
                
                # Autocorrelation
                autocorr = np.fft.irfft(np.abs(np.fft.rfft(frames, n=frame_size*2))**2, axis=1)
                autocorr = autocorr[:, :frame_size]
                
                # Find peaks
                peaks = np.argmax(autocorr[:, 20:], axis=1) + 20  # Skip first 20 samples
                
                # Convert to frequency
                freqs = sr / peaks.astype(float)
                return freqs
            
            # Get pitches
            pitches = get_pitch(self.audio_data, self.sample_rate)
            
            # Convert frequencies to sargam notes
            def freq_to_note(freq):
                if freq <= 0:
                    return ""
                    
                # A4 = 440 Hz, 12 semitones per octave
                note_num = 12 * (np.log2(freq) - np.log2(440)) + 69
                note_num = int(round(note_num))
                
                # Sargam notes (Sa Re Ga Ma Pa Dha Ni)
                notes = ['Sa', 'Re', 'Ga', 'Ma', 'Pa', 'Dha', 'Ni']
                
                # Map to Indian classical notes (simplified)
                note_index = (note_num - 45) % 12  # Adjust for C as Sa
                if 0 <= note_index < len(notes):
                    return notes[note_index]
                return ""
            
            # Convert all pitches to notes
            notes = [freq_to_note(p) for p in pitches if p > 0]
            
            # Group and count consecutive notes
            if not notes:
                self.update_text("No notes detected in the audio.")
                return
                
            current_note = notes[0]
            count = 1
            result = []
            
            for note in notes[1:]:
                if note == current_note:
                    count += 1
                else:
                    if current_note:  # Only add if not empty
                        result.append(f"{current_note}")
                    current_note = note
                    count = 1
            
            # Add the last note
            if current_note:
                result.append(current_note)
            
            # Display the result
            self.update_text("\n".join(["Transcription complete:", " ".join(result)]))
            
        except Exception as e:
            self.update_text(f"Error during transcription: {str(e)}")

if __name__ == '__main__':
    # Install required packages if not found
    try:
        import numpy
        import soundfile
        import librosa
        import scipy
        import kivy
    except ImportError:
        print("Installing required packages...")
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                             "numpy", "soundfile", "librosa", "scipy", "kivy"])
        
        # Additional platform-specific dependencies
        if sys.platform != 'android':
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "sounddevice", "pyaudio"])
    
    SargamTranscriberApp().run()
