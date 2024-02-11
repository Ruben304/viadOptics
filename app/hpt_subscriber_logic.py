import paho.mqtt.client as mqtt
import json

previous_message = None  # Initialize a variable to store the previous message

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('hpt')

def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')

def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    global previous_message  # Use the global variable to store the previous message
    messageJSON = json.loads(msg.payload.decode())
    if messageJSON != previous_message:
        print('Received message:', messageJSON)
        previous_message = messageJSON  # Update the previous message with the new one
        degree = messageJSON.get("degree", "")
        intensity = messageJSON.get("intensity", "")
        print(f"\ndegree: {degree}\nintensity{intensity}\n")


client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')

client.loop_forever()