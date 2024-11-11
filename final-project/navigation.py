from utils.brick import Motor, reset_brick
import time
import math

MOTOR_POLL_DELAY = 0.1
MOTOR_SLEEP = 0.15

RW = 0.022 # wheel radius
RB = 0.11  # axle length

DIST_TO_DEG = 180/(math.pi*RW)   # scale factor for distance
ORIENT_TO_DEG = RB/RW           # scale factor for rotation

LEFT_MOTOR = Motor('A')
RIGHT_MOTOR = Motor('B')
POWER_LIMIT = 600
SPEED_LIMIT = 720

# sizes had to be changed otherwise the turns weren't made properly
# so i adjusted the sized of the wheels to be smaller
ROBOT_LEN = 0.15
MAP_SIZE = 1.00
NB_S = int((MAP_SIZE/ROBOT_LEN)/2)
FWD_SPEED = 300
TRN_SPEED = 300


def wait_for_motor(motor: Motor):
    "Function to block until motor completion"
    while math.isclose(motor.get_speed(),0): # wait for motor to spin up
        time.sleep(MOTOR_POLL_DELAY)
    while not math.isclose(motor.get_speed(),0): # wait for motor to spin down
        time.sleep(MOTOR_POLL_DELAY)


def init_motors():
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
    # angle < 0: rotate right
    # angle > 0: rotate left
    try:
        LEFT_MOTOR.set_dps(speed)
        RIGHT_MOTOR.set_dps(speed)
        LEFT_MOTOR.set_limits(POWER_LIMIT, speed)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, speed)
        LEFT_MOTOR.set_position_relative(int(angle * ORIENT_TO_DEG)) 
        RIGHT_MOTOR.set_position_relative(-int(angle * ORIENT_TO_DEG))
        wait_for_motor(RIGHT_MOTOR)
    except IOError as error:
        print(error)


def right_rotate_at_wall():
    # right rotates at wall and positions itself in
    # the next row to sweep
    try:
        rotate(-90, TRN_SPEED)
        move_dist_fwd(ROBOT_LEN, FWD_SPEED)
        rotate(-90, TRN_SPEED)
    except IOError as error:
        print(error)


def left_rotate_at_wall():
    # left rotates at wall and positions itself in
    # the next row to sweep
    try:
        rotate(+90, TRN_SPEED)
        move_dist_fwd(ROBOT_LEN, FWD_SPEED)
        rotate(+90, TRN_SPEED)
    except IOError as error:
        print(error)


def do_s_shape():
    move_dist_fwd(MAP_SIZE, FWD_SPEED)
    left_rotate_at_wall()
    move_dist_fwd(MAP_SIZE, FWD_SPEED)
    right_rotate_at_wall()


def stop():
    time.sleep(1)
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_power(0)
    print("Navigation stopped")


try: 
    print("Navigation started")
    init_motors()
    for i in range(0,NB_S):
        time.sleep(0.15)
        move_dist_fwd(MAP_SIZE,FWD_SPEED)
        left_rotate_at_wall()
        move_dist_fwd(MAP_SIZE,FWD_SPEED)
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

