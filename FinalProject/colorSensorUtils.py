import math
import time

from numpy import integer
from numpy.ma.extras import average

from utils.brick import TouchSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick, EV3ColorSensor

SensorPort = 2

greenFloorMapping = [0,255,0,"greenFloor"]
blueFloorMapping = [0,0,255,"blueFloor"]
redFloorMapping = [0,0,255,"redFloor"]

yellowCubeMapping = [125,125,0,"yellowCube"]
orangeCubeMapping = [170,125,0,"orangeCube"]
greenCubeMapping = [0,100,0,"greenCube"]
blueCubeMapping = [0,0,100,"blueCube"]


knownColors = {greenCubeMapping,blueCubeMapping,yellowCubeMapping,orangeCubeMapping,greenFloorMapping,blueFloorMapping,redFloodMapping}


def getNormaliedRGBValues() :

    COLOR_SENSOR = EV3ColorSensor(1)
    return normalize_rgb(COLOR_SENSOR.get_rgb())



def getAveragedValues(precision) :
    redValues = []
    greenValues = []
    blueValues = []

    for i in range(precision) :
        reading = getNormaliedRGBValues()
        redValues.append(reading[0])
        greenValues.append(reading[1])
        blueValues.append(reading[2])
        time.sleep(0.5/precision)

    return average(redValues), average(greenValues), average(blueValues)



def normalize_rgb(r, g, b):
    print("normalized")
    sum_rgb = r + g + b
    if sum_rgb == 0:
        return r, g, b
    return r / sum_rgb, g / sum_rgb, b / sum_rgb


def returnClosestValue(r,g,b) :
    minColor = [10000,"default"]
    for knownColor in knownColors :
        distance = math.sqrt((r-knownColor[0])**2+(g-knownColor[1])**2+(b-knownColor[2])**2)
        if distance < minColor[0] :
            minColor.append(distance, knownColor[3])
    return minColor[1]
