import paho.mqtt.client as mqtt
import json

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('detect')

def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')

def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    # print('Received message:', msg.payload.decode())
    messageJSON = json.loads(msg.payload.decode())
    print('Received message J:', messageJSON)


client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')

client.loop_forever()