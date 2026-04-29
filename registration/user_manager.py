import os
import json

PROFILE_DIR = "user_profiles"


def ensure_profile_folder():
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR)


def save_user_profile(name, week, face_learned=True):
    ensure_profile_folder()
    profile = {
        "name": name,
        "week": week,
        "face_learned": face_learned
    }
    file_path = os.path.join(PROFILE_DIR, name.lower() + ".json")
    with open(file_path, "w") as f:
        json.dump(profile, f)


def load_user_profile(name):
    file_path = os.path.join(PROFILE_DIR, name.lower() + ".json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return None


def list_all_profiles():
    ensure_profile_folder()
    profiles = []
    for filename in os.listdir(PROFILE_DIR):
        if filename.endswith(".json"):
            profiles.append(filename.replace(".json", ""))
    return profiles

