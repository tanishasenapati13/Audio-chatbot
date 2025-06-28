from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
import whisper
import os
import uuid
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Directories for audio files
UPLOAD_FOLDER = "uploads"
RESPONSE_FOLDER = "responses"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESPONSE_FOLDER, exist_ok=True)

# Load Whisper model
model = whisper.load_model("base")

# Hugging Face API setup (Free Model)
HUGGINGFACE_API_KEY = "HUGGINGFACE_API_KEY"  # Your key
HF_MODEL = "" # FREE model

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
    "Content-Type": "application/json"
}

@app.route('/process_audio', methods=['POST'])
def process_audio():
    # Validate request
    if 'audio' not in request.files or 'role' not in request.form:
        return jsonify({'error': 'Audio file and role are required'}), 400

    # Save audio input
    role = request.form['role']
    audio = request.files['audio']
    audio_filename = f"{uuid.uuid4()}.wav"
    audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
    audio.save(audio_path)

    # Transcribe audio using Whisper
    try:
        result = model.transcribe(audio_path)
        user_text = result['text'].strip()
        print("User said:", user_text)
    except Exception as e:
        print("Transcription failed:", e)
        return jsonify({'error': 'Transcription failed'}), 500

    user_text_lower = user_text.lower()

    # Initial mock interview prompt
    start_phrases = [
        "start the interview",
        "ask me interview questions",
        "ask me questions",
        "begin interview",
        "ask me questions related to",
        "do a mock interview"
    ]

    # Check if user is starting the mock interview
    if any(phrase in user_text_lower for phrase in start_phrases):
        reply_text = "Sure, let's begin. Can you please introduce yourself?"
    else:
        # Generate feedback + follow-up prompt
        prompt = (
            f"You are an expert interviewer for the job role of {role}. "
            f"A candidate gave the following answer:\n\n"
            f"'{user_text}'\n\n"
            f"Evaluate it and provide professional feedback. "
            f"Also, suggest one relevant follow-up question if applicable."
        )

        try:
            payload = {
                "inputs": prompt,
                "parameters": {"return_full_text": False}
            }

            response = requests.post(
                f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                headers=headers,
                json=payload,
                timeout=20
            )
            response.raise_for_status()

            result_json = response.json()
            reply_text = result_json[0].get('generated_text', '').strip()

            # Fallback if the model returns nothing
            if not reply_text:
                reply_text = "Thank you. Please elaborate more on your response."

        except Exception as e:
            print("Error with Hugging Face API:", e)
            reply_text = "Sorry, I couldn't evaluate your answer right now. Please try again shortly."

    # Convert reply text to speech using gTTS
    try:
        tts = gTTS(reply_text)
        response_filename = f"{uuid.uuid4()}.mp3"
        response_path = os.path.join(RESPONSE_FOLDER, response_filename)
        tts.save(response_path)
    except Exception as e:
        print("Text-to-Speech conversion failed:", e)
        return jsonify({'error': 'TTS failed'}), 500

    # Return audio + text data to frontend
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
