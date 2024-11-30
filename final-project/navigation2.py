from utils.brick import EV3GyroSensor, Motor
import time, math
from colorSensorUtils import *
from grabber import *


MOTOR_POLL_DELAY = 0.2
US_POLL_DELAY = 0.1

RW = 0.022  # wheel radius
RB = 0.05  # axle length

DIST_TO_DEG = 180 / (3.1416 * RW)  # scale factor for distance
ORIENT_TO_DEG = RB / RW  # scale factor for rotation

POWER_LIMIT = 400
SPEED_LIMIT = 720

ROBOT_LEN = 0.15  # m
MAP_SIZE = 120  # cm
NB_S = int(MAP_SIZE / (ROBOT_LEN*100))  # number of back and forth s motions to cover the entire board
FWD_SPEED = 250
TRN_SPEED = 320

# bang bang controller constants
DEADBAND = 2  # degrees
DELTA_SPEED = 70  # dps

# put value small enough so that if it's following the wall
# the distance measured from the side won't have an impact
MIN_DIST_FROM_WALL = 10  # cm


def wait_for_motor(motor: Motor):
    "Function to block until motor completion"
    while math.isclose(motor.get_speed(), 0):  # wait for motor to spin up
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(), 0):  # wait for motor to spin down
        time.sleep(MOTOR_POLL_DELAY)


def rotate(angle, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    """
    In-place rotation for the given (absolute) angle
    - angle > 0: rotate right
    - angle < 0: rotate left
    """
    try:
        print("rotating by setting motors to :" + str(angle))
        LEFT_MOTOR.set_dps(TRN_SPEED)
        RIGHT_MOTOR.set_dps(TRN_SPEED)
        LEFT_MOTOR.set_position_relative(int(angle * ORIENT_TO_DEG))
        RIGHT_MOTOR.set_position_relative(-int(angle * ORIENT_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)


def rotate_at_wall(dir: str, GYRO: EV3GyroSensor, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor,offset : int):
    """
    Rotates the robot in the given direction and positions itself in
    the next row to sweep
    - dir = "right" : right rotate (go from -180 to 0 deg on gyro)
    - dir = "left" : left rotate (go from 0 to -180 deg on gyro)
    """
    try:
        # go to -90 deg on gyro
        rotate(-90 - GYRO.get_abs_measure(), LEFT_MOTOR, RIGHT_MOTOR)
        if offset > 0 : #robot has gone left too much, needs to go right
            move_fwd(abs(offset), LEFT_MOTOR, RIGHT_MOTOR)
        elif offset < 0:
            rotate(GYRO.get_abs_measure()-180, LEFT_MOTOR, RIGHT_MOTOR)
            move_fwd(abs(offset), LEFT_MOTOR, RIGHT_MOTOR)
            rotate(GYRO.get_abs_measure() + 180, LEFT_MOTOR, RIGHT_MOTOR)

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
    "Move the robot foward without turning for the given distance"
    try:
        LEFT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))
        RIGHT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)


def move_bwd(distance, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    "Move the robot backward without turning for the given distance"
    try:
        LEFT_MOTOR.set_position_relative(-distance*DIST_TO_DEG)
        RIGHT_MOTOR.set_position_relative(-distance*DIST_TO_DEG)
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)


def stop(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    "Stop left and right motors"
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_power(0)

def pause(duration, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    "Temporarily pauses the motors for a set duration"
    rightMotorPower = RIGHT_MOTOR.get_power()
    leftMotorPower = LEFT_MOTOR.get_power()
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_power(0)
    time.sleep(duration)
    RIGHT_MOTOR.set_power(rightMotorPower)
    LEFT_MOTOR.set_power(leftMotorPower)

def bang_bang_controller(error: int, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    if (abs(error) <= DEADBAND):  # no correction
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
    elif (error > 0):  # angle too big
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
    else:  # angle too small
        LEFT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
    time.sleep(US_POLL_DELAY)


def avoid_obstacle(direction: str, LEFT_MOTOR:Motor,RIGHT_MOTOR : Motor, US_SENSOR : EV3UltrasonicSensor):
    """
    Method to avoid an obstacle (colored cube) following a predertermined path,
    and the return to its start position
    """
    # move_bwd(0.1, LEFT_MOTOR, RIGHT_MOTOR)
    smallMovement = 0.05
    bigMovement = 0.1

    move_bwd(0.08, LEFT_MOTOR, RIGHT_MOTOR)
    if (direction == "left"):
        rotate(90, LEFT_MOTOR, RIGHT_MOTOR)
        time.sleep(0.1)
        distanceFromWall = US_SENSOR.get_value()
        if (distanceFromWall > 10):
            rotate(-65, LEFT_MOTOR, RIGHT_MOTOR)
        else:
            rotate(-120, LEFT_MOTOR, RIGHT_MOTOR)
    else:
        rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)
        time.sleep(0.1)
        distanceFromWall = US_SENSOR.get_value()
        if (distanceFromWall > 10):
            rotate(65, LEFT_MOTOR, RIGHT_MOTOR)
        else:
            rotate(120, LEFT_MOTOR, RIGHT_MOTOR)

