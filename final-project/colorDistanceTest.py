from colorSensorUtils import getAveragedValues, returnClosestValue



def color_distance_test():
    for i in range(10):
        r,g,b = getAveragedValues(10)
        print(returnClosestValue())
        
        
if __name__ == "__main__":
    color_distance_test()