#!/usr/bin/env python
import sys
import time
import serial
import struct

class ChatlightController(object) :
	TOPLIGHTS = 6
	LN_TOP0 = 6
	LN_TOP1 = 3
	LN_TOP2 = 5
	LN_TOP3 = 4
	LN_TOP4 = 1
	LN_TOP5 = 2
	
	LN_MAINRED = 10
	LN_MAINBLUE = 8
	LN_MAINGREEN = 11
	LN_MAINYELLOW = 9
	LN_MAINWHITE = 7

	def __init__(self, serial_opener) :
		self.serial_opener = serial_opener
		self.serial = self.serial_opener()
		self.mains = list()
	
	@property
	def lightnames(self) :
		return filter(lambda s: s.startswith('LN_'), dir(self))

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

	def off(self, light) :
		self.set_parameters(light, 0, 1, 0, 1)

	def record_main(self, m) :
		self.mains.append(m)
		self.mains = self.mains[-2:]

	def revert_main(self) :
		c = None
		try :
			c = self.mains.pop()
			m = self.mains.pop()

			self.set_main(m)

			return True
		except IndexError :
			if c :
				self.mains.append(c)
			return False

	def set_main(self, d, record=True) :
		_d = dict()

		for k in d :
			_d['LN_MAIN%s' % k.upper()] = d[k]

		for n in filter(lambda s: s.startswith('LN_MAIN'), dir(self)) :
			if n not in _d :
				_d[n] = (0, 1, 0, 1)

		for k in _d :
			self.set_parameters(getattr(self, k), *(_d[k]))

		if record :
			self.record_main(d)

	def set_parameters(self, light, pwm_on, pwm_off, blink_on, blink_off) :
		msg = self.light_control_code(light, pwm_on, pwm_off, blink_on, blink_off)
		msg = self.wrap(msg)
		while True :
			try :
				if self.serial :
					self.serial.write(msg)
					break
			except OSError :
				self.serial = None
			except serial.serialutil.SerialException :
				self.serial = None
			
			if self.serial is None :
				try :
					self.serial = self.serial_opener()
				except serial.serialutil.SerialException :
					time.sleep(0.5)
if __name__ == '__main__' :
	device = '/dev/ttyUSB0'
	try :
		device = sys.argv[6]
	except IndexError :
		pass
	s = lambda: serial.Serial(device, 115200, timeout=1)
	clc = ChatlightController(s)
	clc.set_parameters(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
