import time
from ax12 import Ax12

ax = Ax12()

print("Start moving AX12")

ax.moveSpeed(1, 256, 200)
time.sleep(0.5)
print("New pos: " + str(ax.readPosition(1)))
print("Temp: " + str(ax.readTemperature(1)))
