from naoqi import ALProxy
import time
from robot_IP import robot_IP

import subprocess
# Replace with your robot's IP address

PORT = 9559

# Connect to ALMemory
memory = ALProxy("ALMemory", robot_IP, PORT)

tts = ALProxy("ALAnimatedSpeech", robot_IP, PORT)
tts.say("Hello there! Im Ada and I am a prototype physiotherapy assistant, I specialise in post elbow replacement exercises and have exercises for the first 8 weeks of your healing journey. If you would like to continue into patient registration via name or facial recognition, press the foot bumper on your left. If you would just like to do the exercises, press the foot bumper on your right. If you want to exit, press the top of my head.")
# Memory keys for foot and head buttons
sensors = {
    "left_foot": "Device/SubDeviceList/LFoot/Bumper/Left/Sensor/Value",
    "right_foot": "Device/SubDeviceList/RFoot/Bumper/Right/Sensor/Value",
    "head_middle": "Device/SubDeviceList/Head/Touch/Middle/Sensor/Value"
}

print("Listening for button presses... (Head touch to stop)")

try:
    while True:
        left_pressed = memory.getData(sensors["left_foot"]) == 1.0
        right_pressed = memory.getData(sensors["right_foot"]) == 1.0
        head_pressed = memory.getData(sensors["head_middle"]) == 1.0

        if left_pressed:
            subprocess.call(['python', 'C:\Users\elwoo\Documents\coding\python\NAO-ROBOT\Social_Service\send_talk-dancopy.py'])
            time.sleep(1)  # Debounce delay

        elif right_pressed:
            subprocess.call(['python', 'registration/face_main.py'])
            time.sleep(1)  # Debounce delay

        elif head_pressed:
            print("Head touched! Exiting...")
            break

        time.sleep(0.1)  # Polling delay

except KeyboardInterrupt:
    print("Script interrupted manually.")

print("Script finished.")
