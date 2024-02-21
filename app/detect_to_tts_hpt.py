import paho.mqtt.client as mqtt
import json
import ast
import math

last_announced_label = None  # tracks the last announced label
label_queue = []  # queue for labels while TTS playback


def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('detections')
    client.subscribe('tts-done')


# this is the base on receiving a regular MQTT and publishing a json
def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    try:
        topic = msg.topic  # topic of message being sent
        label = ' '
        status = ' '
        msgDict = ' '
        if topic == 'detections':
            # getting content msg rdy to search
            msgContent = msg.payload.decode()
            msgList = ast.literal_eval(msgContent)
            msgDict = ast.literal_eval(msgList[0])
            print('Received detection:', msgDict)
            label = msgDict.get('label', '').lower()

        elif topic == 'tts-done':
            tts_done_message = json.loads(msg.payload.decode())  # Decode JSON payload
            status = tts_done_message.get("status")  # Extract the "status" value
            print('TTS completion message:', status)

        if label or status:  # NEED TO FIX: is an issue
            # if msgDict.get('confidence') > 80:
            process_label(label, msgDict, status, client)

    except json.JSONDecodeError as e:
        print('Error decoding JSON: ', e)


def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')


# processing the information given to call helper functions
def process_label(label, msgDict, status, client):
    global last_announced_label, label_queue

    # add confidence interval here to ensure extra filter
    # prep the message
    xCord = msgDict.get('x')
    zCord = msgDict.get('z')
    degree = calculate_degree(xCord, zCord)
    message, intensity = alert(label, degree, zCord)

    # Check if the label is the same as the last announced
    if label != last_announced_label:
        # Announce the label if it's new
        publish_message(label, degree, intensity, message, client)
        last_announced_label = label  # Update the last announced label
    else:  # if label != last and tts is free
        last_announced_label = label

    # ideally this is the logic:
    # if tts is free and label_queue is empty:
    #    publish_message()
    #    last_announced_label = label
    # elif tts is free and label_queue is full
    #    publish_message to the next message in queue not the same as last_announced
    #    last_announced_label = label
    # elif tts is busy:
    #   if label_queue is empty:
    #       if last_announced_label != label:
    #         publish_message()
    #         last_announced_label = label
    #   elif label_queue is full:
    #     publish_message to the next message in queue not the same as last_announced
    #     last_announced_label = label
    # ========================================
    # if status != "busy" and not label_queue:
    #    publish_message()
    #    last_announced_label = label
    # elif status != "busy" and len(label_queue) > 0:
    #    publish_message to the next message in queue not the same as last_announced
    #    last_announced_label = label
    # elif status == "busy":
    #   if not label_queue:
    #       if last_announced_label != label:
    #         publish_message()
    #         last_announced_label = label
    #   elif len(label_queue) > 0:
    #     publish_message to the next message in queue not the same as last_announced
    #     last_announced_label = label


def publish_message(label, degree, intensity, message, client):
    # Logic to publish the message based on label specifics
    client.publish('hpt', json.dumps({'degree': degree, 'intensity': intensity}))
    client.publish('tts', json.dumps({'message': message}))


# to find degree in respect to the camera
def calculate_degree(xCord, zCord):
    degree = math.atan(xCord/zCord)
    return degree


# alerts and messages being sent out
def alert(label, degree, zCord):

    if zCord < 304:  # 1 foot
        intensity = 100
    elif 304 <= zCord < 609:  # 1 to 2 feet
        intensity = 80
    elif 609 <= zCord < 1219:  # 2 to 4 feet
        intensity = 60
    else:  # 4 or more
        intensity = 0

    # make the messages shorter to its not that long for each message
    if degree < -60:
        message = f"{label} {zCord} millimeters away on your left"
    elif degree > 60:
        message = f"{label} {zCord} millimeters away on your right"
    else:
        message = f"{label} {zCord} millimeters away in front of you"

    return message, intensity


client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')
client.loop_forever()
