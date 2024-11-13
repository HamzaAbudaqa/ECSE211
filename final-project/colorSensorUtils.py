import math
import time

from utils.brick import wait_ready_sensors, reset_brick, EV3ColorSensor

CS_R = EV3ColorSensor(3)
CS_L = EV3ColorSensor(4)
wait_ready_sensors()

yellowCube = [0.527,0.430,0.043,"yellowCube"]
orangeCube = [0.704,0.197,0.099,"orangeCube"]
greenCube = [0.136,0.690,0.081,"greenCube"]
blueCube = [0.190,0.390,0.420,"blueCube"]
purpleCube = [0.391,0.298,0.310,"purpleCube"]
redCube = [0.803,0.130,0.066,"redCube"]
greenFloor = [0.316,0.603,0.080,"greenFloor"]
blueFloor = [0.205,0.315,0.480,"blueFloor"] 


knownColors = [greenCube,purpleCube,yellowCube,orangeCube,greenFloor,blueFloor]

def getNormalizedRGBValues(colorSensor) :
    return normalize_rgb(colorSensor.get_rgb()[0],colorSensor.get_rgb()[1],colorSensor.get_rgb()[2])


def getAveragedValuesLeft(precision) :
    redValues = []
    greenValues = []
    blueValues = []

    for i in range(precision) :
        reading = getNormalizedRGBValues(CS_L)
        #print(reading)
        redValues.append(reading[0])
        greenValues.append(reading[1])
        blueValues.append(reading[2])
        #time.sleep(1/precision)

    return average(redValues), average(greenValues), average(blueValues)

def getAveragedValuesRight(precision) :
    redValues = []
    greenValues = []
    blueValues = []

    for i in range(precision) :
        reading = getNormalizedRGBValues(CS_R)
        #print(reading)
        redValues.append(reading[0])
        greenValues.append(reading[1])
        blueValues.append(reading[2])
        #time.sleep(1/precision)

    return average(redValues), average(greenValues), average(blueValues)



def normalize_rgb(r, g, b):
    #print("normalized")
    sum_rgb = r + g + b
    if sum_rgb == 0:
        return r, g, b
    return (r/sum_rgb), (g/sum_rgb ), (b/sum_rgb)


def returnClosestValue(r,g,b) :
    minColor = [10000,"default"]
    for knownColor in knownColors :
        distance = math.sqrt((r-knownColor[0])**2+(g-knownColor[1])**2+(b-knownColor[2])**2)
        if distance < minColor[0] :
            minColor = [distance, knownColor[3]]
    return minColor[1]

def average(values) :
    sumOfValues = 0
    for val in values :
        sumOfValues += val
    return sumOfValues/len(values)