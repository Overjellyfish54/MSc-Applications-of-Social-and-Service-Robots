import time
from naoqi import ALProxy
from user_manager import load_user_profile, save_user_profile
from face_recognition import face_scan_returning_user
from learning_name import spell_name, save_name
from newface import save_user_profile, enroll_user_with_face, ask_week, spell_name_face
import subprocess
from robot_IP import robot_IP

IP = robot_IP  #todo input actual ip address
PORT = 9559 #todo input actual port number if not nao default used

tts = ALProxy("ALTextToSpeech", IP, PORT)
recognizer = ALProxy("ALSpeechRecognition", IP, PORT)
memory = ALProxy("ALMemory", IP, PORT)


# functions
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
            if isinstance(data, list) and len(data) > 1 and data[1] > 0.4:
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



def get_saved_name():
    try:
        with open("face_name.txt", "r") as f:
            getname = f.read().strip()
            return getname
    except IOError:
        return None


def intro(tts, recognizer, memory):
    recognizer.setLanguage("English")
    tts.say("You have selected patient registration, this function will allow me to remember who you are based on the information you choose to give to me. I will ask you a series of questions, I will say that I am listening when you should respond, please respond with Yes or No only. If you wish to restart this section, please say restart.")
    main(tts, recognizer, memory)  # moves to main so that intro never repeats


def main(tts, recognizer, memory):
    tts.say("Let's begin, are you a returning client?")
    response = get_user_input(tts, recognizer, memory, ["yes", "no"])
    if response == "yes":
        returning(tts, recognizer, memory)
    elif response == "no":
        new(tts, recognizer, memory)


def returning(tts, recognizer, memory):
    tts.say("Brilliant, have you used our facial recognition before?")
    response = get_user_input(tts, recognizer, memory, ["yes", "no", "restart", "reminder"])
    if response == "yes":
        tts.say("Amazing, if you would just step into position we can scan your face and get started, let me know if "
                "you need a reminder of the process for this by saying reminder, are you ready?")
        response = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])
        if response == "restart":
            tts.say("no problem, taking you back to the start")
            main(tts, recognizer, memory)
        elif response == "yes":
            tts.say("Okay, here we go!")
            status = face_scan_returning_user(tts, recognizer, memory)
            if status == "restart":
                main(tts, recognizer, memory)
        elif response == "no":
            tts.say("no problem, let me know when you are ready and we can begin")
            response = get_user_input(tts, recognizer, memory, ["ready", "restart"])
            if response == "ready":
                tts.say("okay, here we go!")
                status = face_scan_returning_user(tts, recognizer, memory)
                if status == "restart":
                    main(tts, recognizer, memory)
            elif response == "restart":
                tts.say("no problem, taking you back to the start")
                main(tts, recognizer, memory)
    elif response == "reminder":
        tts.say("No problem, how this will work is you will have 5 seconds to place your face approximately 3 meters "
                "away from my face. When my eyes turn blue it means i am scanning your face, and after a few seconds "
                "if successful my eyes will turn green, if unsuccessful my eyes will turn red, meaning we will have "
                "to try again, are you ready?")
        response = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])
        if response == "yes":
            tts.say("okay, here we go!")
            status = face_scan_returning_user(tts, recognizer, memory)
            if status == "restart":
                main(tts, recognizer, memory)
        elif response == "no":
            tts.say("no problem, let me know when you are ready and we can begin")
            response = get_user_input(tts, recognizer, memory, ["ready", "restart"])
            if response == "ready":
                tts.say("okay here we go!")
                status = face_scan_returning_user(tts, recognizer, memory)
                if status == "restart":
                    main(tts, recognizer, memory)
            elif response == "restart":
                tts.say("no problem, taking you back to the start")
                main(tts, recognizer, memory)
        elif response == "restart":
            tts.say("no problem, taking you back to the start")
            main(tts, recognizer, memory)
    elif response == "no":
        tts.say("Not a problem, would you be interested in using our facial recognition feature? This will allow you "
                "to log in next session more easily and allow us to log your progress, and all data will be secured "
                "with me")
        response = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])
        if response == "yes":
            tts.say("No Problem, how this will work is you will have 5 seconds to place your face approximately 3 "
                    "meters away from my face. When my eyes turn blue it means i am learning your face, and after a "
                    "few seconds if successful my eyes will turn green, if unsuccessful my eyes will turn red, "
                    "meaning we will have to try again, are you ready?")
            response = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])
            if response == "yes":
                tts.say("brilliant, let's begin")
                status, week = enroll_user_with_face(tts, recognizer, memory)
                if status == "earlyWeeks":
                    tts.say("Sending you to early week exercises, here we go.")
                    subprocess.call(['python', './NAO-ROBOT/Social_Service/earlyweeks.py'])
                    time.sleep(1)  # Debounce delay
                elif status == "laterWeeks":
                    tts.say("Sending you to later week exercises, here we go.")
                    subprocess.call(['python', './NAO-ROBOT/Social_Service/laterweeks.py'])
                    time.sleep(1)  # Debounce delay
            elif response == "no":
                tts.say("no problem, let me know when you're ready and we can begin")
                response = get_user_input(tts, recognizer, memory, ["ready", "restart"])
                if response == "ready":
                    tts.say("okay, let's get started")
                    status, week = enroll_user_with_face(tts, recognizer, memory)
                    if status == "earlyWeeks":
                        tts.say("Sending you to early week exercises, here we go.")
                        subprocess.call(['python', './NAO-ROBOT/Social_Service/earlyweeks.py'])
                        time.sleep(1)  # Debounce delay
                    elif status == "laterWeeks":
                        tts.say("Sending you to later week exercises, here we go.")
                        subprocess.call(['python', './NAO-ROBOT/Social_Service/laterweeks.py'])
                        time.sleep(1)  # Debounce delay
                elif response == "restart":
                    tts.say("no problem, taking you back to the start")
                    main(tts, recognizer, memory)
            elif response == "restart":
                tts.say("no problem, taking you back to the start")
                main(tts, recognizer, memory)
        elif response == "no":
            tts.say("that's okay, you can change your mind anytime!")
            noface(tts, recognizer, memory)
        elif response == "restart":
            tts.say("no problem, taking you back to the start")
            main(tts, recognizer, memory)
    elif response == "restart":
        tts.say("no problem, taking you back to the start")
        main(tts, recognizer, memory)


