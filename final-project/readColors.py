from colorSensorUtils import *
from utils.brick import reset_brick


CS_L = EV3ColorSensor(4)
wait_ready_sensors()

lastColor = ""

yellowsForLine = 5
colorDetected = ""
consecutiveYellows = 0
while True:
    lastColorDetected = colorDetected
    reading = getAveragedValues(66,CS_L)
    colorDetected = returnClosestValue(reading[0],reading[1],reading[2])
    if colorDetected==lastColorDetected and not colorDetected=="yellowCube" :
        consecutiveYwllows = 0
    elif (consecutiveYellows >=yellowsForLine) :
        print("POOP AHEAD")
        consecutiveYellows = 0
    elif (colorDetected=="yellowCube" and colorDetected==lastColorDetected) :
        consecutiveYellows = consecutiveYellows + 1
    elif (consecutiveYellows<yellowsForLine and not colorDetected=="yellowCube") :
        print("LINE DETECTED WEEE")
        consecutiveYellows = 0
    
        
    #print(returnClosestValue(colorDetected[0],colorDetected[1],colorDetected[2]))

