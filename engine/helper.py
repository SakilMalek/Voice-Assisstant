import os
import re
import time

### 🟢 TEXT PROCESSING FUNCTIONS ###
def extract_yt_term(command):
    """
    Extracts a search term from a YouTube play command.

    Example: "Play Despacito on YouTube" → "Despacito"
    """
    match = re.search(r'play\s+(.*?)\s+on\s+youtube', command, re.IGNORECASE)
    return match.group(1) if match else None

def remove_words(input_string, words_to_remove):
    """
    Removes specified words from the input string.

    Example: "Send a message to John" → "message John" (after removing ["send", "a", "to"])
    """
    return ' '.join([word for word in input_string.split() if word.lower() not in words_to_remove])

def replace_spaces_with_percent_s(input_string):
    """
    Replaces spaces with '%s' to ensure proper formatting for ADB input.

    Example: "Hello World" → "Hello%sWorld"
    """
    return input_string.replace(' ', '%s')

### 🟢 ADB INTERACTION FUNCTIONS ###
def execute_adb_command(command):
    """
    Executes an ADB shell command safely with error handling.

    Example: execute_adb_command("adb shell input tap 500 500")
    """
    try:
        os.system(command)
        time.sleep(1)  # Ensure the command has time to execute
    except Exception as e:
        print(f"ADB Command Error: {e}")

def keyEvent(key_code):
    """Triggers a key event using ADB (e.g., back, call receive, call end)."""
    execute_adb_command(f'adb shell input keyevent {key_code}')

def tapEvents(x, y):
    """Simulates a screen tap at specified coordinates."""
    execute_adb_command(f'adb shell input tap {x} {y}')

def adbInput(message):
    """Sends text input to a mobile device using ADB."""
    execute_adb_command(f'adb shell input text "{message}"')

def goback(key_code, steps=6):
    """Presses the back button multiple times to ensure a full exit."""
    for _ in range(steps):
        keyEvent(key_code)
