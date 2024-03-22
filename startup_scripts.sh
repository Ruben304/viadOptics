#!/bin/bash

# Start the Python scripts
python3 app/camera.py &
python3 app/detections.py &
python3 app/tts.py &