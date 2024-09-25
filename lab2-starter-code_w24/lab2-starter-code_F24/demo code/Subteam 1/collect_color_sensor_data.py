#!/usr/bin/env python3

"""
This test is used to collect data from the color sensor.
It must be run on the robot.
"""

# Add your imports here, if any
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor
import time

COLOR_SENSOR_DATA_FILE = "../data_analysis/color_sensor.csv"

# complete this based on your hardware setup
COLOR_SENSOR = EV3ColorSensor(1)
TOUCH_SENSOR = TouchSensor(2)

wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.

nb_times_cs_pressed = 0

def collect_color_sensor_data():
    try:
        output_file = open(COLOR_SENSOR_DATA_FILE, "w+")
        while True:
                if TOUCH_SENSOR.is_pressed():
                    print("touched")
                    red, gre, blu =  COLOR_SENSOR.get_rgb()
                    time.sleep(0.5)
                    print(red, gre, blu)			
                    norm_red, norm_gre, norm_blu = normalize_rgb(red, gre, blu)
                    print(norm_red, norm_gre, norm_blu)
                    output_file.write(f"{norm_red},{norm_gre},{norm_blu}\n")
                    time.sleep(0.5)
                    print("slept")
        
    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        pass
    finally:
        print("Done collecting CS RGB samples")
        output_file.close()
        exit()

def normalize_rgb(r, g, b):
     print("normalized")
     sum_rgb = r + g + b
     if sum_rgb == 0 :
          return r,g,b
     return (r/sum_rgb, g/sum_rgb, b/sum_rgb)
     

if __name__ == "__main__":
    collect_color_sensor_data()
