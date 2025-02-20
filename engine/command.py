import pyttsx3
import speech_recognition as sr
import eel
import time


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


def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 8)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        time.sleep(2)
       
    except Exception as e:
        return ""
    
    return query.lower()

@eel.expose
def allCommands(message=1):
    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)
    
    try:
        query = query.lower()  # Normalize query for better matching

        # Define keyword variations
        message_keywords = {"send message", "write a message", "type a message", "can you send a message", "text", "message"}
        call_keywords = {"make a call", "please make a call", "can you call", "call", "dial"}

        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
            
        elif "close" in query:
            from engine.features import closeApplication
            app_name = query.replace("close", "").strip()
            if app_name:
                closeApplication(app_name)


        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)

        elif any(kw in query for kw in message_keywords) or any(kw in query for kw in call_keywords):
            from engine.features import findContact, whatsApp, makeCall, sendMessage
            contact_no, name = findContact(query)

            if contact_no != 0:
                speak("Which mode do you want to use: WhatsApp or Mobile?")
                preference = takecommand().lower()
                print(preference)

                if "mobile" in preference:
                    if any(kw in query for kw in message_keywords):  
                        speak("What message should I send?")
                        message = takecommand()
                        sendMessage(message, contact_no, name)

                    elif any(kw in query for kw in call_keywords):  
                        makeCall(name, contact_no)
                    else:
                        speak("Please try again.")

                elif "whatsapp" in preference:
                    message_type = ""
                    if any(kw in query for kw in message_keywords):
                        message_type = "message"
                        speak("What message should I send?")
                        query = takecommand()

                    elif any(kw in query for kw in call_keywords):
                        message_type = "call"
                    else:
                        message_type = "video call"

                    whatsApp(contact_no, query, message_type, name)

        else:
            from engine.features import chatBot
            chatBot(query)

    except Exception as e:
        print("Error:", e)

    eel.ShowHood()
