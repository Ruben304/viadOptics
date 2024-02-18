import paho.mqtt.client as mqtt
import json
import ast


PWIDTH = 1400

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('detections')


# this is the base on receiving a regular MQTT and publishing a json
def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    try:
        # getting content msg rdy to search
        msgContent = msg.payload.decode()
        msgList = ast.literal_eval(msgContent)
        msgDict = ast.literal_eval(msgList[0])
        print('Received dict:', msgDict)

        label = msgDict.get('label', '').lower()
        if label:
            if msgDict.get('confidence') > 80:
                process_label(label, msgDict, client)

    except json.JSONDecodeError as e:
        print('Error decoding JSON: ', e)


def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')


def process_label(label, msgDict, client):
    if label == 'train':
        xCord = msgDict.get('x')
        zCord = msgDict.get('z')
        degree = (xCord / PWIDTH) * 180
        message, intensity = alert(label, degree, zCord)
        # publish JSON messages
        client.publish('hpt', json.dumps({'degree': degree, 'intensity': intensity}))
        client.publish('tts', json.dumps({'message': message}))
    elif label == 'car':
        xCord = msgDict.get('x')
        zCord = msgDict.get('z')
        degree = (xCord / PWIDTH) * 180
        message, intensity = alert(label, degree, zCord)
        # publish JSON messages
        client.publish('hpt', json.dumps({'degree': degree, 'intensity': intensity}))
        client.publish('tts', json.dumps({'message': message}))
    if label == 'person':
        xCord = msgDict.get('x')
        zCord = msgDict.get('z')
        degree = (xCord / PWIDTH) * 180
        message, intensity = alert(label, degree, zCord)
        # publish JSON messages
        client.publish('hpt', json.dumps({'degree': degree, 'intensity': intensity}))
        client.publish('tts', json.dumps({'message': message}))
    # add all other map cases

def alert(obj, degree, zCord):
    message = ''
    intensity = 0

    if zCord < 304:  # 1 foot
        intensity = 100
    elif 304 <= zCord < 609:  # 1 to 2 feet
        intensity = 80
    elif 609 <= zCord < 1219:  # 2 to 4 feet
        intensity = 60
    elif 1219 <= zCord < 1524:  # 4 to 5 feet
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
