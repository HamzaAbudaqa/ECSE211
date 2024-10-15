from utils import sound
from utils.brick import TouchSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick, Motor
from time import sleep

duration = 0.5

def sampleAverageDistance(u, precision) :
    us = EV3UltrasonicSensor(u)
    sensorSum = 0
    for i in range(precision):  # gets an average distance over 20 samples
        sensorSum = us.get_value()  # Float value in centimeters 0, capped to 255 cm
        sleep(0.01)
    averageDistance = sensorSum / precision
    print(f"Current distance{averageDistance}\n")
    return averageDistance

def playSound(US) :
    us = EV3UltrasonicSensor(US)
    while True:
        distance = sampleAverageDistance(us, 20)
        playNote(distance, 0.5)
    return


def playNote(distance, duration) :
    if distance < 2.5 :
        sleep(0.5)
        return
    elif distance < 5 :
        sound.Sound(duration=duration, pitch = 300, volume=100).play()
    elif distance < 7.5  :
        sound.Sound(duration=duration, pitch = 600, volume=100).play()
    elif distance < 10 :
        sound.Sound(duration=duration, pitch = 900, volume=100).play()
    elif distance < 12.6 :
        sound.Sound(duration=duration, pitch = 1200, volume=100).play()
    sleep(0.05)