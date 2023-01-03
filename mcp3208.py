import time
import spidev

class MCP3208(object):
	def __init__(self, spi_interface, cs):
		MSBFIRST = 1
		self.spi=spidev.SpiDev()
		self.spi.open(spi_interface, cs)
		self.spi.max_speed_hz=1000000
		
	def __del__(self):
		self.spi.close()

	def read(self, channel):
		if 7 <= channel <= 0:
			raise Exception('MCP3208 channel must be 0-7: ' + str(ch))

		adc = self.spi.xfer2([ 6 | (channel&4) >> 2, (channel&3) << 6, 0])
		data = ((adc[1]&15) << 8) + adc[2]
		return (data & 0x0FFF)  # ensure we are only sending 12b
		
	def readf(self, channel):
		data = self.read(channel)		
		return ((3.3/4096)*(data & 0x0FFF))  # return as voltage