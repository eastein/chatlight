import analysis
import unittest

class SubjectTests(unittest.TestCase) :
	def setUp(self) :
		self.analyzer = analysis.Analyzer()

	def test_nosubject(self) :
		self.assertEqual(None, self.analyzer.categorize("I the and then. The. Yes."))

	def test_specific_subject(self) :
		self.assertEqual("COMPUTERS", self.analyzer.categorize("Use python. Problem solved."))

	def test_random_subject(self) :
		n_outdoors = 0
		n_computers = 0
		for i in xrange(10000) :
			cat = self.analyzer.categorize("Use python. Ski later.")
			if cat == "COMPUTERS" :
				n_computers += 1
			elif cat == "OUTDOORS" :
				n_outdoors += 1
			else :
				self.fail("did not expect category %s" % cat)

			if n_outdoors > 0 and n_computers > 0 :
				break

		self.assertTrue(n_outdoors > 0)
		self.assertTrue(n_computers > 0)
