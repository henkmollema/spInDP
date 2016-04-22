from ax12 import Ax12
import time

servo = Ax12()

print("start move ")

#print("reading pos")
##temp = servo.readPosition(15)
#print("pos: " + str(temp))

speed = 200
sleepT = 0.1

for x in range(0, 3):
  servo.moveSpeed(16, 512, speed)
  time.sleep(sleepT)
  servo.moveSpeed(17, 512, speed)
  time.sleep(sleepT)
  servo.moveSpeed(18, 512, speed)

  servo.moveSpeed(16, 256, speed)
  time.sleep(sleepT)
  servo.moveSpeed(17, 256, speed)
  time.sleep(sleepT)
  servo.moveSpeed(18, 256, speed)

  servo.moveSpeed(16, 512, speed)
  time.sleep(sleepT)
  servo.moveSpeed(17, 512, speed)
  time.sleep(sleepT)
  servo.moveSpeed(18, 512, speed)

#print("reading temp")
##temp = servo.readPosition(15)
#print("temp: " + str(temp))