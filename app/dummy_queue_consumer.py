import paho.mqtt.client as mqtt
import json
import pygame  # Used for audio output
from gtts import gTTS  # Used for text-to-speech
import os  # Used for getting json file location
import time  # Used to get timestamp to check if json changed
import glob  # Used to find MP3 files in the folder

previous_message = None  # Initialize a variable to store the previous message

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('tts')

def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')

def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    global previous_message  # Use the global variable to store the previous message
    messageJSON = json.loads(msg.payload.decode())

    # Compare the current message with the previous one
    if messageJSON != previous_message:
        print('Received message:', messageJSON)
        previous_message = messageJSON  # Update the previous message with the new one
        message_text = messageJSON.get("message", "")
        tts = gTTS(text=message_text, lang = 'en')
        mp3_file = "myText.mp3"
        tts.save(mp3_file)
        # Initialize the mixer again
        pygame.mixer.init()

        # Load the updated MP3 file
        pygame.mixer.music.load(mp3_file)

        # Play the updated audio
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Quit the mixer after audio playback
        pygame.mixer.quit()
        
        # Delete the MP3 file after it finishes playing
        os.remove(mp3_file)


pygame.init()

client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')

client.loop_forever()