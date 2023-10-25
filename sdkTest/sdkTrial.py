from depthai_sdk import OakCamera, RecordType


def callback(synced_packets):
    print(synced_packets)

# code from SDK this one has better FPS
# with OakCamera() as oak:
#     color = oak.create_camera('color', resolution='800p')  # resolution needs to be 800 or 720, cant be 1080
#     # stereo = oak.create_stereo(resolution='800p')  # works with stereo devices only!
#     # oak.visualize([color, stereo]) # creates a pop up of regular camera(color) and depth (stereo)
#     yolo = oak.create_nn('yolov6n_coco_640x640', input=color) # creates a YOLO neural network
#     oak.visualize([color, yolo]) # creates a pop up of regular camera(color) and NN(yolo) - NN is used to identify objects, good with people, fruit, and monitors
#     # oak.sync([color.out.main, yolo.out.main], callback=callback) # prints in the console a "syncronized output"
#     oak.start(blocking=True)

# # code from SDK AI models
# with OakCamera() as oak:  # NN options: https://docs.luxonis.com/projects/sdk/en/latest/features/ai_models/
#     color = oak.create_camera('color')
#     nn = oak.create_nn('yolov6n_coco_640x640', color) # dosen't support models below this one on the website IDK
#     oak.visualize([nn], fps=True)
#     oak.start(blocking=True)

# # Recording Test - saves them in a .dat file for some reason instead of .mp4
# with OakCamera() as oak:
#     color = oak.create_camera('color', resolution='800P', fps=20, encode='avc')
#     left = oak.create_camera('left', resolution='800p', fps=20, encode='avc')
#     right = oak.create_camera('right', resolution='800p', fps=20, encode='avc')
#
#     # Synchronize & save all (encoded) streams
#     oak.record([color.out.encoded, left.out.encoded, right.out.encoded], './', RecordType.VIDEO)
#     # Show color stream
#     oak.visualize([color.out.camera], scale=2/3, fps=True)
#
#     oak.start(blocking=True)

