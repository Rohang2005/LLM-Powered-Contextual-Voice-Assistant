# --- assistant_core.py ---
import os
import time
from google import genai
from google.genai.errors import APIError

from memory_db import load_history, save_conversation 
from io_live import (
    live_face_recognition,
    live_speech_to_text,
    live_text_to_speech, 
    digital_servo_action 
)

API_KEY = os.getenv("GEMINI_API_KEY", "API_KEY") 
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"


def build_system_prompt(name, history):
    """
    Constructs the prompt sent to the LLM, injecting the user's name and history.
    """
    history_text = "\n".join([f"User: {turn['user']}\nModel: {turn['bot']}" for turn in history])
    
    system_prompt = (
        f"You are a friendly, tabletop voice assistant bot named Jules. "
        f"The user you are currently speaking to is identified as **{name}**. "
        f"Keep your responses concise and conversational, referring to the user by name if possible."
    )

    if history:
        memory_context = (
            f"\n\n***MEMORY CONTEXT START***\n"
            f"Your current memory for this user is the following past conversation turns. "
            f"Use this history to make your response contextually relevant and personalized:\n"
            f"{history_text}\n"
            f"***MEMORY CONTEXT END***"
        )
    else:
        memory_context = "\n\nThis is your first time speaking to this user. No conversation history is available."


    return system_prompt + memory_context


def get_llm_response(system_prompt, user_query):
    """
    Sends the request (prompt + query) to the Gemini LLM API using the
    compatible method for older SDKs.
    """
    print("\n[LLM] Sending prompt to Gemini...")
    
    combined_prompt = f"{system_prompt}\n\nUser Query: {user_query}"
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": combined_prompt}]}
            ]
        )
        
        return response.text
    except APIError as e:
        print(f"[ERROR] LLM API Error: {e}")
        return "I'm sorry, I'm currently having trouble connecting to my cloud brain. Check the API key and internet connection."
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        print(f"Error details: {e}")
        return "An unexpected system error occurred."


def main_assistant_loop():
    """
    The main control loop for the robot assistant, featuring a continuous loop
    that doesn't require hitting Enter.
    """
    print("--- Starting Tabletop Assistant Core (Continuous Demo) ---")
    
    while True:
        user_id, name = live_face_recognition()
        
        if user_id is None:
            live_text_to_speech("I don't recognize you. I will treat this as a one-off conversation.")
            user_id = "Guest_" + str(time.time()) 
            name = "Guest"
            
        digital_servo_action(name)
        history = load_history(user_id)
        
        if history:
            print(f"[{name}] Previous conversation found. Last turn: {history[-1]['user']}")
            greeting = f"Welcome back, {name}. What's on your mind today?"
        else:
            greeting = f"Hello, {name}. I don't believe we've spoken before. How can I help you?"

        live_text_to_speech(greeting)
        
        conversation_active = True
        while conversation_active:
            
            user_query = live_speech_to_text()
            
            if not user_query:
                print("[SYSTEM] Waiting for user input...")
                time.sleep(1) 
                continue 

            if any(phrase in user_query.lower() for phrase in ["stop listening", "that's all", "goodbye", "quit"]):
                live_text_to_speech(f"It was nice speaking with you, {name}. I'll return to scanning now.")
                conversation_active = False 
                break
                
            system_prompt = build_system_prompt(name, history)
            bot_response = get_llm_response(system_prompt, user_query)
            
            live_text_to_speech(bot_response)
            save_conversation(user_id, name, user_query, bot_response)
            
            history = load_history(user_id)
        
        print("\n--- Conversation Ended. Returning to Face Monitoring. ---")

if __name__ == "__main__":

    main_assistant_loop()
