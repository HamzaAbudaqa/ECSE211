import threading
from colorSensorUtils import getAveragedValues, returnClosestValue

from utils.brick import EV3GyroSensor, EV3UltrasonicSensor, Motor, reset_brick, wait_ready_sensors, EV3ColorSensor
import time, math
from navigation2 import *

MOTOR_POLL_DELAY = 0.1
US_POLL_DELAY = 0.025

RW = 0.022  # wheel radius
RB = 0.065  # axle length

DIST_TO_DEG = 180 / (3.1416 * RW)  # scale factor for distance
ORIENT_TO_DEG = RB / RW  # scale factor for rotation

RIGHT_MOTOR = Motor('A')
LEFT_MOTOR = Motor('D')
POWER_LIMIT = 400
SPEED_LIMIT = 720

ROBOT_LEN = 0.15  # m
MAP_SIZE = 120  # cm
NB_S = int((MAP_SIZE / ROBOT_LEN) / 2)  # number of back and forth s motions to cover the entire board
FWD_SPEED = 200
TRN_SPEED = 320

# bang bang controller constants
DEADBAND = 8  # degrees
DELTA_SPEED = 40  # dps

# put value small enough so that if it's following the wall
# the distance measured from the side won't have an impact
MIN_DIST_FROM_WALL = 15  # cm

# sensors
GYRO = EV3GyroSensor(port=1, mode="abs")
US_SENSOR = EV3UltrasonicSensor(2)
CS_L = EV3ColorSensor(4)
CS_R = EV3ColorSensor(3)
print("waiting for sensors")
wait_ready_sensors()


def move_fwd_until_wall(angle):
    """
    Makes the robot go in a straight line at the given angle (absolute angle
    rotated since start) by implementing the bang bang controller

    The robot stops once it finds itself at a distance smaller than 3cm from
    a wall
    """
    init_motors()
    try:
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        i = 0
        while (US_SENSOR.get_value() > MIN_DIST_FROM_WALL):
            if (lakeDetectedLeft.is_set()):
                print("lake detected left")
                break
            if (lakeDetectedRight.is_set()):
                print("lake detected right")
                
                break
            if (obstacleDetectedLeft.is_set()):
                print("object detected left")
               
                break
            if (obstacleDetectedRight.is_set()):
                print("object detected right")
                
                break
            if (poopDetectedLeft.is_set()):
                print("poop detected left")
                detect_and_grab()
                
                break
            if (poopDetectedRight.is_set()):
                print("poop detected right")
                detect_and_grab()
                
                break

            if (i % 5 != 0):  # increase delay for bang bang controller
                time.sleep(0.2)
                continue
            # bang bang controller
            gyro_angle = GYRO.get_abs_measure()
            if gyro_angle is None:
                print("Gyro angle is none")
                continue
            error = gyro_angle - angle
            if (abs(error) <= DEADBAND):  # no correction
                LEFT_MOTOR.set_dps(FWD_SPEED)
                RIGHT_MOTOR.set_dps(FWD_SPEED)
            elif (error > 0):  # angle too big
                # print("increasing right motor speed")
                LEFT_MOTOR.set_dps(FWD_SPEED)
                RIGHT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
            else:  # angle too small
                # print("increasing left motor speed")
                LEFT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
                RIGHT_MOTOR.set_dps(FWD_SPEED)
            time.sleep(US_POLL_DELAY)
        stop()
        time.sleep(5)
        move_fwd_until_wall(0)
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
    finally :
        exit()



def init_motors():
    "Initialize left and right motors"
    try:
        LEFT_MOTOR.reset_encoder()
        LEFT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        LEFT_MOTOR.set_power(0)
        RIGHT_MOTOR.reset_encoder()
        RIGHT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        RIGHT_MOTOR.set_power(0)
    except IOError as error:
        print(error)
    

def stop():
    "Stop left and right motors"
    time.sleep(0.15)
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_power(0)
    time.sleep(0.15)
    
def start():
    "Start left and right motors"
    time.sleep(0.15)
    RIGHT_MOTOR.set_dps(FWD_SPEED)
    LEFT_MOTOR.set_dps(FWD_SPEED)
    time.sleep(0.15)

#COLOR CODE
lakeColor = ["blueFloor"]
cubesToAvoid = ["greenCube", "purpleCube"]
poop = ["yellowCube", "orangeCube"]
ignore = ["greenFloor", "redFloor"]

lakeDetectedLeft = threading.Event()
lakeDetectedRight = threading.Event()
poopDetectedLeft = threading.Event()
poopDetectedRight = threading.Event()
obstacleDetectedLeft = threading.Event()
obstacleDetectedRight = threading.Event()

