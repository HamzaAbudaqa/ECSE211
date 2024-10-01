
from ..utils import sound
from ..utils.brick import TouchSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick, Motor
from time import sleep
import threading


print("Hello Hooman")
DELAY_SEC = 0.6

wait_ready_sensors(True)
print("Done waiting.")

def playInstrument() :
    playSensor = TouchSensor(3)
    stopSensor = TouchSensor(2)
    try:
        setup(1)
        motorThread = threading.Thread(target=rythmFunction, args=(1, 1)) #make a thread for playing percussion in parallel to flute
        mod = 2
        motorOn = False
        while ~stopSensor.is_pressed() :
            while ~waitUntilLongPress(1): #setup phase
                mod = changeOctave(mod, 1)
                motorOn = setMotorOn(3, motorOn)
            instrumentThread = threading.Thread(target=instrumentFunction,args=(playSensor, mod, 1, 1, 0.5, 20))

            if motorOn: motorThread.start()
            instrumentThread.start()
            instrumentThread.join()
            if motorOn: motorThread.join()





    finally:
        print("Byebye hooman")
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()




def waitUntilLongPress(t1) :
    """
    Returns true if touch sensor is long pressed
    Args:
        touchSensor: the port where t1 is connected
    Returns: False when the sensor is not pressed or True when the sensor is held and released
    """
    touch = TouchSensor(t1)
    count = 0
    if ~(touch.is_pressed()):
        return False
    else :
        while count != 1 :
            sleep(0.01)
            if touch.is_pressed(): count+=1
            else : return False
        return True

def changeOctave(oldMod, t1) :
    """
    Args:
        oldMod: current modifier for note frequencies
        t1: port of the T1 sensor

    Returns: a new note modifier if T1 has been pressed

    """
    T1 = TouchSensor(t1)
    sleep(0.2)
    if T1.is_pressed() & oldMod < 3:
        return oldMod + 0.25
    elif T1.is_pressed() & oldMod == 3:
        return 0.25
    return oldMod

def setMotorOn(t3, oldMotorOn) :
    touch = TouchSensor(t3)
    sleep(0.1)
    if touch.is_pressed(): return ~oldMotorOn
    return oldMotorOn

def playNote(mod, distance, duration) :
    if distance < 2.5 :
        sound.Sound(duration=duration, pitch = 300*mod, volume=100).play()
    elif distance < 5  :
        sound.Sound(duration=duration, pitch = 600*mod, volume=100).play()
    elif distance < 7.5 :
        sound.Sound(duration=duration, pitch = 900*mod, volume=100).play()
    elif distance >= 10 :
        sound.Sound(duration=duration, pitch = 1200*mod, volume=100).play()
    sleep(duration+0.05)

def sampleAverageDistance(u, precision) :
    us = EV3UltrasonicSensor(u)
    sensorSum = 0
    for i in range(precision):  # gets an average distance over 20 samples
        sensorSum = us.get_value()  # Float value in centimeters 0, capped to 255 cm
        sleep(0.01)
    averageDistance = sensorSum / precision
    print(f"Current distance{averageDistance}\n")
    return averageDistance

def rythm(m1, period) :
    motor = Motor(m1)
    motor.reset_encoder()
    motor.set_position(90)  # rotates 90
    sleep(period)
    motor.set_position(0)
    sleep(period)

def rythmFunction(m1, period) :
    while True : rythm(m1, period)


def setup(t1) :
    T1 = TouchSensor(t1)
    if ~(T1.is_pressed()): pass
    print("Touch sensor pressed")
    sleep(1)
    print("Starting sensors")

def instrumentFunction(playSensor, mod,t1,u1,duration, precision) :
    while ~waitUntilLongPress(t1):
        averageDistance = sampleAverageDistance(u1, precision)
        print(f"Current distance{averageDistance}\n")
        if playSensor.is_pressed(): playNote(mod, averageDistance, duration)


if __name__ == "__main__":
    playInstrument()
