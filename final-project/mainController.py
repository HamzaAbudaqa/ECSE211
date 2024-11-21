import threading, time
from colorSensorUtils import getAveragedValues, returnClosestValue
from grabber import *
from utils.brick import EV3GyroSensor, EV3UltrasonicSensor, Motor, reset_brick, wait_ready_sensors, EV3ColorSensor
from navigation2 import *


# sensors
GYRO = EV3GyroSensor(port=1, mode="abs")
US_SENSOR = EV3UltrasonicSensor(2)
CS_L = EV3ColorSensor(4)
CS_R = EV3ColorSensor(3)

# wheel motors
RIGHT_MOTOR = Motor('A')
LEFT_MOTOR = Motor('D')
# claw motors
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


def navigation_program():
    "Do an entire sweep of the board"
    try:
        print("Starting board sweeping started")
        do_first_s_shape(GYRO, US_SENSOR, LEFT_MOTOR, RIGHT_MOTOR)
        for i in range(NB_S - 1):
            do_s_shape()
    except KeyboardInterrupt:
        print("Navigation program terminated")
    finally:
        stop()
        reset_brick()



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
    navigationThread = threading.Thread(target=navigation_program, args=[0], daemon=True)
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







# HELPER METHODS FOR NAVIGATION THAT CAN'T BE PUT IN navigation2.py
# BECAUSE THEY NEED ACCESS TO THREAD EVENTS


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
                if (US_SENSOR.get_value() < 15): # not enough space to go around
                    break
                else:
                    avoid_obstacle("left", LEFT_MOTOR, RIGHT_MOTOR)
            if (obstacleDetectedRight.is_set()):
                print("object detected right")
                if (US_SENSOR.get_value() < 15): # not enough space to go around
                    break
                else:
                    avoid_obstacle("right", LEFT_MOTOR, RIGHT_MOTOR)
            if (poopDetectedLeft.is_set()):
                print("poop detected left")
                detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR)
            if (poopDetectedRight.is_set()):
                print("poop detected right")
                detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR)

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

def do_s_shape():
    """
    Do an "S" back and forth shape from wall to wall
    """
    # going in initial dir
    time.sleep(0.15)
    move_fwd_until_wall(0)
    time.sleep(0.15)
    rotate_at_wall("left", LEFT_MOTOR, RIGHT_MOTOR)  # going to angle -180 on gyro
    # going in opposite dir
    time.sleep(0.15)
    move_fwd(ROBOT_LEN, LEFT_MOTOR, RIGHT_MOTOR)
    time.sleep(0.15)
    move_fwd_until_wall(-180)
    time.sleep(0.15)
    rotate_at_wall("right", LEFT_MOTOR, RIGHT_MOTOR)  # going to angle 0 on gyro

def do_first_s_shape():
    """
    Do an "S" back and forth shape from wall to wall. Before it reaches the
    first wall, this method moves the robot further away from the wall to
    account for its start position.
    """
    # going in initial dir
    time.sleep(0.15)
    move_fwd_until_wall(-10)  # move away from the wall
    time.sleep(0.15)
    rotate_at_wall("left")  # going to angle -180 on gyro
    # going in opposite dir
    time.sleep(0.15)
    move_fwd(ROBOT_LEN, LEFT_MOTOR, RIGHT_MOTOR)
    time.sleep(0.15)
    move_fwd_until_wall(-180)
    time.sleep(0.15)
    rotate_at_wall("right")  # going to angle 0 on gyro


def turn_until_no_obstacle(direction: str):
    if (direction == "left"):
        while (obstacleDetectedLeft.is_set() or obstacleDetectedRight.isSet()):
            rotate(-5, LEFT_MOTOR, RIGHT_MOTOR)
    else:  # turn in + angle
        while (obstacleDetectedLeft.is_set() or obstacleDetectedRight.isSet()):
            rotate(+5, LEFT_MOTOR, RIGHT_MOTOR)
    stop(LEFT_MOTOR, RIGHT_MOTOR)