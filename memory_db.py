import json
import os
import time

# Define the file path for the memory database
MEMORY_FILE = 'user_memory.json'

def load_all_profiles():
    """Loads the entire user memory dictionary from the JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("[DB WARNING] user_memory.json is empty or corrupted. Starting fresh.")
        return {}

def save_all_profiles(data):
    """Saves the entire user memory dictionary to the JSON file."""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_history(user_id):
    """Retrieves the conversation history for a specific User ID."""
    profiles = load_all_profiles()
    return profiles.get(user_id, {}).get('history', [])

def save_conversation(user_id, name, user_msg, bot_msg):
    """Saves the latest interaction to the user's history."""
    profiles = load_all_profiles()

    if user_id not in profiles:
        profiles[user_id] = {'name': name, 'history': []}

    profiles[user_id]['history'].append({
        'timestamp': time.time(),
        'user': user_msg,
        'bot': bot_msg
    })

    # Keep the history to the last 5 turns
    profiles[user_id]['history'] = profiles[user_id]['history'][-5:] 

    save_all_profiles(profiles)
    
    print(f"\n[DB] Saved conversation for {name}. History length: {len(profiles[user_id]['history'])}")