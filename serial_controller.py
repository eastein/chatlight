import sys
import time
import serial
import struct

class ChatlightController(object) :
	def __init__(self, s) :
		self.serial = s

	def wrap(self, s) :
		msg = ':P' + s
		xord = ord(msg[0])
		for i in range(len(msg) - 1) :
			xord ^= ord(msg[i + 1])
		msg += chr(xord)

		return msg

	def light_control_code(self, light, pwm_on, pwm_off, blink_on, blink_off) :
		r = chr(light);
		r += struct.pack('!H', pwm_on)
		r += struct.pack('!H', pwm_off)
		r += struct.pack('!H', blink_on)
		r += struct.pack('!H', blink_off)
		return r

	def set_parameters(self, light, pwm_on, pwm_off, blink_on, blink_off) :
		msg = self.light_control_code(light, pwm_on, pwm_off, blink_on, blink_off)
		self.serial.write(self.wrap(msg))

if __name__ == '__main__' :
	device = '/dev/ttyUSB0'
	try :
		device = sys.argv[6]
	except IndexError :
		pass
	s = serial.Serial(device, 115200, timeout=1)
	clc = ChatlightController(s)
	clc.set_parameters(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
