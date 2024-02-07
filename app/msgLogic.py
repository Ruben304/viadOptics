import paho.mqtt.client as mqtt
import json


def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('hpt')


def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    try:
        # decode to json
        msgContent = json.loads(msg.payload.decode())

        print('Received message:', msgContent)
        buzzOne = False
        buzzTwo = False
        buzzThree = False
        buzzFour = False
        zCord = msgContent.get('zCoordinate', 'placeHolderX')
        xCord = msgContent.get('xCoordinate', 'placeHolderY')
        direction = ''
        if msgContent.get('type') == 'car':
            alert(xCord, buzzOne, buzzTwo, buzzThree, buzzFour, direction)

            # Publish JSON formatted messages
            client.publish('hpt', json.dumps(
                {'response': 'Hello haptic!', 'buzzers': [buzzOne, buzzTwo, buzzThree, buzzFour]}))
            client.publish('tts', json.dumps({'response': 'Hello texttospeech!', 'direction': direction}))

        elif msgContent.get('type') == 'branch':
            print('There is a branch, watch out!')
    except json.JSONDecodeError as e:
        print('Error decoding JSON: ', e)


def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')


def highAlert(xCord, buzzOne, buzzTwo, buzzThree, buzzFour, direction):
    if xCord > 0:
        direction = 'right'
        buzzOne = True
        buzzTwo = True
    elif xCord < 0:
        direction = 'left'
        buzzThree = True
        buzzFour = True
    else:
        direction = 'straight'
        buzzOne = True
        buzzThree = True


def alert(xCord, buzzOne, buzzTwo, buzzThree, buzzFour, direction):
    if xCord > 0:
        direction = 'right'
        buzzOne = True
        buzzTwo = True
    elif xCord < 0:
        direction = 'left'
        buzzThree = True
        buzzFour = True
    else:
        direction = 'straight'
        buzzOne = True
        buzzThree = True


client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')
client.loop_forever()
