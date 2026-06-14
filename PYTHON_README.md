# EchoType - Python Desktop Version

This is the Python desktop application version of EchoType using **PyQt6** for the UI and **OpenAI Whisper** for advanced speech-to-text capabilities.

## 🎯 Features

- **PyQt6 GUI**: Modern, responsive desktop interface
- **Text-to-Speech (TTS)**: Using `pyttsx3` for cross-platform audio
- **Speech-to-Text (STT)**: Using OpenAI **Whisper** for accurate transcription
- **Typing Tests**: Practice typing with audio prompts
- **Real-time Feedback**: Visual feedback with word color coding
- **WPM & Accuracy Metrics**: Track your progress

## 🛠️ Tech Stack

- **PyQt6**: Modern desktop UI framework
- **pyttsx3**: Cross-platform text-to-speech
- **openai-whisper**: Advanced speech recognition
- **SoundDevice & SoundFile**: Audio input/output
- **Python 3.9+**

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- macOS, Linux, or Windows

## 🚀 Setup & Installation

### 1. Clone and Switch to Python Branch

```bash
cd echotype
git checkout python-desktop
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

⚠️ **Note**: The first run of Whisper will download the model (~140MB for base model). Use smaller models for faster startup:
- `tiny`: ~39MB (fastest, least accurate)
- `base`: ~140MB (recommended, good balance)
- `small`: ~466MB
- `medium`: ~1.5GB
- `large`: ~2.9GB (most accurate, slowest)

### 4. Run the Application

```bash
python main.py
```

## 🎮 How to Use

1. **Start Test**: Click the "Start Test" button
2. **Listen**: Audio will play the word you need to type
3. **Type**: Type the word in the input field
4. **Submit**: Press SPACE to submit your answer
5. **Continue**: The app will play the next word
6. **Quit**: Press ESC at any time to end the test
7. **Results**: View your WPM, accuracy, and time

## 📁 Project Structure

```
src/python/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── audio_manager.py      # Text-to-speech functionality
│   ├── constants.py           # App configuration
│   ├── speech_recognizer.py   # Whisper STT integration
│   └── test_engine.py         # Typing test logic
└── ui/
    ├── __init__.py
    ├── home_screen.py         # Main test screen
    └── main_window.py         # Application window

main.py                         # Entry point
requirements.txt               # Python dependencies
```

## 🔧 Configuration

Edit `src/python/core/constants.py` to customize:

- Default paragraph for typing tests
- Speech rate, volume, and pitch
- Window size and appearance
- Keyboard shortcuts

## 🎙️ Future Enhancements

- [ ] Whisper speech-to-text integration in UI
- [ ] Custom word lists/paragraphs
- [ ] Result history and statistics
- [ ] Multiple difficulty levels
- [ ] Keyboard layout support
- [ ] Settings/preferences UI
- [ ] Dark/Light theme toggle
- [ ] Export results

## 🐛 Troubleshooting

### No sound output
- Check system volume
- Verify `pyttsx3` is properly installed
- Try reinstalling: `pip install --upgrade pyttsx3`

### Whisper model won't download
- Check internet connection
- Ensure sufficient disk space
- Try specifying a smaller model in code

### UI looks wrong
- Ensure PyQt6 is properly installed
- Update Qt bindings: `pip install --upgrade PyQt6`

## 📝 License

Same as original EchoType project

## 👨‍💻 Development

To contribute to the Python version:

1. Create a new feature branch
2. Make your changes
3. Test thoroughly
4. Submit a PR

### Running from Source (Development Mode)

```bash
python -m main
```

Or set `PYTHONPATH` and run:

```bash
PYTHONPATH=. python main.py
```
