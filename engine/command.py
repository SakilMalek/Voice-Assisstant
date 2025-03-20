import pyttsx3
import speech_recognition as sr
import eel

# Initialize the Text-to-Speech (TTS) engine
engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 174)  # Default speech rate
engine.setProperty('voice', engine.getProperty('voices')[0].id)  # Select voice

def speak(text, async_mode=False):
    """
    Converts text to speech and updates UI with spoken text.
    
    :param text: The text to be spoken.
    :param async_mode: If True, speaks asynchronously without blocking execution.
    """
    try:
        text = str(text).strip()
        if not text:
            return  # Avoid speaking empty strings
        
        # Update UI
        eel.DisplayMessage(text)
        eel.receiverText(text)

        # Adjust speech rate dynamically
        engine.setProperty('rate', 150 if len(text) > 100 else 174)

        if async_mode:
            engine.say(text)  # Non-blocking mode
        else:
            engine.say(text)
            engine.runAndWait()  # Blocking mode
    
    except Exception as e:
        print(f"❌ Speech Error: {e}")
        eel.DisplayMessage("Speech error occurred.")

def take_command():
    """
    Captures voice input from the user and converts it to text.
    
    :return: Recognized speech as a lowercase string, or an empty string if recognition fails.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        eel.DisplayMessage("Listening...")
        print("🎤 Listening...")

        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise

        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            eel.DisplayMessage("No input detected.")
            print("⚠ No voice detected.")
            return ""

    try:
        eel.DisplayMessage("Recognizing...")
        print("⏳ Recognizing...")
        
        query = recognizer.recognize_google(audio, language="en-in")
        eel.DisplayMessage(query)
        print(f"✅ User said: {query}")
        
        return query.lower()

    except sr.UnknownValueError:
        eel.DisplayMessage("Sorry, I couldn't understand that.")
        print("⚠ Speech was unclear.")
    except sr.RequestError:
        eel.DisplayMessage("Speech recognition service unavailable.")
        print("⚠ Google Speech API issue.")
    except Exception as e:
        eel.DisplayMessage("Error in voice processing.")
        print(f"❌ Error: {e}")

    return ""

@eel.expose
def all_commands(message=1):
    """
    Handles all user commands based on voice input or UI input.
    
    :param message: If 1, captures voice command; otherwise, processes given message.
    """
    query = take_command() if message == 1 else str(message).lower()
    eel.senderText(query)

    # Define keyword variations for specific tasks
    message_keywords = {"send message", "write a message", "text", "message"}
    call_keywords = {"make a call", "call", "dial"}

    try:
        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "set an alarm" in query:
            from engine.features import setAlarm
            setAlarm(query)
        elif "add a note" in query:
            from engine.features import addNote
            speak("Which note do you want to add?")
            note_content = take_command()
            if note_content:
                addNote(note_content)
            else:
                speak("I couldn't hear the note. Please try again.")
        elif "close" in query:
            from engine.features import closeApplication
            closeApplication(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
        elif any(kw in query for kw in message_keywords | call_keywords):
            from engine.features import findContact, whatsApp, makeCall, sendMessage
            contact_no, name = findContact(query)
            
            if contact_no:
                speak("Which mode do you want to use: WhatsApp or Mobile?")
                preference = take_command().lower()
                
                if "mobile" in preference:
                    if any(kw in query for kw in message_keywords):
                        speak("What message should I send?")
                        message = take_command()
                        sendMessage(message, contact_no, name)
                    elif any(kw in query for kw in call_keywords):
                        makeCall(name, contact_no)
                elif "whatsapp" in preference:
                    speak("What message should I send?")
                    message = take_command()
                    whatsApp(contact_no, message, "message", name)
        else:
            from engine.features import chatBot
            chatBot(query)
    except Exception as e:
        print(f"Error: {e}")
    
    eel.ShowHood()
