import sys
import time
import serial
import struct

def wrap(s) :
	msg = ':P' + s
	xord = ord(msg[0])
	for i in range(len(msg) - 1) :
		xord ^= ord(msg[i + 1])
	msg += chr(xord)

	print repr(msg)

	return msg

def light_control_code(light, pwm_on, pwm_off, blink_on, blink_off) :
	r = chr(light);
	r += struct.pack('!H', pwm_on)
	r += struct.pack('!H', pwm_off)
	r += struct.pack('!H', blink_on)
	r += struct.pack('!H', blink_off)
	return r

if __name__ == '__main__' :
	s = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)
	msg = light_control_code(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
	s.write(wrap(msg))
