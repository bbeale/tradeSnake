import sys, getopt
import urllib2
import time

from botchart import BotChart
from botstrategy import BotStrategy
from botcandlestick import BotCandlestick


def main(argv):

    """ TODO: Parameterize these as cli args.
    Make startTime take a datetime input and then convert
    to timestamp and calculate endTime on the fly """

    period = 300
    pair = "BTC_ETH"
    now = float(time.time())
    backTest = False
    startTime = 1513296000
    endTime = 1513490400
    stopLossAmount = 0  # 0.005

    try:
        opts, args = getopt.getopt(argv, "hp:c:n:s:e:", ["period=", "currency=", "points="])
    except getopt.GetoptError:
        print 'trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>'
            sys.exit()
        elif opt in ("-p", "--period"):
            if int(arg) in [300, 900, 1800, 7200, 14400, 86400]:
                period = arg
            else:
                print 'Poloniex requires periods in 300,900,1800,7200,14400, or 86400 second increments'
                sys.exit(2)
        elif opt in ("-c", "--currency"):
            pair = arg
        elif opt in ("-n", "--points"):
            lengthOfMA = int(arg)
        elif opt in "-s":
            startTime = arg
        elif opt in "-e":
            endTime = arg

    if backTest:
        chart = BotChart("poloniex", pair, period, now=endTime, earlier=startTime)
        strategy = BotStrategy(chart.conn, pair, period, stopLossAmount, backTest, now)

        for candlestick in chart.getPoints():
            print type(candlestick.current)
            strategy.tick(candlestick, chart.getBalances(pair))

    else:
        chart = BotChart("poloniex", pair, period, now, False)
        strategy = BotStrategy(chart.conn, pair, period, stopLossAmount, backTest, now)

    candlesticks = []
    developingCandlestick = BotCandlestick(period, now)

    while True:
        try:
            developingCandlestick.tick(chart.getCurrentPrice(),
                                       chart.getLowestAsk(),
                                       chart.getHighestBid())
        except urllib2.URLError:
            time.sleep(int(5))
            developingCandlestick.tick(chart.getCurrentPrice(),
                                       chart.getLowestAsk(),
                                       chart.getHighestBid())

        if developingCandlestick.isClosed():
            candlesticks.append(developingCandlestick)
            balances = chart.getBalances(pair)
            print "BTC: ", balances[0], "Other: ", balances[1]
            strategy.tick(developingCandlestick, balances)
            developingCandlestick = BotCandlestick(period, now)

        time.sleep(int(5))


if __name__ == "__main__":
    main(sys.argv[1:])
