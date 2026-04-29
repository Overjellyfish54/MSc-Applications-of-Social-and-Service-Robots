import os
import time
from naoqi import ALProxy
from robot_IP import robot_IP

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
        return None  # Retry


# spelling name
def spell_name(tts, recognizer, memory):
    valid_letters = list("abcdefghijklmnopqrstuvwxyz")
    stop_words = ["stop", "done", "finish", "finished"]

    tts.say("Okay, let's begin. Please start spelling out your first name one letter at a time.")
    full_name = ""

    while True:
        letter = get_user_input(tts, recognizer, memory, valid_letters + stop_words)

        if letter in stop_words:
            tts.say("Got it. Saving your name.")
            break
        elif letter in valid_letters:
            tts.say("You said " + letter.upper())
            full_name += letter
        else:
            tts.say("Please say a valid letter.")

    return full_name.capitalize()


# saving name to file
def save_name(name):
    path = os.path.join(os.getcwd(), "face_name.txt")
    with open(path, "w") as f:
        f.write(name)
    print("[Saved name]:", name)
    print("[To file]:", path)


# set up and run
IP = robot_IP  # todo replace with ip number
PORT = 9559  # change if not nao default port number


def run():
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    recognizer = ALProxy("ALSpeechRecognition", IP, PORT)
    memory = ALProxy("ALMemory", IP, PORT)

    name = spell_name(tts, recognizer, memory)
    save_name(name)


if __name__ == "__main__":
    run()
