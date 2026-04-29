import os
import json
import time
from naoqi import ALProxy
from robot_IP import robot_IP

# user input
# def get_user_input(tts=None, recognizer=None, memory=None, vocabulary=None, timeout=10):
#     return raw_input("You say: ").strip().lower()


def get_user_input(tts, recognizer, memory, vocabulary, timeout=10):
    sub_name = "SpeechRecogApp"

    try:
        recognizer.unsubscribe(sub_name)
        time.sleep(0.2)
    except:
        pass

    recognizer.pause(True)
    recognizer.setLanguage("English")
    recognizer.setVocabulary(vocabulary, False)
    recognizer.pause(False)

    event_key = "WordRecognized"
    try:
        memory.removeData(event_key)
    except:
        pass

    recognizer.subscribe(sub_name)
    tts.say("Listening...")

    result = None
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            data = memory.getData(event_key)
            if isinstance(data, list) and len(data) > 1 and data[1] > 0.5:
                result = data[0].lower()
                break
        except RuntimeError:
            time.sleep(0.1)

    recognizer.unsubscribe(sub_name)

    if result:
        print("[NAO heard]:", result)
        return result
    else:
        tts.say("I didn't catch that.")
        return None


# spell name
def spell_name_face(tts, recognizer, memory):
    valid_letters = list("abcdefghijklmnopqrstuvwxyz")
    stop_words = ["stop", "done", "finish"]

    name = ""
    tts.say("Please spell your name one letter at a time. Say 'stop' when done.")

    while True:
        letter = get_user_input(tts, recognizer, memory, valid_letters + stop_words)
        if letter in stop_words:
            break
        elif letter in valid_letters:
            tts.say("You said " + letter.upper())
            name += letter
        else:
            tts.say("Please say a valid letter.")

    return name.capitalize()


# selecting week
def ask_week(tts, recognizer, memory):
    week_map = {
        "0": "0", "zero": "0",
        "1": "1", "one": "1", "week one": "1",
        "2": "2", "two": "2", "week two": "2",
        "3": "3", "three": "3", "week three": "3",
        "4": "4", "four": "4", "week four": "4",
        "5": "5", "five": "5", "week five": "5",
        "6": "6", "six": "6", "week six": "6",
        "7": "7", "seven": "7", "week seven": "7",
        "8": "8", "eight": "8", "week eight": "8"
    }

    tts.say("What week of your recovery are you on? Say something like 'week two' or 'four'.")

    response = get_user_input(tts, recognizer, memory, week_map.keys())
    if response in week_map:
        week_number = week_map[response]
        if int(week_number) <= 4:
            return "earlyWeeks", week_number
        else:
            return "laterWeeks", week_number
    else:
        tts.say("Sorry, I didn't catch that. Let's try again.")
        return ask_week(tts, recognizer, memory)


# saving the profile
def save_user_profile(name, week, face_learned=True):
    profile = {
        "name": name,
        "week": week,
        "face_learned": face_learned
    }

    folder = "user_profiles"
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, name.lower() + ".json")
    with open(path, "w") as f:
        json.dump(profile, f)

    print("[Profile saved]:", path)


# main function
def enroll_user_with_face(tts, recognizer, memory, attempts=None):
    faceProxy = ALProxy("ALFaceDetection", IP, PORT)
    ledProxy = ALProxy("ALLeds", IP, PORT)

    name = spell_name_face(tts, recognizer, memory)

    tts.say("Great, your name is " + name + ". Is that correct?")
    confirm = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])

    if confirm == "yes":
        status, week = ask_week(tts, recognizer, memory)

        # Start scanning
        tts.say("Now please stand still while I scan your face.")
        ledProxy.fadeRGB("FaceLeds", "blue", 0.5)
        time.sleep(1)

        faceProxy.subscribe("EnrollFace")
        time.sleep(5)  # wait for face to be visible
        try:
            faceProxy.learnFace(name)
            ledProxy.fadeRGB("FaceLeds", "green", 0.5)
            tts.say("Face scan successful.")
        except:
            ledProxy.fadeRGB("FaceLeds", "red", 0.5)
            tts.say("Face scan failed.")
            if attempts < 2:
                tts.say("Let's try that again.")
                return enroll_user_with_face(tts, recognizer, memory, attempts + 1)
            else:
                tts.say("Too many attempts. Returning to main menu.")
                return "restart"
        faceProxy.unsubscribe("EnrollFace")

        save_user_profile(name, week, face_learned=True)
        tts.say("Thank you " + name + ". You are now fully enrolled.")
        return status, week  # status is "earlyWeeks" or "laterWeeks", week is like "4"

    elif confirm == "no":
        tts.say("Let's try spelling your name again.")
        enroll_user_with_face(tts, recognizer, memory)


# setup and run
IP = robot_IP  # todo replace with ip
PORT = 9559 # replace with port if not default nao port

if __name__ == "__main__":
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    recognizer = ALProxy("ALSpeechRecognition", IP, PORT)
    memory = ALProxy("ALMemory", IP, PORT)

    enroll_user_with_face(tts, recognizer, memory)
