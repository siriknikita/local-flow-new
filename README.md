# Whisper Transcription App

A web application that allows you to record audio from your microphone and get real-time transcription using OpenAI's Whisper API.

## Features

- 🎤 Record audio directly from your browser
- 🤖 Transcribe audio using OpenAI Whisper API
- 💬 Display transcription in real-time
- 🎨 Modern, responsive UI

## Setup

### Prerequisites

- Python 3.8+ (with `uv` package manager)
- Node.js (for Playwright tests)
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies using `uv`:
```bash
uv pip install -r requirements.txt
```

3. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

4. Run the backend server:
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Open `frontend/index.html` in a web browser, or serve it using a local server:
```bash
cd frontend
python -m http.server 8080
```

2. Open `http://localhost:8080` in your browser

## Usage

1. Click "Start Recording" to begin recording audio
2. Speak into your microphone
3. Click "Stop Recording" when finished
4. Wait for the transcription to appear

## API Endpoints

- `GET /` - Health check
- `POST /transcribe` - Transcribe audio file (multipart/form-data with 'file' field)

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required)
