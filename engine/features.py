import os
import subprocess
import pywhatkit as kit
import struct
import time
import logging
import webbrowser
import sqlite3
from playsound import playsound
import eel
import pvporcupine
import pyaudio
import pyautogui
import requests
import urllib
from engine.command import speak
from engine.config import ASSISTANT_NAME  # Playing assiatnt sound function
from engine.helper import extract_yt_term, remove_words


con = sqlite3.connect("friday.db")
cursor = con.cursor()


@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)
    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "").replace("open", "").strip()
    query = query.lower().replace(" ", "")  # Normalize by removing spaces and making lowercase

    try:
        # Normalize database query
        cursor.execute('SELECT path FROM sys_command')
        results = cursor.fetchall()

        # Convert database entries to lowercase without spaces
        app_dict = {row[0].lower().replace(" ", ""): row[0] for row in results}

        if query in app_dict:
            speak(f"Opening {app_dict[query]}")
            os.startfile(app_dict[query])
            query = ""  # Clear query after execution
            return

        # Check for web commands
        cursor.execute('SELECT url FROM web_command')
        results = cursor.fetchall()

        web_dict = {row[0].lower().replace(" ", ""): row[0] for row in results}

        if query in web_dict:
            speak(f"Opening {web_dict[query]}")
            webbrowser.open(web_dict[query])
            query = ""  # Clear query after execution
            return

        # Last attempt using os.system
        speak(f"Opening {query}")
        try:
            os.system(f'start {query}')
        except:
            speak("Not found")
        
        query = ""  # Clear query after execution

    except Exception as e:
        speak("Something went wrong")
        print("Error:", str(e))
    
    finally:
        query = ""  # Ensure query is cleared at the end
def closeApplication(query):
    """Closes an application based on its name and prevents query persistence."""
    try:
        app_name = query.replace("close", "").strip().lower()  # Extract app name

        if not app_name:
            speak("Please specify the application to close.")
            return

        if os.name == "nt":  # Windows
            result = subprocess.run(f"taskkill /F /IM {app_name}.exe", shell=True, capture_output=True, text=True)
            if "not found" in result.stdout.lower():
                speak(f"{app_name} is not running.")
            else:
                speak(f"Closing {app_name}.")
                                
    except Exception as e:
        speak("Something went wrong while closing the application.")
        print(f"Error closing application: {e}")
    
    finally:
        query = ""  # Ensure query is cleared        
def PlayYoutube(query):
    """Plays a video on YouTube based on the user's query and resets query after execution."""
    try:
        search_term = extract_yt_term(query)  # Extract search term

        if search_term:
            speak(f"Playing {search_term} on YouTube.")
            try:
                kit.playonyt(search_term)  # Primary method
            except:
                webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(search_term)}")  # Backup method
        else:
            speak("No valid search term found.")
            
    except Exception as e:
        speak("An error occurred while playing the video.")
        print(f"Error in PlayYoutube: {e}")
    
    finally:
        query = ""  # Ensure query is cleared

def hotword():
    """ Listens for a wake word and triggers a shortcut (Win+J) when detected. """
    porcupine = None
    paud = None
    audio_stream = None

    try:
        # Initialize Porcupine with pre-trained keywords
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])

        # Initialize PyAudio
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Listening for hotwords...")

        # Loop for continuous hotword detection
        while True:
            keyword = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)

            # Process keyword detection
            if porcupine.process(keyword) >= 0:
                print("Hotword detected!")

                # Simulate shortcut key press (Win+J)
                pyautogui.hotkey("win", "j")

                time.sleep(2)  # Prevent repeated triggers

    except KeyboardInterrupt:
        print("\nHotword detection stopped by user.")
    
    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Cleanup resources
        if porcupine:
            porcupine.delete()
        if audio_stream:
            audio_stream.close()
        if paud:
            paud.terminate()

        print("Resources released. Exiting...")

# find contacts
def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'can', 'you', 'if', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove)

    if not query.strip():
        speak("Query is empty after removing stop words.")
        return 0, 0

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()

        if not results:
            speak('Contact not found')
            return 0, 0

        mobile_number_str = str(results[0][0])
        mobile_number_str = mobile_number_str if mobile_number_str.startswith('+91') else '+91' + mobile_number_str

        return mobile_number_str, query
    except Exception as e:
        speak(f"An error occurred: {str(e)}")
        return 0, 0


