from poloniex import poloniex
import urllib, json
import pprint, time
from botcandlestick import BotCandlestick

class BotChart(object):
	def __init__(self, exchange, pair, period, backtest=True, now=None, earlier=None):

		self.pair = pair
		self.period = period
		self.now = now
		if ( earlier is None):
			self.earlier = self.now - (86400 * 27)
		else:
			self.earlier = earlier
			print "earlier= ", self.earlier
		self.historicPrices = []

		# for testing in the backtest conditional below:
		# self.startTime = 1491048000
		# self.endTime = 1491591200

		self.data = []

		if (exchange == "poloniex"):
			self.conn = poloniex('43MX0MSE-MZ3ZU1MP-PFYZXQYO-JA6ZB105','02e0dd3dadf622debd4d2ce8d0d5c300d06cb145766aacbed0e9ea1a7658ae1aab4f0dbfb31d7b3a5fa60680f263e56cdeec15b670d3b40651efa2b0c86d8135')

			if backtest:	
				poloData = self.conn.api_query("returnChartData",{"currencyPair":self.pair,"start":self.earlier,"end":self.now,"period":self.period})
				for datum in poloData:
					if (datum['open'] and datum['close'] and datum['high'] and datum['low']):
						self.data.append(BotCandlestick(self.period,datum['open'],datum['close'],datum['high'],datum['low'],datum['weightedAverage']))

		if (exchange == "bittrex"):
			if backtest:
				url = "https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName="+self.pair+"&tickInterval="+self.period+"&_="+str(self.earlier)
				response = urllib.urlopen(url)
				rawdata = json.loads(response.read())

				self.data = rawdata["result"]

	def getPoints(self):
		return self.data

	def getCurrentPrice(self):
		currentValues = self.conn.api_query("returnTicker")
		lastPairPrice = {}
		lastPairPrice = currentValues[self.pair]["last"]
		return lastPairPrice
	
	def getBalances(self):
		return self.conn.returnBalances()