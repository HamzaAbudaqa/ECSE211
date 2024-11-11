from colorSensorUtils import getAveragedValues, returnClosestValue

FREQ = 2 #Hz
def color_freq_test():
    while(1):
        print(returnClosestValue(getAveragedValues(FREQ)))

if __name__ == "__main__":
    color_freq_test()