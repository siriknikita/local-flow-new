"""
Audio preprocessing utilities for format conversion and normalization.
Handles various audio formats and converts them to a format compatible with Whisper.
"""
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio format conversion and preprocessing."""
    
    @staticmethod
    def check_ffmpeg() -> bool:
        """Check if ffmpeg is available in the system."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True,
                timeout=5
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod
    def convert_to_wav(
        input_path: str,
        output_path: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1
    ) -> str:
        """
        Convert audio file to WAV format with specified sample rate and channels.
        
        Args:
            input_path: Path to input audio file
            output_path: Optional output path. If None, creates a temporary file.
            sample_rate: Target sample rate (default: 16000 Hz for Whisper)
            channels: Number of audio channels (default: 1 for mono)
        
        Returns:
            Path to converted WAV file
        
        Raises:
            RuntimeError: If ffmpeg is not available or conversion fails
        """
        if not AudioProcessor.check_ffmpeg():
            raise RuntimeError(
                "ffmpeg is not available. Please install ffmpeg to process audio files. "
                "Visit https://ffmpeg.org/download.html for installation instructions."
            )
        
        # Create temporary file if output_path not provided
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            output_path = temp_file.name
            temp_file.close()
        
        try:
            # Convert audio using ffmpeg
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-ar", str(sample_rate),  # Sample rate
                "-ac", str(channels),     # Audio channels
                "-y",                     # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"ffmpeg conversion failed: {error_msg}")
            
            if not os.path.exists(output_path):
                raise RuntimeError("ffmpeg conversion completed but output file not found")
            
            logger.info(f"Successfully converted audio: {input_path} -> {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio conversion timed out after 30 seconds")
        except Exception as e:
            # Clean up output file on error
            if output_path and os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except:
                    pass
            raise RuntimeError(f"Error during audio conversion: {str(e)}")
    
    @staticmethod
    def process_audio_file(
        input_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Process audio file: convert to WAV format suitable for Whisper.
        
        Args:
            input_path: Path to input audio file
            output_path: Optional output path. If None, creates a temporary file.
        
        Returns:
            Path to processed WAV file
        """
        # Check if file is already WAV format with correct settings
        # For simplicity, we'll always convert to ensure compatibility
        return AudioProcessor.convert_to_wav(input_path, output_path)
