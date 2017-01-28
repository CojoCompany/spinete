
import time


class Beepy:
    def __init__(self):

        self.old_mil = 0
        # define values and frequency in milisec to trigger the beep
        self.ranges = {0:0, 10: 1000, 15: 500, 20: 100}

    def beep(self, x):

        x=abs(x)

        thereshold = 0
        for key in sorted(self.ranges.keys()):
            if key > x:
                break
            thereshold = key


        if (self.ranges[thereshold]==0):
            return

        millis = int(round(time.time() * 1000))
        dif = millis - self.old_mil
        if (dif > self.ranges[thereshold]):
            print (chr(7))
            self.old_mil = millis