import threading
from colorSensorUtils import getAveragedValues, returnClosestValue
from grabber import *
from utils.brick import EV3GyroSensor, EV3UltrasonicSensor, Motor, reset_brick, wait_ready_sensors, EV3ColorSensor
import time, math
from navigation2 import init_motors, bang_bang_controller, rotate, stop, move_fwd, move_bwd

MOTOR_POLL_DELAY = 0.1
US_POLL_DELAY = 0.025

RIGHT_MOTOR = Motor('A')
LEFT_MOTOR = Motor('D')
POWER_LIMIT = 400
SPEED_LIMIT = 720

ROBOT_LEN = 0.15  # m
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

# claw
CLAW_MOTOR = Motor('B')
LIFT_MOTOR = Motor('C')


def init_motors():
    "Initialize all 4 motors"
    try:
        # wheel motors
        LEFT_MOTOR.reset_encoder()
        LEFT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        LEFT_MOTOR.set_power(0)
        RIGHT_MOTOR.reset_encoder()
        RIGHT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        RIGHT_MOTOR.set_power(0)
        # claw motors
        CLAW_MOTOR.reset_encoder()
        CLAW_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        CLAW_MOTOR.set_power(0)
        LIFT_MOTOR.reset_encoder()
        LIFT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        LIFT_MOTOR.set_power(0)
    except IOError as error:
        print(error)


def move_fwd_until_wall(angle):
    """
    Makes the robot go in a straight line at the given angle (absolute angle
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
                break
            if (lakeDetectedRight.is_set()):
                print("lake detected right")
                break
            if (obstacleDetectedLeft.is_set()):
                print("object detected left")
                avoid_obstacle("right", GYRO, LEFT_MOTOR, RIGHT_MOTOR)
            if (obstacleDetectedRight.is_set()):
                print("object detected right")
                avoid_obstacle("left", GYRO, LEFT_MOTOR, RIGHT_MOTOR)
            if (poopDetectedLeft.is_set()):
                print("poop detected left")
                detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR)
                break
            if (poopDetectedRight.is_set()):
                print("poop detected right")
                detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR)
                break

            if (i % 5 != 0):  # increase delay for bang bang controller corrections
                time.sleep(0.2)
                continue
            bang_bang_controller(angle, GYRO, LEFT_MOTOR, RIGHT_MOTOR)
            i += 1
        stop(LEFT_MOTOR, RIGHT_MOTOR)
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
    finally:
        exit()


def avoid_obstacle(direction: str, GYRO: EV3GyroSensor, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    move_bwd(11, LEFT_MOTOR, RIGHT_MOTOR)
    angle = GYRO.get_abs_measure()
    turn_until_no_obstacle(direction)
    move_fwd(11, LEFT_MOTOR, RIGHT_MOTOR)
    rotate(GYRO.get_abs_measure() - angle, LEFT_MOTOR, RIGHT_MOTOR)
    move_fwd(ROBOT_LEN, LEFT_MOTOR, RIGHT_MOTOR)
    if (direction == "left"):
        rotate(90, LEFT_MOTOR, RIGHT_MOTOR)  # right to go back
        move_fwd(10, LEFT_MOTOR, RIGHT_MOTOR)
        rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)
    else:
        rotate(-90, TRN_SPEED, LEFT_MOTOR, RIGHT_MOTOR)  # rotate left to go back
        move_fwd(10, LEFT_MOTOR, RIGHT_MOTOR)
        rotate(90, LEFT_MOTOR, RIGHT_MOTOR)


def turn_until_no_obstacle(direction: str):
    if (direction == "left"):
        while (obstacleDetectedLeft.is_set() or obstacleDetectedRight.isSet()):
            rotate(-5, LEFT_MOTOR, RIGHT_MOTOR)
    else:  # turn in + angle
        while (obstacleDetectedLeft.is_set() or obstacleDetectedRight.isSet()):
            rotate(+5, LEFT_MOTOR, RIGHT_MOTOR)
    stop(LEFT_MOTOR, RIGHT_MOTOR)


def start():
    "Start left and right motors"
    time.sleep(0.15)
    RIGHT_MOTOR.set_dps(FWD_SPEED)
    LEFT_MOTOR.set_dps(FWD_SPEED)
    time.sleep(0.15)


# COLOR CODE
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
            rgbL = getAveragedValues(5, CS_L)
            rgbR = getAveragedValues(5, CS_R)  # Get color data

            colorDetectedLeft = returnClosestValue(rgbL[0], rgbL[1], rgbL[2])
            colorDetectedRight = returnClosestValue(rgbR[0], rgbR[1],
                                                    rgbR[2])  # map color data to a known sample of colors

            if colorDetectedLeft in poop:
                poopDetectedLeft.set()
                lakeDetectedLeft.clear()
                obstacleDetectedLeft.clear()
            elif colorDetectedLeft in lakeColor:
                lakeDetectedLeft.set()  # set the flag for a lake being detected left, note that you will need to reset it once read
                poopDetectedLeft.clear()
                obstacleDetectedLeft.clear()
            elif colorDetectedLeft in cubesToAvoid:
                print(colorDetectedLeft)
                obstacleDetectedLeft.set()
                lakeDetectedLeft.clear()
                poopDetectedLeft.clear()
            elif colorDetectedLeft in ignore:  # if green detected reset all other uncaught flags
                lakeDetectedLeft.clear()
                obstacleDetectedLeft.clear()
                poopDetectedLeft.clear()

            if colorDetectedRight in poop:
                poopDetectedRight.set()
                obstacleDetectedRight.clear()
                lakeDetectedRight.clear()
                detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR)
            elif colorDetectedRight in lakeColor:
                lakeDetectedRight.set()
                poopDetectedRight.clear()
                obstacleDetectedRight.clear()
            elif colorDetectedRight in cubesToAvoid:
                print(colorDetectedRight)
                obstacleDetectedRight.set()
                poopDetectedRight.clear()
                lakeDetectedRight.clear()
            elif colorDetectedRight in ignore:  # if green detected reset all other uncaught flags
                lakeDetectedRight.clear()
                obstacleDetectedRight.clear()
                poopDetectedRight.clear()

            # sleep(0.25) in case a sleep is necessary to sync information between sensors
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
    finally:
        exit()


if __name__ == "__main__":
    wait_ready_sensors()
    init_motors()

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
    finally:
        reset_brick()
        exit()

































