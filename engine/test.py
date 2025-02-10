import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 174)

# Test message
engine.say("Hello, this is a test.")
engine.runAndWait()
