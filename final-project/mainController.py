import threading, time
from colorSensorUtils import getAveragedValues, returnClosestValue
from grabber import *
from utils.brick import EV3GyroSensor, EV3UltrasonicSensor, Motor, reset_brick, wait_ready_sensors, EV3ColorSensor
from navigation2 import *
import time

is_going_home = False
count = 0
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
        LEFT_MOTOR.set_limits(POWER_LIMIT,  FWD_SPEED +  DELTA_SPEED + 10)
        LEFT_MOTOR.set_power(0)
        RIGHT_MOTOR.reset_encoder()
        RIGHT_MOTOR.set_limits(POWER_LIMIT,  FWD_SPEED +  DELTA_SPEED + 10)
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
    print("GOING BACK HOME")
    global going_left
    
    if going_left:
        start_angle = 0
    else:
        start_angle = -180
    while (not (poopDetectedLeft.is_set() and poopDetectedRight.is_set())):
        move_fwd_until_wall(start_angle, MIN_DIST_FROM_WALL)
        rotate(90,LEFT_MOTOR, RIGHT_MOTOR)
        start_angle += 90
        move_fwd_until_wall(start_angle, MIN_DIST_FROM_WALL)
        rotate(90,LEFT_MOTOR, RIGHT_MOTOR)
        start_angle += 90
        #going_left = not going_left
        time.sleep(0.1)
            
 
    rotate(180,LEFT_MOTOR, RIGHT_MOTOR)
    print("Found yellow")
    dump_storage(CLAW_MOTOR,LIFT_MOTOR)
    print("Dumping now")
    move_bwd(0.05, LEFT_MOTOR, RIGHT_MOTOR)


def avoid_obstacle(direction: str, amplitude :float, curr_straight: int):
    """
    Method to avoid an obstacle (colored cube) following a predertermined path,
    and the return to its start position
    """
    # move_bwd(0.1, LEFT_MOTOR, RIGHT_MOTOR)
    smallMovement = 0.05
    bigMovement = 0.1
    move_bwd(0.08, LEFT_MOTOR,RIGHT_MOTOR)
    if (direction == "left"):
        rotate(90, LEFT_MOTOR, RIGHT_MOTOR)
        time.sleep(0.1)
        distanceFromWall = US_SENSOR.get_value()
        if (distanceFromWall > 10):
            dodge_right(amplitude, smallMovement, curr_straight)
        else :
            rotate(-180, LEFT_MOTOR, RIGHT_MOTOR)
            dodge_left(amplitude, bigMovement, curr_straight)
    else:
        rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)
        time.sleep(0.1)
        distanceFromWall = US_SENSOR.get_value()
        if (distanceFromWall>10) : 
            dodge_left(amplitude, smallMovement, curr_straight)
        else :
            rotate(180, LEFT_MOTOR, RIGHT_MOTOR)
            dodge_right(amplitude, bigMovement, curr_straight)


def dodge_right(length : int, width : int, curr_straight: int):
    global avoidance_offset

    distanceFromWall = US_SENSOR.get_value()
    move_fwd_until_wall(curr_straight, distanceFromWall - width*100)
    rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)
    distanceFromWall = US_SENSOR.get_value()
    avoidance_offset += width
    if distanceFromWall < length:
        return
    avoidance_offset -= width
    time.sleep(0.1)
    move_fwd_until_wall(curr_straight, distanceFromWall - length*100)
    rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)
    distanceFromWall = US_SENSOR.get_value()
    move_fwd_until_wall(curr_straight, distanceFromWall - width * 100)
    time.sleep(0.1)
    rotate(90, LEFT_MOTOR, RIGHT_MOTOR)


def dodge_left(length : int, width : int, curr_straight: int):
    global avoidance_offset
    
    distanceFromWall = US_SENSOR.get_value()
    time.sleep(0.1)
    move_fwd_until_wall(curr_straight, distanceFromWall - width * 100)
    rotate(90, LEFT_MOTOR, RIGHT_MOTOR)
    distanceFromWall = US_SENSOR.get_value()
    avoidance_offset -= width
    if distanceFromWall < length:
        return
    time.sleep(0.1)
    move_fwd_until_wall(curr_straight, distanceFromWall - length * 100)
    avoidance_offset += width
    rotate(90, LEFT_MOTOR, RIGHT_MOTOR)
    distanceFromWall = US_SENSOR.get_value()
    time.sleep(0.1)
    move_fwd_until_wall(curr_straight, distanceFromWall - width * 100)
    rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)


