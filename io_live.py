import cv2
import speech_recognition as sr
import time
import os 
from gtts import gTTS 
import platform 
import subprocess 

TTS_FILE = "bot_response.mp3" 

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

KNOWN_USERS = {
    "User_A": "Rohan (User A)",
    "User_B": "Vasist (User B)",
}

def play_audio_fallback(filename):
    """Plays the audio file using a native system command (OS fallback)."""
    current_os = platform.system()
    
    if current_os == "Windows":
        subprocess.Popen(f"start {filename}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
    elif current_os == "Darwin": # macOS
        subprocess.Popen(f"afplay {filename}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif current_os == "Linux":
        # Try common players
        try:
            subprocess.Popen(['mpg321', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
             try:
                subprocess.Popen(['xdg-open', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
             except FileNotFoundError:
                 print("[AUDIO WARNING] No suitable audio player found (mpg321/xdg-open).")
    else:
        print(f"[AUDIO WARNING] Unsupported OS: {current_os}. Cannot play audio.")


def live_face_recognition():
    """
    Runs the camera until a face is detected, then asks for user confirmation via console input.
    """
    cap = cv2.VideoCapture(0)
    user_id = None
    user_name = "Guest"
    face_found = False

    print("\n[CAMERA] Opening camera for continuous face monitoring...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read from camera.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        cv2.putText(frame, "Look into the camera...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected! (Closing Camera)", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Face Scanner', frame)
            cv2.waitKey(2000) 
            
            face_found = True
            break
        else:
            cv2.putText(frame, "Looking for Face...", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow('Face Scanner', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break


    cap.release()
    cv2.destroyAllWindows()
    
    if face_found:
        print("\n[RECOGNITION] Face detected! Who is speaking?")
        print("Type 'A' for Rohan, 'B' for Vasist, or 'S' to skip/treat as Guest.")
        
        choice = input("Enter choice (A/B/S): ").strip().upper()
        
        if choice == 'A':
            user_id = "User_A"
            user_name = KNOWN_USERS[user_id]
        elif choice == 'B':
            user_id = "User_B"
            user_name = KNOWN_USERS[user_id]
        else:
            print("[SYSTEM] Proceeding as Guest.")
    
    print(f"[RECOGNITION] User selected: {user_name} ({user_id})")
    return user_id, user_name


def live_speech_to_text():
    """Captures audio continuously until silence is detected."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening... Speak your query clearly.")
        r.adjust_for_ambient_noise(source, duration=0.5) 
        try:
            audio = r.listen(source, phrase_time_limit=10) 
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

    try:
        text = r.recognize_google(audio)
        print(f"Heard: \"{text}\"")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""


def live_text_to_speech(text):
    """
    Generates speech using gTTS, saves it, plays it using the system's audio player, and cleans up.
    """
    
    print(f"\nBOT: {text}")
    
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(TTS_FILE)
    except Exception as e:
        print(f"[TTS ERROR] Failed to generate audio file: {e}. Check internet connection.")
        return 

    play_audio_fallback(TTS_FILE)
    
    words = len(text.split())
    delay_time = max(1.0, words * 0.25) 
    time.sleep(delay_time)
    
    if os.path.exists(TTS_FILE):
        try:
            os.remove(TTS_FILE)
        except PermissionError:
            print("[CLEANUP WARNING] Could not delete audio file. It might be locked by the player.")


def digital_servo_action(name):
    """Simulates the servo action for the software demo."""
    print(f"[ACTION] Bot gives a digital nod to {name}.")