def whatsApp(mobile_no, message, flag, name):
    try:
        # Determine the action based on the flag
        if flag == 'message':
            jarvis_message = f"Message sent successfully to {name}"
            
            # Encode the message for the WhatsApp URI
            encoded_message = urllib.parse.quote(message)
            
            # Open WhatsApp Desktop for sending a message
            whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

        elif flag == 'call':
            jarvis_message = f"Calling {name}"

            # Open WhatsApp Desktop for voice call
            whatsapp_url = f"whatsapp://call?phone={mobile_no}"

        elif flag == 'audio call':
            jarvis_message = f"Starting video call with {name}"

            # Open WhatsApp Desktop for video call
            whatsapp_url = f"whatsapp://call?phone={mobile_no}&video=true"

        else:
            speak("Invalid request. Please check your inputs.")
            return

        # Open WhatsApp using the URI
        webbrowser.open(whatsapp_url)
        time.sleep(5)  # Allow WhatsApp to open

        # Provide user feedback
        speak(f"Opening WhatsApp and preparing action with {name}.")

        # Press Enter key to confirm the action
        pyautogui.hotkey('enter')
        speak(jarvis_message)

    except Exception as e:
        speak(f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")
        
        
# chat bot


def chatBot(query):
    user_input = query.lower().strip()

    # Ollama API endpoint
    url = "http://localhost:11434/api/generate"

    # Structured prompt to optimize response quality
    refined_prompt = f"You are an AI assistant. Provide a clear, concise, and accurate response to the following user query:\n\n{user_input}"

    # JSON payload for the API request
    payload = {
        "model": "llama3",
        "prompt": refined_prompt,
        "stream": False,
        "temperature": 0.7,  # Adjust for response randomness
        "max_tokens": 200  # Limit response length
    }

    try:
        # Sending request to Ollama
        response = requests.post(url, json=payload)
        response_data = response.json()

        # Extract and refine the response
        if "response" in response_data:
            response_text = response_data["response"].strip()

            # Basic text cleaning (remove disclaimers, redundant phrases)
            refined_response = post_process_response(response_text)

            print("Chatbot response:", refined_response)

            # Display and speak the message
            eel.DisplayMessage(refined_response)
            eel.receiverText(refined_response)
            speak(refined_response)

            return refined_response

        else:
            return handle_error()

    except Exception as e:
        print("Error with Ollama API:", e)
        return handle_error()

def post_process_response(response_text):
    """Refines the AI response by removing unnecessary phrases."""
    unwanted_phrases = [
        "As an AI language model, I", 
        "I'm just an AI", 
        "I apologize", 
        "I am unable to"
    ]

    for phrase in unwanted_phrases:
        response_text = response_text.replace(phrase, "")

    return response_text.strip()

def handle_error():
    """Handles chatbot errors gracefully."""
    error_message = "Sorry, I couldn't process that request. Please try again."
    eel.DisplayMessage(error_message)
    eel.receiverText(error_message)
    speak(error_message)
    return error_message

# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

import subprocess
import time
import logging
from engine.command import speak

def sendMessage(message, mobileNo, name):
    try:
        speak(f"Sending message to {name}")
        logging.info(f"Preparing to send message to {name} ({mobileNo})")

        # Ensure correct phone number format (remove spaces & country code if needed)
        mobileNo = mobileNo.replace(" ", "").replace("+91", "")  

        # Open SMS app with pre-filled phone number
        subprocess.run(f'adb shell am start -a android.intent.action.VIEW -d sms:{mobileNo}', shell=True)
        time.sleep(3)  # Wait for the messaging app to open

        # Type the message
        subprocess.run(f'adb shell input text "{message}"', shell=True)
        time.sleep(1)  # Wait before sending

        # Press the "Send" button (Works on most devices)
        # subprocess.run("adb shell input keyevent 66", shell=True)  # Keyevent 66 = Enter key

        # Alternative method (if Enter key doesn't work)
        subprocess.run("adb shell input tap 977 1489", shell=True)  # Adjust coordinates for the Send button
        time.sleep(1)

        speak(f"Message sent successfully to {name}")
        logging.info(f"Message sent successfully to {name}")

    except Exception as e:
        logging.error(f"Error sending message: {e}")
        speak("Sorry, there was an error sending the message.")

