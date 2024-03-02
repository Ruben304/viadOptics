import paho.mqtt.client as mqtt
import json
import ast
import math

last_announced_label = None  # tracks the last announced label
label_queue = []  # queue for labels while TTS playback

last_msgDict = None  # stores last msg dictionary
last_status = "free"  # status of the tts starts as free

labelMap = ["bench",    "bicycle",    "branch",    "bus",    "bush",
            "car",    "chair",    "crosswalk",    "door", "elevator",
            "fire_hydrant",    "green_light",    "gun", "motorcycle",
            "person",    "pothole",    "rat",    "red_light", "scooter",
            "stairs",    "stop_sign",    "stop_walking_signal", "table",
            "traffic_cone",    "train",    "tree",    "truck",
            "umbrella",    "walking_man_signal",    "yellow_light"]
labelDic = {} # Store dictionary of z-distance for each label
for label in labelMap:
    labelDic[label] = {"count": 0, "total": []} # 'count' is total number of entries in total, 'total' stores distances
mov_ave_count = 5 # initialize moving average count

def onConnect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe('detections')
    client.subscribe('tts-done')


# this is the base on receiving a regular MQTT and publishing a json
def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    global last_msgDict, last_status

    try:
        topic = msg.topic  # topic of message being sent
        print("msg topic:",topic)
        if topic == 'detections':
            # getting content msg rdy for variable get
            msgContent = msg.payload.decode()
            msgList = ast.literal_eval(msgContent)
            msgDict = ast.literal_eval(msgList[0])
            print('Received detection:', msgDict)

            # check if there is a new msg dictionary
            if msgDict != last_msgDict:
                print('Received new detection:', msgDict)
                last_msgDict = msgDict
                process_label(msgDict, last_status, client)

        elif topic == 'tts-done':
            # get the status of tts
            tts_done_message = json.loads(msg.payload.decode())
            status = tts_done_message.get("status")

            if status != last_status:
                # update the new status of tts with old Dict to prevent multiple detections of same obj
                print('TTS status update:', status)
                last_status = status
                process_label(last_msgDict, last_status, client)

    except json.JSONDecodeError as e:
        print('Error decoding JSON: ', e)


def onFail(client, userdata, flags, rc):
    print('Failed to connect to MQTT broker')


# processing the information given to call helper functions
def process_label(msgDict, status, client):
    global last_announced_label, label_queue, labelDic, mov_ave_count

    # add confidence interval here to ensure extra filter
    # prep the message
    label = msgDict.get('label', '').lower()
    xCord = msgDict.get('x')
    zCord = msgDict.get('z')
    confidence = msgDict.get('confidence')
    degree = calculate_degree(xCord, zCord)
    message, intensity = alert(label, degree, zCord)

    # create object for the queue for easier publish message
    detection = {'label': label, 'degree': degree, 'intensity': intensity, 'message': message}

    if confidence > 0.6: # activate only if confidence is greater than 0.6
        if labelDic[label]["count"] < mov_ave_count: # if current label's count is less than the moving count
            labelDic[label]["total"].append(math.ceil(zCord/1000)) # add rounded up meters to total
            labelDic[label]["count"] = labelDic[label]["count"] + 1 # increment count
        else: #if current label's count is equal to the moving average count
            labelDic[label]["total"].pop(0) # remove oldest z distance entry
            labelDic[label]["total"].append(math.ceil(zCord/1000)) # add new z distance entry

        # if first time seeing object OR moving average and z distance difference is greater than 2
        if math.fabs(sum(labelDic[label]["total"]) / labelDic[label]["count"] - math.ceil(zCord/1000)) > 2 or labelDic[label]["count"] == 1:
            if status == "busy": # if tts is currently busy
                label_queue.append(detection) # add to queue
            else: # if not busy
                if label_queue: # if there is a queue then pop
                    publish_message(label_queue.pop(0), client)
                else: # if no queue then publish directly
                    publish_message(detection, client)

        '''
        if status == "busy":
            # add to queue if it's not the same as the last announced label or if the queue is empty
            if not label_queue or label_queue[-1]['label'] != label:
                label_queue.append(detection)
        else:  # if status is free, check the queue first
            if label_queue:
                # if there is something in queue then add first in queue to detect
                # logic to make sure it is not a repeat is already done
                next_detection = label_queue.pop(0)
                publish_message(next_detection, client)
                last_announced_label = next_detection['label']
            elif last_announced_label != label:
                # if queue is empty and label is new, publish immediately
                publish_message(detection, client)
                last_announced_label = label
        '''


def publish_message(detection, client):
    # publish message with label info
    client.publish('hpt', json.dumps({'degree': detection['degree'], 'intensity': detection['intensity']}))
    client.publish('tts', json.dumps({'message': detection['message']}))
    print(f"Published: {detection['message']}")


# to find degree in respect to the camera
def calculate_degree(xCord, zCord):
    if zCord == 0:
        zCord = 1
    radianAng = math.atan(xCord/zCord)
    degreeAng = math.degrees(radianAng)
    return degreeAng


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

    zMeters = math.ceil(zCord/1000)

    # make the messages shorter to its not that long for each message
    if degree < -60:
        if zMeters == 1:
            message = f"{label} {zMeters} meter to your left"
        else:
            message = f"{label} {zMeters} meters to your left"
    elif degree > 60:
        if zMeters == 1:
            message = f"{label} {zMeters} meter to your right"
        else:
            message = f"{label} {zMeters} meters to your right"
    else:
        if zMeters == 1:
            message = f"{label} {zMeters} meter ahead"
        else:
            message = f"{label} {zMeters} meters ahead"

    return message, intensity


client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')
client.loop_forever()
