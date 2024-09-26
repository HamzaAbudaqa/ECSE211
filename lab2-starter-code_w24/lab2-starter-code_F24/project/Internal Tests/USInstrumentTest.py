
from utils import sound
from utils.brick import TouchSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick
from time import sleep



print("Hello Hooman")
TOUCH_SENSOR = TouchSensor(2)
US_SENSOR = EV3UltrasonicSensor(1)
DELAY_SEC = 0.6

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
            sensorSum = 0
            for i in range(20): #gets an average distance over 20 samples
                us_data = US_SENSOR.get_value()  # Float value in centimeters 0, capped to 255 cm
                sensorSum += us_data
                sleep(0.01)
            averageDistance = sensorSum/20
            print(f"Current distance{averageDistance}\n")
            if averageDistance < 10 : # plays a different note based on the distance
                sound.Sound(duration=0.5, pitch = "A4", volume=100).play()
            elif averageDistance < 12 :
                sound.Sound(duration=0.5, pitch = "B4", volume=100).play()
            elif averageDistance < 14 :
                sound.Sound(duration=0.5, pitch = "C4", volume=100).play()
            elif averageDistance < 16 :
                sound.Sound(duration=0.5, pitch = "D4", volume=100).play()
            elif averageDistance < 18 :
                sound.Sound(duration=0.5, pitch = "E4", volume=100).play()
            elif averageDistance < 20 :
                sound.Sound(duration=0.5, pitch = "F4", volume=100).play()
            elif averageDistance < 22 :
                sound.Sound(duration=0.5, pitch = "G4", volume=100).play()
            else : #if the distance is further than what is comfortable, then dont play a sound
                continue
            sleep(DELAY_SEC) #gives time to reposition
    finally:
        print("Byebye hooman")
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()


if __name__ == "__main__":
    playInstrument()
