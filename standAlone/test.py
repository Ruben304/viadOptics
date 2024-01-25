# Module
import GPIO

# General
GPIO.setup(gpio, dir, pud, exclusive)
GPIO.release(gpio)
GPIO.write(gpio, value)
GPIO.read(gpio)

# Interrupts
GPIO.waitInterruptEvent(gpio = -1) # blocks until any interrupt or interrupt by specified gpio is fired. Interrupts with callbacks are ignored here
GPIO.hasInterruptEvent(gpio = -1) # returns whether interrupt happened on any or specified gpio. Interrupts with callbacks are ignored here
GPIO.setInterrupt(gpio, edge, priority, callback = None) # adds interrupt to specified pin
GPIO.clearInterrupt(gpio) # clears interrupt of specified pin

# PWM
GPIO.setPwm(gpio, highCount, lowCount, repeat=0) # repeat == 0 means indefinite
GPIO.enablePwm(gpio, enable)

# Enumerations
GPIO.Direction: GPIO.IN, GPIO.OUT
GPIO.State: GPIO.LOW, GPIO.HIGH
GPIO.PullDownUp: GPIO.PULL_NONE, GPIO.PULL_DOWN, GPIO.PULL_UP
GPIO.Edge: GPIO.RISING, GPIO.FALLING, GPIO.LEVEL_HIGH, GPIO.LEVEL_LOW

pipeline = dai.Pipeline()
script = pipeline.create(dai.node.Script)

