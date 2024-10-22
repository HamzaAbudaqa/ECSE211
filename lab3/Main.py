import threading, logging,time
from Notes import *
from multiThreadingCapableRhythm import *

EMERG_SENSOR = TouchSensor(2) # get the touch sensor used for the emergency stop
STARTSTOP = TouchSensor (3) # get the touch sensor used for starting/stopping percussion

stop_event = threading.Event() #create events to interrupt threads
end_event = threading.Event()



def start_playing():
   """
     Args :
        none
    Returns :
        none
    While the end_event is not set, this function will continuously play the note associated to the current distance
    otherwise, this function will exit
   """
   while not end_event.is_set():
       playSound(1)



def start_drumming():
    """
    Args :
        none
    Returns :
        none
    While the end_event is not set, this function will continuously rotate the drum, otherwise it will exit
    If the stop_event is called while this is active, the function will not exit, but the drum will stop rotating, when it is called again, it will resume
    """
    while not end_event.is_set() :
        if not stop_event.is_set() :
            drumRotate()
        else :
            time.sleep(0.05)
            continue

rythm = threading.Thread(target=start_drumming) #define the subsystem threads
note = threading.Thread(target=start_playing)



def emergency_stop():
    """
    Args :
        none
    Returns :
        none
    When this function is called, the end even is set, and both subsystem threads will be terminated once the function execution is done.
    Afterwords, the brickPi is reset.
    """
    end_event.set()
    rythm.join()
    note.join()
    reset_brick()



if __name__ == "__main__":
    wait_ready_sensors() #initalize the sensors
    stop_event.set() #set the drumming at idle on start
    rythm.start() #start both threads
    note.start()
    try:
        while True: #check for any of the buttons inputs and stop/resume the appropriate system
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




