#!/bin/bash

# get the mqtt


# Start the Python scripts
python app/camera.py &
python app/detections.py &
python app/tts.py &