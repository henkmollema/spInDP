import time
from ax12 import Ax12

ax = Ax12()

print("Start moving AX12")

ax.moveSpeed(1, 0, 200)
time.sleep(2.0)
ax.moveSpeed(1, 512, 200)
time.sleep(2.0)
ax.moveSpeed(1, 0, 200)
time.sleep(2.0)
ax.moveSpeed(1, 1023, 200)
time.sleep(3.0)
ax.moveSpeed(1, 0, 200)
print("New pos: " + str(ax.readPosition(1)))
print("Temp: " + str(ax.readTemperature(1)))
print("Load: " + str(ax.readLoad(1)))
