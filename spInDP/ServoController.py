import time
from spInDP.pyax12.connection import Connection
import RPi.GPIO as GPIO
import math

class ServoController(object):
    """Provides interaction with the physical servos."""

    def __init__(self):
        self.connection = Connection(port="/dev/ttyAMA0", baudrate=1000000, timeout=0.1)

    def move(self, servo, angle, speed=200):        
        print("servo move " + str(servo) + ": " + str(angle))
        self.connection.goto(servo, angle, speed=None, degrees=True)
        time.sleep(abs(angle) * 0.0033)

    def getTemp(self, servo):
        return self.connection.get_present_temperature(servo)