import sys, getopt
import time
import pprint
import urllib2
import time

from botchart import BotChart
from botstrategy import BotStrategy
from botlog import BotLog
from botcandlestick import BotCandlestick

def main(argv):

	# print argv[1]
	
	""" Parameterize these as cli args
	Make startTime take a datetime 
	input and then convert to timestamp 
	and calculate endTime on the fly """
	print "num args=", len(argv)
	pair = "USDT_ETH"  # "USDT_ETH"  # Will primarily use eth
	period = 300
	now = float(time.time())
	earlier = now - (86400 * 27) # migt need to try a longer range
	startTime = False  # 1513296000
	endTime = False  # 1513490400
	stopLossAmount = 0  # 0.005

	try:
		opts, args = getopt.getopt(argv,"hp:c:n:s:e:",["period=","currency=","points="])
	except getopt.GetoptError:
		print 'trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>'
			sys.exit()
		elif opt in ("-p", "--period"):
			if (int(arg) in [300,900,1800,7200,14400,86400]):
				period = arg
			else:
				print 'Poloniex requires periods in 300,900,1800,7200,14400, or 86400 second increments'
				sys.exit(2)
		elif opt in ("-c", "--currency"):
			pair = arg
		elif opt in ("-n", "--points"):
			lengthOfMA = int(arg)
		elif opt in ("-s"):
			startTime = arg
		elif opt in ("-e"):
			endTime = arg

	if (startTime):
		chart = BotChart("poloniex",pair,period,now=endTime,earlier=startTime)
		strategy = BotStrategy(pair, period, now, stopLossAmount)

		for candlestick in chart.getPoints():
			strategy.tick(candlestick)

	else:
		chart = BotChart("poloniex",pair,period,False,now=now)
		strategy = BotStrategy(pair, period, now, stopLossAmount)

	candlesticks = []
	developingCandlestick = BotCandlestick(period, now)

	while True:
		try:
			developingCandlestick.tick(chart.getCurrentPrice())
			balances = chart.getBalances()
			print "bitcoin=", balances["BTC"]

		except urllib2.URLError:
			time.sleep(int(10))
			developingCandlestick.tick(chart.getCurrentPrice())
			balances = chart.getBalances()
			print "bitcoin=", balances["BTC"]
			
		if (developingCandlestick.isClosed()):
			candlesticks.append(developingCandlestick)
			strategy.tick(developingCandlestick)
			developingCandlestick = BotCandlestick(period, now=now)

		time.sleep(int(10))

if __name__ == "__main__":
	main(sys.argv[1:])




# highest 24 hour profit: 80.16915146