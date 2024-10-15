import threading, logging, subprocess
from utils.brick import TouchSensor, wait_ready_sensors, Motor
import time
import os


EMERG_SENSOR = TouchSensor(3)
STARTSTOP = TouchSensor (1)
DRUM_MOTOR = Motor('B')  # Motor for the drumming mechanism# Button sensor for triggering drumming
DRUM_DELAY = 0.15  # sec

stop_event = threading.Event()
end_event = threading.Event()

def start_drumming():
    while not end_event.is_set() :
        print(stop_event.is_set())
        if not stop_event.is_set() :
            DRUM_MOTOR.set_limits(power=70)  # Limit power to avoid damage
            time.sleep(.5)
            DRUM_MOTOR.set_position(60)

            time.sleep(DRUM_DELAY)
            DRUM_MOTOR.set_position(0)
            time.sleep(DRUM_DELAY)
        else :
            time.sleep(0.05)
            continue
    

rythm = threading.Thread(target=start_drumming)



def start_rythm():
    logging.info("Starting the Rythm.py")
    subprocess.run(["python3", "Rythm.py"])

def start_notes():
    logging.info("Starting the Notes.py")
    subprocess.run(["python3", "Notes.py"])

def emergency_stop():
    print("AAAAAAA")
    end_event.set()
    rythm.join()
    


if __name__ == "__main__":
    rythm.start()
    try:
        while True:
            if EMERG_SENSOR.is_pressed():
                emergency_stop()
                os._exit(0)
            if STARTSTOP.is_pressed() and stop_event.is_set():
                stop_event.clear()
                time.sleep(0.5)
            elif STARTSTOP.is_pressed() and not stop_event.is_set():
                stop_event.set()
                time.sleep(0.5)
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        logging.exception(e)
        exit




