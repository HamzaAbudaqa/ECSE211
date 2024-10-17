import threading, logging, subprocess
from utils.brick import TouchSensor, wait_ready_sensors, Motor,reset_brick
from Notes import *
from multiThreadingCapableRhythm import *

import time
import os
import sys


EMERG_SENSOR = TouchSensor(2)
STARTSTOP = TouchSensor (3)
DRUM_MOTOR = Motor('A')  # Motor for the drumming mechanism# Button sensor for triggering drumming
DRUM_DELAY = 0.15  # sec

stop_event = threading.Event()
end_event = threading.Event()

def start_playing():
   while not end_event.is_set():
       playSound(1)

    
       
def start_drumming():
    while not end_event.is_set() :
        if not stop_event.is_set() :
            drumRotate()
        else :
            time.sleep(0.05)
            continue
    

rythm = threading.Thread(target=start_drumming)
note = threading.Thread(target=start_playing)


def emergency_stop():
    end_event.set()
    rythm.join()
    note.join()
    reset_brick()
    


if __name__ == "__main__":
    wait_ready_sensors()
    stop_event.set()
    rythm.start()
    note.start()
    try:
        while True:
            if EMERG_SENSOR.is_pressed():
                emergency_stop()
                break
            if STARTSTOP.is_pressed() and stop_event.is_set():
                stop_event.clear()
                time.sleep(0.5)
            elif STARTSTOP.is_pressed() and not stop_event.is_set():
                stop_event.set()
                time.sleep(0.5)
    except Exception as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        logging.exception(e)
        exit()




