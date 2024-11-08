from utils.brick import Motor, reset_brick
import time
import math

MOTOR_POLL_DELAY = 0.05

RW = 0.028 # wheel radius
RB = 0.09  # axle length

DIST_TO_DEG = 180/(3.1416*RW)   # scale factor for distance
ORIENT_TO_DEG = RB/RW           # scale factor for rotation

LEFT_MOTOR = Motor('A')
RIGHT_MOTOR = Motor('B')
POWER_LIMIT = 70
SPEED_LIMIT = 720

ROBOT_LEN = 15 # cm
MAP_SIZE = 120 # cm
NB_S = int (MAP_SIZE/ROBOT_LEN)/2
FWD_SPEED = 100
TRN_SPEED = 180


def wait_for_motor(motor: Motor):
    "Function to block until completion"
    while math.isclose(motor.get_speed(),0): # wait for motor to spin up
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(),0): # wait for motor to spin down
        time.sleep(MOTOR_POLL_DELAY)


def init_motors():
    try:
        LEFT_MOTOR.reset_encoder()
        LEFT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        LEFT_MOTOR.set_power(0)
        RIGHT_MOTOR.reset_encoder()
        RIGHT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        RIGHT_MOTOR.set_power(0)
    except IOError as error:
        print(error)


def move_dist_fwd(distance, speed):
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)
        LEFT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))
        RIGHT_MOTOR.set_position_relative(int(distance * DIST_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)

        
def rotate(angle, speed):
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)
        LEFT_MOTOR.set_position_relative(int(angle * ORIENT_TO_DEG)) 
        RIGHT_MOTOR.set_position_relative(-int(angle * ORIENT_TO_DEG))
    except IOError as error:
        print(error)


def right_rotate_at_wall():
    try:
        rotate(90, TRN_SPEED)
        move_dist_fwd(ROBOT_LEN, FWD_SPEED)
        rotate(90, TRN_SPEED)
    except IOError as error:
        print(error)


def left_rotate_at_wall():
    try:
        rotate(-90, TRN_SPEED)
        move_dist_fwd(ROBOT_LEN, FWD_SPEED)
        rotate(-90, TRN_SPEED)
    except IOError as error:
        print(error)


def stop():
    time.sleep(1)
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_power(0)
    print("Navigation stopped")


try: 
    print("Navigation started")
    init_motors()
    for i in range(NB_S):
        move_dist_fwd(MAP_SIZE, FWD_SPEED)
        left_rotate_at_wall()
        move_dist_fwd(MAP_SIZE, FWD_SPEED)
        right_rotate_at_wall()
    # get back to start position
    right_rotate_at_wall()
    move_dist_fwd(MAP_SIZE, FWD_SPEED)
    print("Finished sweep of the map")
    print("Navigation program ended")
except KeyboardInterrupt:
    print("Navigation program terminated")
finally:
    stop()
    reset_brick()


