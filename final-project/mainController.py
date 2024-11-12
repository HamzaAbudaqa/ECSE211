from utils import *
import threading
from colorSensorUtils import *


lakeColor = {knownColors[5]}
cubesToAvoid = {knownColors[0],knownColors[1]}
poop = {knownColors[2],knownColors[3]}

lakeDetectedLeft = threading.Event()
lakeDetectedRight = threading.Event()
poopDetectedLeft = threading.Event()
poopDetectedRight = threading.Event()
obstacleDetectedLeft = threading.Event()
obstacleDetectedRight = threading.Event()

runColorSensorThread = threading.Event()
runColorSensorThread.set()


def recognizeObstacles(csL,csR) :
    try:
        while runColorSensorThread.is_set():
            rgbL = getAveragedValues(25, csL)
            rgbR = getAveragedValues(25, csR) #Get color data

            colorDetectedLeft = returnClosestValue(rgbL[0],rgbL[1],rgbL[2])
            colorDetectedRight = returnClosestValue(rgbR[0],rgbR[1],rgbR[2]) #map color data to a known sample of colors

            if colorDetectedLeft in lakeColor:
                lakeDetectedLeft.set() #set the flag for a lake being detected left, note that you will need to reset it once read
            elif colorDetectedLeft in cubesToAvoid:
                obstacleDetectedLeft.set()
            elif colorDetectedLeft in poop:
                poopDetectedLeft.set()
            else : #if green detected reset all other uncaught flags
                lakeDetectedLeft.clear()
                obstacleDetectedLeft.clear()
                poopDetectedLeft.clear()

            if colorDetectedRight in lakeColor:
                lakeDetectedRight.set()
            elif colorDetectedRight in cubesToAvoid:
                obstacleDetectedRight.set()
            elif colorDetectedRight in poop:
                poopDetectedRight.set()
            else:  # if green detected reset all other uncaught flags
                lakeDetectedRight.clear()
                obstacleDetectedRight.clear()
                poopDetectedRight.clear()

            #sleep(0.25) in case a sleep is necessary to sync information between sensors
    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        pass
    finally:
        reset_brick()

colorSensorThread = threading.Thread(target=recognizeObstacles, args=(3,4))
navigationThread = threading.Thread()
grabbingThread = threading.Thread()

colorSensorThread.start()
navigationThread.start()
grabbingThread.start()


colorSensorThread.join()

















