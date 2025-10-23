# utils/auth_utils.py
import json, os

USERS_FILE = "data/users.json"

def load_json(filepath):
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f: json.dump({}, f)
    with open(filepath, "r") as f: return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w") as f: json.dump(data, f, indent=4)

def signup(username, password, confirm_password, question, answer):
    users = load_json(USERS_FILE)
    if username in users:
        return False, "Username already exists!"
    if password != confirm_password:
        return False, "Passwords do not match!"
    users[username] = {
        "password": password,
        "secret_question": question,
        "secret_answer": answer
    }
    save_json(USERS_FILE, users)
    return True, "Signup successful!"

def login(username, password):
    users = load_json(USERS_FILE)
    if username not in users:
        return False, "User not found!"
    if users[username]["password"] != password:
        return False, "Incorrect password!"
    return True, "Login successful."

def get_secret_question(username):
    users = load_json(USERS_FILE)
    return users.get(username, {}).get("secret_question")

def verify_secret_answer(username, answer):
    users = load_json(USERS_FILE)
    return users.get(username, {}).get("secret_answer", "").lower().strip() == answer.lower().strip()

def reset_password(username, new_password):
    users = load_json(USERS_FILE)
    if username not in users:
        return False
    users[username]["password"] = new_password
    save_json(USERS_FILE, users)
    return True














