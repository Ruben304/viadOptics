import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import json
import logging

# Set up logging
logging.basicConfig(filename='haptic_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set GPIO mode to BCM (Broadcom SOC channel)
GPIO.setmode(GPIO.BCM)

# Define motor pins
motor_pins = [14, 15, 23, 24]

# Set PWM frequency (Hz)
PWM_FREQUENCY = 1000

# Initialize GPIO pins for PWM control and create PWM instances for each motor
pwm_motors = []
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, PWM_FREQUENCY)
    pwm.start(0)  # Initialize with 0 intensity
    pwm_motors.append(pwm)


def adjust_motor_intensity(degree):
    # map degree (-90 to 90) for motor intensity
    for index, pwm_motor in enumerate(pwm_motors):
        # Adjust the formula based on  requirements
        distance = abs(degree - ((index - 1.5) * 60))  # Adjusted for -90 to 90 range
        intensity = max(0, int((1 - distance / 180) * 100))  # Ensure intensity is not negative
        pwm_motor.ChangeDutyCycle(intensity)

    # Wait for 2 seconds
    time.sleep(2)

    # Turn off all motors after 2 seconds
    for pwm_motor in pwm_motors:
        pwm_motor.ChangeDutyCycle(0)


def onConnect(client, userdata, flags, rc):
    logging.info('Connected to MQTT broker')
    client.subscribe('hpt')

def onFail(client, userdata, flags, rc):
    logging.error('Failed to connect to MQTT broker')

def onMessage(client, userdata, msg: mqtt.MQTTMessage):
    messageJSON = json.loads(msg.payload.decode())
    logging.info('Received message: %s', messageJSON)
    degree_text = messageJSON.get("degree", 0)

    try:
        degree = int(degree_text)
        if -90 <= degree <= 90:
            adjust_motor_intensity(degree)
        else:
            logging.warning("Degree out of bounds: %d. Please ensure it's between -90 and 90.", degree)

    except ValueError:
        logging.error("Invalid degree value received: %s", degree_text)

def cleanup():
    # Clean up GPIO on exit
    for pwm_motor in pwm_motors:
        pwm_motor.stop()
    GPIO.cleanup()

try:
    client = mqtt.Client()
    client.on_connect = onConnect
    client.on_message = onMessage

    client.connect('localhost')
    client.loop_forever()

except KeyboardInterrupt:
    cleanup()
