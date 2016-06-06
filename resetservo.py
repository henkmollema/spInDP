from spInDP.ax12 import Ax12
import time

ax12 = Ax12()

# Poot 1
print ("Set servo 3")
ax12.setAngleLimit(3, 512, 1023) # Tibia

time.sleep(0.1)
print ("Set servo 2")
ax12.setAngleLimit(2, 0, 512) # Femur

# Poot 2
time.sleep(0.1)
print ("Set servo 5")
ax12.setAngleLimit(5, 512, 1023) # Tibia

time.sleep(0.1)
print ("Set servo 6")
ax12.setAngleLimit(6, 0, 512) # Femur

# Poot 3
time.sleep(0.1)
print ("Set servo 8")
ax12.setAngleLimit(8, 512, 1023) # Tibia

time.sleep(0.1)
print ("Set servo 9")
ax12.setAngleLimit(9, 0, 512) # Femur

# Poot 4
time.sleep(0.1)
print ("Set servo 11")
ax12.setAngleLimit(11, 512, 1023) # Tibia

time.sleep(0.1)
print ("Set servo 12")
ax12.setAngleLimit(12, 0, 512) # Femur

 # Poot 5
time.sleep(0.1)
print ("Set servo 15")
ax12.setAngleLimit(15, 512, 1023) # Tibia

time.sleep(0.1)
print ("Set servo 14")
ax12.setAngleLimit(14, 0, 512) # Femur

# Poot 6
time.sleep(0.1)
print ("Set servo 18")
ax12.setAngleLimit(18, 512, 1023) # Tibia

time.sleep(0.1)
print ("Set servo 17")
ax12.setAngleLimit(17, 0, 512) # Femur
