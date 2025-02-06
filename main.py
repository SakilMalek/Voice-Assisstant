import os
import eel
from engine.command import *
from engine.features import *
eel.init('www')

# playAssistantSound()

os.system('start chrome.exe --app="http://localhost:8000/index.html"')

eel.start('index.html', mode=None, host='localhost', block=True)
