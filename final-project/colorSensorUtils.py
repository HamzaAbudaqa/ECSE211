import math
import time




from utils.brick import TouchSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick, EV3ColorSensor

SensorPort = 1


yellowCubeMapping = [0.56,0.38,0.055,"yellow"]
orangeCubeMapping = [0.74,0.15,0.10,"orange"]
greenCubeMapping = [0.17,0.63,0.20,"green"]
blueCubeMapping = [0.20,0.33,0.47,"blue"]
purpleCubeMapping = [0.38,0.26,0.33,"purple"]
redCubeMapping = [0.91,0.11,0.08,"red"]


knownColors = [greenCubeMapping,blueCubeMapping,yellowCubeMapping,orangeCubeMapping,redCubeMapping]


def getNormalizedRGBValues() :
    COLOR_SENSOR = EV3ColorSensor(SensorPort)
    wait_ready_sensors()
    return normalize_rgb(COLOR_SENSOR.get_rgb()[0],COLOR_SENSOR.get_rgb()[1],COLOR_SENSOR.get_rgb()[2])



def getAveragedValues(precision) :
    redValues = []
    greenValues = []
    blueValues = []

    for i in range(precision) :
        
        reading = getNormalizedRGBValues()
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

while(1):
    FREQ=8
    #time.sleep(1/FREQ)
    r, g, b = getAveragedValues(25)
    print(returnClosestValue(r,g,b))