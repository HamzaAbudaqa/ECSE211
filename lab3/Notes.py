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
    while True:
        distance = sampleAverageDistance(US, 5)
        playNote(distance, 0.3)
    return


def playNote(distance, duration) :
    
    if distance < 7.5 :
        sleep(duration)
        return
    elif distance < 15 :
        sound.Sound(duration=duration, pitch = 523.25, volume=100).play()
        print("playing 1")
    elif distance < 22.5  :
        sound.Sound(duration=duration, pitch = 587.33, volume=100).play()
        print("playing 2")
    elif distance < 30 :
        sound.Sound(duration=duration, pitch = 659.26, volume=100).play()
        print("playing 3")
    elif distance < 37.5 :
        sound.Sound(duration=duration, pitch = 698.46, volume=100).play()
        print("playing 4")



#Main Loop

if __name__ == "__main__":
    playSound(1)
