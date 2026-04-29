# combined_server.py
from flask import Flask, request, jsonify
from ollama import chat
import speech_recognition as sr
import os
import json
import shutil

app = Flask(__name__)

# Animation alias map
ANIMATION_MAP = {
    "week0-4_exercise1.py": "animations/week0-4_exercise1.py",
    "week0-4_exercise2.py": "animations/week0-4_exercise2.py",
    "week0-4_exercise3.py": "animations/week0-4_exercise3.py",
    "week0-4_exercise4.py": "animations/week0-4_exercise4.py",
    "week5-8_exercise1.py": "animations/week5-8_exercise1.py",
    "week5-8_exercise1.py": "animations/week5-8_exercise2.py",
    "week5-8_exercise1.py": "animations/week5-8_exercise3.py",
}

# PROMPT base with animation instruction logic
PROMPT_BASE = (
    "You are a robot named Ada assisting elbow replacement patients."
    "Please only follow the instruction in this prompt and never go off the topic. You only talk about the exercises and no ther information."
    "Keep answers short and to the point. Use natural, human-like phrases. "
    "If the user asks to start a specific exercise, return JSON like this: "
    '{"action": "play_animation", "name": "week0-4_exercise1.py"} or {"action": "play_animation", "name": "week5-8_exercise1.py"}. Otherwise, just talk normally. '
    "Always return the exercise command as a json with the naming convention I mentioned. It is important to get the week number right: if the patient mentions any week between 0 and 4 " \
    "you need to use week0-4_exercise and the exercise number. Also, if they mentioned weeks 5 to 8, use week5-8_exercise with the exercise number. Always use this naming convention"
    "You have to determine the exercise number from context. If you are unsure, ask the user to repeat themselves. "
    "Also, if the animation is not in the following animation map, just say there is no exercise matching the user "
    "requirement. Never make up anything as we could harm the user this way."
    "The user is only able to do the exercises either between weeks 0 to 4 or 5 to 8, never both as this may injure the user."###
    "Recommend that the user performs the exercises specific to their weekly span of time in numerical order according to the NHS guideline pamphlet."###
    "If you are playing an exercise, never give the user indications please. Just return the json as specified." \
    "Finally, this is the animation map of our possible animations:" + str(ANIMATION_MAP)
)


def normalize_name(name):
    return name.lower().replace(":", "").strip()

def speech_to_text(wav_file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            print(f"Transcribed Speech: {text}")
            return text
        except sr.UnknownValueError:
            print("Speech Recognition could not understand the audio.")
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError:
            print("Error with the Speech-to-Text service.")
            return "Error with the Speech-to-Text service."

@app.route('/chat', methods=['POST'])
def chat_with_ollama():
    # Handle both audio and text JSON
    if 'audio' in request.files:
        # Speech input
        audio_file = request.files['audio']
        wav_file_path = 'temp_audio.wav'
        audio_file.save(wav_file_path)
        user_message = speech_to_text(wav_file_path)
    else:
        # JSON text input
        user_message = request.json.get("message", "").strip()

    prompt = PROMPT_BASE + "\nUser: " + user_message
    stream = chat(
        model='llama3.2:3b',
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )
    full_response = "".join(chunk['message']['content'] for chunk in stream)
    print("LLM Response:", full_response)

    return jsonify({"response": full_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
