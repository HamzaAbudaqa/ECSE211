from threading import Thread

from lab3.utils.brick import EV3UltrasonicSensor
from navigation import *
import threading, logging,time





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
        time.sleep(0.05) #sleep to allow for a different sample to be collected
    averageDistance = sensorSum / precision
    return averageDistance


def isCloseTo(measureA, measureB, precision) :
    return abs(measureA - measureB)/max(measureA,measureB) <= precision


def continuouslySample(u, precision) :
    minMeasurement = 255
    lastMeasurement = 0

    while True :
        time.sleep(0.05)
        currMeasure = sampleAverageDistance(u, precision)
        if isCloseTo(lastMeasurement, currMeasure, 0.05):
            break
        elif currMeasure > lastMeasurement: ##getting further from initial spot
            lastMeasurement = currMeasure
        else:
            break ##getting closer

    minMeasurement = 255
    lastMeasurement = 0


    while True:
        time.sleep(0.05)
        currMeasure = sampleAverageDistance(u, precision)
        if isCloseTo(lastMeasurement, currMeasure, 0.05) :
            continue
        elif currMeasure < lastMeasurement : ##robot is getting closer to a block
            lastMeasurement = currMeasure
            minMeasurement = currMeasure
        else : ##robot is getting further
            return minMeasurement



def flyBy(u, precision) :
    if continuouslySample(u, precision)>0 :
        print("OHO DETECTED CUBE WOO")
        stopEvent.set()


def moveForward():
    if not stopEvent.is_set() :
        move_dist_fwd(10,70)



stopEvent = threading.Event()
stopEvent.clear()
detect = threading.Thread(target=flyBy(2,10))
move = threading.Thread(target=moveForward)


move.start()
detect.start()