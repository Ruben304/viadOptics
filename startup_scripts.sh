#!/bin/bash

# mosquitto installed on setup_environment
sudo systemctl status mosquitto

# Start the Python scripts
python app/camera.py &
python app/detections.py &
python app/tts.py &