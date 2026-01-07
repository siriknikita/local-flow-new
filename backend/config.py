"""
Configuration management for Whisper transcription service.
Supports environment variables for model selection and device configuration.
"""
import os
from typing import Literal
from dataclasses import dataclass


@dataclass
class WhisperConfig:
    """Configuration for Whisper model and transcription settings."""
    model_size: str = os.getenv("WHISPER_MODEL_SIZE", "turbo")
    device: Literal["cpu", "cuda"] = os.getenv("WHISPER_DEVICE", "cpu")
    compute_type: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    model_cache_dir: str = os.getenv("WHISPER_MODEL_CACHE_DIR", os.path.expanduser("~/.cache/whisper"))
    
    @property
    def model_name(self) -> str:
        """Get the full model name based on model_size."""
        return f"openai/whisper-{self.model_size}"
    
    def __post_init__(self):
        """Validate configuration values."""
        valid_sizes = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3", "turbo"]
        if self.model_size not in valid_sizes:
            raise ValueError(f"Invalid model_size: {self.model_size}. Must be one of {valid_sizes}")
        
        if self.device not in ["cpu", "cuda"]:
            raise ValueError(f"Invalid device: {self.device}. Must be 'cpu' or 'cuda'")
        
        valid_compute_types = ["int8", "int8_float16", "int16", "float16", "float32"]
        if self.compute_type not in valid_compute_types:
            raise ValueError(f"Invalid compute_type: {self.compute_type}. Must be one of {valid_compute_types}")


# Global configuration instance
config = WhisperConfig()
