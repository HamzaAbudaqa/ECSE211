from utils import sound
from utils.brick import  EV3UltrasonicSensor, wait_ready_sensors, reset_brick, Motor
from time import sleep

wait_ready_sensors(True) #initialize sensors

def sampleAverageDistance(u, precision) :
    """
    Args :
        u : int, the port of the ultrasonic sensor
        precision : int, the number of samples to average
    Returns :
        float : averageDistance, an averaged distance
    Returns an averaged distance value using the sliding window of width precision
    """
    us = EV3UltrasonicSensor(u)
    sensorSum = 0
    for i in range(precision):
        value = us.get_value()# gets an average distance over 20 samples
        if value is not None :
            sensorSum = sensorSum + value  # Accumulate the samples
        sleep(0.05) #sleep to allow for a different sample to be collected
    averageDistance = sensorSum / precision
    return averageDistance

def playSound(US) :
    """
       Args :
           US : int, the port of the ultrasonic sensor
       Returns :
           none : averageDistance, an averaged distance
       When called, collects the average distance and plays the associated note
       """
    distance = sampleAverageDistance(US, 5)
    playNote(distance, 0.3)
    return

def pickPitch(distance) :
    """
       Args :
           distance : float, a distance
       Returns :
           float, maps the input distance to a pitch
       Returns the pitch associated to an input distance
       """
    if distance < 12 : return  523.25 #frequency of Do
    elif distance < 24 : return 587.33 #frequency of Ré
    elif distance < 36 : return 659.26 #frequency of Mi
    elif distance <= 48 : return 698.46 #frequency of Fa

def playNote(distance, duration) :
    """
       Args :
           distance : float, a distance
           duration : float, the duration of the note
       Returns :
           none
       When called, either plays the correct note based on distance, or pauses if the user is out of range
       """
    if distance < 4 :
        sleep(duration/4)
    elif distance > 48 :
        sleep(duration/4)
    else :
        sound.Sound(duration, 100,pickPitch(distance)).play()
        sleep(duration/8)

if __name__ == "__main__":
    playSound(1)
