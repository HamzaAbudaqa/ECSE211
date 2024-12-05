import math
import time

from utils.brick import EV3ColorSensor,  wait_ready_sensors, reset_brick

#RAW RGB
yellowCube = [140.48, 123.044, 10.026,"yellowCube"]
orangeCube = [142.288, 39.452, 18.876,"orangeCube"]
purpleCube = [28.608, 21.928, 25.772,"purpleCube"]
greenFloor = [6.734, 12.568, 1.772,"greenFloor"]
greenCube = [13.886, 70.006, 18.134,"greenCube"]
blueFloor = [1.558, 3.872, 4.856,"blueFloor"]
redFloor = [8.984, 6.688, 2.47,"redFloor"]
yellowFloor = [27.2, 18.784, 3.868, "yellowFloor"]

knownColors = [yellowFloor,greenCube,purpleCube,yellowCube,greenFloor,blueFloor,redFloor,orangeCube]


def getAveragedValues(precision,CS) :
    redValues = []
    greenValues = []
    blueValues = []

    for i in range(precision) :
        reading = CS.get_rgb()
        redValues.append(reading[0])
        greenValues.append(reading[1])
        blueValues.append(reading[2])
        time.sleep(0.05/precision)

    return average(redValues), average(greenValues), average(blueValues)


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
        if val is not None :
            sumOfValues += val
        else :
            print("None reading in ColorSensor !")
    return sumOfValues/len(values)


if __name__ == "__main__":
    function = "TESTING"
    reset_brick()
    Rsensor = EV3ColorSensor(3)
    Lsensor = EV3ColorSensor(4)
    wait_ready_sensors()

    try:
        if(function == "CALIBRATION"):
            print(getAveragedValues(500,Rsensor))

        if(function == "TESTING"):
            while(1):
                time.sleep(.5)
                r,g,b = getAveragedValues(25,Rsensor)
                print("readings are :" + str(r) + "," + str(g) + "," + str(b) + ",")
                print(returnClosestValue(r,g,b))
    except BaseException as e:
        print(e)
    finally:
        reset_brick()
        
    