runColorSensorThread = threading.Event()
runColorSensorThread.set()

consecutiveYellowR = 0
consecutiveYellowL = 0

lineThreshold = 4

lastColorDetectedL = ""
lastColorDetectedR = ""

currentColorDetectedL = ""
currentColorDetectedR = ""


def recognizeObstacles():
    global consecutiveYellowR
    global consecutiveYellowL
    global lineThreshold
    global lastColorDetectedL
    global lastColorDetectedR
    global currentColorDetectedL
    global currentColorDetectedR
    print("started color thread")
    try:
        print("tryingToDectColor")
        while True:
            rgbL = getAveragedValues(10, CS_L)
            rgbR = getAveragedValues(10, CS_R)  # Get color data
            
            colorDetectedLeft = returnClosestValue(rgbL[0], rgbL[1], rgbL[2])
            colorDetectedRight = returnClosestValue(rgbR[0], rgbR[1],rgbR[2])  # map color data to a known sample of colors

            #print("Left: ")
            #print(rgbL)
            #print("Right: ")
            #print(rgbR)

            if colorDetectedLeft in poop:
                poopDetectedLeft.set()
                lakeDetectedLeft.clear()
                obstacleDetectedLeft.clear()
            elif colorDetectedLeft in lakeColor:
                lakeDetectedLeft.set()  # set the flag for a lake being detected left, note that you will need to reset it once read
                poopDetectedLeft.clear()
                obstacleDetectedLeft.clear()
            elif colorDetectedLeft in cubesToAvoid:
                print(rgbL)
                obstacleDetectedLeft.set()
                lakeDetectedLeft.clear()
                poopDetectedLeft.clear()
                print(currentColorDetectedL)
            elif colorDetectedLeft in ignore:  # if green detected reset all other uncaught flags
                lakeDetectedLeft.clear()
                obstacleDetectedLeft.clear()
                poopDetectedLeft.clear()

            if colorDetectedRight in poop:
                poopDetectedRight.set()
                obstacleDetectedRight.clear()
                lakeDetectedRight.clear()
                detect_and_grab()
            elif colorDetectedRight in lakeColor:
                lakeDetectedRight.set()
                poopDetectedRight.clear()
                obstacleDetectedRight.clear()
            elif colorDetectedRight in cubesToAvoid:
                obstacleDetectedRight.set()
                poopDetectedRight.clear()
                lakeDetectedRight.clear()
                print(currentColorDetectedR)
            elif colorDetectedRight in ignore:  # if green detected reset all other uncaught flags
                lakeDetectedRight.clear()
                obstacleDetectedRight.clear()
                poopDetectedRight.clear()

            # sleep(0.25) in case a sleep is necessary to sync information between sensors
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
    finally :
        exit()


def poopDetectedLeftF():
    global consecutiveYellowR
    global consecutiveYellowL
    global lineThreshold
    global lastColorDetectedL
    global lastColorDetectedR
    global currentColorDetectedL
    global currentColorDetectedR
    if not lastColorDetectedL == "yellowCube":
        consecutiveYellowL = 0
        return False
    elif (consecutiveYellowL >= lineThreshold):
        consecutiveYellowL = 0
        return True
    elif (currentColorDetectedL == "yellowCube" and currentColorDetectedL == lastColorDetectedL):
        consecutiveYellowL += 1
        return False
    elif (consecutiveYellowL < lineThreshold and not currentColorDetectedL == "yellowCube"):
        print("line detected")
        consecutiveYellowL = 0
        return False


def poopDetectedRightF():
    global consecutiveYellowR
    global consecutiveYellowL
    global lineThreshold
    global lastColorDetectedL
    global lastColorDetectedR
    global currentColorDetectedL
    global currentColorDetectedR
    if not lastColorDetectedR == "yellowCube":
        consecutiveYellowR = 0
        return False
    elif (consecutiveYellowR >= lineThreshold):
        consecutiveYellowR = 0
        return True
    elif (currentColorDetectedR == "yellowCube" and currentColorDetectedR == lastColorDetectedR):
        consecutiveYellowR += 1
        return False
    elif (consecutiveYellowR < lineThreshold and not currentColorDetectedR == "yellowCube"):
        print("line detected")
        consecutiveYellowR = 0
        return False


colorSensorThread = threading.Thread(target=recognizeObstacles)
navigationThread = threading.Thread(target=move_fwd_until_wall, args=[0], daemon=True)
colorSensorThread.daemon = True
navigationThread.daemon = True
try:
    navigationThread.start()
    colorSensorThread.start()
    colorSensorThread.join()
    navigationThread.join()
    
except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
    print(e)
finally :
    reset_brick()
    exit()
































