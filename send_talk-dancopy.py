# -*- coding: utf-8 -*-

import os
import time
import requests
import paramiko
import json as json
import subprocess
from naoqi import ALProxy
from robot_IP import robot_IP

# Robot IP and port
robot_PORT = 9559

def saved_name():
    try:
        with open("./NAO-ROBOT/Social_Service/face_name.txt", "r") as f:
            getname = f.read().strip()
            return getname
    except IOError:
        return None

getname = str(saved_name())

BASE_ANIMATION_PATH = os.path.join(os.path.dirname(__file__), "animations")

ANIMATION_MAP = {}

# Week 0–4 exercises
for i in range(1, 5):
    key = "week0-4_exercise%d.py" % i
    value = os.path.join(BASE_ANIMATION_PATH, "week0-4_exercise%d.py" % i)
    ANIMATION_MAP[key] = value

# Week 5–8 exercises
for i in range(1, 4):
    key = "week5-8_exercise%d.py" % i
    value = os.path.join(BASE_ANIMATION_PATH, "week5-8_exercise%d.py" % i)
    ANIMATION_MAP[key] = value

EXERCISE_EXPLANATION = {
    "week0-4_exercise1.py": "Bend your elbow as far as you can. Then relax your arm and allow gravity to help straighten/stretch your arm out straight. You may wish to support the upper arm, as shown below. Repeat this 10-20 times. I will now demonstrate the exercise to you.",
    "week0-4_exercise2.py": "Tuck your operated elbow into your side and at a right angle. Slowly turn your hand over so that your palm is facing the floor, then turn it up to face the ceiling. Do this 10-20 times. If you are struggling, you may use your other hand to gently help, without causing pain. I will now demonstrate the exercise to you.",
    "week0-4_exercise3.py": "With your fingers relaxed into a fist, bend your wrist forwards and backwards 10 times. I will now demonstrate the exercise to you.",
    "week0-4_exercise4.py": "Support the upper arm with your other hand or the arm of a chair. Relax your arm and allow gravity to stretch your arm out straight. Hold for 3-5 minutes. This exercise could be done with somebody else ither by helping to support underneath the elbow and pushing down on the wrist or with your elbow resting on a worktop/table/armchair and the other person supporting your shoulder with one hand and pulling the forearm with the other hand. I will now demonstrate the exercise to you.",
    "week5-8_exercise1.py": "Place your wrist against the edge of a worktop or table. Straighten your elbow as far as you can. Then, use your other hand to push the elbow straighter. Hold the stretch for 3-5 minutes. This may be uncomfortable but not painful, so you can tolerate it. I will now demonstrate the exercise to you.",    
    "week5-8_exercise2.py": "Bend your elbow as far as you can. Then use your other hand to hold your forearm and bend the elbow further, holding the stretch for 3-5 minutes. This may be uncomfortable but should not be painful, so you can tolerate it. I will now demonstrate the exercise to you.",
    "week5-8_exercise3.py": "Using a tennis ball, roll it on a table, forwards and backwards or side to side. Place the ball on a book or tray and roll from side to side in a controlled way as shown below. Complete each activity for 1 minute. I will now demonstrate the exercise to you.",
}

def normalize_name(name):
    return name.lower().replace(":", "").strip()

def run_script(filepath):
    try:
        #print("Executing animation:", filepath)
        subprocess.call(["python", filepath])
    except subprocess.CalledProcessError as e:
        print("Error running animation:")
        print(e)
    except FileNotFoundError:
        print("File not found: " + str(filepath))

# Initialize the proxies
record = ALProxy("ALAudioRecorder", robot_IP, robot_PORT)
tts = ALProxy("ALAnimatedSpeech", robot_IP, robot_PORT)

# URL for sending the recorded audio
llama_url = 'http://localhost:5000/chat'

# File paths
record_path = '/data/home/nao/recordings/recorded_audio.wav'
local_path = os.getcwd()  # Current directory to save the file locally

# Start speaking on the robot
#tts.say("So, " + getname + " you are now onto the exercise section. In this section we will go over several exercises to aid in your rehabilitation after full elbow replacement surgery. These exercises are important for the full recovery of your elbow joints post replacement surgery, I will give an explanation of the exercise and demonstrate them visually to you. Each time, please tell me the number of the exercise and what week range you are between, 0 to 4 or 5 to 8.")

# Start recording audio
print('recording ...')
tts.say('I am recording!')
record.startMicrophonesRecording(record_path, 'wav', 16000, (0, 0, 1, 0))

# Wait for the recording to finish
time.sleep(5)
record.stopMicrophonesRecording()

# Now we need to transfer the recorded file from the robot to the local machine
# Now we need to transfer the recorded file from the robot to the local machine
robot_username = 'nao'
robot_password = 'nao'  # Replace with the actual password if different

# Use paramiko to establish an SFTP connection to the robot
print('transferring file...')
try:
    # Connect to the robot via SSH
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(robot_IP, username=robot_username, password=robot_password)

    # Create SFTP session
    sftp = ssh_client.open_sftp()

    # Download the file from the robot to the local machine
    local_audio_path = os.path.join(local_path, 'recorded_audio.wav')
    sftp.get(record_path, local_audio_path)

    # Close the SFTP session and SSH client
    sftp.close()
    ssh_client.close()

except Exception as e:
    exit(1)

# Now that the file is locally saved, send it to your server
print('Sending to server')
with open(local_audio_path, 'rb') as f:
    files = {'audio': f}
    response = requests.post(llama_url, files=files)

# Process the server's response
response_text = response.json().get('response', 'No response found')
print(response_text)

speak = True
try:
    parsed = json.loads(response_text)
    if parsed.get("action") == "play_animation":
        anim_key = normalize_name(parsed.get("name", ""))
        #print(anim_key)
        if anim_key in ANIMATION_MAP:
            # run the script
            print("Executing animation:", ANIMATION_MAP[anim_key])
            tts.say(EXERCISE_EXPLANATION[anim_key])
            time.sleep(2)
            run_script(ANIMATION_MAP[anim_key])
            tts.say('Now lets go onto the next exercise.')
            speak = False
        else:
            response_text = "Animation" + str(anim_key) + " not found."
except:
    pass

if speak == True:
    tts.say(str(response_text))

#tts.say("Thank you for coming to this guided physiotherapy session, remember to do these exercises outside of these sessions and if you are in weeks 5 to 8 you are encouraged to also do the exercises from the first four weeks.")