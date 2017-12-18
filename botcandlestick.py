import sys, getopt
import time

from botlog import BotLog
from botindicators import BotIndicators

class BotCandlestick(object):
	def __init__(self, period, now, open=None, close=None, high=None, low=None, priceAverage=None):
		self.current = None
		self.open = open
		self.close = close
		self.high = high
		self.low = low
		self.now = now
		self.period = period
		self.output = BotLog()
		self.priceAverage = priceAverage
		self.diff = None
		self.diffp = None

	def tick(self,price):
		self.current = float(price)
		if (self.open is None):
			self.open = self.current

		if ( (self.high is None) or (self.current > self.high) ):
			self.high = self.current

		if ( (self.low is None) or (self.current < self.low) ):
			self.low = self.current

		if ( time.time() >= ( self.now + self.period) ):
			self.close = self.current
			self.priceAverage = ( self.high + self.low + self.close ) / float(3)

		self.output.log("Open: "+str(self.open)+"\tClose: "+str(self.close)+"\tHigh: "+str(self.high)+"\tLow: "+str(self.low)+"\tCurrent: "+str(self.current))

	def isClosed(self):
		if (self.close is not None):
			return True
		else:
			return False
