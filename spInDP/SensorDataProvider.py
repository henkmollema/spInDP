import smbus
import math

class SensorDataProvider(object):
		"""Provides data from sensors"""

		# Power management registers
		power_mgmt_1 = 0x6b
		power_mgmt_2 = 0x6c

		bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
		address = 0x68       # This is the address value read via the i2cdetect command

		def __init__(self):
			# Now wake the 6050 up as it starts in sleep mode
			self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)

		def getGyro(self):
				gyro_xout = self.read_word_2c(0x43)
				gyro_yout = self.read_word_2c(0x45)
				gyro_zout = self.read_word_2c(0x47)
				return (gyro_xout, gyro_yout, gyro_zout)

		def getAccelerometer(self):
				accel_xout = self.read_word_2c(0x3b)
				accel_yout = self.read_word_2c(0x3d)
				accel_zout = self.read_word_2c(0x3f)
				return (accel_xout, accel_yout, accel_zout)

		def read_byte(self, adr):
				return self.bus.read_byte_data(self.address, adr)

		def read_word(self, adr):
				high = self.bus.read_byte_data(self.address, adr)
				low = self.bus.read_byte_data(self.address, adr + 1)
				val = (high << 8) + low
				return val

		def read_word_2c(self, adr):
				val = self.read_word(adr)
				if (val >= 0x8000):
						return -((65535 - val) + 1)
				else:
						return val
						
		'''
		def dist(self, a,b):
			return math.sqrt((a*a)+(b*b))

		def get_y_rotation(self, x,y,z):
			radians = math.atan2(x, dist(y,z))
			return -math.degrees(radians)

		def get_x_rotation(self,x,y,z):
			radians = math.atan2(y, dist(x,z))
			return math.degrees(radians)

		'''
	