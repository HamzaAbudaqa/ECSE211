from utils import sound
from utils.brick import TouchSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick, Motor
from time import sleep

duration = 0.5
wait_ready_sensors(True)
def sampleAverageDistance(u, precision) :
    us = EV3UltrasonicSensor(u)
    sensorSum = 0
    for i in range(precision):
        value = us.get_value()# gets an average distance over 20 samples
        if value is not None :
            sensorSum = sensorSum + value  # Float value in centimeters 0, capped to 255 cm
        sleep(0.05)
    averageDistance = sensorSum / precision
    return averageDistance

def playSound(US) :
    us = EV3UltrasonicSensor(US)
    distance = sampleAverageDistance(US, 5)
    playNote(distance, 0.3)
    return

def pickPitch(distance) :
    if distance < 15 : return  523.25
    elif distance < 22.5 : return 587.33
    elif distance < 30 : return 659.26
    elif distance < 37.5 : return 698.46

def playNote(distance, duration) :
    if distance < 7.5 :
        sleep(duration/4)
    elif distance > 37.5 :
        sleep(duration/4)
    else :
        sound.Sound(duration, 100,pickPitch(distance)).play()



#Main Loop

if __name__ == "__main__":
    playSound(1)
