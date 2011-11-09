import sys
import time
import json
import zmq
import serial
import serial_controller
import wordlists

if __name__ == '__main__' :
	zmq_url = sys.argv[1]
	device = '/dev/ttyUSB0'
	try :
		device = sys.argv[2]
	except IndexError :
		pass

	c = zmq.Context(1)
	s = c.socket(zmq.SUB)
	s.connect(zmq_url)
	s.setsockopt (zmq.SUBSCRIBE, "")

	ser = serial.Serial(device, 115200, timeout=1)
	ctl = serial_controller.ChatlightController(ser)

	for n in ctl.lightnames :
		ctl.off(getattr(ctl, n))

	ctl.set_main({})

	while True :
		r, w, x = zmq.core.poll.select([s], [], [], 0.1)
		if r :
			msg = s.recv()
			msg = json.loads(msg)
	
			print msg

			# TODO missing
			if msg['type'] == 'chat_report' :
				n, r, c = msg['chatters'], msg['rate'], msg['category']

				n = min(n, ctl.TOPLIGHTS)
				for i in range(ctl.TOPLIGHTS) :
					if i < n :
						# fix dimming TODO
						ctl.set_parameters(getattr(ctl, 'LN_TOP%d' % i), 1, 7, 1, 0)
					else :
						ctl.off(getattr(ctl, 'LN_TOP%d' % i))
				print 'set up top lights'

				color = "white"

				if c in wordlists.COLORS :
					color = wordlists.COLORS[c]
				
				blink_on = 0

				# ratecap
				if r > 2.0 :
					r = 2.0

				if r > 1/120.0 :
					blink_on = int(1000 * 1/r * 35)

				print 'blink_on = %d' % blink_on

				if blink_on > 0 :
					ctl.set_main({color : (1, 4, blink_on, 800)})
				else :
					ctl.set_main(dict())
			elif msg['type'] == 'page' :
				# TODO make this actually cool to look at, this is silly
				# will there be a buzzer added maybe?

				ctl.set_main({"blue" : (1, 5, 500, 500), "yellow" : (1, 3, 500, 500)})
				print 'set paging settings.'
				time.sleep(20)
				if ctl.revert_main() :
					print 'reverted paging settings'
				else :
					print 'failed to revert paging settings.'
			else :
				print 'unhandled'
