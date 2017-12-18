from poloniex import poloniex
from botlog import BotLog
from botindicators import BotIndicators
from bottrade import BotTrade
from datetime import datetime
import time

class BotStrategy(object):
	def __init__(self, pair, period, now, stopLoss):
		self.conn 			= poloniex('key goes here','Secret goes here')
		self.pair 			= pair
		self.period 		= period
		self.now 			= now
		self.stopLossAmount = stopLoss
		self.earlier 		= self.now - (86400 * 27)
		self.indicators 	= BotIndicators()
		self.output 		= BotLog()
		self.prices 		= []
		self.closes 		= [] # Needed for Momentum Indicator
		self.trades 		= []
		self.currentPrice 	= ""
		self.currentClose 	= ""
		self.numSimulTrades = 2  # trying 2 open trades
		self.macdPrices 	= []
		self.movingAvg 		= 0
		self.currentAvgVariance	= 0
		self.macd 			= 0
		self.signal 		= 0
		self.buy 			= False
		self.sell 			= False
		self.buyTrigger 	= float(-.2)
		self.sellTrigger 	= float(.1)
		self.targetProfitMargin = float(.5)  # default was .6
		self.margin 		= 0
		self.tradeprofit 	= 0
		self.profit 		= 0
		self.macds 			= []
		self.profitable 	= False

	def tick(self,candlestick):

		self.macdPrices 	= self.getHistoricPrices()
		self.movingAvg 		= self.indicators.movingAverage(self.prices,15)
		self.currentPrice 	= float(candlestick.current)
		self.prices.append(self.currentPrice)
 		self.macd 			= self.indicators.MACD(self.macdPrices)
		# print "len of prices=", len(self.macdPrices)
		self.macds.append(self.macd)
		self.signal 		= self.indicators.signal(self.macdPrices, 9)
		self.currentAvgVariance = self.percentDiff(self.currentPrice, self.movingAvg)
		self.output.log("Price: "+str(candlestick.current)+"\tMoving Average: "+str(self.movingAvg)+"\t Price/MA Variance: "+str(self.currentAvgVariance)+ "\tMACD: " +str(self.macd))

		self.evaluatePositions()
		self.updateOpenTrades()
		self.showPositions()

	def evaluatePositions(self):
		openTrades = []
		for trade in self.trades:
			if (trade.status == "OPEN"):
				openTrades.append(trade)

		# Debug
		# self.output.log("MA variance less than buy trigger: " +str(self.currentAvgVariance < self.buyTrigger)+ "\tMA greater than sell trigger: " +str(self.currentAvgVariance > self.sellTrigger))

		if (len(openTrades) < self.numSimulTrades):
			if (self.currentPrice < self.movingAvg) and (self.currentAvgVariance < self.buyTrigger) and (self.macd > 5):
 				self.trades.append(BotTrade(self.pair,self.currentPrice,stopLoss=self.stopLossAmount))

		for trade in openTrades:
			self.margin = self.percentDiff(self.currentPrice, trade.entryPrice)
			self.profitable = self.margin >= self.targetProfitMargin

			# debug -- Might want to put self.margin >= self.targetProfitMargin back if self.profitable doesn't work
			print "Entry/Current Variance:", self.margin, "Target:", self.targetProfitMargin, "Profitable?", self.profitable

			if ( self.margin >= self.targetProfitMargin):
				trade.close(self.currentPrice)

			else:
				# print "trade.diff (should be negative)=", trade.diff
				self.output.log("HODLing!")

			# print "old profit=", self.profit,
			self.profit += trade.diff
			
		self.output.log("Profit: " +str(self.profit))

	def updateOpenTrades(self):
		for trade in self.trades:
			if (trade.status == "OPEN"):
				trade.tick(self.currentPrice)

	def showPositions(self):
		for trade in self.trades:
			trade.showTrade()

	def percentDiff(self, new, old):
		if new != None and old != None:
			return float(new - old) / float(old) * 100
		else:
			return None

	def getHistoricPrices(self):
		prices = []
		# conn = poloniex('key goes here','Secret goes here')
		dayChart = self.conn.api_query("returnChartData",{"currencyPair":self.pair,"start":self.earlier,"end":self.now,"period":86400})
		for dc in range(len(dayChart)):
			prices.append(dayChart[dc][u'close'])
		return prices
