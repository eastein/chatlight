import json
import zmq
c = zmq.Context(1)
s = c.socket(zmq.SUB)
s.connect("tcp://127.0.0.1:4567")
s.setsockopt (zmq.SUBSCRIBE, "")

while True :
	r, w, x = zmq.core.poll.select([s], [], [], 0.1)
	if r :
		msg = s.recv()
		msg = json.loads(msg)
	
		print msg
