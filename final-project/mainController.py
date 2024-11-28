import threading, time
from colorSensorUtils import getAveragedValues, returnClosestValue
from grabber import *
from utils.brick import EV3GyroSensor, EV3UltrasonicSensor, Motor, reset_brick, wait_ready_sensors, EV3ColorSensor
from navigation2 import *

going_left = True
avoiding_lake = False # will be necessary to make sure we do not avoid obstacles and end up in the lake
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

avoidance_offset = 0 #keeps track of how far right (>0) or left(<0) we have gone in one


def init_motors():
    "Initializes all 4 motors"
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


def Eback_to_start():
    global going_left
    if going_left == False:
        angleRot = 1  # after testing we will determine the magnitude
        move_fwd_until_wall(0, MIN_DIST_FROM_WALL)
        rotate(90*angleRot,LEFT_MOTOR, RIGHT_MOTOR)
        move_fwd_until_wall(90*angleRot, MIN_DIST_FROM_WALL)
        going_left = not going_left
        rotate(90*angleRot, LEFT_MOTOR, RIGHT_MOTOR)
        move_fwd_until_wall(180*angleRot, MIN_DIST_FROM_WALL)

    else:
        move_fwd_until_wall(0, MIN_DIST_FROM_WALL)
        rotate(-90,LEFT_MOTOR, RIGHT_MOTOR)
        move_fwd_until_wall(-90, MIN_DIST_FROM_WALL)


def avoid_obstacle(direction: str, amplitude :int, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    """
    Method to avoid an obstacle (colored cube) following a predertermined path,
    and the return to its start position
    """
    time.sleep(0.5)
    # move_bwd(0.1, LEFT_MOTOR, RIGHT_MOTOR)
    smallMovement = 0.05
    bigMovement = 0.1
    move_bwd(0.08, LEFT_MOTOR,RIGHT_MOTOR)
    if (direction == "left"):
        rotate(90, LEFT_MOTOR, RIGHT_MOTOR)
        time.sleep(0.1)
        distanceFromWall = US_SENSOR.get_value()
        if (distanceFromWall > 10):
            dodge_right(LEFT_MOTOR,RIGHT_MOTOR,0.25, smallMovement)
        else :
            rotate(-180, LEFT_MOTOR, RIGHT_MOTOR)
            dodge_left(LEFT_MOTOR, RIGHT_MOTOR, 0.25, bigMovement)
    else:
        rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)
        time.sleep(0.1)
        distanceFromWall = US_SENSOR.get_value()
        if (distanceFromWall>10) :
            dodge_left(LEFT_MOTOR, RIGHT_MOTOR, 0.25, smallMovement)
        else :
            rotate(180, LEFT_MOTOR, RIGHT_MOTOR)
            dodge_right(LEFT_MOTOR, RIGHT_MOTOR, 0.25, bigMovement)



def dodge_right(LEFT_MOTOR : Motor, RIGHT_MOTOR : Motor, length : int, width : int):
    global avoidance_offset

    distanceFromWall = US_SENSOR.get_value()
    curr_angle = GYRO.get_abs_measure()
    move_fwd_until_wall(curr_angle, distanceFromWall - width*100)
    rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)
    distanceFromWall = US_SENSOR.get_value()
    curr_angle = GYRO.get_abs_measure()
    avoidance_offset += width
    if distanceFromWall < length:
        return
    avoidance_offset -= width
    time.sleep(0.1)
    move_fwd_until_wall(curr_angle, distanceFromWall - length*100)
    rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)
    distanceFromWall = US_SENSOR.get_value()
    curr_angle = GYRO.get_abs_measure()
    move_fwd_until_wall(curr_angle, distanceFromWall - width * 100)
    time.sleep(0.1)
    rotate(90, LEFT_MOTOR, RIGHT_MOTOR)


def dodge_left(LEFT_MOTOR : Motor, RIGHT_MOTOR : Motor, length : int, width : int):
    global avoidance_offset

    distanceFromWall = US_SENSOR.get_value()
    curr_angle = GYRO.get_abs_measure()
    time.sleep(0.1)
    move_fwd_until_wall(curr_angle, distanceFromWall - width * 100)
    rotate(90, LEFT_MOTOR, RIGHT_MOTOR)
    distanceFromWall = US_SENSOR.get_value()
    avoidance_offset -= width
    curr_angle = GYRO.get_abs_measure()
    if distanceFromWall < length:
        return
    time.sleep(0.1)
    move_fwd_until_wall(curr_angle, distanceFromWall - length * 100)
    avoidance_offset += width
    rotate(90, LEFT_MOTOR, RIGHT_MOTOR)
    distanceFromWall = US_SENSOR.get_value()
    curr_angle = GYRO.get_abs_measure()
    time.sleep(0.1)
    move_fwd_until_wall(curr_angle, distanceFromWall - width * 100)
    rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)


