# Run docker mosquitto
# docker run -it -p 1883:1883 -v /Users/axelsariel/repos/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto
# docker run -it -p 1883:1883 -v C:\Users\ruben\VIAD\viadOptics\app\mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto

import paho.mqtt.client as mqtt

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('detections')

def onPublish(client, userdata, mid):
    print('Published MQTT message:', mid)

def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    msgContent = msg.payload.decode()
    print("Message: "+ msgContent)


client = mqtt.Client()
client.on_connect = onConnect
client.on_publish = onPublish
client.on_message = onMessage

client.connect('localhost')

client.publish('detect', 'car is 5 meter away')

client.loop_forever()