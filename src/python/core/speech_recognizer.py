"""
Speech-to-text manager using OpenAI Whisper
"""

import whisper
from typing import Optional
import sounddevice as sd
import soundfile as sf
import numpy as np


class SpeechRecognizer:
    """Uses Whisper to recognize spoken words"""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize the speech recognizer
        
        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large)
                       Smaller models are faster but less accurate
        """
        self.model = whisper.load_model(model_name)
    
    def record_audio(self, duration: float = 5.0, sample_rate: int = 16000) -> np.ndarray:
        """
        Record audio from microphone
        
        Args:
            duration: Duration to record in seconds
            sample_rate: Sample rate in Hz
            
        Returns:
            Audio data as numpy array
        """
        print(f"Recording for {duration} seconds...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()
        return audio_data.flatten()
    
    def save_audio(self, audio_data: np.ndarray, filepath: str, sample_rate: int = 16000) -> None:
        """Save audio to file"""
        sf.write(filepath, audio_data, sample_rate)
    
    def transcribe(self, audio_path: Optional[str] = None, audio_data: Optional[np.ndarray] = None) -> str:
        """
        Transcribe audio to text
        
        Args:
            audio_path: Path to audio file
            audio_data: Audio data as numpy array
            
        Returns:
            Transcribed text
        """
        if audio_path:
            result = self.model.transcribe(audio_path)
        elif audio_data is not None:
            # Save to temporary file
            temp_path = "/tmp/whisper_temp.wav"
            self.save_audio(audio_data, temp_path)
            result = self.model.transcribe(temp_path)
        else:
            raise ValueError("Either audio_path or audio_data must be provided")
        
        return result['text'].strip()
    
    def record_and_transcribe(self, duration: float = 5.0) -> str:
        """
        Record and immediately transcribe audio
        
        Args:
            duration: Duration to record in seconds
            
        Returns:
            Transcribed text
        """
        audio_data = self.record_audio(duration)
        return self.transcribe(audio_data=audio_data)
