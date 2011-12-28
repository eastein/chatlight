import json
import zmq
import random
import analysis
import time

class Chatter(object) :
	def __init__(self) :
		self.categories = set()
		self.lines = 0

class Trender(object) :
	def __init__(self, zmq_url) :
		self.analyzer = analysis.Analyzer()
		self.events = list()
		if zmq_url is not None :
			c = zmq.Context(1)
			self.zmq_socket = c.socket(zmq.PUB)
			self.zmq_socket.bind(zmq_url)

	@classmethod
	def event_after(self, event, ts_thr) :
		ts, mask, line, cat = event
		return ts >= ts_thr

	def cleanup(self, sec) :
		wipe_before = time.time() - sec
		self.events = filter(lambda event: Trender.event_after(event, wipe_before), self.events)

	def log(self, mask, line) :
		ts = time.time()
		cat = self.analyzer.categorize(line)
		self.events.append((ts, mask, line, cat))


	def publish(self, obj) :
		if hasattr(self, 'zmq_socket') :
			self.zmq_socket.send(json.dumps(obj))

	def report(self, sec) :
		self.cleanup(sec)

		chatters = dict()
		for ts, mask, line, cat in self.events :
			chatters.setdefault(mask, Chatter())
			chatters[mask].lines += 1
			if cat is not None :
				chatters[mask].categories.add(cat)

		n_chatters = len(chatters)
		n_lps = float(len(self.events) / float(sec))

		max_cat = 0
		category = None
		catcnt = {}
		randomized_chatters = chatters.values()
		random.shuffle(randomized_chatters)
		for chatter in randomized_chatters :
			for cat in chatter.categories :
				catcnt.setdefault(cat, 0)
				catcnt[cat] += 1
				if catcnt[cat] == max_cat :
					if random.randint(0, 1) == 1 :
						category = cat
				elif catcnt[cat] > max_cat :
					max_cat = catcnt[cat]
					category = cat

		self.publish({'type':'chat_report', 'chatters':n_chatters, 'rate':n_lps, 'category':category})
		return n_chatters, n_lps, category
