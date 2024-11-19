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

poopColor=[yellowCube, orangeCube]
#NORMALIZED
# yellowCube = [0.527,0.430,0.043,"yellowCube"]
# orangeCube = [0.704,0.197,0.099,"orangeCube"]
# 
# blueCube = [0.190,0.390,0.420,"blueCube"]
# purpleCube = [0.391,0.298,0.310,"purpleCube"]
# redCube = [0.803,0.130,0.066,"redCube"]
# greenFloor = [0.316,0.603,0.080,"greenFloor"]
# greenCube = [0.136,0.690,0.081,"greenCube"]
# blueFloor = [0.205,0.315,0.480,"blueFloor"]
# redFloor = [0.76, 0.18,0.06,"redFloor"]

consecutiveMin = 10
consecutiveMax = 15

lakeColor = ["blueFloor"]
cubesToAvoid = ["greenCube", "purpleCube"]
poop = ["yellowCube", "orangeCube"]
ignore = ["greenFloor", "redFloor"]


knownColors = [greenCube,purpleCube,yellowCube,greenFloor,blueFloor,redFloor,orangeCube]

def getNormalizedRGBValues(colorSensor) :
    return normalize_rgb(colorSensor.get_rgb()[0],colorSensor.get_rgb()[1],colorSensor.get_rgb()[2])


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



def normalize_rgb(r, g, b):
    #print("normalized")
    if r is None or g is None or b is None :
        #print("None in color Sensor!")
        return 0.313,0.603,0.080
    sum_rgb = r + g + b
    if sum_rgb == 0:
        return r, g, b
    return (r/sum_rgb), (g/sum_rgb ), (b/sum_rgb)


def returnClosestValue(r,g,b) :
    #print(r, g, b)
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


class colorSensingSubsystem :
    def __init__(self,precision):
        self.past5L = []
        self.past5R = []
        self.consecutiveR = 0
        self.consecutiveL = 0
        self.sensorPrecision = precision
        self.currentReadingL = [0,0,0]
        self.currentReadingR = [0,0,0]

    def getNormalizedRGBValuesL(self) :
        return getNormalizedRGBValues(self.CS_L)

    def getNormalizedRGBValuesR(self):
        return getNormalizedRGBValues(self.CS_R)

    def getAveragedValuesL(self,CS_L) :
        avg = getAveragedValues(self.sensorPrecision,CS_L)
        self.appendToL(avg)
        self.currentReadingL = avg
        return avg

    def getAveragedValuesR(self, CS_R) :
        avg = getAveragedValues(self.sensorPrecision,CS_R)
        self.appendToR(avg)
        self.currentReadingR = avg
        return avg

    def getPastValuesL(self) :
        print(self.past5L)
        return self.past5L

    def getPastValuesR(self) :
        print(self.past5R)
        return self.past5R

    def getClosestValue(self,val) :
        return returnClosestValue(val[0],val[1],val[2])

    def appendToL(self,val):
        self.past5L.append([val, returnClosestValue(val[0],val[1],val[2])])
        if len(self.past5L) > 5:
            self.past5L.pop(0)

    def appendToR(self,val):
        self.past5R.append([val, returnClosestValue(val[0],val[1],val[2])])
        if len(self.past5R) > 5:
            self.past5R.pop(0)

    def getPoopDetectedL(self):
        lastColorDetected = self.past5L[-2]
        currentClosest = self.getClosestValue(self.currentReadingL)
        lastClosest = self.getClosestValue(lastColorDetected)
        if not lastClosest == "yellowCube":
            print(lastColorDetected)
            self.consecutiveL = 0
            return False
        elif self.consecutiveL >= consecutiveMin:
            self.consecutiveL = 0
            return True
        elif currentClosest == "yellowCube" and currentClosest == lastClosest :
            self.currentReadingL += 1
            return False
        elif self.consecutiveL < consecutiveMin and not currentClosest == "yellowCube":
            print("line detected")
            self.consecutiveL = 0
            return False


    def getPoopDetectedR(self):
        lastColorDetected = self.past5R[-2]
        currentClosest = self.getClosestValue(self.currentReadingR)
        lastClosest = self.getClosestValue(lastColorDetected)
        if not lastClosest == "yellowCube":
            print(lastColorDetected)
            self.consecutiveR = 0
            return False
        elif self.consecutiveR >= consecutiveMin:
            self.consecutiveR = 0
            return True
        elif currentClosest == "yellowCube" and currentClosest == lastClosest :
            self.currentReadingR += 1
            return False
        elif self.consecutiveR < consecutiveMin and not currentClosest == "yellowCube":
            print("line detected")
            self.consecutiveR = 0
            return False

if __name__ == "__main__":
    function = "TESTING"
    reset_brick()
    Rsensor = EV3ColorSensor(3)
    Lsensor = EV3ColorSensor(4)
    wait_ready_sensors()
    
    if(function == "CALIBRATION"):
        print(getAveragedValues(500,Rsensor))
        
    if(function == "TESTING"):
        while(1):
            time.sleep(.5)
            r,g,b = getAveragedValues(25,Rsensor)
            print(returnClosestValue(r,g,b))
        
    





