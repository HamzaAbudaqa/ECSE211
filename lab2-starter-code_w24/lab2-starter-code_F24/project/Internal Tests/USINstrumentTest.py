
from utils import sound
from utils.brick import TouchSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick
from time import sleep



print("Hello Hooman")
TOUCH_SENSOR = TouchSensor(1)
US_SENSOR = EV3UltrasonicSensor(2)
DELAY_SEC = 0.75

wait_ready_sensors(True)
print("Done waiting.")

def playInstrument() :
    try:
        while not TOUCH_SENSOR.is_pressed():
            pass
        print("Touch sensor pressed")
        sleep(1)
        print("Starting sensors")
        while not TOUCH_SENSOR.is_pressed():
            us_data = US_SENSOR.get_value()  # Float value in centimeters 0, capped to 255 cm
            print(f"Current distance{us_data}\n")
            if us_data > 10 :
                sound.Sound(duration=0.5, pitch = us_data*20, volume=100).play()
            else :
                continue
            sleep(DELAY_SEC)
    finally:
        print("Byebye hooman")
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()


if __name__ == "__main__":
    playInstrument()