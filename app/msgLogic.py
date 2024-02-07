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

        if msgContent.get('type') == 'car':
            xCord = msgContent.get('xCoordinate', 0)
            zCord = msgContent.get('zCoordinate', 0)

            if zCord < 3:
                buzzers, direction = highAlert(xCord)
            else:
                buzzers, direction = alert(xCord)

            message = f"There is a car {zCord} meters away from you on your {direction}"
            # publish JSON formatted mgs
            client.publish('hpt', json.dumps(
                {'obstacle': 'car!', 'buzzers': buzzers}))
            client.publish('tts', json.dumps(
                {'message': message}))

        elif msgContent.get('type') == 'branch':
            xCord = msgContent.get('xCoordinate', 0)
            zCord = msgContent.get('zCoordinate', 0)

            buzzers, direction = alert(xCord)

            message = f"There is a branch {zCord} meters away from you on your {direction}"
            # publish JSON formatted mgs
            client.publish('hpt', json.dumps(
                {'obstacle': 'car!', 'buzzers': buzzers}))
            client.publish('tts', json.dumps(
                {'message': message}))
            print('There is a branch, watch out!')

    except json.JSONDecodeError as e:
        print('Error decoding JSON: ', e)


def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')


def highAlert(xCord):
    # Initialize buzzers to False
    buzzers = [True, True, True, True]  # the four buzzers we would have

    if xCord > 0:
        direction = 'right'
    elif xCord < 0:
        direction = 'left'
    else:
        direction = 'straight'
    return buzzers


def alert(xCord):
    # Initialize buzzers to False
    buzzers = [False, False, False, False]  # the four buzzers we would have
    direction = ''

    if xCord > 0:
        direction = 'right'
        buzzers[0] = True  # buzzOne
        buzzers[1] = True  # buzzTwo
    elif xCord < 0:
        direction = 'left'
        buzzers[2] = True  # buzzThree
        buzzers[3] = True  # buzzFour
    else:
        direction = 'straight'
        buzzers[0] = True  # buzzOne
        buzzers[2] = True  # buzzThree

    return buzzers, direction


client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')
client.loop_forever()
