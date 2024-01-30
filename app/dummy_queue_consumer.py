import paho.mqtt.client as mqtt

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('testTopic')

def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')

def onMessage(client, userdata, msg):
    print('Received message:', msg)

client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')

client.loop_forever()