from utils.brick import Motor, configure_ports, reset_brick
from time import sleep


CLAW_MOTOR = Motor('A')
LIFT_MOTOR = Motor('B')
GRAB_POSITION = 0
#RELEASE_POSITION = -250
LIFT_UP_POSITION = 225
LIFT_DOWN_POSITION = 0
DUMP_PUSH_POSITION = 45

POWER_LIMIT = 50
SPEED_LIMIT = 250
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

        CLAW_MOTOR.set_position_relative(GRAB_POSITION)
        CLAW_MOTOR.set_power(POWER_LIMIT)
        sleep(1)
        
        print ("Lifting the block to storage unit")
        LIFT_MOTOR.set_position(LIFT_UP_POSITION)
        sleep(1)  

        print ("Releasing the block")
        CLAW_MOTOR.set_position(initial_claw_position)
        sleep(1)

        print ("Returning claw to initial position")
        LIFT_MOTOR.set_position(initial_lift_position)
        sleep(1)
    except IOError as error:
        print(f"Error: {error}")

def dump_storage():
    ''' function to dump blocks inside storage unit into the trash'''
    try:
        LIFT_MOTOR.reset_encoder()
        CLAW_MOTOR.reset_encoder()
        initial_claw_position = CLAW_MOTOR.get_position()
        initial_lift_position = LIFT_MOTOR.get_position()
        print(initial_lift_position, initial_claw_position)
        CLAW_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
        LIFT_MOTOR.set_limits(LIFT_POWER_LIMIT, LIFT_SPEED_LIMIT)

        print ("Starting the dumping operation")

        LIFT_MOTOR.set_position(LIFT_UP_POSITION)
        sleep(2)


        print("Retracting the arm now")
        LIFT_MOTOR.set_position(LIFT_DOWN_POSITION)
        sleep(2)

        print ("Mission accomplished")
    except IOError as error:
        print (f"Error during dumping operation: {error}")


dump_storage()
reset_brick()

