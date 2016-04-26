import time
from pyax12.connection import Connection

class ServoController(object):
    """Provides interaction with the physical servos."""

    def __init__(self):
        self.connection = Connection("/dev/ttyAMA0", baudrate=1000000, timeout=0.5)

    def move(self, servo, angle, speed=200):        
        print("servo move " + str(servo) + ": " + str(angle))
        self.connection.goto(servo, angle, speed=speed, degrees=True)
        
        time.sleep(abs(angle) * 0.0033)

    def getTemp(self, servo):
        return self.connection.get_present_temperature(servo)
