import pygame
from gtts import gTTS
import os

# Function to play mp3 file audio
def play_audio(mp3_file):
    # Initialize pygame and mixer
    pygame.init()
    pygame.mixer.init()

    # Load the MP3 file as a sound object
    sound = pygame.mixer.Sound(mp3_file)

    # Play the audio
    sound.play()

    # Wait for the audio to finish playing
    while pygame.mixer.get_busy():
        pygame.time.Clock().tick(10)

    # Quit pygame
    pygame.quit()


# Text that you want to convert to speech
my_text = "Hello World!"
filename = "test.mp3"

# Use gTTS to generate a WAV file from the text
tts = gTTS(text=my_text, lang='en')

# Directory to save the audio file
output_directory = "audio"

# Check if the directory exists, if not, create it
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Save the generated MP3 file in the 'audio' directory
mp3_file = os.path.join(output_directory, filename)
tts.save(mp3_file)

play_audio(mp3_file)

# Remove the temporary WAV file if needed
os.remove(mp3_file)