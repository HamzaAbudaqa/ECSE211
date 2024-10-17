
from utils.brick import TouchSensor, Motor
import time

EMERG_SENSOR = TouchSensor(3)
STARTSTOP = TouchSensor (1)
DRUM_MOTOR = Motor('B')  # Motor for the drumming mechanism# Button sensor for triggering drumming
DRUM_DELAY = 0.15  # sec


def drumRotate() :
    DRUM_MOTOR.set_limits(power=70)  # Limit power to avoid damage
    time.sleep(.5)
    DRUM_MOTOR.set_position(60)

    time.sleep(DRUM_DELAY)
    DRUM_MOTOR.set_position(0)
    time.sleep(DRUM_DELAY)