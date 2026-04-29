import time
from naoqi import ALProxy
from user_manager import load_user_profile, save_user_profile

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
            if isinstance(data, list) and len(data) > 1 and data[1] > 0.2:
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


def face_scan_returning_user(tts, recognizer, memory, ip='172.18.16.53', port=9559): # todo change ip and port to correct
    tts.say("Scanning your face now. Please stand still and look at me.")

    # Setup proxies
    faceProxy = ALProxy("ALFaceDetection", ip, port)
    ledProxy = ALProxy("ALLeds", ip, port)
    memProxy = ALProxy("ALMemory", ip, port)

    # Set eye LED to blue while scanning
    ledProxy.fadeRGB("FaceLeds", "blue", 0.5)

    faceProxy.subscribe("FaceScanApp")
    tts.say("Looking for a face...")

    recognized_name = None
    timeout = 10  # seconds
    start_time = time.time()

    while time.time() - start_time < timeout:
        data = memProxy.getData("FaceDetected")
        if isinstance(data, list) and len(data) > 1:
            face_info = data[1]
            if isinstance(face_info, list) and len(face_info) > 0:
                if len(face_info[0]) > 1:
                    name = face_info[0][1]
                    if name and name != "Unknown":
                        recognized_name = name
                        break
        time.sleep(0.5)

    faceProxy.unsubscribe("FaceScanApp")

    if recognized_name:
        ledProxy.fadeRGB("FaceLeds", "yellow", 0.5)
        tts.say("Are you " + str(recognized_name) + "?")
        confirm = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])

        if confirm == "yes":
            profile = load_user_profile(recognized_name)

            if not profile:
                tts.say(
                    "I recognized your face, but couldn't find your profile data. Would you like to try again or "
                    "restart from the beginning")
                next_step = get_user_input(tts, recognizer, memory, ["try again", "restart"])
                if next_step == "try again":
                    return face_scan_returning_user(tts, recognizer, memory)
                elif next_step == "restart":
                    return "restart"

            week = int(profile.get("week", 0))
            tts.say("Welcome back, " + str(recognized_name) + ". You are currently on week " + str(week) + ".")

            tts.say("Would you like to move on to the next week?")
            next_step = get_user_input(tts, recognizer, memory, ["yes", "no", "restart"])

            if next_step == "yes":
                next_week = min(week + 1, 8)
                if next_week == week:
                    tts.say("You are already on the final week. let's repeat week 8.")
                    #todo code to week 8 exercise
                else:
                    tts.say("Updating your profile to week " + str(next_week) + ", let's get started")
                save_user_profile(recognized_name, str(next_week), face_learned=True)
                #todo code to the next exercise

            elif next_step == "no":
                tts.say("Okay, we'll repeat week " + str(week) + ", let's get started")
                #todo code to the correct exercise

            elif next_step == "restart":
                tts.say("Restarting now.")
                return "restart"

            ledProxy.fadeRGB("FaceLeds", "green", 0.5)

        else:
            tts.say("Okay, maybe I got it wrong.")
            ledProxy.fadeRGB("FaceLeds", "red", 0.5)
            face_scan_returning_user(tts, recognizer, memory) # todo change to have ip and port if needed
    else:
        ledProxy.fadeRGB("FaceLeds", "red", 0.5)
        tts.say("Sorry, I couldn't recognize your face. lets try again")
        return "restart"
