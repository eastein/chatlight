import wordlists
import re
import random

MATCH_CAT = re.compile('^L_(.*)$')

class Analyzer(object) :
	def __init__(self) :
		self.lookup = {}
		self.cats = {}

		for n in dir(wordlists) :
			m = MATCH_CAT.match(n)
			if m :
				cat, = m.groups(1)
				cat_words = getattr(wordlists, n)
				for word in cat_words :
					self.lookup[word] = cat
				self.cats[cat] = cat_words

	def categorize(self, line) :
		words = line.lower().split(' ')
		# in order to not bias towards the beginning of the sentence in
		# tie situations, we should randomize the word analysis order.
		random.shuffle(words)
		catcounts = {}
		maxc = 0
		selected_cat = None
		for word in words :
			#print 'analyzing %s' % word
			for cat in self.cats :
				for catword in self.cats[cat] :
					if word.startswith(catword) :
						#print '%s matches category %s' % (word, cat)
						catcounts.setdefault(cat, 0)
						catcounts[cat] += 1
						if catcounts[cat] > maxc :
							#print 'new lvl for cat %s' % cat
							maxc = catcounts[cat]
							selected_cat = cat

		return selected_cat
