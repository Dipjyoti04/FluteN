"""
Sargam Transcriber Pro - Mobile App
Simplified version for Android build
"""
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.widget import Widget
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup

import threading
import json
from pathlib import Path

# Simplified transcriber for mobile
class SimpleMobileTranscriber:
    def __init__(self):
        self.base_frequency = 261.63
        
    def transcribe_audio_file(self, file_path):
        """Simplified transcription for mobile"""
        import time
        time.sleep(2)  # Simulate processing
        
        # Return mock transcription data
        return {
            'file_path': file_path,
            'duration': 120.0,
            'base_frequency': self.base_frequency,
            'note_segments': [
                {'note': 'Sa', 'start_time': 0.0, 'end_time': 1.0, 'duration': 1.0},
                {'note': 'Re', 'start_time': 1.0, 'end_time': 2.0, 'duration': 1.0},
                {'note': 'Ga', 'start_time': 2.0, 'end_time': 3.0, 'duration': 1.0},
                {'note': 'Ma', 'start_time': 3.0, 'end_time': 4.0, 'duration': 1.0},
                {'note': 'Pa', 'start_time': 4.0, 'end_time': 5.0, 'duration': 1.0},
                {'note': 'Dha', 'start_time': 5.0, 'end_time': 6.0, 'duration': 1.0},
                {'note': 'Ni', 'start_time': 6.0, 'end_time': 7.0, 'duration': 1.0},
                {'note': 'Sa', 'start_time': 7.0, 'end_time': 8.0, 'duration': 1.0},
            ]
        }

