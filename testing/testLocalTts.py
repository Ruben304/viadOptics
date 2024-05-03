import pyttsx3
import platform

system = platform.system()

if system == 'Darwin':  # macOS
    thisEngine = 'nsss'
elif system == 'Linux':
    thisEngine = 'espeak'
elif system == 'Windows':
    thisEngine = 'sapi5'
else:
    thisEngine = 'Unknown'

engine = pyttsx3.init(thisEngine)
engine.say("I will speak this text")
engine.runAndWait()