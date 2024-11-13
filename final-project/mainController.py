
import threading
from colorSensorUtils import getAveragedValuesLeft, getAveragedValuesRight, returnClosestValueRight, returnClosestValueLeft

from utils.brick import EV3GyroSensor, EV3UltrasonicSensor, Motor, reset_brick, wait_ready_sensors
import time, math

MOTOR_POLL_DELAY = 0.2
US_POLL_DELAY = 0.1

RW = 0.022 # wheel radius
RB = 0.065  # axle length

DIST_TO_DEG = 180/(3.1416*RW)  # scale factor for distance
ORIENT_TO_DEG = RB/RW          # scale factor for rotation

RIGHT_MOTOR = Motor('A')
LEFT_MOTOR = Motor('B')
POWER_LIMIT = 400
SPEED_LIMIT = 720

ROBOT_LEN = 0.15 # m
MAP_SIZE = 120 # cm
NB_S = int((MAP_SIZE/ROBOT_LEN)/2) # number of back and forth s motions to cover the entire board
FWD_SPEED = 300
TRN_SPEED = 320

# bang bang controller constants
DEADBAND = 8 # degrees
DELTA_SPEED = 40 # dps

# put value small enough so that if it's following the wall
# the distance measured from the side won't have an impact
MIN_DIST_FROM_WALL = 15 # cm

# sensors
GYRO = EV3GyroSensor(port=1, mode="abs")
US_SENSOR = EV3UltrasonicSensor(2)
print("waiting for sensors")
wait_ready_sensors()

# code for nav


def wait_for_motor(motor: Motor):
    "Function to block until motor completion"
    while math.isclose(motor.get_speed(),0): # wait for motor to spin up
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(),0): # wait for motor to spin down
        time.sleep(MOTOR_POLL_DELAY)


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


def move_fwd_until_wall(angle):
    """
    Makes the robot go in a staright line at the given angle (absolute angle
    rotated since start) by implementing the bang bang controller

    The robot stops once it finds itself at a distance smaller than 3cm from
    a wall
    """
    try:
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        i = 0
        while (US_SENSOR.get_value() > MIN_DIST_FROM_WALL):
            if (lakeDetectedLeft.is_set()):
                print("lake detected left")
                stop()
                break
            if (lakeDetectedRight.is_set()):
                print("lake detected right")
                stop()
                break
            if (obstacleDetectedLeft.is_set()):
                print("object detected left")
                stop()
            if (obstacleDetectedRight.is_set()):
                print("object detected right")
                stop()
            if (poopDetectedLeft.is_set()):
                print("poop detected left")
                stop()
                break
            if (poopDetectedRight.is_set()):
                print("poop detected right")
                stop()
                break
            
            if (i%5 != 0):# increase delay for bang bang controller
                time.sleep(0.2)
                continue
            # bang bang controller
            gyro_angle = GYRO.get_abs_measure()
            #print("current angle is: " + str(gyro_angle))
                  
            error = gyro_angle - angle
            if (abs(error) <= DEADBAND): # no correction
                LEFT_MOTOR.set_dps(FWD_SPEED)
                RIGHT_MOTOR.set_dps(FWD_SPEED)
            elif (error > 0): # angle too big
                #print("increasing right motor speed")
                LEFT_MOTOR.set_dps(FWD_SPEED)
                RIGHT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
            else: # angle too small
                #print("increasing left motor speed")
                LEFT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
                RIGHT_MOTOR.set_dps(FWD_SPEED)
            time.sleep(US_POLL_DELAY)
        stop()
    except IOError as error:
        print(error)

    

def stop():
    "Stop left and right motors"
    time.sleep(0.15)
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_power(0)
    time.sleep(0.15)


def navigation_program():
    "Make an entire sweep of the board and go back to start position"
    try: 
        print("Navigation program started")
        init_motors()
        move_fwd_until_wall()
    except KeyboardInterrupt:
        print("Navigation program terminated")
    finally:
        stop()
        reset_brick()


lakeColor = [knownColors[5]]
cubesToAvoid = [knownColors[0],knownColors[1]]
poop = [knownColors[2],knownColors[3]]

lakeDetectedLeft = threading.Event()
lakeDetectedRight = threading.Event()
poopDetectedLeft = threading.Event()
poopDetectedRight = threading.Event()
obstacleDetectedLeft = threading.Event()
obstacleDetectedRight = threading.Event()

runColorSensorThread = threading.Event()
runColorSensorThread.set()


def recognizeObstacles(csL,csR) :
    print("started color thread")
    try:
        print("tryingToDectColor")
        while True:
            rgbL = getAveragedValuesLeft(25)
            rgbR = getAveragedValuesRight(25) #Get color data

            colorDetectedLeft = returnClosestValueLeft(rgbL[0],rgbL[1],rgbL[2])
            colorDetectedRight = returnClosestValueRight(rgbR[0],rgbR[1],rgbR[2]) #map color data to a known sample of colors
            
            print(colorDecetedLeft)
            
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

colorSensorThread = threading.Thread(target=recognizeObstacles(3,4))
colorSensorThread.start()
navigationThread = threading.Thread(target=move_fwd_until_wall(0))
navigationThread.start()



colorSensorThread.join()
navigationThread.join()


















