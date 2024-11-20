
from utils.brick import Motor, configure_ports, reset_brick
from time import sleep
from navigation2 import *

CLAW_MOTOR = Motor('B')
LIFT_MOTOR = Motor('C')
GRAB_POSITION = 300
HIT_POSITION = 20
LIFT_UP_POSITION = -240
HITTING_POSITION = -210
LIFT_HALF_UP_POSITION = -50
LIFT_DOWN_POSITION = 0
DUMP_PUSH_POSITION = 45

POWER_LIMIT = 50
SPEED_LIMIT = 250
HIGH_POWER_LIMIT = 100
HIGH_SPEED_LIMIT = 400
LIFT_POWER_LIMIT = 70
LIFT_SPEED_LIMIT = 200
DUMP_WAIT_TIME = 3

def grab_and_release():
    ''' Function to grab a block lift it & release it into storage unit '''
    
    try:
        LIFT_MOTOR.reset_encoder()
        CLAW_MOTOR.reset_encoder()
        initial_claw_position = CLAW_MOTOR.get_position()
        initial_lift_position = LIFT_MOTOR.get_position()
        print(initial_lift_position, initial_claw_position)

        CLAW_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        LIFT_MOTOR.set_limits(LIFT_POWER_LIMIT, LIFT_SPEED_LIMIT)


        print("Grabbing the block now.")
        CLAW_MOTOR.set_position(initial_claw_position)
        sleep(1)
        
        print ("Lifting the block to storage unit")
        LIFT_MOTOR.set_position(LIFT_UP_POSITION)
        sleep(1)  

        print ("Releasing the block")
        CLAW_MOTOR.set_position(20)
        sleep(1)

        print ("Returning claw to initial position")
        LIFT_MOTOR.set_position(initial_lift_position)
        sleep(4)
        
        print ("Returning claw to normal mode")
        CLAW_MOTOR.set_position(initial_claw_position)

    except IOError as error:
        print(f"Error: {error}")


def dump_storage():
    ''' function to dump blocks inside storage unit into the trash'''
    try:

        LIFT_MOTOR.reset_encoder()
        CLAW_MOTOR.reset_encoder()
        initial_claw_position = CLAW_MOTOR.get_position()
        initial_lift_position = LIFT_MOTOR.get_position()

        CLAW_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        LIFT_MOTOR.set_limits(LIFT_POWER_LIMIT, LIFT_SPEED_LIMIT)

        print ("Starting the dumping operation")

        print("Lifting the arm slightly")
        LIFT_MOTOR.set_position(LIFT_HALF_UP_POSITION)
        sleep(1)

        print("Rotating claw to hitting position")
        CLAW_MOTOR.set_position_relative(HIT_POSITION)
        sleep(1)

        print("Hitting storage unit with momentum")
        LIFT_MOTOR.set_limits(HIGH_POWER_LIMIT, HIGH_SPEED_LIMIT)
        LIFT_MOTOR.set_position(HITTING_POSITION)
        sleep(1)

        print("Resetting to initial positions")
        CLAW_MOTOR.set_position(initial_claw_position)
        LIFT_MOTOR.set_position(initial_lift_position)
        sleep(1)
        
        print ("Mission accomplished")

    except IOError as error:
        print (f"Error during dumping operation: {error}")


def detect_and_grab(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor):
    move_bwd(11, LEFT_MOTOR, RIGHT_MOTOR)
    grab_and_release()



