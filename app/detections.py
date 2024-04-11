import logging
import paho.mqtt.client as mqtt
import json
import ast
import math

# Set up logging
logging.basicConfig(filename='detections_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

last_announced_label = None  # tracks the last announced label
label_queue = []  # queue for labels while TTS playback
haptic_queue = []

last_msgDict = None  # stores last msg dictionary
last_status = "free"  # status of the tts starts as free

labelMap = ["bench", "bicycle", "branch", "bus", "bush",
            "car", "chair", "crosswalk", "door", "elevator",
            "emergency_exit_sign", "emergency_light", "fire_alarm",
            "fire_extinguisher", "fire_hydrant", "green_light",
            "gun", "motorcycle", "person", "pothole", "rat",
            "red_light", "scooter", "stairs", "stop_sign",
            "stop_walking_signal", "table", "traffic_cone", "train",
            "tree", "truck", "umbrella", "walking_man_signal",
            "yellow_light"]

haptic_label = ["bus", "car", "gun", "motorcycle", "pothole", "rat", "stairs", "train"]

labelDic = {}  # Store dictionary of z-distance for each label
for label in labelMap:
    labelDic[label] = {"count": 0, "total": [], "last": 0}  # 'count' is total number of entries in total, 'total' stores distances
mov_ave_count = 100  # initialize moving average count
dist_check = 1  # distance to check for moving average

def onConnect(client, userdata, flags, rc):
    logging.info('Connected to MQTT broker')
    client.subscribe('detections')
    client.subscribe('tts-done')

def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    global last_msgDict, last_status

    try:
        topic = msg.topic  # topic of message being sent
        logging.info("msg topic: %s", topic)
        if topic == 'detections':
            # getting content msg rdy for variable get
            msgContent = msg.payload.decode()
            msgList = ast.literal_eval(msgContent)
            msgDict = ast.literal_eval(msgList[0])
            logging.info('Received detection: %s', msgDict)

            # check if there is a new msg dictionary
            if msgDict != last_msgDict:
                logging.info('Received new detection: %s', msgDict)
                last_msgDict = msgDict
                process_label(msgDict, last_status, client)

        elif topic == 'tts-done':
            # get the status of tts
            tts_done_message = json.loads(msg.payload.decode())
            status = tts_done_message.get("status")

            if status != last_status:
                # update the new status of tts with old Dict to prevent multiple detections of same obj
                logging.info('TTS status update: %s', status)
                last_status = status
                process_label(last_msgDict, last_status, client)

    except json.JSONDecodeError as e:
        logging.error('Error decoding JSON: %s', e)

def onFail(client, userdata, flags, rc):
    logging.error('Failed to connect to MQTT broker')

def process_label(msgDict, status, client):
    global last_announced_label, label_queue, labelDic, mov_ave_count

    # add confidence interval here to ensure extra filter
    # prep the message
    if msgDict is None:
        return

    label = msgDict.get('label', '').lower()
    xCord = msgDict.get('x')
    zCord = msgDict.get('z')
    confidence = msgDict.get('confidence')
    degree = calculate_degree(xCord, zCord)
    message = alert(label, degree, zCord)

    # create object for the queue for easier publish message
    detection = {'label': label, 'degree': degree, 'message': message}

    if confidence is not None and confidence > 0.5:  # activate only if confidence is greater than 0.6
        if labelDic[label]["count"] < mov_ave_count:  # if current label's count is less than the moving count
            # labelDic[label]["total"].append(math.ceil(zCord/1000)) # add rounded up meters to total
            labelDic[label]["total"].append(zCord/1000)
            labelDic[label]["count"] = labelDic[label]["count"] + 1  # increment count
        else:  # if current label's count is equal to the moving average count
            labelDic[label]["total"].pop(0)  # remove oldest z distance entry
            # labelDic[label]["total"].append(math.ceil(zCord/1000)) # add new z distance entry
            labelDic[label]["total"].append(zCord/1000)

        # if first time seeing object OR moving average and z distance difference is greater than 2
        if math.fabs(sum(labelDic[label]["total"]) / labelDic[label]["count"] - zCord/1000) > dist_check or labelDic[label]["count"] == 1:
            diff = math.fabs((zCord/1000) - labelDic[label]["last"])
            if not (diff < 1 or math.floor(zCord == 0)):
                if status == "busy":  # if tts is currently busy
                    label_queue.append(detection)  # add to queue
                else:  # if not busy
                    if label_queue:  # if there is a queue then pop
                        publish_message(label_queue.pop(0), client)
                    else:  # if no queue then publish directly
                        publish_message(detection, client)
                labelDic[label]["last"] = round(zCord/1000)

def publish_message(detection, client):
    global haptic_label

    # publish message with label info
    if detection['label'] in haptic_label:
        client.publish('hpt', json.dumps({'degree': detection['degree']}))
    client.publish('tts', json.dumps({'message': detection['message']}))
    logging.info("Published: %s", detection['message'])

# to find degree in respect to the camera
def calculate_degree(xCord, zCord):
    if zCord == 0:
        zCord = 1
    radianAng = math.atan(xCord/zCord)
    degreeAng = math.degrees(radianAng)
    return degreeAng

# alerts and messages being sent out
def alert(label, degree, zCord):
    zMeters = round(zCord/1000)
    logging.info(degree)
    # make the messages shorter to its not that long for each message
    if degree < -20:
        if zMeters == 1:
            message = f"{label} {zMeters} meter left"
        else:
            message = f"{label} {zMeters} meters left"
    elif degree > 20:
        if zMeters == 1:
            message = f"{label} {zMeters} meter right"
        else:
            message = f"{label} {zMeters} meters right"
    else:
        if zMeters == 1:
            message = f"{label} {zMeters} meter ahead"
        else:
            message = f"{label} {zMeters} meters ahead"

    return message,

client = mqtt.Client()
client.on_connect = onConnect
client.on_connect_fail = onFail
client.on_message = onMessage

client.connect('localhost')
client.loop_forever()