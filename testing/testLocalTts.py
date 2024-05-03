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
voices = engine.getProperty('voices')
for voice in voices:
   engine.setProperty('voice', voice.id)  # changes the voice
   engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()