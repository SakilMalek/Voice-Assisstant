import os
import eel
from engine.command import *
from engine.features import *
from engine.auth import recognize

def start():
    eel.init('www')
    flag = recognize.AuthenticateFace()
    os.system('start chrome.exe --app="http://localhost:8000/index.html"')
    eel.start('index.html', mode=None, host='localhost', block=True)