def move_fwd_until_wall(angle, dist):
    """
    Makes the robot go in a straight line at the given angle (absolute angle
    rotated since start) by implementing the bang bang controller

    The robot stops once it finds itself at distance dist from the wall
    """
    try:
        global avoiding_lake
        global avoidance_offset
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED +  DELTA_SPEED + 10)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED +  DELTA_SPEED + 10)
        print("distance to stop at is : " + str(dist))
        print("angle to follow is :" + str(angle))
        print("absolute angle is :" + str(GYRO.get_abs_measure()))

        while (US_SENSOR.get_value() > dist):
            # TODO: implement lake avoiding
            if (lakeDetectedLeft.is_set()):
                print("lake detected left")
                #stop(LEFT_MOTOR, RIGHT_MOTOR)
                avoidance_offset += 0.1
                avoid_lake(90,0.1)
            if (lakeDetectedRight.is_set()):
                #stop(LEFT_MOTOR, RIGHT_MOTOR)
                print("lake detected right")
                avoidance_offset += 0.1
                avoid_lake(-90,0.1)
            if (obstacleDetectedLeft.is_set()):
                print("object detected left")
                #if (US_SENSOR.get_value() < 15):  # not enough space to go around
                #    break
                #else:
                avoid_obstacle("left",0, LEFT_MOTOR, RIGHT_MOTOR)
            if (obstacleDetectedRight.is_set()):
                print("object detected right")
                #if (US_SENSOR.get_value() < 15):  # not enough space to go around
                #    break
                #else:
                avoid_obstacle("right",0, LEFT_MOTOR, RIGHT_MOTOR)
            if (poopDetectedLeft.is_set()):
#                 stop(LEFT_MOTOR, RIGHT_MOTOR)
                print("poop detected left")
                detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
            if (poopDetectedRight.is_set()):
#                 stop(LEFT_MOTOR, RIGHT_MOTOR)
                print("poop detected right")
                detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
            time.sleep(0.2)
            bang_bang_controller(GYRO.get_abs_measure() - angle, LEFT_MOTOR, RIGHT_MOTOR)
        #stop(LEFT_MOTOR, RIGHT_MOTOR)
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
        reset_brick()
        exit()



def do_s_shape():
    global going_left
    global avoidance_offset

    if (going_left):
        move_fwd_until_wall(0, MIN_DIST_FROM_WALL)  # go straight
        rotate_at_wall("left", GYRO, LEFT_MOTOR, RIGHT_MOTOR,avoidance_offset)  # going to angle -180 on gyro
    else:
        move_fwd_until_wall(-180, MIN_DIST_FROM_WALL)  # go straight
        rotate_at_wall("right", GYRO, LEFT_MOTOR, RIGHT_MOTOR,avoidance_offset)  # going to angle 0 on gyro
    avoidance_offset = 0
    going_left = not going_left


def navigation_program():
    "Do an entire sweep of the board while doing 'S' motions"
    try:
        print("Starting board sweeping started")
        for i in range(NB_S):
            do_s_shape()
    except KeyboardInterrupt:
        print("Navigation program terminated")
    finally:
        stop(LEFT_MOTOR, RIGHT_MOTOR)
        reset_brick()


# COLOR CODE
lakeColor = ["blueFloor"]
cubesToAvoid = ["greenCube", "purpleCube"]
poop = ["yellowCube", "orangeCube"]
ignore = ["greenFloor", "redFloor", "yellowFloor"]

lakeDetectedLeft = threading.Event()
lakeDetectedRight = threading.Event()
poopDetectedLeft = threading.Event()
poopDetectedRight = threading.Event()
obstacleDetectedLeft = threading.Event()
obstacleDetectedRight = threading.Event()
runColorSensorThread = threading.Event()
runColorSensorThread.set()


def recognizeObstacles():
    print("started color thread")
    try:
        print("tryingToDectColor")
        while True:
            rgbL = getAveragedValues(15, CS_L)
            rgbR = getAveragedValues(15, CS_R)  # Get color data

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
            elif colorDetectedRight in lakeColor:
                lakeDetectedRight.set()
                poopDetectedRight.clear()
                obstacleDetectedRight.clear()
            elif colorDetectedRight in cubesToAvoid:
                obstacleDetectedRight.set()
                poopDetectedRight.clear()
                lakeDetectedRight.clear()
            elif colorDetectedRight in ignore:  # if green detected reset all other uncaught flags
                lakeDetectedRight.clear()
                obstacleDetectedRight.clear()
                poopDetectedRight.clear()

            # sleep(0.25) in case a sleep is necessary to sync information between sensors
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        reset_brick()
        print(e)
    finally:
        exit()

def avoid_lake(angleOfRotation, distanceChange):
    '''
    Will go around a lake from the right
    '''
    print("avoiding lake with rotation:" + str(angleOfRotation))
    time.sleep(0.10)
    move_bwd(distanceChange*0.8,LEFT_MOTOR,RIGHT_MOTOR)
    rotate(angleOfRotation, LEFT_MOTOR, RIGHT_MOTOR)
    currDistance = US_SENSOR.get_value()
    curr_angle = GYRO.get_abs_measure()
    newDistance = currDistance-distanceChange*100
    if newDistance < 0.1 :
        newDistance = 0.1
    time.sleep(0.10)
    move_fwd_until_wall(curr_angle,newDistance)
    rotate(-angleOfRotation, LEFT_MOTOR, RIGHT_MOTOR)
    print("done avoiding lake")


if __name__ == "__main__":
    wait_ready_sensors()
    init_motors()
    navigationThread = threading.Thread(target=navigation_program)
    colorSensorThread = threading.Thread(target=recognizeObstacles)
    colorSensorThread.daemon = True
    navigationThread.daemon = True
    try:
         navigationThread.start()
         colorSensorThread.start()
         colorSensorThread.join()
         navigationThread.join()
        #avoid_obstacle("left", LEFT_MOTOR, RIGHT_MOTOR)
         #Eback_to_start()


    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
    finally:
        reset_brick()
        exit()



