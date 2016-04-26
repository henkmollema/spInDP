import time
from ax12 import Ax12

ax = Ax12()

print("Start moving AX12")

ax.moveSpeed(10, 512, 200)
time.sleep(0.3)
print("New pos: " + str(ax.readPosition(10)))
print("Temp: " + str(ax.readTemperature(10)))
