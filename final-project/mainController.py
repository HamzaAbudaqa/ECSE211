import threading, time
from navigation2 import *
from grabber import *
from utils.brick import EV3ColorSensor, EV3GyroSensor, EV3UltrasonicSensor, Motor, reset_brick, wait_ready_sensors
from colorSensorUtils import getAveragedValues, returnClosestValue

start_time = time.time()

start_time2= None
gyro_readings=[]
is_going_home = False
count = 3
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
    while not dumpsterDetected.is_set():
        move_fwd_until_wall(start_angle, MIN_DIST_FROM_WALL)
        rotate(90,LEFT_MOTOR, RIGHT_MOTOR)
        start_angle += 90
        move_fwd_until_wall(start_angle, MIN_DIST_FROM_WALL)
        rotate(90,LEFT_MOTOR, RIGHT_MOTOR)
        start_angle += 90
        going_left = not going_left
        time.sleep(0.1)


    rotate(180,LEFT_MOTOR, RIGHT_MOTOR)
    print("Found yellow")
    dump_storage(CLAW_MOTOR,LIFT_MOTOR)
    print("Dumping now")
    move_bwd(0.05, LEFT_MOTOR, RIGHT_MOTOR)

def check_for_wall():
    global start_time2
    global gyro_readings

    GYRO_THRESHOLD = 2
    TIME_LIMIT = 5
    
    current_angle = GYRO.get_value()
    #print(f"Current Angle: {current_angle}")
    gyro_readings.append(current_angle)
    
    if len(gyro_readings) > 10:
        gyro_readings.pop(0)  
    if len(gyro_readings) > 1:
        gyro_variation = max(gyro_readings) - min(gyro_readings)
    else:
        gyro_variation = 0
    distance_from_wall = US_SENSOR.get_value()
    if (gyro_variation<GYRO_THRESHOLD and distance_from_wall < MIN_DIST_FROM_WALL):
        if start_time2 == None:
            start_time2 = time.time()
        
        if time.time() - start_time2 > TIME_LIMIT:
            print("Detected prolonged stuck condition")
            move_bwd(0.5, LEFT_MOTOR, RIGHT_MOTOR)
            rotate(current_angle + 90,LEFT_MOTOR, RIGHT_MOTOR)
            start_time2 = None
        else:
            start_time2 = None


def turn_until_no_lake(direction: str):

    # if both sensors detect lake, make a bigger turn to ensure
    # the robot doesn't get stuck in infinite corrections
    if direction == "both":
        rotate(90, LEFT_MOTOR, RIGHT_MOTOR)
        lakeDetectedLeft.clear()
        lakeDetectedRight.clear()
        return

    if direction == "left":
        #i = 1
        i = -1
    else:
        i = -1
    while (lakeDetectedRight.is_set() or lakeDetectedLeft.is_set()):
        rotate(20*i, LEFT_MOTOR, RIGHT_MOTOR)
        lakeDetectedLeft.clear()
        lakeDetectedRight.clear()
    move_bwd(0.02, LEFT_MOTOR, RIGHT_MOTOR)


def rotate_at_wall(dir: str):
    """
    Rotates the robot in the given direction and positions itself in
    the next row to sweep
    - dir = "right" : right rotate (go from -180 to 0 deg on gyro)
    - dir = "left" : left rotate (go from 0 to -180 deg on gyro)
    """
    try:
        global going_left
        # go to -90 deg on gyro
        rotate(-90 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)

        if (US_SENSOR.get_value() <= MIN_DIST_FROM_WALL):
            if (going_left):
                # go to right wall
                rotate(-180 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
                move_fwd_until_wall(-180, MIN_DIST_FROM_WALL)
            rotate(-270 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
            move_fwd_until_wall(-270, MIN_DIST_FROM_WALL)
            rotate(0 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
            #print(str(GYRO.reset_measure()))
            going_left = True
            return

        LEFT_MOTOR.set_position_relative(int(ROBOT_LEN * DIST_TO_DEG))
        RIGHT_MOTOR.set_position_relative(int(ROBOT_LEN * DIST_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)

        if (dir == "right"):
            # go to 0 deg on gyro
            rotate(- GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
        else:
            # go to -180 deg on gyro
            rotate(-180 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
        
        going_left = not going_left
    except IOError as error:
        print(error)


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
        print("distance to stop at is : " + str(dist))
        print("angle to follow is :" + str(angle))
        #print("absolute angle is :" + str(GYRO.get_abs_measure()))


        while (US_SENSOR.get_value() > dist):
            if not is_going_home :
                # lake avoidance
                if (lakeDetectedLeft.is_set() and lakeDetectedRight.is_set()):
                    print("LAKE LEFT AND RIGHT")
                    turn_until_no_lake("both")
                elif (lakeDetectedLeft.is_set()):
                    print("LAKE LEFT")
                    turn_until_no_lake("left")
                elif (lakeDetectedRight.is_set()):
                    print("LAKE RIGHT")
                    turn_until_no_lake("right")
                
                # obstacle avoidance
                if (obstacleDetectedLeft.is_set()):
                    print("OBSTACLE LEFT")
                    if (US_SENSOR.get_value() < 25):  # not enough space to go around
                        move_bwd(0.03, LEFT_MOTOR, RIGHT_MOTOR)
                        break
                    else:
                        avoid_obstacle("left",LEFT_MOTOR, RIGHT_MOTOR, US_SENSOR)
                if (obstacleDetectedRight.is_set()):
                    print("OBSTACLE RIGHT")
                    if (US_SENSOR.get_value() < 25):  # not enough space to go around
                        move_bwd(0.03, LEFT_MOTOR, RIGHT_MOTOR)
                        break
                    else:
                        avoid_obstacle("right",LEFT_MOTOR, RIGHT_MOTOR, US_SENSOR)
                
                # poop pickup
                if (poopDetectedLeft.is_set()):
                    print("POOP LEFT")
                    detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
                    count += 1
                if (poopDetectedRight.is_set()):
                    print("POOP RIGHT")
                    
                    detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
                    count += 1
            check_for_wall()
            # correct trajectory
            time.sleep(0.1)
            bang_bang_controller(GYRO.get_abs_measure() - angle, LEFT_MOTOR, RIGHT_MOTOR)
            
            # initialize go back to start sequence
            if ((count >= 6 ) or (time.time() - start_time > 135)):
                is_going_home = True
                Eback_to_start()
                break

    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
        reset_brick()
        exit()


def do_s_shape():

    global avoidance_offset

    if (going_left):
        move_fwd_until_wall(0, MIN_DIST_FROM_WALL)  # go straight
        rotate_at_wall("left")  # going to angle -180 on gyro
    else:
        move_fwd_until_wall(-180, MIN_DIST_FROM_WALL)  # go straight
        rotate_at_wall("right")  # going to angle 0 on gyro
    avoidance_offset = 0


def navigation_program():
    "Do an entire sweep of the board while doing 'S' motions"
    try:
        print("Starting board sweeping started")
        while True:
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
dumpsterDetected = threading.Event()


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

            if colorDetectedLeft == "yellowFloor" or colorDetectedRight == "yellowFloor": #
                lakeDetectedRight.clear()
                obstacleDetectedRight.clear()
                poopDetectedRight.clear()
                dumpsterDetected.set()

            # sleep(0.25) in case a sleep is necessary to sync information between sensors
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        reset_brick()
        print(e)
    finally:
        exit()


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