def new(tts, recognizer, memory):
    tts.say(
        "No problem, would you like to use our facial recognition feature so we can log your progress? this will make "
        "starting each session a lot more easier")
    response = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])
    if response == "yes":
        tts.say(
            "Awesome, how this will work is you will have 5 seconds to place your face approximately 3 meters away "
            "from my face. When my eyes turn blue it means i am learning your face, and after a few seconds if "
            "successful my eyes will turn green, if unsuccessful my eyes will turn red, meaning we will have to try "
            "again, are you ready?")
        response = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])
        if response == "yes":
            tts.say("brilliant, let's begin")
            status, week = enroll_user_with_face(tts, recognizer, memory)
            if status == "earlyWeeks":
                tts.say("Sending you to early week exercises, here we go.")
                subprocess.call(['python', './NAO-ROBOT/Social_Service/earlyweeks.py'])
                time.sleep(1)  # Debounce delay
            elif status == "laterWeeks":
                tts.say("Sending you to later week exercises, here we go.")
                subprocess.call(['python', './NAO-ROBOT/Social_Service/laterweeks.py'])
                time.sleep(1)  # Debounce delay
        elif response == "no":
            tts.say("no problem, let me know when you're ready and we can begin")
            response = get_user_input(tts, recognizer, memory, ["ready", "restart"])
            if response == "ready":
                tts.say("brilliant, let's begin")
                status, week = enroll_user_with_face(tts, recognizer, memory)
                if status == "earlyWeeks":
                    tts.say("Sending you to early week exercises, here we go.")
                    subprocess.call(['python', './NAO-ROBOT/Social_Service/earlyweeks.py'])
                    time.sleep(1)  # Debounce delay
                elif status == "laterWeeks":
                    tts.say("Sending you to later week exercises, here we go.")
                    subprocess.call(['python', './NAO-ROBOT/Social_Service/laterweeks.py'])
                    time.sleep(1)  # Debounce delay
            elif response == "restart":
                tts.say("no problem, taking you back to the start")
                main(tts, recognizer, memory)
        elif response == "restart":
            tts.say("no problem, taking you back to the start")
            main(tts, recognizer, memory)
    elif response == "no":
        tts.say("that's okay, you can change your mind anytime!")
        noface(tts, recognizer, memory)
    elif response == "restart":
        tts.say("no problem, taking you back to the start")
        main(tts, recognizer, memory)


def noface(tts, recognizer, memory):
    tts.say(
        "So what we will do is take some information from you so we can log your progress, what i need you to do is "
        "to spell your first name out, and i will repeat the letter to confirm your input, then just say stop once "
        "you're done, are you ready?")
    response = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])
    if response == "yes":
        nofacename(tts, recognizer, memory)
    elif response == "no":
        tts.say("no problem, just let me know when you're ready and we can begin!")
        response = get_user_input(tts, recognizer, memory, ["ready", "restart"])
        if response == "ready":
            nofacename(tts, recognizer, memory)
        elif response == "restart":
            tts.say("no problem, taking you back to the start")
            main(tts, recognizer, memory)
    elif response == "restart":
        tts.say("no problem, taking you back to the start")
        main(tts, recognizer, memory)


def nofacename(tts, recognizer, memory):
    early_weeks = ["0", "zero", "1", "one", "2", "two", "3", "three",
                   "week one", "week two", "week three", "4", "four", "week four"]
    late_weeks = ["5", "five", "6", "six", "7", "seven", "8", "eight",
                  "week five", "week six", "week seven", "week eight"]
    username = spell_name(tts)
    save_name(username)
    getname = get_saved_name()

    tts.say("Great, so your name is " + getname + " , is that correct?")
    response = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])
    if response == "yes":
        tts.say("Awesome, thanks for that " + getname + "now that we have your name, if you could let me know what "
                                                        "week of exercises you are on today, we can get you started. "
                                                        "state the week number, like one, two, three etcetera ")
        week_vocab = early_weeks + late_weeks + ["restart"]
        response = get_user_input(tts, recognizer, memory, week_vocab)
        if response in early_weeks:
            tts.say("Brilliant, you're on the early weeks of your recovery, lets get started " + getname)
            subprocess.call(['python', './NAO-ROBOT/Social_Service/earlyweeks.py'])
            time.sleep(1)  # Debounce delay
        elif response in late_weeks:
            tts.say("Brilliant, you're on the later stage of your recovery, lets get started " + getname)
            subprocess.call(['python', './NAO-ROBOT/Social_Service/laterweeks.py'])
            time.sleep(1)  # Debounce delay
    elif response == "no":
        tts.say("no problem, lets try this again")
        nofacename(tts, recognizer, memory)
    elif response == "restart":
        tts.say("no problem, taking you back to the start")
        main(tts, recognizer, memory)


# --- Setup + Execution ---

# if i add these here, then i don't have to call in every function

def run():
   # robot_check()  # this will test that mic and listening works before running code
    intro(tts, recognizer, memory)


if __name__ == "__main__":
    run()
