"""
WhisperService for local audio transcription using faster-whisper.
Implements lazy loading, caching, and error handling.
"""
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from faster_whisper import WhisperModel
from config import config
from audio_processor import AudioProcessor

logger = logging.getLogger(__name__)


class WhisperService:
    """Service for local Whisper transcription with lazy loading and caching."""
    
    _instance: Optional['WhisperService'] = None
    _model: Optional[WhisperModel] = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(WhisperService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize WhisperService (model loaded lazily)."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._model = None
            self._model_loaded = False
    
    def _load_model(self) -> None:
        """Lazy load the Whisper model if not already loaded."""
        if self._model_loaded and self._model is not None:
            return
        
        try:
            logger.info(f"Loading Whisper model: {config.model_name} on {config.device}")
            logger.info(f"Using compute type: {config.compute_type}")
            
            # Create cache directory if it doesn't exist
            os.makedirs(config.model_cache_dir, exist_ok=True)
            
            self._model = WhisperModel(
                model_size_or_path=config.model_size,
                device=config.device,
                compute_type=config.compute_type,
                download_root=config.model_cache_dir
            )
            
            self._model_loaded = True
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise RuntimeError(f"Failed to load Whisper model: {str(e)}")
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using the local Whisper model.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'en', 'es'). If None, auto-detect.
            task: Task type - 'transcribe' or 'translate'
            **kwargs: Additional transcription parameters
        
        Returns:
            Dictionary containing transcription results with keys:
            - text: Transcribed text
            - language: Detected language
            - segments: List of segment dictionaries
            - success: Boolean indicating success
        """
        # Ensure model is loaded
        self._load_model()
        
        # Process audio file to ensure compatibility
        processed_audio_path = None
        try:
            # Convert audio to WAV format if needed
            processed_audio_path = AudioProcessor.process_audio_file(audio_path)
            
            # Perform transcription
            logger.info(f"Transcribing audio: {audio_path}")
            
            segments, info = self._model.transcribe(
                processed_audio_path,
                language=language,
                task=task,
                **kwargs
            )
            
            # Collect segments and full text
            segment_list = []
            full_text_parts = []
            
            for segment in segments:
                segment_dict = {
                    "id": segment.id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }
                segment_list.append(segment_dict)
                full_text_parts.append(segment.text.strip())
            
            full_text = " ".join(full_text_parts).strip()
            
            result = {
                "text": full_text,
                "language": info.language,
                "language_probability": info.language_probability,
                "segments": segment_list,
                "success": True
            }
            
            logger.info(f"Transcription completed. Language: {info.language}, Text length: {len(full_text)}")
            return result
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return {
                "text": "",
                "language": None,
                "language_probability": None,
                "segments": [],
                "success": False,
                "error": str(e)
            }
        
        finally:
            # Clean up processed audio file if it was created
            if processed_audio_path and processed_audio_path != audio_path:
                try:
                    if os.path.exists(processed_audio_path):
                        os.unlink(processed_audio_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary audio file: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self._model_loaded:
            return {
                "loaded": False,
                "model_size": config.model_size,
                "device": config.device,
                "compute_type": config.compute_type
            }
        
        return {
            "loaded": True,
            "model_size": config.model_size,
            "device": config.device,
            "compute_type": config.compute_type,
            "model_name": config.model_name
        }


# Global service instance
whisper_service = WhisperService()
