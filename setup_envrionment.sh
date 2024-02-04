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

# Optionally, check for virtualenv and install if it's not present (pip3)
if ! command -v virtualenv &> /dev/null; then
    echo "Installing virtualenv..."
    sudo pip3 install virtualenv

    virtualenv venv # creates a virtual environment to avoid messing with system packages such as python packages
    
    source venv/bin/activate # starts the virtual environment
fi

# Run the script to install Python requirements
# Make sure install_requirements.py is good for ARM compatable
python3 install_requirements.py

# Upgrade pip within the virtual environment
pip install --upgrade pip

# deactivate env if needed
# deactivate
