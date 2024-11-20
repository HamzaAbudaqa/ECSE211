from utils.brick import EV3GyroSensor, EV3UltrasonicSensor, Motor
import time, math
from colorSensorUtils import *
from grabber import *

MOTOR_POLL_DELAY = 0.2
US_POLL_DELAY = 0.1

RW = 0.022 # wheel radius
RB = 0.065  # axle length

DIST_TO_DEG = 180/(3.1416*RW)  # scale factor for distance
ORIENT_TO_DEG = RB/RW          # scale factor for rotation

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


def wait_for_motor(motor: Motor):
    "Function to block until motor completion"
    while math.isclose(motor.get_speed(),0): # wait for motor to spin up
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(),0): # wait for motor to spin down
        time.sleep(MOTOR_POLL_DELAY)


def init_motors(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
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


def move_fwd_until_wall(angle, GYRO: EV3GyroSensor, US_SENSOR: EV3UltrasonicSensor, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    """
    Makes the robot go in a straight line at the given angle (absolute angle
    rotated since start) by implementing the bang bang controller

    The robot stops once it finds itself at a distance smaller than 
    MIN_DIST_FROM_WALL from a wall
    """
    try:
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        i = 0
        while (US_SENSOR.get_value() > MIN_DIST_FROM_WALL):
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
        stop(LEFT_MOTOR, RIGHT_MOTOR)
    except IOError as error:
        print(error)

        
def rotate(angle, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    """
    In-place rotation for the given (absolute) angle
    - angle > 0: rotate right
    - angle < 0: rotate left
    """
    try:
        LEFT_MOTOR.set_dps(TRN_SPEED)
        RIGHT_MOTOR.set_dps(TRN_SPEED)
        LEFT_MOTOR.set_limits(POWER_LIMIT, TRN_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, TRN_SPEED)
        LEFT_MOTOR.set_position_relative(int(angle * ORIENT_TO_DEG)) 
        RIGHT_MOTOR.set_position_relative(-int(angle * ORIENT_TO_DEG))

        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)


def rotate_at_wall(dir: str, GYRO: EV3GyroSensor, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    """
    Rotates the robot in the given direction and positions itself in 
    the next row to sweep
    - dir = "right" : right rotate (go from -180 to 0 deg on gyro)
    - dir = "left" : left rotate (go from 0 to -180 deg on gyro)
    """
    try:
        # go to -90 deg on gyro
        if (dir == "right"):
            print("rotating right")
            rotate(-90 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
        else:
            print("rotating left 1")
            rotate(-90 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)

        # go straight for the length of the robot
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        LEFT_MOTOR.set_position_relative(int(ROBOT_LEN * DIST_TO_DEG))
        RIGHT_MOTOR.set_position_relative(int(ROBOT_LEN * DIST_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)

        if (dir == "right"): 
            # go to 0 deg on gyro
            rotate(- GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
        else:
            # go to -180 deg on gyro
            print("rotating left 2 ")
            rotate(-180 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
    except IOError as error:
        print(error)

def move_fwd(distance, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    try:
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        LEFT_MOTOR.set_position_relative(int(distance*DIST_TO_DEG))
        RIGHT_MOTOR.set_position_relative(int(distance*DIST_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)

def move_bwd(distance, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    try:
        LEFT_MOTOR.set_dps(-FWD_SPEED)
        RIGHT_MOTOR.set_dps(-FWD_SPEED)
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        LEFT_MOTOR.set_position_relative(int(-distance*DIST_TO_DEG))
        RIGHT_MOTOR.set_position_relative(int(-distance*DIST_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print (error)


def do_s_shape(GYRO: EV3GyroSensor, US_SENSOR: EV3UltrasonicSensor, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    """
    Do an "S" back and forth shape from wall to wall
    """
    # going in initial dir
    time.sleep(0.15)
    move_fwd_until_wall(0, GYRO, US_SENSOR, LEFT_MOTOR, RIGHT_MOTOR)
    time.sleep(0.15)
    rotate_at_wall("left", LEFT_MOTOR, RIGHT_MOTOR) # going to angle -180 on gyro
    # going in opposite dir
    time.sleep(0.15)
    move_fwd(ROBOT_LEN, LEFT_MOTOR, RIGHT_MOTOR)
    time.sleep(0.15)
    move_fwd_until_wall(-180, GYRO, US_SENSOR, LEFT_MOTOR, RIGHT_MOTOR)
    time.sleep(0.15)
    rotate_at_wall("right", LEFT_MOTOR, RIGHT_MOTOR) # going to angle 0 on gyro

def do_first_s_shape(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    """
    Do an "S" back and forth shape from wall to wall. Before it reaches the
    first wall, this method moves the robot further away from the wall to 
    account for its start position.
    """
    # going in initial dir
    time.sleep(0.15)
    move_fwd_until_wall(-10, LEFT_MOTOR, RIGHT_MOTOR) # move away from the wall
    time.sleep(0.15)
    rotate_at_wall("left") # going to angle -180 on gyro
    # going in opposite dir
    time.sleep(0.15)
    move_fwd(ROBOT_LEN, LEFT_MOTOR, RIGHT_MOTOR)
    time.sleep(0.15)
    move_fwd_until_wall(-180, LEFT_MOTOR, RIGHT_MOTOR)
    time.sleep(0.15)
    rotate_at_wall("right") # going to angle 0 on gyro

def get_back_to_start(GYRO: EV3GyroSensor, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    """
    Gets the robot back to the start area given that the start area
    is in direction -270 deg (90 deg) abs angle on gyro
    """
    # initially, robot is at wall
    time.sleep(0.15)
    rotate(-270 - GYRO.get_abs_measure(), TRN_SPEED) # turn in direction of start area
    move_fwd_until_wall(90, LEFT_MOTOR, RIGHT_MOTOR)
    

def stop(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    "Stop left and right motors"
    time.sleep(0.15)
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_power(0)
    time.sleep(0.15)


# def navigation_program():
#     "Make an entire sweep of the board and go back to start position"
#     try: 
#         print("Navigation program started")
#         init_motors()
#         do_first_s_shape()
#         for i in range(NB_S - 1):
#             do_s_shape()
#         # get back to start position
#         get_back_to_start()
#         print("Finished sweep of the map")
#         print("Navigation program ended")
#     except KeyboardInterrupt:
#         print("Navigation program terminated")
#     finally:
#         stop()
#         reset_brick()

def bang_bang_controller(expected_angle: int, GYRO: EV3GyroSensor, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    gyro_angle = GYRO.get_abs_measure()
    if gyro_angle is None:
        print("Gyro angle is none")
        return
    error = gyro_angle - expected_angle
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


def detect_and_grab(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    move_bwd(11, LEFT_MOTOR, RIGHT_MOTOR)
    grab_and_release()