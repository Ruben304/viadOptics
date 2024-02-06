import paho.mqtt.client as mqtt

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('testTopic')


def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    msgContent = msg.payload.decode()
    print('Received message:', msgContent)
    dangerFlag = False
    moderateFlag = False

    if 'car' in msgContent:
        dangerFlag = True
        print('There is a car, vroom vroom!')
    elif 'branch' in msgContent:
        moderateFlag = True
        print('There is a car, vroom vroom!')

    if dangerFlag:
        highAlert()
    elif moderateFlag:
        alert()



def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')


def highAlert():
    allBuzzers = True
    print('Move before you die!')

def alert():
    buzzers = True
    print('Watch out!')

client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')
client.loop_forever()

# import json
#
#
# def onMessage(client, userdata, msg: mqtt.MQTTMessage):
#     try:
#         # Assuming the message payload is a JSON string
#         message_data = json.loads(msg.payload.decode())
#         command = message_data.get('command')
#         value = message_data.get('value')
#
#         if command == 'light' and value == 'on':
#             print('Turning on the light!')
#             # Code to turn on the light
#         elif command == 'light' and value == 'off':
#             print('Turning off the light!')
#             # Code to turn off the light
#         else:
#             print('Unrecognized command or value')
#     except json.JSONDecodeError:
#         print('Error decoding JSON from message')