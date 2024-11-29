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
DELTA_SPEED = 40  # dps

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
        print("rotating by setting motors to :" + str(angle * ORIENT_TO_DEG))
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
    try:
        # not sure whether this works or not:
        # LEFT_MOTOR.set_dps(FWD_SPEED)
        # RIGHT_MOTOR.set_dps(FWD_SPEED)
        # LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        # RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        LEFT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))
        RIGHT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)


def move_bwd(distance, LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    "Move the robot backward without turning for the given distance"
    try:
        # not sure whether this works or not:
        # LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        # RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        LEFT_MOTOR.set_position_relative(-distance*DIST_TO_DEG)
        RIGHT_MOTOR.set_position_relative(-distance*DIST_TO_DEG)
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)


def stop(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    "Stop left and right motors"
    #     time.sleep(0.15)
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_power(0)
    # time.sleep(0.15)

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
    print("BANG BANG ERROR IS : " + str(error))
    if (abs(error) <= DEADBAND):  # no correction
        print("no correction")
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
    elif (error > 0):  # angle too big
        print("increasing right motor speed")
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
    else:  # angle too small
        print("increasing left motor speed")
        LEFT_MOTOR.set_dps(FWD_SPEED + DELTA_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
    time.sleep(US_POLL_DELAY)


def rotate_single_wheel(abs_angle, Motor: Motor):
    """
    In-place rotation for the given (absolute) angle
    - angle > 0: rotate right
    - angle < 0: rotate left
    """
    try:

        Motor.set_dps(TRN_SPEED)
        Motor.set_limits(POWER_LIMIT, TRN_SPEED)
        Motor.set_position_relative(int(abs_angle * ORIENT_TO_DEG))
    except IOError as error:
        print(error)


def setup_for_zigZag(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor, GYRO: EV3GyroSensor):
    """
    Sets up the robot for a zigzag movement

    """
    try:
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)

        angleBefore = GYRO.get_abs_measure()
        rotate_single_wheel(90 / 2, LEFT_MOTOR)
        rotate_single_wheel(90 / 6, RIGHT_MOTOR)  # go half to the right
        #wait_for_motor(RIGHT_MOTOR)
        wait_for_motor(LEFT_MOTOR)
        angleAfter = GYRO.get_abs_measure()
        changeInAngle = angleAfter - angleBefore
        adjust(LEFT_MOTOR, RIGHT_MOTOR, -14 - changeInAngle)
        gyro_angle = GYRO.get_abs_measure()
    except IOError as error:
        print(error)


def adjust(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor, error):
    if abs(error) <= 3:
        return
    print("ERROR IS : " + str(error))
    rotate(error, LEFT_MOTOR, RIGHT_MOTOR)


def zigZag(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor, GYRO: EV3GyroSensor):
    try :
        LEFT_MOTOR.set_dps(FWD_SPEED)
        RIGHT_MOTOR.set_dps(FWD_SPEED)
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)

        angleBefore = GYRO.get_abs_measure()
        rotate_single_wheel(180 / 2, LEFT_MOTOR)
        rotate_single_wheel(180 / 6, RIGHT_MOTOR)  ##ZigZag to the right
        #wait_for_motor(RIGHT_MOTOR)
        wait_for_motor(LEFT_MOTOR)
        
        
        angleAfter = GYRO.get_abs_measure()
        changeInAngle = angleBefore - angleAfter
        adjust(LEFT_MOTOR, RIGHT_MOTOR, 29 - changeInAngle)
        time.sleep(0.25)
        angleBefore = GYRO.get_abs_measure()
        print(changeInAngle)
        rotate_single_wheel(180 / 6, LEFT_MOTOR)
        rotate_single_wheel(180 / 2, RIGHT_MOTOR)  # ZigZag to the left
        wait_for_motor(RIGHT_MOTOR)
        #wait_for_motor(LEFT_MOTOR)
        angleAfter = GYRO.get_abs_measure()
        changeInAngle = angleBefore - angleAfter
        print(changeInAngle)
        adjust(LEFT_MOTOR, RIGHT_MOTOR, -29 - changeInAngle)
    except IOError as error:
        print(error)


def straightenOut(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor, isRight) :
    if isRight :
        rotate(-22,LEFT_MOTOR,RIGHT_MOTOR)
    else :
        rotate(22,LEFT_MOTOR,RIGHT_MOTOR)




if __name__ == "__main__":
     try:
        GYRO = EV3GyroSensor(port=1, mode="abs")
        LEFT_MOTOR = Motor('A')
        RIGHT_MOTOR = Motor('D')
        wait_ready_sensors()
        setup_for_zigZag(LEFT_MOTOR, RIGHT_MOTOR, GYRO)  # start the movement
        #navigation_program()
        
        print(str(GYRO.get_abs_measure()))
        for i in range(4):
            zigZag(LEFT_MOTOR, RIGHT_MOTOR, GYRO)
            sleep(0.25)
        sleep(1)
        straightenOut(LEFT_MOTOR, RIGHT_MOTOR, True)
     except BaseException as e:
         print(e)
     finally:
         reset_brick()