class CustomButton(Button):
    """Custom styled button"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.1, 0.45, 0.91, 1)  # Blue
        self.color = (1, 1, 1, 1)  # White text
        self.size_hint_y = None
        self.height = dp(50)

class PillNavigation(FloatLayout):
    """Pill-style bottom navigation"""
    
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.size_hint_y = None
        self.height = dp(80)
        self.create_nav()
    
    def create_nav(self):
        """Create navigation bar"""
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White
            self.nav_bg = RoundedRectangle(
                pos=(dp(50), dp(15)), 
                size=(dp(300), dp(50)),
                radius=[dp(25)]
            )
            Color(0.85, 0.87, 0.91, 1)  # Border
            Line(
                rounded_rectangle=(dp(50), dp(15), dp(300), dp(50), dp(25)),
                width=2
            )
        
        # Navigation buttons
        nav_box = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            size=(dp(300), dp(50))
        )
        
        buttons = [
            ('Home', 'home'),
            ('Results', 'results'),
            ('Playback', 'playback'),
            ('Settings', 'settings')
        ]
        
        for text, screen_name in buttons:
            btn = Button(
                text=text,
                size_hint=(0.25, 1),
                background_color=(0, 0, 0, 0),  # Transparent
                color=(0.42, 0.48, 0.6, 1),  # Gray
                on_release=lambda x, s=screen_name: self.navigate_to(s)
            )
            nav_box.add_widget(btn)
        
        self.add_widget(nav_box)
    
    def navigate_to(self, screen_name):
        """Navigate to screen"""
        self.screen_manager.current = screen_name

class HomeScreen(Screen):
    """Home/Dashboard screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        self.transcriber = SimpleMobileTranscriber()
        self.current_file = None
        self.build_ui()
    
    def build_ui(self):
        """Build home screen"""
        main_layout = FloatLayout()
        main_layout.canvas.before.clear()
        with main_layout.canvas.before:
            Color(0.94, 0.95, 0.97, 1)  # Background color
            self.bg = RoundedRectangle(pos=(0, 0), size=Window.size)
        
        # Content area
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(20), dp(20), dp(20), dp(100)],
            pos_hint={'top': 1}
        )
        
        # Title
        title = Label(
            text="Sargam Transcriber Pro",
            font_size=dp(24),
            color=(0.1, 0.17, 0.29, 1),
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(title)
        
        # Upload area
        upload_area = Widget(size_hint_y=None, height=dp(200))
        with upload_area.canvas:
            Color(0.91, 0.95, 0.98, 1)  # Light blue
            RoundedRectangle(pos=(0, 0), size=(dp(360), dp(200)), radius=[dp(15)])
        
        upload_label = Label(
            text="Tap to Upload Audio File",
            font_size=dp(18),
            color=(0.1, 0.17, 0.29, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        upload_area.add_widget(upload_label)
        
        # Make upload area clickable
        upload_btn = Button(
            text="",
            background_color=(0, 0, 0, 0),
            on_release=self.select_file
        )
        upload_area.add_widget(upload_btn)
        
        content.add_widget(upload_area)
        
        # Transcribe button
        self.transcribe_btn = CustomButton(
            text="Start Transcription",
            disabled=True,
            on_release=self.start_transcription
        )
        content.add_widget(self.transcribe_btn)
        
        # Status label
        self.status_label = Label(
            text="Select an audio file to begin",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(self.status_label)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def select_file(self, *args):
        """Open file selector"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # File chooser
        if platform == 'android':
            # For Android, show a simple input
            file_input = Label(
                text="Android file selection\nwould open here",
                size_hint_y=None,
                height=dp(100)
            )
            content.add_widget(file_input)
            
            # Mock file selection
            mock_btn = Button(
                text="Select Demo Audio",
                size_hint_y=None,
                height=dp(50),
                on_release=self.mock_file_select
            )
            content.add_widget(mock_btn)
        else:
            # Desktop file chooser
            filechooser = FileChooserListView(
                filters=['*.mp3', '*.wav', '*.flac', '*.m4a', '*.ogg']
            )
            content.add_widget(filechooser)
            
            select_btn = Button(
                text="Select",
                size_hint_y=None,
                height=dp(50),
                on_release=lambda x: self.file_selected(filechooser.selection[0] if filechooser.selection else None)
            )
            content.add_widget(select_btn)
        
        # Create popup
        self.file_popup = Popup(
            title="Select Audio File",
            content=content,
            size_hint=(0.9, 0.9)
        )
        self.file_popup.open()
    
    def mock_file_select(self, *args):
        """Mock file selection for demo"""
        self.current_file = "/demo/sample_audio.mp3"
        self.file_selected(self.current_file)
    
    def file_selected(self, file_path):
        """Handle file selection"""
        if file_path:
            self.current_file = file_path
            filename = os.path.basename(file_path)
            self.status_label.text = f"Selected: {filename}"
            self.transcribe_btn.disabled = False
        
        if hasattr(self, 'file_popup'):
            self.file_popup.dismiss()
    
    def start_transcription(self, *args):
        """Start transcription"""
        if not self.current_file:
            return
        
        self.status_label.text = "Transcribing..."
        self.transcribe_btn.disabled = True
        
        # Start in thread
        threading.Thread(target=self.transcribe_audio, daemon=True).start()
    
    def transcribe_audio(self):
        """Perform transcription"""
        try:
            transcription = self.transcriber.transcribe_audio_file(self.current_file)
            self.app.transcription_data = transcription
            
            Clock.schedule_once(lambda dt: self.transcription_complete())
        except Exception as e:
            Clock.schedule_once(lambda dt: self.transcription_error(str(e)))
    
    def transcription_complete(self):
        """Handle completion"""
        self.status_label.text = "Transcription completed! Check Results tab."
        self.transcribe_btn.disabled = False
    
    def transcription_error(self, error):
        """Handle error"""
        self.status_label.text = f"Error: {error}"
        self.transcribe_btn.disabled = False

class ResultsScreen(Screen):
    """Results screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'results'
        self.build_ui()
    
    def build_ui(self):
        """Build results screen"""
        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(0.94, 0.95, 0.97, 1)
            self.bg = RoundedRectangle(pos=(0, 0), size=Window.size)
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(20), dp(20), dp(20), dp(100)],
            pos_hint={'top': 1}
        )
        
        # Title
        title = Label(
            text="Transcription Results",
            font_size=dp(20),
            color=(0.1, 0.17, 0.29, 1),
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(title)
        
        # Results area
        scroll = ScrollView()
        self.results_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        
        scroll.add_widget(self.results_layout)
        content.add_widget(scroll)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Update results when entering screen"""
        self.display_results()
    
    def display_results(self):
        """Display transcription results"""
        self.results_layout.clear_widgets()
        
        if not hasattr(self.app, 'transcription_data') or not self.app.transcription_data:
            no_data = Label(
                text="No transcription data available.\nGo to Home to transcribe an audio file.",
                halign="center",
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(100)
            )
            self.results_layout.add_widget(no_data)
            return
        
        transcription = self.app.transcription_data
        segments = transcription.get('note_segments', [])
        
        # File info
        filename = os.path.basename(transcription.get('file_path', 'Unknown'))
        info_label = Label(
            text=f"File: {filename}\nDuration: {transcription.get('duration', 0):.1f}s",
            size_hint_y=None,
            height=dp(60),
            color=(0.1, 0.17, 0.29, 1)
        )
        self.results_layout.add_widget(info_label)
        
        # Sargam notes
        if segments:
            sargam_notes = " ".join([seg.get('note', '') for seg in segments])
            
            sargam_widget = Widget(size_hint_y=None, height=dp(80))
            with sargam_widget.canvas:
                Color(1, 1, 1, 1)  # White background
                RoundedRectangle(pos=(0, 0), size=(dp(360), dp(80)), radius=[dp(10)])
            
            sargam_label = Label(
                text=f"Sargam: {sargam_notes}",
                text_size=(dp(340), None),
                halign="left",
                valign="middle",
                color=(0.1, 0.17, 0.29, 1),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            sargam_widget.add_widget(sargam_label)
            self.results_layout.add_widget(sargam_widget)

class PlaybackScreen(Screen):
    """Playback screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'playback'
        self.build_ui()
    
    def build_ui(self):
        """Build playback screen"""
        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(0.94, 0.95, 0.97, 1)
            self.bg = RoundedRectangle(pos=(0, 0), size=Window.size)
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(20), dp(20), dp(20), dp(100)],
            pos_hint={'center_x': 0.5, 'top': 1}
        )
        
        title = Label(
            text="Playback & Edit",
            font_size=dp(20),
            color=(0.1, 0.17, 0.29, 1),
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(title)
        
        # Waveform placeholder
        waveform = Widget(size_hint_y=None, height=dp(120))
        with waveform.canvas:
            Color(0.91, 0.95, 0.98, 1)
            RoundedRectangle(pos=(0, 0), size=(dp(360), dp(120)), radius=[dp(15)])
        
        waveform_label = Label(
            text="Waveform Visualization",
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            color=(0.1, 0.17, 0.29, 1)
        )
        waveform.add_widget(waveform_label)
        content.add_widget(waveform)
        
        # Play button
        play_btn = CustomButton(
            text="Play / Pause",
            on_release=self.toggle_playback
        )
        content.add_widget(play_btn)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def toggle_playback(self, *args):
        """Toggle audio playback"""
        # Placeholder for playback functionality
        pass

class SettingsScreen(Screen):
    """Settings screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        self.build_ui()
    
    def build_ui(self):
        """Build settings screen"""
        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(0.94, 0.95, 0.97, 1)
            self.bg = RoundedRectangle(pos=(0, 0), size=Window.size)
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(20), dp(20), dp(20), dp(100)],
            pos_hint={'top': 1}
        )
        
        title = Label(
            text="Settings",
            font_size=dp(20),
            color=(0.1, 0.17, 0.29, 1),
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(title)
        
        # Settings options
        options = [
            "Base Frequency: 261.63 Hz",
            "Tolerance: 50.0 Hz",
            "Min Duration: 0.1s",
            "Theme: Light",
            "About Sargam Transcriber Pro"
        ]
        
        for option in options:
            option_widget = Widget(size_hint_y=None, height=dp(50))
            with option_widget.canvas:
                Color(1, 1, 1, 1)
                RoundedRectangle(pos=(0, 0), size=(dp(360), dp(50)), radius=[dp(10)])
            
            option_label = Label(
                text=option,
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                color=(0.1, 0.17, 0.29, 1)
            )
            option_widget.add_widget(option_label)
            content.add_widget(option_widget)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)

class SargamTranscriberApp(App):
    """Main application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Sargam Transcriber Pro"
        self.transcription_data = None
    
    def build(self):
        """Build the app"""
        # Set window size for desktop
        if platform not in ('android', 'ios'):
            Window.size = (400, 700)
        
        # Main container
        main_layout = FloatLayout()
        
        # Screen manager
        self.sm = ScreenManager()
        
        # Add screens
        screens = [
            HomeScreen(),
            ResultsScreen(),
            PlaybackScreen(),
            SettingsScreen()
        ]
        
        for screen in screens:
            screen.app = self
            self.sm.add_widget(screen)
        
        main_layout.add_widget(self.sm)
        
        # Add bottom navigation
        self.nav = PillNavigation(self.sm)
        main_layout.add_widget(self.nav)
        
        return main_layout

def main():
    """Run the app"""
    SargamTranscriberApp().run()

if __name__ == "__main__":
    main()
