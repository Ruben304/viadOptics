# Run docker mosquitto
# docker run -it -p 1883:1883 -v /Users/axelsariel/repos/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto

import paho.mqtt.client as mqtt

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')

def onPublish(client, userdata, mid):
    print('Published MQTT message:', mid)

client = mqtt.Client()
client.on_connect = onConnect
client.on_publish = onPublish

client.connect('localhost')

client.publish('testTopic', 'Hello world!')

client.loop_forever()