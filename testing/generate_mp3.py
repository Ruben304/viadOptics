import pygame
from gtts import gTTS
import os

# Text that you want to convert to speech
my_text = "Hello World!"

# Use gTTS to generate a WAV file from the text
tts = gTTS(text=my_text, lang='en')

# Save the generated WAV file
mp3_file = "test.mp3"
tts.save(mp3_file)

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Load the WAV file as a sound object
sound = pygame.mixer.Sound(mp3_file)

# Play the audio
sound.play()

# Wait for the audio to finish playing
while pygame.mixer.get_busy():
    pygame.time.Clock().tick(10)

# Quit pygame
pygame.quit()

# Remove the temporary WAV file if needed
os.remove(mp3_file)
