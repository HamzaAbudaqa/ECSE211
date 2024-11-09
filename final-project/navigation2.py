from utils.brick import EV3GyroSensor, EV3UltrasonicSensor, Motor, reset_brick, wait_ready_sensors
import time, math

MOTOR_POLL_DELAY = 0.15
US_POLL_DELAY = 0.1

RW = 0.028 # wheel radius
RB = 0.09  # axle length

DIST_TO_DEG = 180/(3.1416*RW)   # scale factor for distance
ORIENT_TO_DEG = RB/RW           # scale factor for rotation

LEFT_MOTOR = Motor('A')
RIGHT_MOTOR = Motor('B')
POWER_LIMIT = 500
SPEED_LIMIT = 720

ROBOT_LEN = 15 # cm
MAP_SIZE = 120 # cm
NB_S = (int) (MAP_SIZE/ROBOT_LEN)/2 # number of back and forth s motions to cover the entire board
FWD_SPEED = 300
TRN_SPEED = 380

# bang bang controller constants
DEADBAND = 10 # degrees
DELTA_SPEED = 50 # dps

# sensors
GYRO = EV3GyroSensor(port=1, mode="abs")
US_SENSOR = EV3UltrasonicSensor(2)
wait_ready_sensors()


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


def move_fwd_until_wall(angle):
    try:
        LEFT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        RIGHT_MOTOR.set_limits(POWER_LIMIT, FWD_SPEED)
        while (US_SENSOR.get_value() > 3): # put value small enough so that if it's following the wall it doesn't matter
            # bang bang controller
            error = GYRO.get_abs_measure() - angle
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
        stop()
    except IOError as error:
        print(error)

        
def rotate(angle):
    """
    In-place rotation for the given angle

    angle > 0: rotate right

    angle < 0: rotate left
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



def rotate_at_wall(dir: str):
    """
    Rotates the robot in the given direction and positions itself in the next row to sweep

    dir = right : right rotate (go from -180 to 0 deg on gyro)

    dir = -1 : left rotate (go from 0 to -180 deg on gyro)
    """
    try:
        # go to -90 deg on gyro
        if (dir == "right"): 
            rotate(-90 + GYRO.get_abs_measure(), TRN_SPEED)
        else:
            rotate(-90 - GYRO.get_abs_measure() , TRN_SPEED)

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
            rotate( - GYRO.get_abs_measure(), TRN_SPEED)
        else:
            # go to -180 deg on gyro
            rotate(-180 - GYRO.get_abs_measure() , TRN_SPEED)
    except IOError as error:
        print(error)


def do_s_shape():
    # going in initial dir
    time.sleep(0.15)
    move_fwd_until_wall(0)
    time.sleep(0.15)
    rotate_at_wall(-1) # want to go to -180 angle
    # going in opposite dir
    time.sleep(0.15)
    move_fwd_until_wall(180)
    time.sleep(0.15)
    rotate_at_wall(+1) # want to go to 0 angle


def stop():
    time.sleep(0.15)
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_power(0)
    time.sleep(0.15)

try: 
    print("Navigation program started")
    init_motors()
    for i in range(NB_S):
        do_s_shape()
    # get back to start position
    rotate(90) # or -270
    move_fwd_until_wall()
    print("Finished sweep of the map")
    print("Navigation program ended")
except KeyboardInterrupt:
    print("Navigation program terminated")
finally:
    stop()
    reset_brick()
    print("Navigation stopped")