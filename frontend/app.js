const API_URL = 'http://localhost:8000';

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const status = document.getElementById('status');
const transcriptionText = document.getElementById('transcriptionText');
const errorDiv = document.getElementById('error');

// Request microphone access and start recording
recordBtn.addEventListener('click', async () => {
    try {
        errorDiv.classList.remove('show');
        errorDiv.textContent = '';
        
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Initialize MediaRecorder
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });
        
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = async () => {
            // Stop all tracks to release microphone
            stream.getTracks().forEach(track => track.stop());
            
            // Create audio blob
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            
            // Send to backend for transcription
            await transcribeAudio(audioBlob);
        };
        
        // Start recording
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        status.textContent = '🔴 Recording...';
        status.className = 'status recording';
        transcriptionText.textContent = '';
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        showError('Failed to access microphone. Please check your permissions.');
        resetUI();
    }
});

// Stop recording
stopBtn.addEventListener('click', () => {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Update UI
        recordBtn.disabled = false;
        stopBtn.disabled = true;
        status.textContent = '⏳ Processing...';
        status.className = 'status processing';
    }
});

// Send audio to backend for transcription
async function transcribeAudio(audioBlob) {
    try {
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');
        
        const response = await fetch(`${API_URL}/transcribe`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to transcribe audio');
        }
        
        const data = await response.json();
        
        // Display transcription
        transcriptionText.textContent = data.transcription || 'No transcription available';
        status.textContent = '✅ Transcription complete!';
        status.className = 'status success';
        
    } catch (error) {
        console.error('Error transcribing audio:', error);
        showError(`Transcription failed: ${error.message}`);
        status.textContent = '';
        status.className = 'status';
    }
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
}

function resetUI() {
    recordBtn.disabled = false;
    stopBtn.disabled = true;
    status.textContent = '';
    status.className = 'status';
}
