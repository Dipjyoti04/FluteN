# Audio to Sargam Transcriber

A Python program that converts audio files into Indian classical music sargam notation (Sa Re Ga Ma Pa Dha Ni) with automatic transcription.

## Features

- **Audio Processing**: Extracts pitch information from various audio formats
- **Sargam Conversion**: Maps frequencies to traditional sargam notes
- **Multiple Octaves**: Supports lower (₋), middle, and upper (₊) octaves
- **Komal Notes**: Includes flat notes (♭) for complete notation
- **Visual Output**: Generates timeline plots and frequency analysis
- **Flexible Input**: Command-line and interactive modes
- **Export Options**: JSON data and readable text formats

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode
```bash
python main.py
```

### Command Line Mode
```bash
python main.py audio_file.wav [options]
```

#### Options:
- `--base-freq`: Base frequency for Sa (default: 261.63 Hz)
- `--tolerance`: Frequency tolerance for note matching (default: 50 Hz)
- `--min-duration`: Minimum note duration (default: 0.1s)
- `--output-dir`: Output directory (default: output)
- `--reference-audio`: Reference file to auto-detect base frequency
- `--no-plot`: Skip visualization generation

### Examples

Basic transcription:
```bash
python main.py flute_recording.wav
```

With custom base frequency:
```bash
python main.py song.mp3 --base-freq 440.0 --tolerance 30
```

Auto-detect base frequency:
```bash
python main.py melody.wav --reference-audio reference_sa.wav
```

## Supported Audio Formats

- WAV, MP3, FLAC, M4A, OGG
- Any format supported by librosa

## Output Files

- `*_transcription.json`: Complete transcription data
- `*_sargam.txt`: Human-readable sargam notation
- `*_visualization.png`: Pitch contour and timeline plot

## Sargam Notation

The program uses traditional Indian classical music notation:

**Shuddha (Natural) Notes:**
- Sa, Re, Ga, Ma, Pa, Dha, Ni

**Komal (Flat) Notes:**
- Re♭, Ga♭, Dha♭, Ni♭

**Octave Markers:**
- Lower octave: ₋ (e.g., Sa₋)
- Middle octave: (no marker)
- Upper octave: ₊ (e.g., Sa₊)

## Tips for Better Results

1. **Clear Audio**: Use high-quality recordings with minimal background noise
2. **Single Instrument**: Works best with monophonic (single melody line) audio
3. **Reference Tuning**: Use a reference Sa recording for accurate pitch detection
4. **Adjust Tolerance**: Fine-tune frequency tolerance based on your audio quality

## Technical Details

- **Pitch Detection**: Uses librosa's piptrack and autocorrelation methods
- **Frequency Smoothing**: Applies median filtering and moving averages
- **Note Segmentation**: Detects note onsets and creates time-based segments
- **Just Intonation**: Uses traditional Indian music frequency ratios
