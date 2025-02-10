import pyttsx3
import speech_recognition as sr
import eel
import time

@eel.expose
def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()

import speech_recognition as sr

@eel.expose
def takecommand():
    r = sr.Recognizer()

    try:
        # Check if microphone is available
        if not sr.Microphone.list_microphone_names():
            print("No microphone found.")
            eel.DisplayMessage("No microphone detected. Please connect a microphone.")
            return ""

        with sr.Microphone() as source:
            print('Listening...')
            eel.DisplayMessage('Listening...')
            r.pause_threshold = 1  # Wait 1 second after the user stops speaking
            r.adjust_for_ambient_noise(source)  # Adjust for background noise

            # Listen for audio input
            print('Please speak...')
            audio = r.listen(source, timeout=10, phrase_time_limit=6)

        # Recognize speech using Google Speech Recognition
        print('Recognizing...')
        eel.DisplayMessage('Recognizing...')
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        eel.DisplayMessage(query)

        return str(query).lower()

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
        eel.DisplayMessage("Sorry, I didn't catch that. Could you repeat?")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        eel.DisplayMessage("Sorry, there was an issue with the speech recognition service.")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        eel.DisplayMessage("Sorry, an unexpected error occurred.")
        return ""
@eel.expose
def allCommands(message=1):
    message = str(message)
    
    
    if message == "1":
        query = takecommand()
        print(query)
    else:
        query = message
    
    if query and query.strip():
        eel.senderText(query)
    
    try:
        if not query:
            speak("Sorry, I didn't catch that. Could you repeat?")
            return ""

        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)        
        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp, makeCall, sendMessage
            contact_no, name = findContact(query)
            if(contact_no != 0):
                speak("Which mode you want to use whatsapp or mobile")
                preferance = takecommand()
                print(preferance)

                if "mobile" in preferance:
                    if "send message" in query or "send sms" in query: 
                        speak("What message you want to send")
                        message = takecommand()
                        sendMessage(message, contact_no, name)
                    elif "phone call" in query:
                        makeCall(name, contact_no)
                    else:
                        speak("please try again")
                elif "whatsapp" in preferance:
                    message = ""
                    if "send message" in query:
                        message = 'message'
                        speak("what message to send")
                        query = takecommand()
                                        
                    elif "phone call" in query:
                        message = 'call'
                    else:
                        message = 'video call'
                                        
                    whatsApp(contact_no, query, message, name)

        else:
            from engine.features import chatBot
            chatBot(query)
    except Exception as e:
        print(f"Error in command processing: {e}")
    
    eel.ShowHood()
    return ""  # Always return an empty string