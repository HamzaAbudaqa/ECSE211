import threading, time
from navigation2 import *
from grabber import *
from utils.brick import EV3ColorSensor, EV3GyroSensor, EV3UltrasonicSensor, Motor, reset_brick, wait_ready_sensors
from colorSensorUtils import getAveragedValues, returnClosestValue

start_time = time.time()

start_time2= None
gyro_readings=[]
is_going_home = False # has Eback_to_start been called already
count = 0 # number of poops that have been picked up
sweep_counter = 0
going_left = True # going_left means the gyro is at 0

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

    rotate_amount = GYRO.get_abs_measure() - start_angle
    move_bwd(0.05, LEFT_MOTOR, RIGHT_MOTOR)
    if abs(rotate_amount) > 5:
        rotate(rotate_amount, LEFT_MOTOR, RIGHT_MOTOR)

    counter = 0
    while not dumpsterDetected.is_set():
        # follow the walls
        move_fwd_until_wall(start_angle, MIN_DIST_FROM_WALL)

        if (dumpsterDetected.is_set()): # we have arrived at the trash area
            break

        if (counter > 4): # the robot must be stuck at a wall and unable to turn
            move_bwd(0.1, LEFT_MOTOR, RIGHT_MOTOR)
            counter = 0

        rotate(start_angle + 90 - GYRO.get_abs_measure() ,LEFT_MOTOR, RIGHT_MOTOR)
        time.sleep(0.1)
        counter += 1
        start_angle += 90

    # rotate to face away from trash area
    rotate(0 - GYRO.get_abs_measure(),LEFT_MOTOR, RIGHT_MOTOR)
    # align the storage unit and trash area
    move_fwd(0.1, LEFT_MOTOR, RIGHT_MOTOR)
    # dump
    dump_storage(CLAW_MOTOR,LIFT_MOTOR)
    # move backwards into start square
    move_bwd(0.35, LEFT_MOTOR, RIGHT_MOTOR)
    # after dumping the navigation program terminates
    exit()

def check_for_wall():
    global start_time2
    global gyro_readings

    GYRO_THRESHOLD = 2
    TIME_LIMIT = 15
    
    current_angle = GYRO.get_value()
    gyro_readings.append(current_angle)
    
    if len(gyro_readings) > 10:
        gyro_readings.pop(0)  
    if len(gyro_readings) > 1:
        gyro_variation = max(gyro_readings) - min(gyro_readings)
    else:
        gyro_variation = 0

    if (gyro_variation < GYRO_THRESHOLD):
        if start_time2 == None:
            start_time2 = time.time()
        
        if time.time() - start_time2 > TIME_LIMIT:
            print("Detected prolonged stuck condition")
            move_bwd(0.5, LEFT_MOTOR, RIGHT_MOTOR)
            rotate(current_angle + 90,LEFT_MOTOR, RIGHT_MOTOR)
            start_time2 = None
        else:
            start_time2 = None


def turn_until_no_lake():
    "avoids a lake by turning rotating the robot 30 degrees"
    move_bwd(0.03, LEFT_MOTOR, RIGHT_MOTOR)
    if (going_left):
        rotate(-30, LEFT_MOTOR, RIGHT_MOTOR)
    else:
        rotate(30, LEFT_MOTOR, RIGHT_MOTOR)
    # reset the thread events
    lakeDetectedLeft.clear()
    lakeDetectedRight.clear()


