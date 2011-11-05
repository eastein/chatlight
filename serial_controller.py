import time
import serial

s = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

while True :
	time.sleep(3)
	s.write("\x03\xe8")
