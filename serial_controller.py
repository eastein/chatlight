import sys
import time
import serial
import struct

def wrap(s) :
	msg = ':P' + s
	xord = ord(msg[0])
	for i in range(len(msg) - 1) :
		print 'xor'
		xord ^= ord(msg[i + 1])
	msg += chr(xord)

	print repr(msg)

	return msg

if __name__ == '__main__' :
	s = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)
	msg = struct.pack('!H', int(sys.argv[1]))
	s.write(wrap(msg))
