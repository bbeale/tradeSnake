import sys, getopt

from botchart import BotChart
from botstrategy import BotStrategy

def main(argv):
	chart = BotChart("poloniex","USDT_ETH",300)
	prices = chart.getMACDPrices()

	strategy = BotStrategy(prices)
	

	for candlestick in chart.getPoints():
		# strategy.tick(candlestick)
		candlestick.tick(chart.getCurrentPrice())

if __name__ == "__main__":
	main(sys.argv[1:])