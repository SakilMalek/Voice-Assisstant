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
import re
import pvporcupine
import pyaudio
import pyautogui
import requests
import urllib
from engine.command import speak
from engine.config import ASSISTANT_NAME
from engine.helper import extract_yt_term, remove_words

# Initialize SQLite database connection
con = sqlite3.connect("friday.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    """Plays the assistant's startup sound."""
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

def openCommand(query):
    """Opens an application or website based on the user's query."""
    query = query.replace(ASSISTANT_NAME, "").replace("open", "").strip()
    query = query.lower().replace(" ", "")  # Normalize by removing spaces and making lowercase

    try:
        # Fetch system commands from the database
        cursor.execute('SELECT path FROM sys_command')
        results = cursor.fetchall()
        app_dict = {row[0].lower().replace(" ", ""): row[0] for row in results}

        if query in app_dict:
            speak(f"Opening {app_dict[query]}")
            os.startfile(app_dict[query])
            return

        # Fetch web commands from the database
        cursor.execute('SELECT url FROM web_command')
        results = cursor.fetchall()
        web_dict = {row[0].lower().replace(" ", ""): row[0] for row in results}

        if query in web_dict:
            speak(f"Opening {web_dict[query]}")
            webbrowser.open(web_dict[query])
            return

        # Fallback to os.system
        speak(f"Opening {query}")
        os.system(f'start {query}')

    except Exception as e:
        speak("Something went wrong")
        logging.error(f"Error in openCommand: {e}")

def closeApplication(query):
    """Closes an application based on its name."""
    try:
        app_name = query.replace("close", "").strip().lower()

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
        logging.error(f"Error closing application: {e}")

def PlayYoutube(query):
    """Plays a video on YouTube based on the user's query."""
    try:
        search_term = extract_yt_term(query)

        if search_term:
            speak(f"Playing {search_term} on YouTube.")
            kit.playonyt(search_term)  # Primary method
        else:
            speak("No valid search term found.")

    except Exception as e:
        speak("An error occurred while playing the video.")
        logging.error(f"Error in PlayYoutube: {e}")

def hotword():
    """Listens for a wake word and triggers a shortcut (Win+J) when detected."""
    porcupine = None
    paud = None
    audio_stream = None

    try:
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Listening for hotwords...")

        while True:
            keyword = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)

            if porcupine.process(keyword) >= 0:
                print("Hotword detected!")
                pyautogui.hotkey("win", "j")
                time.sleep(2)  # Prevent repeated triggers

    except KeyboardInterrupt:
        print("\nHotword detection stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if porcupine:
            porcupine.delete()
        if audio_stream:
            audio_stream.close()
        if paud:
            paud.terminate()
        print("Resources released. Exiting...")

def findContact(query):
    """Finds a contact in the database."""
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

def chatBot(query):
    """Interacts with the Ollama chatbot API."""
    user_input = query.lower().strip()
    url = "http://localhost:11434/api/generate"
    refined_prompt = f"You are an AI assistant. Provide a clear, concise, and accurate response to the following user query:\n\n{user_input}"

    payload = {
        "model": "llama3",
        "prompt": refined_prompt,
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        response = requests.post(url, json=payload)
        response_data = response.json()

        if "response" in response_data:
            response_text = response_data["response"].strip()
            refined_response = post_process_response(response_text)
            print("Chatbot response:", refined_response)
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

def makeCall(name, mobileNo):
    """Makes a phone call using ADB."""
    mobileNo = mobileNo.replace(" ", "")
    speak("Calling " + name)
    command = f'adb shell am start -a android.intent.action.CALL -d tel:{mobileNo}'
    os.system(command)

def sendMessage(message, mobileNo, name):
    """Sends an SMS to a contact using ADB.

    Args:
        message: The message content to send.
        mobileNo: The recipient's phone number.
        name: The recipient's name.
    """
    try:
        speak(f"Sending message to {name}")
        logging.info(f"Preparing to send message to {name} ({mobileNo})")

        # Ensure correct phone number format (remove spaces & country code if needed)
        mobileNo = mobileNo.replace(" ", "").replace("+91", "")

        # Replace spaces with `%s` to handle spaces in the message
        formatted_message = message.replace(" ", "%s")

        # Open SMS app with pre-filled phone number
        subprocess.run(f'adb shell am start -a android.intent.action.VIEW -d sms:{mobileNo}', shell=True)
        time.sleep(3)  # Wait for the messaging app to open

        # Type the message
        subprocess.run(f'adb shell input text "{formatted_message}"', shell=True)
        time.sleep(1)  # Wait before sending

        # Press the "Send" button (Works on most devices)
        # subprocess.run("adb shell input keyevent 66", shell=True)  # Keyevent 66 = Enter key

        # Alternative method (if Enter key doesn't work)
        send_button_coordinates = "977 1489"  # Adjust coordinates for the Send button
        subprocess.run(f'adb shell input tap {send_button_coordinates}', shell=True)
        time.sleep(1)

        speak(f"Message sent successfully to {name}")
        logging.info(f"Message sent successfully to {name}")

    except Exception as e:
        logging.error(f"Error sending message: {e}")
        speak("Sorry, there was an error sending the message.")
def setAlarm(query):
    """Sets an alarm on an Android device using ADB.

    Args:
        query: The user's query containing the alarm time (e.g., "Set an alarm for 5:00 PM").
    """
    try:
        # Extract time from the query using regex
        time_pattern = re.compile(r'(\d{1,2}):(\d{2})\s*(AM|PM)?', re.IGNORECASE)
        match = time_pattern.search(query)
        
        if not match:
            speak("I couldn't find a valid time in your request.")
            return False

        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3).upper() if match.group(3) else None

        # Convert to 24-hour format
        if period == "PM" and hour != 12:
            hour += 12
        elif period == "AM" and hour == 12:
            hour = 0

        # Validate the time
        if not (0 <= hour < 24 and 0 <= minute < 60):
            speak("The time you provided is invalid.")
            return False

        # Format the time for display
        alarm_time = f"{hour:02d}:{minute:02d}"

        # Try the direct ADB command first
        adb_command = (
            f'adb shell am start -a com.android.deskclock.action.SET_ALARM '
            f'-e android.intent.extra.HOUR {hour} '
            f'-e android.intent.extra.MINUTES {minute} '
            f'--ez android.intent.extra.SKIP_UI true'
        )
        result = subprocess.run(adb_command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            speak(f"Alarm set for {alarm_time}.")
            return True

        # Fallback to UI interaction if the direct command fails
        speak("Falling back to manual alarm setup.")

        # Open the alarm app
        open_alarm_command = 'adb shell am start -n com.android.deskclock/com.android.deskclock.AlarmClock'
        subprocess.run(open_alarm_command, shell=True)
        time.sleep(3)

        # Simulate tapping the "Add Alarm" button
        add_alarm_button_coordinates = "913 2101"  # Adjust coordinates as needed
        subprocess.run(f'adb shell input tap {add_alarm_button_coordinates}', shell=True)
        time.sleep(1)

        # Simulate setting the hour
        subprocess.run(f'adb shell input text "{hour}"', shell=True)
        time.sleep(1)

        # Simulate setting the minute
        subprocess.run(f'adb shell input text "{minute}"', shell=True)
        time.sleep(1)

        # Simulate tapping the "Save" button
        save_button_coordinates = "975 405"  # Adjust coordinates as needed
        subprocess.run(f'adb shell input tap {save_button_coordinates}', shell=True)

        speak(f"Alarm set for {alarm_time}.")
        return True

    except Exception as e:
        speak("Something went wrong while setting the alarm.")
        logging.error(f"Error in set_alarm_adb: {e}")
        return False

def addNote(query):
    """Adds a note on an Android device using ADB.

    Args:
        query: The user's query containing the note content (e.g., "Add a note: Buy groceries").
    """
    try:
        # Extract the note content from the query
        note_content = query.replace("add a note", "").replace(":", "").strip()

        if not note_content:
            speak("I couldn't find any content for the note.")
            return False

        # Replace spaces with `%s` to handle spaces in the note content
        formatted_note_content = note_content.replace(" ", "%s")

        # Open the notes app
        open_notes_command = 'adb shell am start -n com.miui.notes/.ui.NotesListActivity'
        result = subprocess.run(open_notes_command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            speak("Failed to open the notes app. Please ensure your phone is connected and ADB is properly configured.")
            logging.error(f"ADB Error: {result.stderr}")
            return False

        # Wait for the notes app to open
        time.sleep(3)

        # Simulate tapping the "New Note" button
        new_note_button_coordinates = "909 2120"  # Adjust coordinates as needed
        subprocess.run(f'adb shell input tap {new_note_button_coordinates}', shell=True)
        time.sleep(1)

        # Simulate typing the note content
        subprocess.run(f'adb shell input text "{formatted_note_content}"', shell=True)
        time.sleep(1)

        # Simulate tapping the "Save" or "Done" button
        save_button_coordinates = "957 175"  # Adjust coordinates as needed
        subprocess.run(f'adb shell input tap {save_button_coordinates}', shell=True)
        time.sleep(1)

        # Simulate pressing the back button
        back_button_coordinates = "103 196"  # Coordinates for the back button
        subprocess.run(f'adb shell input tap {back_button_coordinates}', shell=True)

        speak("Note added successfully.")
        return True

    except Exception as e:
        speak("Something went wrong while adding the note.")
        logging.error(f"Error in addNote: {e}")
        return False