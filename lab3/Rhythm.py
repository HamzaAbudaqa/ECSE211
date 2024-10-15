#!/usr/bin/env python3

import time
from utils.brick import Motor, TouchSensor, reset_brick, wait_ready_sensors


# Set up motor and button ports
DRUM_MOTOR = Motor('A')  # Motor for the drumming mechanism
BUTTON = TouchSensor(3)  # Button sensor for triggering drumming
DRUM_DELAY = 1 #sec


# Set the subsystem's initial state (idle)
DRUM_MOTOR.set_power(0)
DRUM_MOTOR.reset_encoder()
wait_ready_sensors(True)

# Function to start the drumming mechanism
def start_drumming():
    DRUM_MOTOR.set_limits(power = 50)  # Limit power to avoid damage
    while True:
        # Drumming rhythm logic
        DRUM_MOTOR.set_position(60) 
        time.sleep(DRUM_DELAY)  # Add delay for rhythm
        DRUM_MOTOR.set_position(0) 
        time.sleep(DRUM_DELAY)
        
        if BUTTON.is_pressed():  # Check if button is pressed again
            DRUM_MOTOR.set_position(0) 
            time.sleep(2)
            DRUM_MOTOR.set_power(0)
            print("Drum Stopped")
            break

# Main loop
try:
    print("System is ready. Press the button to start drumming...")
    # Initial state: drumming mechanism is idle
    while True:
        # Wait for the button press to start drumming
        if BUTTON.is_pressed():  # Button pressed
            print("Starting drumming mechanism...")
            start_drumming()

except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
    # Gracefully stop the program and motors
    reset_brick()
    print("Program terminated.")

finally:
    # Ensure motors are stopped when the program exits
    reset_brick()
