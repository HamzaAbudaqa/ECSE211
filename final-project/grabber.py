from utils.brick import *
from time import sleep
# from navigation2 import move_bwd, move_fwd

RIGHT_MOTOR = Motor('A')
LEFT_MOTOR = Motor('D')
CLAW_MOTOR = Motor('B')
LIFT_MOTOR = Motor('C')


GRAB_POSITION = 300
HIT_POSITION = 20
LIFT_UP_POSITION = -180
HITTING_POSITION = -210
LIFT_HALF_UP_POSITION = -50
LIFT_DOWN_POSITION = 0
DUMP_PUSH_POSITION = 45

POWER_LIMIT = 50
SPEED_LIMIT = 250
HIGH_POWER_LIMIT = 80
HIGH_SPEED_LIMIT = 300
LIFT_POWER_LIMIT = 90
LIFT_SPEED_LIMIT = 150
DUMP_WAIT_TIME = 3



def grab_and_release(CLAW_MOTOR: Motor, LIFT_MOTOR: Motor):
    ''' Function to grab a block lift it & release it into storage unit '''

    try:

        initial_claw_position = CLAW_MOTOR.get_position()
        initial_lift_position = LIFT_MOTOR.get_position()
        print(initial_lift_position, initial_claw_position)

        CLAW_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        LIFT_MOTOR.set_limits(LIFT_POWER_LIMIT, LIFT_SPEED_LIMIT)

        print("Lowering the arm")
        LIFT_MOTOR.set_position_relative(-25)

        print("Opening claw")
        CLAW_MOTOR.set_position(-80)
        sleep(1)

        print("Lowering the arm")
        LIFT_MOTOR.set_position_relative(-250)
        sleep(2)

        move_fwd(0.1, LEFT_MOTOR, RIGHT_MOTOR)
        sleep(0.05)

        print("Closing claw")
        CLAW_MOTOR.set_position(25)
        sleep(1)

        print("lifting arm now")
        LIFT_MOTOR.set_position(-25)
        sleep(2)

        print("Releasing claw")
        CLAW_MOTOR.set_position(-40)
        sleep(2)

        print("Returning claw to initial position")
        LIFT_MOTOR.set_position(-25)

        print("Closing claw")
        CLAW_MOTOR.set_position(0)
        sleep(1)

    except IOError as error:
        print(f"Error: {error}")


def dump_storage(CLAW_MOTOR: Motor, LIFT_MOTOR: Motor):
    ''' function to dump blocks inside storage unit into the trash'''
    try:

        LIFT_MOTOR.reset_encoder()
        CLAW_MOTOR.reset_encoder()
        initial_claw_position = CLAW_MOTOR.get_position()
        initial_lift_position = LIFT_MOTOR.get_position()

        CLAW_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        LIFT_MOTOR.set_limits(LIFT_POWER_LIMIT, LIFT_SPEED_LIMIT)

        print("Starting the dumping operation")

        print("lowering the arm slightly")
        LIFT_MOTOR.set_position(-230)
        sleep(1)

        print("Rotating claw to hitting position")
        CLAW_MOTOR.set_position(-55)
        sleep(1)

        print("Hitting storage unit with momentum")
        LIFT_MOTOR.set_limits(HIGH_POWER_LIMIT, HIGH_SPEED_LIMIT)
        sleep(1)

        print("Resetting to initial positions")
        # CLAW_MOTOR.set_position(initial_claw_position)
        LIFT_MOTOR.set_position(initial_lift_position + 40)
        sleep(1)
        LIFT_MOTOR.set_position(initial_lift_position - 40)
        sleep(1)

        print("Mission accomplished")

    except IOError as error:
        print(f"Error during dumping operation: {error}")


def detect_and_grab(LEFT_MOTOR: Motor, RIGHT_MOTOR: Motor, CLAW_MOTOR: Motor, LIFT_MOTOR: Motor):
    move_bwd(0.14, LEFT_MOTOR, RIGHT_MOTOR)
    sleep(2)
    grab_and_release(CLAW_MOTOR, LIFT_MOTOR)


if __name__ == "__main__":
    try:
        LIFT_MOTOR.reset_encoder()
        CLAW_MOTOR.reset_encoder()
        RIGHT_MOTOR.reset_encoder()
        LEFT_MOTOR.reset_encoder()
        
#         detect_and_grab(RIGHT_MOTOR, LEFT_MOTOR, CLAW_MOTOR, LIFT_MOTOR)
        dump_storage(CLAW_MOTOR, LIFT_MOTOR)
    except BaseException as e:
        print(e)
    finally:
        reset_brick()



