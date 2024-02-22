import paho.mqtt.client as mqtt
import json
import pygame  # Used for audio output
from gtts import gTTS  # Used for text-to-speech
import os  # Used for getting json file location
import glob  # Used to find MP3 files in the folder

previous_message = None  # Initialize a variable to store the previous message


def delete_all_wav_files():
    wav_files = glob.glob("*.wav")
    for wav_file in wav_files:
        os.remove(wav_file)


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
        wav_file = "myText.wav"
        tts.save(wav_file)
        # Initialize pygame and mixer
        pygame.init()
        pygame.mixer.init()

        client.publish('tts-done', json.dumps({"status": "busy"}))

        # Load the WAV file as a sound object
        sound = pygame.mixer.Sound(wav_file)

        # Play the audio
        sound.play()

        # Wait for the audio to finish playing
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)

        # alert the message is done
        client.publish('tts-done', json.dumps({"status": "free"}))

        # Quit pygame
        pygame.quit()

        # Remove the temporary WAV file if needed
        os.remove(wav_file)

delete_all_wav_files()

pygame.init()

client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')

client.loop_forever()