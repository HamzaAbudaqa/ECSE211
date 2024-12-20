
from utils.brick import TouchSensor, Motor
import time

EMERG_SENSOR = TouchSensor(3)
STARTSTOP = TouchSensor (1)
DRUM_MOTOR = Motor('A')  # Motor for the drumming mechanism# Button sensor for triggering drumming
DRUM_DELAY = 0.15  # sec


def drumRotate() :
    """
    Args :
        none
    Returns :
        none
    Calling this function once will cause the motor to hit the base once and return to position
    """
    DRUM_MOTOR.set_limits(power=100)  # Limit power to avoid damage
    time.sleep(.5)
    DRUM_MOTOR.set_position(30)

    time.sleep(DRUM_DELAY)
    DRUM_MOTOR.set_position(-30)
    time.sleep(DRUM_DELAY)