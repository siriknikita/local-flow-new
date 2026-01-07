from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import Optional, Literal
import uvicorn
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local Whisper service
from whisper_service import whisper_service

app = FastAPI(title="Whisper Transcription API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Provider selection: 'local' or 'openai' (default: 'local')
TRANSCRIPTION_PROVIDER = os.getenv("TRANSCRIPTION_PROVIDER", "local").lower()


@app.get("/")
async def root():
    return {"message": "Whisper Transcription API is running"}


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file using local Whisper model or OpenAI API (based on provider setting).
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an audio file"
        )
    
    temp_file_path = None
    try:
        # Read the audio file
        audio_content = await file.read()
        
        # Determine file extension from content type or filename
        file_ext = ".webm"  # default
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1] or file_ext
        elif file.content_type:
            # Try to infer from content type
            content_type_map = {
                "audio/webm": ".webm",
                "audio/mp4": ".m4a",
                "audio/mpeg": ".mp3",
                "audio/wav": ".wav",
                "audio/ogg": ".ogg"
            }
            file_ext = content_type_map.get(file.content_type, ".webm")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        # Transcribe using selected provider
        if TRANSCRIPTION_PROVIDER == "local":
            logger.info("Using local Whisper model for transcription")
            result = whisper_service.transcribe(temp_file_path)
            
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown transcription error")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error transcribing audio: {error_msg}"
                )
            
            transcription_text = result.get("text", "")
            
            return JSONResponse(content={
                "transcription": transcription_text,
                "success": True,
                "language": result.get("language"),
                "provider": "local"
            })
        
        else:
            # Fallback to OpenAI (if needed in future)
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported transcription provider: {TRANSCRIPTION_PROVIDER}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {str(e)}")


@app.get("/model/info")
async def get_model_info():
    """Get information about the loaded Whisper model."""
    try:
        info = whisper_service.get_model_info()
        return JSONResponse(content=info)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting model info: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
