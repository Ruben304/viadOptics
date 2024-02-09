import paho.mqtt.client as mqtt
import json

PWIDTH = 1400

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('detect')


# this is the base on receiving a regular MQTT and publishing a json
def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    try:
        # decode to json
        msgContent = json.loads(msg.payload.decode())
        print('Received message:', msgContent)

        if msgContent == 'car':
            xCord = msgContent.get('xCoordinate', 0)
            zCord = msgContent.get('zCoordinate', 0)
            obj = 'car'
            degree = (xCord/PWIDTH) * 180
            message, intensity = alert(obj, degree, zCord)
            # publish JSON formatted mgs
            client.publish('hpt', json.dumps(
            {'degree': degree, 'intensity': intensity}))
            client.publish('tts', json.dumps(
            {'message': message}))

    except json.JSONDecodeError as e:
        print('Error decoding JSON: ', e)


def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')


def alert(obj, degree, zCord):
    message = ''
    intensity = 0

    if zCord < 2:
        intensity = 100
    elif 2 <= zCord < 5:
        intensity = 80
    elif 5 <= zCord < 8:
        intensity = 60
    elif 8 <= zCord < 10:
        intensity = 40

    if degree < 60:
        message = f"There is a {obj} {zCord} meters away from you on your left"
    elif degree > 120:
        message = f"There is a {obj} {zCord} meters away from you on your right"
    else:
        message = f"There is a {obj} {zCord} meters away in front of you"

    return message, intensity


client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')
client.loop_forever()
