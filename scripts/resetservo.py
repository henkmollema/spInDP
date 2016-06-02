from spInDP.ax12 import Ax12
import time

ax12 = Ax12()
ax12.move(2, 512)
time.sleep(2)
ax12.move(2, 0)
#for x in range(1, 19):
#  ax.move(x, 0)