from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
import whisper
import os
import uuid
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
RESPONSE_FOLDER = "responses"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESPONSE_FOLDER, exist_ok=True)

# Load Whisper model
model = whisper.load_model("base")

# Hugging Face API
HUGGINGFACE_API_KEY = "HUGGINGFACE_API_KEY"  #Replace with your api key
HF_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
    "Content-Type": "application/json"
}

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files or 'role' not in request.form:
        return jsonify({'error': 'Audio file and role are required'}), 400

    role = request.form['role']
    audio = request.files['audio']
    audio_filename = f"{uuid.uuid4()}.wav"
    audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
    audio.save(audio_path)

    # Transcribe user speech
    result = model.transcribe(audio_path)
    user_text = result['text'].strip()
    print("User said:", user_text)

    # Prepare interview-style prompt
    prompt = (
        f"You are a job interviewer for the role of {role}. "
        f"Evaluate the following candidate response:\n"
        f"Candidate: {user_text}\n\n"
        f"Give constructive feedback and optionally a follow-up question to improve their answer."
    )

    try:
        payload = {
            "inputs": prompt,
            "parameters": {"return_full_text": False}
        }
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        reply_text = response.json()[0]['generated_text'].strip()
        print("Interview Feedback:", reply_text)

    except Exception as e:
        print("Error with Hugging Face API:", e)
        reply_text = "Sorry, I couldn't evaluate your answer right now."

    # Convert to audio
    tts = gTTS(reply_text)
    response_filename = f"{uuid.uuid4()}.mp3"
    response_path = os.path.join(RESPONSE_FOLDER, response_filename)
    tts.save(response_path)

    return jsonify({
        "audio_url": f"http://localhost:5000/audio/{response_filename}",
        "reply_text": reply_text,
        "transcription": user_text
    })

@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(RESPONSE_FOLDER, filename)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
