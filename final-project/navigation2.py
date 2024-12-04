from utils.brick import Motor, EV3UltrasonicSensor
import time, math
from colorSensorUtils import *


MOTOR_POLL_DELAY = 0.2
US_POLL_DELAY = 0.1

RW = 0.022  # wheel radius
RB = 0.05  # axle length

DIST_TO_DEG = 180 / (3.1416 * RW)  # scale factor for distance
ORIENT_TO_DEG = RB / RW  # scale factor for rotation

POWER_LIMIT = 400
SPEED_LIMIT = 720

ROBOT_LEN = 0.15  # m
FWD_SPEED = 250
TRN_SPEED = 320

# bang bang controller constants
DEADBAND = 2  # degrees
DELTA_SPEED = 70  # dps

# put value small enough so that if it's following the wall
# the distance measured from the side won't have an impact
MIN_DIST_FROM_WALL = 7  # cm


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
        LEFT_MOTOR.set_dps(TRN_SPEED)
        RIGHT_MOTOR.set_dps(TRN_SPEED)
        LEFT_MOTOR.set_position_relative(int(angle * ORIENT_TO_DEG))
        RIGHT_MOTOR.set_position_relative(-int(angle * ORIENT_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)
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
    """
    Implementation of a bang-bang controller to adjust the angle of the robot.
    This is done by increasing the speed of a single wheel to offset the error,
    if it is above the predetermined deadband
    """
    if (abs(error) <= DEADBAND): # no correction
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
    elif (error > 0): # angle too big
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
    else: # angle too small
        LEFT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
    time.sleep(US_POLL_DELAY)


def avoid_obstacle(direction: str, LEFT_MOTOR:Motor,RIGHT_MOTOR : Motor, US_SENSOR : EV3UltrasonicSensor):
    """
    Method to avoid an obstacle (colored cube) by turning for a set angle. The function checks
    if there is a wall blocking the optimal path before making a correction.
    The function expects the bang-bang controller to set the robot back to its original path
    after its execution.
    """
    # move backwards, further from the obstacke
    move_bwd(0.08, LEFT_MOTOR, RIGHT_MOTOR)

    if (direction == "left"):
        rotate(90, LEFT_MOTOR, RIGHT_MOTOR)
        time.sleep(0.1)
        distanceFromWall = US_SENSOR.get_value()
        if (distanceFromWall > 10):
            # make a small correction on the right
            rotate(-65, LEFT_MOTOR, RIGHT_MOTOR)
        else: 
            # robot is too close to wall to avoid by the right
            # make a bigger correction on the left
            rotate(-120, LEFT_MOTOR, RIGHT_MOTOR)
    else:
        rotate(-90, LEFT_MOTOR, RIGHT_MOTOR)
        time.sleep(0.1)
        distanceFromWall = US_SENSOR.get_value()
        if (distanceFromWall > 10):
            # make a small correction on the left
            rotate(65, LEFT_MOTOR, RIGHT_MOTOR)
        else: 
            # robot is too close to wall to avoid by the left
            # make a bigger correction on the right
            rotate(120, LEFT_MOTOR, RIGHT_MOTOR)

