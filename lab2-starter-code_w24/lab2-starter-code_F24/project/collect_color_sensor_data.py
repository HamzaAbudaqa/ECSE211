#!/usr/bin/env python3

"""
This test is used to collect data from the color sensor.
It must be run on the robot.
"""

# Add your imports here, if any
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor


COLOR_SENSOR_DATA_FILE = "../data_analysis/color_sensor.csv"

# complete this based on your hardware setup
COLOR_SENSOR = EV3ColorSensor(...)
TOUCH_SENSOR = TouchSensor(...)

wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.

nb_times_cs_pressed = 0

def collect_color_sensor_data():
    try:
        output_file = open(COLOR_SENSOR_DATA_FILE, "w")
        while True:
                if TOUCH_SENSOR.is_pressed():
                    red, gre, blu, lum = COLOR_SENSOR.get_value()
                    norm_red, norm_gre, norm_blu = normalize_rgb(red, gre, blu)
                    output_file.write('R={:d},G={:d},B={:d}\n'.format(norm_red,norm_gre,norm_blu))
        
    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        pass
    finally:
        print("Done collecting CS RGB samples")
        output_file.close()
        exit()

def normalize_rgb(r, g, b):
     sum_rgb = r + g + b
     return r/sum_rgb, g/sum_rgb, b/sum_rgb
     

if __name__ == "__main__":
    collect_color_sensor_data()
