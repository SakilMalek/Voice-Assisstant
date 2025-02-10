import os
import shlex
import re
import struct
import ollama
import subprocess
import time
import webbrowser
import sqlite3
from playsound import playsound
import eel
import pvporcupine
import pyaudio
import pyautogui
import pyttsx3
import requests
from engine.command import speak
from engine.config import ASSISTANT_NAME  # Playing assiatnt sound function
import pywhatkit as kit
from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat
import os
import openai


con = sqlite3.connect("friday.db")
cursor = con.cursor()


@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)
    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")
  
        
import pywhatkit as kit

def PlayYoutube(query):
    try:
        search_term = extract_yt_term(query)
        if search_term:
            speak(f"Playing {search_term} on YouTube")
            kit.playonyt(search_term)
        else:
            speak("No valid search term found.")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")

def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


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


import shlex
import subprocess
import time
import pyautogui

def whatsApp(mobile_no, message, flag, name):
    try:
        if flag == 'message':
            target_tab = 12
            jarvis_message = f"Message sent successfully to {name}"
        elif flag == 'call':
            target_tab = 7
            message = ''  # Clear the message as it's not needed for a call
            jarvis_message = f"Calling {name}"
        else:  # Default to video call if the flag is neither 'message' nor 'call'
            target_tab = 6
            message = ''  # Clear the message for video call
            jarvis_message = f"Starting video call with {name}"

        # Encode the message for URL (safely using shlex.quote)
        encoded_message = shlex.quote(message)
        print(encoded_message)

        # Construct the WhatsApp URL
        whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

        # Construct the full command to open WhatsApp with the URL
        full_command = f'start "" "{whatsapp_url}"'

        # Open WhatsApp using subprocess to run the command
        subprocess.run(full_command, shell=True)
        time.sleep(5)  # Allow some time for WhatsApp to open
        subprocess.run(full_command, shell=True)  # Retry to ensure WhatsApp opens properly

        # Perform the keypress sequence to focus on the correct tab
        pyautogui.hotkey('ctrl', 'f')

        # Navigate through tabs based on target_tab
        for _ in range(1, target_tab):
            pyautogui.hotkey('tab')

        pyautogui.hotkey('enter')  # Press Enter to execute the action
        speak(jarvis_message)

    except Exception as e:
        speak(f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")


 # Optional, for text-to-speech if needed

# Function to initialize OpenAI and fetch response
# chat bot
def chatBot(query):
    user_input = query.lower()
    
    # Ollama API endpoint
    url = "http://localhost:11434/api/generate"
    
    # JSON payload for the API request
    payload = {
        "model": "llama3",
        "prompt": user_input,
        "stream": False
    }
    
    try:
        # Sending request to Ollama
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        # Extract the response text
        if "response" in response_data:
            response = response_data["response"].strip()
            print("Chatbot response:", response)
            
            # Display message in the UI using existing Eel functions
            eel.DisplayMessage(response)
            eel.receiverText(response)
            
            # Use existing speak function
            speak(response)
            
            return response
            
        else:
            error_message = "Sorry, there was an error with the chatbot."
            print("Error: No response from Ollama.")
            eel.DisplayMessage(error_message)
            eel.receiverText(error_message)
            speak(error_message)
            return error_message
            
    except Exception as e:
        error_message = "Sorry, there was an error with the chatbot."
        print("Error with Ollama API:", e)
        eel.DisplayMessage(error_message)
        eel.receiverText(error_message)
        speak(error_message)
        return error_message
    
        
# Function for text-to-speech (example)
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send message
import time
import logging
from engine.helper import (
    replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
)
from engine.command import speak  # Assuming speak is defined here

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def sendMessage(message, mobileNo, name):
    try:
        # Format input values
        message = replace_spaces_with_percent_s(message)
        mobileNo = replace_spaces_with_percent_s(mobileNo)

        speak("Sending message to " + name)
        logging.info(f"Preparing to send message to {name} ({mobileNo})")

        # Ensure we start from the home screen
        goback(4)
        time.sleep(1)

        keyEvent(3)  # Press Home button
        time.sleep(1)

        # Open SMS app (adjust coordinates as needed)
        tapEvents(136, 2220)
        time.sleep(1)

        # Start a new chat
        tapEvents(819, 2192)
        time.sleep(1)

        # Enter mobile number
        adbInput(mobileNo)
        time.sleep(1)

        # Select contact (adjust coordinates if necessary)
        tapEvents(601, 574)
        time.sleep(1)

        # Tap on the input field
        tapEvents(390, 2270)
        time.sleep(1)

        # Enter message
        adbInput(message)
        time.sleep(1)

        # Send message
        tapEvents(957, 1397)
        time.sleep(1)

        speak(f"Message sent successfully to {name}")
        logging.info(f"Message sent successfully to {name}")

    except Exception as e:
        logging.error(f"Error sending message: {e}")
        speak("Sorry, there was an error sending the message.")