def turn_until_no_lake(direction: str):
    if direction == "left":
        i = 1
    else:
        i = -1
    while (lakeDetectedRight.is_set() or lakeDetectedLeft.is_set()):
        rotate(20*i, LEFT_MOTOR, RIGHT_MOTOR)
        lakeDetectedLeft.clear()
        lakeDetectedRight.clear()
    move_bwd(0.02, LEFT_MOTOR, RIGHT_MOTOR)


def move_fwd_until_wall(angle, dist):
    """
    Makes the robot go in a straight line at the given angle (absolute angle
    rotated since start) by implementing the bang bang controller

    The robot stops once it finds itself at distance dist from the wall
    """
    try:
        global avoiding_lake
        global avoidance_offset
        global count
        global is_going_home

        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
        #print("curr distance to wall is : " + str(US_SENSOR.get_value()))
        #print("distance to stop at is : " + str(dist))
        #print("angle to follow is :" + str(angle))
        #print("absolute angle is :" + str(GYRO.get_abs_measure()))
        

        while (US_SENSOR.get_value() > dist):
            if (lakeDetectedLeft.is_set()):
                print("LAKE LEFT")
                # avoidance_offset += 0.1
                # avoid_lake(90,0.1)
                turn_until_no_lake("left")
            if (lakeDetectedRight.is_set()):
                print("LAKE RIGHT")
                # avoidance_offset += 0.1
                # avoid_lake(-90,0.1)
                turn_until_no_lake("right")
            if (obstacleDetectedLeft.is_set()):
                print("OBSTACLE LEFT")
                if (US_SENSOR.get_value() < 25):  # not enough space to go around
                    move_bwd(0.03, LEFT_MOTOR, RIGHT_MOTOR)
                    break
                else:
                    avoid_obstacle("left",0.25, angle)
            if (obstacleDetectedRight.is_set()):
                print("OBSTACLE RIGHT")
                if (US_SENSOR.get_value() < 25):  # not enough space to go around
                    move_bwd(0.03, LEFT_MOTOR, RIGHT_MOTOR)
                    break
                else:
                    avoid_obstacle("right",0.25, angle)
            if (poopDetectedLeft.is_set()):
                print("POOP LEFT")
                detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
                count += 1
            if (poopDetectedRight.is_set()):
                print("POOP RIGHT")
                detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
                count += 1
            time.sleep(0.1)
            bang_bang_controller(GYRO.get_abs_measure() - angle, LEFT_MOTOR, RIGHT_MOTOR)
            
            if (count >= 6 ) and not is_going_home:
                is_going_home = True
                Eback_to_start()
                break
               
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
        reset_brick()
        exit()





def do_s_shape():
    
    global going_left
    global avoidance_offset

    if (going_left):
        move_fwd_until_wall(0, MIN_DIST_FROM_WALL)  # go straight
        rotate_at_wall("left", GYRO, LEFT_MOTOR, RIGHT_MOTOR,0)  # going to angle -180 on gyro
    else:
        move_fwd_until_wall(-180, MIN_DIST_FROM_WALL)  # go straight
        rotate_at_wall("right", GYRO, LEFT_MOTOR, RIGHT_MOTOR,0)  # going to angle 0 on gyro
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

            # map color data to a known sample of colors
            colorDetectedLeft = returnClosestValue(rgbL[0], rgbL[1], rgbL[2])
            colorDetectedRight = returnClosestValue(rgbR[0], rgbR[1], rgbR[2])

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
    originalAngle = GYRO.get_abs_measure()
    print("avoiding lake with rotation:" + str(angleOfRotation))
    time.sleep(0.1)
    move_bwd(distanceChange*0.8,LEFT_MOTOR,RIGHT_MOTOR)
    rotate(angleOfRotation, LEFT_MOTOR, RIGHT_MOTOR)
    currDistance = US_SENSOR.get_value()
    curr_angle = GYRO.get_abs_measure()
    newDistance = max(currDistance-distanceChange*100,7)
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
        #avoid_obstacle("left")
         #Eback_to_start()
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
    finally:
        reset_brick()
        exit()



