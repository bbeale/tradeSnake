from poloniex import poloniex
from botlog import BotLog

class BotTrade(object):
	def __init__(self,pair,currentPrice,stopLoss):
		self.output 	= BotLog()
		self.status 	= "OPEN"
		self.entryPrice = currentPrice
		self.exitPrice 	= ""
		self.output.log("Trade opened")
		self.stopLossNumber = stopLoss
		if (stopLoss) and (stopLoss > 0):
			self.stopLoss = currentPrice - self.stopLossNumber
		else:
			self.stopLoss = stopLoss
		self.diff = 0
		
		try:
			self.conn = poloniex(
				'43MX0MSE-MZ3ZU1MP-PFYZXQYO-JA6ZB105','02e0dd3dadf622debd4d2ce8d0d5c300d06cb145766aacbed0e9ea1a7658ae1aab4f0dbfb31d7b3a5fa60680f263e56cdeec15b670d3b40651efa2b0c86d8135')
			self.orderNumber = self.conn.buy(pair, currentPrice, 1)
		except:
			self.conn = None
	
	def close(self,currentPrice):
		self.status 	= "CLOSED"
		self.exitPrice 	= currentPrice
		self.output.log("Trade closed")
		self.diff 		= self.exitPrice - self.entryPrice

	def tick(self, currentPrice):
		if ( self.stopLoss > 0):

			print self.stopLoss, "Greater than zero?", (self.stopLoss > 0)

			print "current=", currentPrice, "stop loss=", self.stopLoss, "closing?", (currentPrice < self.stopLoss)

			if self.stopLoss == 0:
				return

			if ( currentPrice > self.stopLoss):
				self.stopLoss = currentPrice - self.stopLossNumber
				print "new stoploss=", self.stopLoss

			if ( currentPrice < self.stopLoss):
				self.close(currentPrice)

	def showTrade(self):
		tradeStatus = "Entry Price: "+str(self.entryPrice)+"\tStatus: "+str(self.status)+" Exit Price: "+str(self.exitPrice)

		if (self.status == "CLOSED"):
			tradeStatus = tradeStatus + " Profit: "
			if (self.exitPrice > self.entryPrice):
				tradeStatus = tradeStatus + "\033[92m"
			else:
				tradeStatus = tradeStatus + "\033[91m"

			tradeStatus = tradeStatus+str(self.exitPrice - self.entryPrice)+"\033[0m"

		self.output.log(tradeStatus)

	def getMargin(self):
		return self.margin
