from utils import sound
from utils.brick import TouchSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick, Motor
from time import sleep
from Notes import *
from Rhythm import *
import sys


EMERG_SENSOR = TouchSensor(3)

def read():
    while not EMERG_SENSOR.is_pressed:
        playSound(1)
    sys.exit()

if __name__ == "__main__":
    read()
        

    