def rotate_at_wall():
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

        if (US_SENSOR.get_value() <= MIN_DIST_FROM_WALL): # arrived at the end of the board
            if (going_left):
                # go to right wall
                rotate(-180 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
                move_fwd_until_wall(-180, MIN_DIST_FROM_WALL)
            # go back to the start position to keep sweeping
            rotate(-270 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
            move_fwd_until_wall(-270, MIN_DIST_FROM_WALL)
            rotate(0 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
            going_left = True
            return

        # move foward for the length of the robot
        LEFT_MOTOR.set_position_relative(int(ROBOT_LEN * DIST_TO_DEG))
        RIGHT_MOTOR.set_position_relative(int(ROBOT_LEN * DIST_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)

        # rotate in direction of the new path
        if (not going_left):
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
    rotated since start) by implementing the bang bang controller.

    Calls obstacle avoidance and poop pickup.

    The robot stops once it finds itself at distance dist from the wall
    """

    try:
        global count
        global is_going_home
        global sweep_counter

        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)

        while (US_SENSOR.get_value() > dist):
            if not is_going_home :
                # lake avoidance
                if (lakeDetectedLeft.is_set() or lakeDetectedRight.is_set()):
                    sweep_counter = 0
                    print("LAKE DETECTED")
                    turn_until_no_lake()
                
                # obstacle avoidance
                if (obstacleDetectedLeft.is_set()):
                    sweep_counter = 0
                    print("OBSTACLE LEFT")
                    if (US_SENSOR.get_value() < 25):  # not enough space to go around
                        move_bwd(0.03, LEFT_MOTOR, RIGHT_MOTOR)
                        break
                    else:
                        avoid_obstacle("left",LEFT_MOTOR, RIGHT_MOTOR, US_SENSOR)
                if (obstacleDetectedRight.is_set()):
                    sweep_counter = 0 
                    print("OBSTACLE RIGHT")
                    if (US_SENSOR.get_value() < 25):  # not enough space to go around
                        move_bwd(0.03, LEFT_MOTOR, RIGHT_MOTOR)
                        break
                    else:
                        avoid_obstacle("right",LEFT_MOTOR, RIGHT_MOTOR, US_SENSOR)
                
                # poop pickup
                if (poopDetectedLeft.is_set() or poopDetectedRight.is_set()):
                    sweep_counter = 0
                    print("POOP DETECTED")
                    detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
                    count += 1

                sweep_counter += 1
                if sweep_counter >= 20:
                    sweep_counter = 0
                    periodic_sweep(LEFT_MOTOR, RIGHT_MOTOR, GYRO)

            # correct the robot trajectory if needed
            check_for_wall()
            time.sleep(0.1)
            bang_bang_controller(GYRO.get_abs_measure() - angle, LEFT_MOTOR, RIGHT_MOTOR)
            
            if (dumpsterDetected.is_set() and is_going_home):
                break
            
            if (((count >= 6 ) or (time.time() - start_time > 135)) and not is_going_home):
                # initialize go back to start sequence
                is_going_home = True
                Eback_to_start()
                break

    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
        reset_brick()
        exit()


def do_s_shape():
    "move in a straight trajectory and rotate once the robot arrives at a wall"
    if (going_left):
        move_fwd_until_wall(0, MIN_DIST_FROM_WALL)
    else:
        move_fwd_until_wall(-180, MIN_DIST_FROM_WALL)
    rotate_at_wall()


def navigation_program():
    """
    Do an entire sweep of the board while doing 'S' motions.
    All other navigation and poop pickup functions are called within this
    loop.
    """
    try:
        print("Starting board sweeping")
        while True:
            do_s_shape()
    except KeyboardInterrupt:
        print("Navigation program terminated")
    finally:
        RIGHT_MOTOR.set_power(0)
        LEFT_MOTOR.set_power(0)
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
        while True:
            rgbL = getAveragedValues(15, CS_L)
            rgbR = getAveragedValues(15, CS_R)  # Get color data

            # map color data to a known sample of colors
            colorDetectedLeft = returnClosestValue(rgbL[0], rgbL[1], rgbL[2])
            colorDetectedRight = returnClosestValue(rgbR[0], rgbR[1], rgbR[2])
            dumpsterDetected.clear()

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
                dumpsterDetected.clear()
            elif colorDetectedRight in cubesToAvoid:
                obstacleDetectedRight.set()
                poopDetectedRight.clear()
                lakeDetectedRight.clear()
              
            elif colorDetectedRight in ignore:  # if green detected reset all other uncaught flags
                lakeDetectedRight.clear()
                obstacleDetectedRight.clear()
                poopDetectedRight.clear()
                 
            if colorDetectedLeft == "yellowFloor" or colorDetectedRight == "yellowFloor": # trash area
                lakeDetectedRight.clear()
                obstacleDetectedRight.clear()
                poopDetectedRight.clear()
                dumpsterDetected.set()
            
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        reset_brick()
        print(e)
    finally:
        exit()


def periodic_sweep(LEFT_MOTOR : Motor, RIGHT_MOTOR : Motor, GYRO : EV3GyroSensor):
    """
    stops and does a left to right sweeping motion to detect obstacles and poops
    in the robot's blind spots
    """
    original_angle = GYRO.get_abs_measure()
    target_angle = original_angle + 60
    count = 0
    while (GYRO.get_abs_measure() < target_angle):
        rotate(20, LEFT_MOTOR,RIGHT_MOTOR)
        count += 1
        if count>= 4 :
            break
        if poopDetectedLeft.is_set() or poopDetectedRight.is_set():
            detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
        elif obstacleDetectedRight.is_set() or obstacleDetectedLeft.is_set():
            rotate(-70, LEFT_MOTOR,RIGHT_MOTOR)
            return
    count = 0
    rotate(-60, LEFT_MOTOR,RIGHT_MOTOR)
    target_angle = original_angle - 60
    while (GYRO.get_abs_measure() > target_angle):
        rotate(-20, LEFT_MOTOR, RIGHT_MOTOR)
        count += 1
        if count>= 4 :
            break
        if poopDetectedLeft.is_set() or poopDetectedRight.is_set():
            detect_and_grab(LEFT_MOTOR, RIGHT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
        elif obstacleDetectedRight.is_set() or obstacleDetectedLeft.is_set():
            rotate(70, LEFT_MOTOR,RIGHT_MOTOR)
            return
    rotate(60,LEFT_MOTOR,RIGHT_MOTOR)



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
    except BaseException as e:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        print(e)
    finally:
        reset_brick()
        exit()



