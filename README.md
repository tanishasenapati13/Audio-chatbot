**Audio Job Interview Chatbot**

This project is a voice-enabled AI chatbot that simulates job interviews using:
1) Hugging Face LLMs (e.g., Zephyr, Falcon)
2) Whisper for voice transcription
3) gTTS for voice response
4) Flask for backend processing
5) Django for frontend interface
   

**Folder Structure**

audio_chatbot/
├── chatbotapp/               
│   ├── migrations/
│   ├── templates/
│   │   └── index.html         
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py

├── django_ui/                
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py

├── flask_backend/            
│   ├── app.py                
│   ├── responses/            
│   └── uploads/              

├── db.sqlite3
├── manage.py
├── Pipfile
└── Pipfile.lock


**Installation & Setup**

1. Clone the Repository
   
git clone https://github.com/yourusername/audio_chatbot.git

cd audio_chatbot

2. Create Virtual Environment

pip install pipenv

pipenv shell

pipenv install

3. Install Required Packages

pip install django flask flask-cors gtts requests openai-whisper

4.Optional (future voice feedback):

pip install praat-parselmouth


**Set Up Hugging Face**
   
1)Create an account at https://huggingface.co

2)Get a free API token from Settings → Access Tokens

3)Pick a supported free model (e.g., HuggingFaceH4/zephyr-7b-beta)


**Update your flask_backend/app.py like this:**

HUGGINGFACE_API_KEY = "your_token_here"

HF_MODEL = "HuggingFaceH4/zephyr-7b-beta" #Replace with your model name

5. Start Django Frontend

python manage.py runserver

Visit: http://localhost:8000

6. Run Flask Backend
   
In a new terminal tab:

cd flask_backend

python app.py

The Flask backend listens at http://localhost:5000/process_audio.

**What It Does**

1) Records user voice input (Web mic)   
2) Transcribes with Whisper   
3) Uses Hugging Face to generate interview questions/feedback   
4) Speaks reply using gTTS   
5) Shows frequency bars during voice input    
6) Displays user and AI text on screen

**Use Case**

User: "Can you take a job interview for me?"
Bot: "Sure, what role or position are you applying for?"
... and continues the conversation in interview style.

**Troubleshooting**

No audio playback?
→ Ensure CORS is enabled and response URL is correctly mapped

Empty transcription?
→ Speak clearly; check your microphone setup

404 Hugging Face error?
→ Check that the model name exists and is public

