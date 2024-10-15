import threading, logging, subprocess
from utils.brick import TouchSensor, wait_ready_sensors

TOUCH_SENSOR = TouchSensor(2)

def start_rythm():
    logging.info("Starting the Rythm.py")
    subprocess.run(["python3", "Rythm.py"])

def start_notes():
    logging.info("Starting the Notes.py")
    subprocess.run(["python3", "Notes.py"])

def emergency_stop():
    logging.info("Emergency stop triggered")
    exit()


def create_threads():

    rythm = threading.Thread(target=start_rythm)
    notes = threading.Thread(target=start_rythm)

    rythm.daemon = True
    notes.daemon = True

    rythm.start()
    notes.start()

if __name__ == "__main__":
    create_threads()
    try:
        while True:
            if TOUCH_SENSOR.is_pressed():
                emergency_stop()
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        logging.exception(e)
        exit()




