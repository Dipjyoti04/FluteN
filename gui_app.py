"""
Professional GUI Application for Audio to Sargam Transcription
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json
from pathlib import Path
import time

from transcriber import MusicTranscriber
from audio_player import AudioPlayer
from drag_drop import DropZone

class SargamTranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Sargam Transcriber Pro")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize audio player
        self.audio_player = AudioPlayer()
        
        # Variables
        self.transcriber = MusicTranscriber()
        self.current_audio_file = None
        self.current_transcription = None
        self.audio_segments = []
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.setup_drag_drop()
        
    def setup_styles(self):
        """Configure custom styles for the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Sargam.TLabel', font=('Consolas', 11), background='#e8f4fd', 
                       foreground='#2c5aa0', padding=5)
        style.configure('Line.TLabel', font=('Arial', 10), background='#fff8dc', 
                       foreground='#8b4513', padding=3)
        
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎵 Sargam Transcriber Pro", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # File input section
        self.create_file_input_section(main_frame)
        
        # Progress section
        self.create_progress_section(main_frame)
        
        # Settings section
        self.create_settings_section(main_frame)
        
        # Results section
        self.create_results_section(main_frame)
        
    def create_file_input_section(self, parent):
        """Create file input section with drag-drop area"""
        file_frame = ttk.LabelFrame(parent, text="Audio File Input", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Enhanced drag and drop zone
        self.drop_zone = DropZone(file_frame, callback=self.handle_file_input)
        self.drop_zone.pack(fill=tk.X, pady=(0, 10), ipady=20)
        
        # Control buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X)
        
        self.select_button = ttk.Button(button_frame, text="📁 Select Audio File", 
                                       command=self.select_file)
        self.select_button.pack(side=tk.LEFT)
        
        # Current file label
        self.file_label = ttk.Label(button_frame, text="No file selected", 
                                   foreground='gray')
        self.file_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Transcribe button
        self.transcribe_button = ttk.Button(button_frame, text="🎼 Start Transcription", 
                                           command=self.start_transcription, state=tk.DISABLED)
        self.transcribe_button.pack(side=tk.RIGHT)
        
    def create_progress_section(self, parent):
        """Create progress tracking section"""
        self.progress_frame = ttk.LabelFrame(parent, text="Transcription Progress", padding=10)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.progress_frame.pack_forget()  # Initially hidden
        
        self.progress_label = ttk.Label(self.progress_frame, text="Initializing...")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
    def create_settings_section(self, parent):
        """Create settings section"""
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Base frequency setting
        freq_frame = ttk.Frame(settings_frame)
        freq_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(freq_frame, text="Base Sa Frequency (Hz):").pack(side=tk.LEFT)
        self.freq_var = tk.StringVar(value="261.63")
        freq_entry = ttk.Entry(freq_frame, textvariable=self.freq_var, width=10)
        freq_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Tolerance setting
        tol_frame = ttk.Frame(settings_frame)
        tol_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(tol_frame, text="Frequency Tolerance (Hz):").pack(side=tk.LEFT)
        self.tolerance_var = tk.StringVar(value="50.0")
        tol_entry = ttk.Entry(tol_frame, textvariable=self.tolerance_var, width=10)
        tol_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Minimum duration setting
        dur_frame = ttk.Frame(settings_frame)
        dur_frame.pack(fill=tk.X)
        
        ttk.Label(dur_frame, text="Min Note Duration (s):").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="0.1")
        dur_entry = ttk.Entry(dur_frame, textvariable=self.duration_var, width=10)
        dur_entry.pack(side=tk.LEFT, padx=(10, 0))
        
    def create_results_section(self, parent):
        """Create results display section"""
        self.results_frame = ttk.LabelFrame(parent, text="Transcription Results", padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self.results_frame.pack_forget()  # Initially hidden
        
        # Results toolbar
        toolbar_frame = ttk.Frame(self.results_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="💾 Export Text", 
                  command=self.export_text).pack(side=tk.LEFT)
        ttk.Button(toolbar_frame, text="💾 Export JSON", 
                  command=self.export_json).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(toolbar_frame, text="🔄 Clear Results", 
                  command=self.clear_results).pack(side=tk.RIGHT)
        
        # Scrollable results area
        canvas_frame = ttk.Frame(self.results_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # Drag-drop is now handled by DropZone widget
        pass
            
    def handle_file_input(self, file_path):
        """Handle file input from drag-drop or selection"""
        if file_path is None:
            # Open file dialog
            self.select_file()
        else:
            # Load dropped file
            self.load_audio_file(file_path)
            
    def select_file(self):
        """Open file dialog to select audio file"""
        file_types = [
            ("Audio Files", "*.mp3 *.wav *.flac *.m4a *.ogg"),
            ("MP3 Files", "*.mp3"),
            ("WAV Files", "*.wav"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=file_types
        )
        
        if file_path:
            self.load_audio_file(file_path)
            
    def load_audio_file(self, file_path):
        """Load and validate audio file"""
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found!")
            return
            
        # Check file extension
        valid_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in valid_extensions:
            messagebox.showerror("Error", "Unsupported file format!")
            return
            
        self.current_audio_file = file_path
        filename = os.path.basename(file_path)
        self.file_label.config(text=f"Selected: {filename}", foreground='green')
        self.transcribe_button.config(state=tk.NORMAL)
        
        # Update drop zone to success state
        self.drop_zone.set_success_state(filename)
        
        # Load audio for playback
        self.audio_player.load_audio_file(file_path)
        
    def start_transcription(self):
        """Start transcription in a separate thread"""
        if not self.current_audio_file:
            messagebox.showerror("Error", "Please select an audio file first!")
            return
            
        # Update settings
        try:
            base_freq = float(self.freq_var.get())
            tolerance = float(self.tolerance_var.get())
            min_duration = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid settings values!")
            return
            
        # Show progress
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar.start()
        self.transcribe_button.config(state=tk.DISABLED)
        
        # Start transcription thread
        thread = threading.Thread(
            target=self.transcribe_audio,
            args=(base_freq, tolerance, min_duration)
        )
        thread.daemon = True
        thread.start()
        
    def transcribe_audio(self, base_freq, tolerance, min_duration):
        """Perform audio transcription (runs in separate thread)"""
        try:
            # Update progress
            self.root.after(0, lambda: self.progress_label.config(text="Loading audio file..."))
            
            # Set base frequency
            self.transcriber.sargam_converter.set_base_frequency(base_freq)
            
            # Update progress
            self.root.after(0, lambda: self.progress_label.config(text="Extracting pitch information..."))
            
            # Perform transcription
            transcription = self.transcriber.transcribe_audio_file(
                self.current_audio_file,
                tolerance=tolerance,
                min_note_duration=min_duration
            )
            
            # Update progress
            self.root.after(0, lambda: self.progress_label.config(text="Processing results..."))
            
            # Create line segments for display
            segments = self.create_line_segments(transcription)
            
            # Update GUI with results
            self.root.after(0, lambda: self.display_results(transcription, segments))
            
        except Exception as e:
            self.root.after(0, lambda: self.handle_transcription_error(str(e)))
            
    def create_line_segments(self, transcription):
        """Create line segments from transcription for display"""
        segments = transcription['note_segments']
        if not segments:
            return []
            
        # Group segments into lines (every 8-12 notes or 10-15 seconds)
        lines = []
        current_line = []
        current_duration = 0
        
        for segment in segments:
            current_line.append(segment)
            current_duration += segment['duration']
            
            # Create new line if we have enough notes or duration
            if len(current_line) >= 10 or current_duration >= 12:
                lines.append(current_line)
                current_line = []
                current_duration = 0
                
        # Add remaining segments
        if current_line:
            lines.append(current_line)
            
        return lines
        
    def display_results(self, transcription, line_segments):
        """Display transcription results in the GUI"""
        self.current_transcription = transcription
        self.audio_segments = line_segments
        
        # Hide progress and show results
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Display file info
        info_frame = ttk.Frame(self.scrollable_frame)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text=f"File: {os.path.basename(self.current_audio_file)}", 
                 style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Duration: {transcription['duration']:.1f}s | "
                                  f"Base Sa: {transcription['base_frequency']:.1f} Hz | "
                                  f"Total Notes: {len(transcription['note_segments'])}").pack(anchor=tk.W)
        
        # Display line by line
        for i, line in enumerate(line_segments):
            self.create_line_display(i + 1, line)
            
        # Re-enable transcribe button
        self.transcribe_button.config(state=tk.NORMAL)
        
    def create_line_display(self, line_number, segments):
        """Create display for a single line of transcription"""
        line_frame = ttk.Frame(self.scrollable_frame)
        line_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        # Line header with play button
        header_frame = ttk.Frame(line_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Play button for this line
        start_time = segments[0]['start_time']
        end_time = segments[-1]['end_time']
        
        play_btn = ttk.Button(header_frame, text="▶️", width=3,
                             command=lambda: self.play_segment(start_time, end_time))
        play_btn.pack(side=tk.LEFT)
        
        # Line number and timing
        ttk.Label(header_frame, 
                 text=f"Line {line_number} ({start_time:.1f}s - {end_time:.1f}s)",
                 style='Header.TLabel').pack(side=tk.LEFT, padx=(10, 0))
        
        # Transcription text (placeholder - you can add actual lyrics here)
        text_frame = ttk.Frame(line_frame)
        text_frame.pack(fill=tk.X, pady=(0, 5))
        
        transcription_text = f"[Audio segment {line_number}]"  # Placeholder
        ttk.Label(text_frame, text=f"Transcription: {transcription_text}", 
                 style='Line.TLabel').pack(anchor=tk.W, fill=tk.X)
        
        # Sargam notes
        sargam_frame = ttk.Frame(line_frame)
        sargam_frame.pack(fill=tk.X)
        
        sargam_notes = " ".join([seg['note'] for seg in segments])
        ttk.Label(sargam_frame, text=f"Sargam: {sargam_notes}", 
                 style='Sargam.TLabel').pack(anchor=tk.W, fill=tk.X)
        
    def play_segment(self, start_time, end_time):
        """Play audio segment"""
        if not self.current_audio_file:
            messagebox.showwarning("Warning", "No audio file loaded!")
            return
            
        success = self.audio_player.play_segment(start_time, end_time)
        if not success:
            messagebox.showerror("Error", "Failed to play audio segment!")
        
    def handle_transcription_error(self, error_msg):
        """Handle transcription errors"""
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        self.transcribe_button.config(state=tk.NORMAL)
        messagebox.showerror("Transcription Error", f"An error occurred:\n{error_msg}")
        
    def export_text(self):
        """Export transcription as text file"""
        if not self.current_transcription:
            messagebox.showwarning("Warning", "No transcription to export!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.transcriber.save_transcription_text(self.current_transcription, file_path)
            messagebox.showinfo("Success", f"Transcription exported to:\n{file_path}")
            
    def export_json(self):
        """Export transcription as JSON file"""
        if not self.current_transcription:
            messagebox.showwarning("Warning", "No transcription to export!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.transcriber.save_transcription(self.current_transcription, file_path)
            messagebox.showinfo("Success", f"Transcription data exported to:\n{file_path}")
            
    def clear_results(self):
        """Clear transcription results"""
        self.results_frame.pack_forget()
        self.current_transcription = None
        self.audio_segments = []
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = SargamTranscriberGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
