from ax12 import Ax12
import time

ax = Ax12()

print("Start moving AX12")

ax.moveSpeed(10, 768, 1024)
time.sleep(1)
ax.moveSpeed(10, 0, 1024)
time.sleep(1)
ax.moveSpeed(10, 512, 1024)
time.sleep(1)
ax.moveSpeed(10, 900, 1024)
time.sleep(1)
#print("New pos: " + str(ax.readPosition(10)))
#print("Temp: " + str(ax.readTemperature(10)))

ax.moveSpeed(10, 0, 512)
#print("New pos: " + str(ax.readPosition(10)))

# ax.moveSpeed(10, 0, 300)
# time.sleep(1)
# print("New pos: " + str(ax.readPosition(10)))

# ax.moveSpeed(10, 512, 300)
# time.sleep(1)
# print("New pos: " + str(ax.readPosition(10)))

# ax.moveSpeed(10, 0, 300)
# time.sleep(1)

# print("New pos: " + str(ax.readPosition(10)))
print("New pos: " + str(ax.readPosition(10)))
print("Temp: " + str(ax.readTemperature(10)))
