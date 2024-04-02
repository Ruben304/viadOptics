import RPi.GPIO as GPIO
import time

# Set GPIO mode to BCM (Broadcom SOC channel)
GPIO.setmode(GPIO.BCM)

# Define motor pins
motor_pins = [14, 15, 18, 23]

# Set PWM frequency (Hz)
PWM_FREQUENCY = 1000

# Initialize GPIO pins for PWM control
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

# Create PWM instances for each motor
pwm_motors = [GPIO.PWM(pin, PWM_FREQUENCY) for pin in motor_pins]

try:
    while True:
        # Prompt the user to input a number between 0 and 180
        user_input = input("Enter a number between 0 and 180: ")

        # Process user input
        try:
            user_input = int(user_input)
            if 0 <= user_input <= 180:
                # Calculate intensity for each motor based on distance
                for index, pin in enumerate(motor_pins):
                    distance = abs(user_input - (index * 45))  # Calculate distance
                    intensity = int((1 - distance / 180) * 100)  # Calculate intensity (percentage)
                    pwm_motors[index].start(intensity)  # Set motor intensity
                time.sleep(3)  # Wait for 3 seconds
            else:
                print("Invalid input. Please enter a number between 0 and 180.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

        # Turn off all motor pins
        for pwm_motor in pwm_motors:
            pwm_motor.stop()

except KeyboardInterrupt:
    # Clean up GPIO on Ctrl+C
    for pwm_motor in pwm_motors:
        pwm_motor.stop()
    GPIO.cleanup()
