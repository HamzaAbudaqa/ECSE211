import time
from utils.brick import MOtor

motor = Motor(1)

motor.reset_encoder() #whatever position it is at now is 0

while True :
    motor.set_position(90) #rotates 90
    time.sleep(1)
    motor.set_position(0)
    time.sleep(1)
