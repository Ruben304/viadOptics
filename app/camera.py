
from pathlib import Path
import sys
import cv2
import depthai as dai
import numpy as np
import time
import platform # used to check if running on raspberry pi
import paho.mqtt.client as mqtt
import json
import subprocess
import logging

# Set up logging
logging.basicConfig(filename='camera_logs.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

nnBlobPath = str((Path(__file__).parent / Path('VIADFinal_V4_openvino_2022.1_5shave.blob')).resolve().absolute())

if not Path(nnBlobPath).exists():
    import sys
    raise FileNotFoundError(f'Required file/s not found, please run "{sys.executable} install_requirements.py"')

# Label Maps
labelMap= [ "bench", "bicycle", "branch", "bus", "bush",
                    "car", "chair", "crosswalk", "door", "elevator",
                    "emergency_exit_sign", "emergency_light", "fire_alarm",
                    "fire_extinguisher", "fire_hydrant",  "green_light",
                    "gun", "motorcycle", "person", "pothole", "rat",
                    "red_light", "scooter", "stairs", "stop_sign",
                    "stop_walking_signal", "table", "traffic_cone", "train",
                    "tree", "truck", "umbrella", "walking_man_signal",
                    "yellow_light"]

syncNN = True

def is_display_connected():
    try:
        result = subprocess.run(['vcgencmd', 'get_display_power'], capture_output=True, text=True)
        return 'display_power=1' in result.stdout
    except Exception as e:
        print("Error checking display status:", e)
        return False

# Initialize camera and pipeline
def initialize_camera():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    camRgb = pipeline.create(dai.node.ColorCamera)
    spatialDetectionNetwork = pipeline.create(dai.node.YoloSpatialDetectionNetwork)
    monoLeft = pipeline.create(dai.node.MonoCamera)
    monoRight = pipeline.create(dai.node.MonoCamera)
    stereo = pipeline.create(dai.node.StereoDepth)
    sysLog = pipeline.create(dai.node.SystemLogger)
    sysLogOut = pipeline.create(dai.node.XLinkOut)
    nnNetworkOut = pipeline.create(dai.node.XLinkOut)

    xoutRgb = pipeline.create(dai.node.XLinkOut)
    xoutNN = pipeline.create(dai.node.XLinkOut)
    xoutDepth = pipeline.create(dai.node.XLinkOut)

    sysLogOut.setStreamName("sysinfo")
    xoutRgb.setStreamName("rgb")
    xoutNN.setStreamName("detections")
    xoutDepth.setStreamName("depth")
    nnNetworkOut.setStreamName("nnNetwork")

    # Properties
    camRgb.setPreviewSize(416, 416)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

    monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoLeft.setCamera("left")
    monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoRight.setCamera("right")

    sysLog.setRate(1)  # 1 Hz

    # setting node configs
    stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    # Align depth map to the perspective of RGB camera, on which inference is done
    stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
    stereo.setOutputSize(monoLeft.getResolutionWidth(), monoLeft.getResolutionHeight())
    stereo.setSubpixel(True)

    spatialDetectionNetwork.setBlobPath(nnBlobPath)
    spatialDetectionNetwork.setConfidenceThreshold(0.4) # --------------------Confidence Threshold 
    spatialDetectionNetwork.input.setBlocking(False)
    spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
    spatialDetectionNetwork.setDepthLowerThreshold(100)
    spatialDetectionNetwork.setDepthUpperThreshold(5000)

    # Yolo specific parameters
    spatialDetectionNetwork.setNumClasses(34) # ------------------------------change the number of classes based on label list
    spatialDetectionNetwork.setCoordinateSize(4)
    spatialDetectionNetwork.setAnchors([10, 13, 16, 30, 33, 23, 30, 61, 62, 45, 59, 119, 116, 90, 156, 198, 373, 326] )
    spatialDetectionNetwork.setAnchorMasks({ "side52": [0,1,2], "side26": [3,4,5], "side13": [6,7,8]})
    spatialDetectionNetwork.setIouThreshold(0.5) # --------------------------- NN confidence threshold

    # Linking
    monoLeft.out.link(stereo.left)
    monoRight.out.link(stereo.right)

    camRgb.preview.link(spatialDetectionNetwork.input)
    if syncNN:
        spatialDetectionNetwork.passthrough.link(xoutRgb.input)
    else:
        camRgb.preview.link(xoutRgb.input)

    spatialDetectionNetwork.out.link(xoutNN.input)

    stereo.depth.link(spatialDetectionNetwork.inputDepth)
    spatialDetectionNetwork.passthroughDepth.link(xoutDepth.input)
    spatialDetectionNetwork.outNetwork.link(nnNetworkOut.input)
    sysLog.out.link(sysLogOut.input)
    
    return pipeline

# MQTT Initialize
def onConnect(client, userdata, flags, rc):
    logging.info('Connected to MQTT Broker')

def onPublish(client, userdata, mid):
    print('Published MQTT message:', mid)

client = mqtt.Client()
client.on_connect = onConnect
client.on_publish = onPublish
client.connect('localhost')

while True:
    try:
        # Initialize pipeline for camera
        pipeline = initialize_camera()

        # if device is available break while loop
        with dai.Device(pipeline) as device:
            break

    except Exception as e: # If camera not connected try again
        logging.error(f"Failed to connect to camera: {e}")
        logging.info("Retrying in 5 seconds...")
        client.publish('tts', json.dumps({'message': f'Failed to connect to camera: {e}\nRetrying in 5 seconds...'}))
        time.sleep(5)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # Output queues will be used to get the rgb frames and nn data from the outputs defined above
    previewQueue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    detectionNNQueue = device.getOutputQueue(name="detections", maxSize=4, blocking=False)
    depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
    networkQueue = device.getOutputQueue(name="nnNetwork", maxSize=4, blocking=False)
    qSysInfo: dai.DataOutputQueue = device.getOutputQueue(name="sysinfo", maxSize=4, blocking=False)

    startTime = time.monotonic()
    counter = 0
    fps = 0
    color = (255, 255, 255)
    printOutputLayersOnce = True

    while True:
        inPreview = previewQueue.get()
        inDet = detectionNNQueue.get()
        depth = depthQueue.get()
        inNN = networkQueue.get()
        sysInfo = qSysInfo.tryGet()

        frame = inPreview.getCvFrame()
        depthFrame = depth.getFrame() # depthFrame values are in millimeters

        depth_downscaled = depthFrame[::4]
        if np.all(depth_downscaled == 0):
            min_depth = 0  # Set a default minimum depth value when all elements are zero
        else:
            min_depth = np.percentile(depth_downscaled[depth_downscaled != 0], 1)
        max_depth = np.percentile(depth_downscaled, 99)
        depthFrameColor = np.interp(depthFrame, (min_depth, max_depth), (0, 255)).astype(np.uint8)
        depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_HOT)

        counter+=1
        current_time = time.monotonic()
        if (current_time - startTime) > 1 :
            fps = counter / (current_time - startTime)
            counter = 0
            startTime = current_time

        detections = inDet.detections

        # If the frame is available, draw bounding boxes on it and show the frame
        height = frame.shape[0]
        width = frame.shape[1]
        detectionMessages = []
        for detection in detections:
            # have to cast detection to SpatialImgDetection to access spatial coordinates
            detection: dai.SpatialImgDetection = detection
            thisDetection = {
                'label': labelMap[detection.label],
                'confidence': detection.confidence,
                'x': int(detection.spatialCoordinates.x),  # Spatial X coordinate (mm)
                'y': int(detection.spatialCoordinates.y),  # Spatial Y coordinate (mm)
                'z': int(detection.spatialCoordinates.z)  # Spatial Z coordinate (mm)
            }
            # append the detection dictionary to messages
            detectionMessages.append(str(thisDetection))

            roiData = detection.boundingBoxMapping
            roi = roiData.roi
            roi = roi.denormalize(depthFrameColor.shape[1], depthFrameColor.shape[0])
            topLeft = roi.topLeft()
            bottomRight = roi.bottomRight()
            xmin = int(topLeft.x)
            ymin = int(topLeft.y)
            xmax = int(bottomRight.x)
            ymax = int(bottomRight.y)
            cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), color, 1)

            # Denormalize bounding box
            x1 = int(detection.xmin * width)
            x2 = int(detection.xmax * width)
            y1 = int(detection.ymin * height)
            y2 = int(detection.ymax * height)
            # print(detection)
            try:
                label = labelMap[detection.label]
            except:
                label = detection.label
            cv2.putText(frame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255))
            cv2.putText(frame, "{:.2f}".format(detection.confidence*100), (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255))
            cv2.putText(frame, f"X: {int(detection.spatialCoordinates.x)} mm", (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255))
            cv2.putText(frame, f"Y: {int(detection.spatialCoordinates.y)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255))
            cv2.putText(frame, f"Z: {int(detection.spatialCoordinates.z)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255))

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

        # Send MQTT Frame Message
        numDetections = len(detectionMessages)
        if numDetections > 0:
            logging.info(f"There were {len(detectionMessages)} detections")
            client.publish('detections', str(detectionMessages))



        cv2.putText(frame, "NN fps: {:.2f}".format(fps), (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color)
        #cv2.imshow("depth", depthFrameColor)
        #cv2.imshow("rgb", frame)
        

        if cv2.waitKey(1) == ord('q'):
            # client.disconnect()
            break