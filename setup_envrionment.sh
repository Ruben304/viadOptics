#!/bin/bash


#Make the script executable: chmod +x setup_environment.sh
#Execute the script: ./setup_environment.sh

# checks for Python3 and pip installation

if ! command -v python3 &> /dev/null; then # install if they're not found and directs output to dev/null to silence
    echo "Installing Python3..." # echo is similar to print 
    sudo apt-get update # refresh list of packages
    sudo apt-get install -y python3 # downloads python 3  w/o confirmation
fi

if ! command -v pip3 &> /dev/null; then # same as python
    echo "Installing pip..."
    sudo apt-get install -y python3-pip
fi

# Check for and install Mosquitto MQTT Broker
if ! command -v mosquitto &> /dev/null; then
    echo "Installing Mosquitto MQTT Broker..."
    sudo apt-get install -y mosquitto mosquitto-clients
    # Enable Mosquitto to start on boot
    sudo systemctl enable mosquitto.service
fi


# Optionally, check for virtualenv and install if it's not present (pip3)
if ! command -v virtualenv &> /dev/null; then
    echo "Installing virtualenv..."
    sudo pip3 install virtualenv

    virtualenv viad # creates a virtual environment to avoid messing with system packages such as python packages
    
    source viad/bin/activate # starts the virtual environment
fi

# Upgrade pip within the virtual environment
python3 -m pip install -U pip
python3 -m pip install --extra-index-url https://artifacts.luxonis.com/artifactory/luxonis-python-snapshot-local/ -r requirements.txt
# deactivate env if needed
# deactivate
