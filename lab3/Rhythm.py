#!/usr/bin/env python3

import time
from utils.brick import Motor, TouchSensor, reset_brick, wait_ready_sensors


# Set up motor and button ports
DRUM_MOTOR = Motor('A')  # Motor for the drumming mechanism
BUTTON = TouchSensor(3)  # Button sensor for triggering drumming
DRUM_DELAY = 0.15 #sec


# Set the subsystem's initial state (idle)
DRUM_MOTOR.set_power(0)
DRUM_MOTOR.reset_encoder()
wait_ready_sensors(True)

def stop():
    DRUM_MOTOR.set_position(0) 
    time.sleep(1)
    DRUM_MOTOR.set_power(0)
    print("Drum Stopped")
    



# Function to start the drumming mechanism
def start_drumming():
    DRUM_MOTOR.set_limits(power = 100)  # Limit power to avoid damage
    time.sleep(.5)
    while True:
        if BUTTON.is_pressed():
            stop()
            break
        DRUM_MOTOR.set_position(75)
        
        
        time.sleep(DRUM_DELAY)  
        if BUTTON.is_pressed():
            stop()
            break
        
        DRUM_MOTOR.set_position(0) 
        time.sleep(DRUM_DELAY)
        
        if BUTTON.is_pressed():
            stop()
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
