from poloniex import poloniex
from botlog import BotLog
from botindicators import BotIndicators
from pprint import PrettyPrinter
import time, os, sys, urllib, urllib2, json, numpy
# from talib import abstract

# TODO: Make hodler.py use BotLog()
# TODO: Add email notifications for trade failure and success

conn = poloniex(os.environ["POLONIEX_KEY"], os.environ["POLONIEX_SECRET"])
pp = PrettyPrinter(indent=2)
usage = \
    """USAGE:
1) Open a trade on the Poloniex exchange (https://poloniex.com/)
2) Run:
    python hodler.py [Currency Pair] [Take Profit]
3) Currency pair and take profit required"""

pairs = ["BTC_ETH", "BTC_LTC", "BTC_XRP", "BTC_BCH", "BTC_ZEC", "BTC_DASH",
         "BTC_XMR", "ETH_REP", "ETH_BCH", "ETH_ZEC", "XMR_LTC", "XMR_ZEC",
         "XMR_DASH", "USDT_BTC", "USDT_ETH", "USDT_XRP", "USDT_BCH", "USDT_LTC"]


def main(args):

    if len(args) != 2:
        print usage
        sys.exit(-1)
    if args[0] not in pairs:
        print usage
        sys.exit(-1)
    if args[1] <= 0:
        print usage
        sys.exit(-1)

    pair            = args[0]
    takeProfit      = args[1]
    balances        = getBalances(pair)

    if balances[0] == 0 and balances[1] == 0:
        print "Insufficient funds for trading"
        sys.exit(-1)

    now             = float(time.time())
    earlier         = str(now - (86400 * 30))
    historicPrices  = getHistoricPrices(pair, earlier, now)
    holding         = True
    indicators      = BotIndicators()
    macd            = indicators.MACD(historicPrices)

    while holding:

        currentPrice = float(conn.api_query("returnTicker")[pair]["last"])
        highestBid = float(conn.api_query("returnTicker")[pair]["highestBid"])
        print "Balance:\t\t{}\t\tCurrent:\t\t{}\t\tHighest Bid:\t\t{}".format(str(balances[1]),
                                                                           str(currentPrice),
                                                                           str(highestBid))

        if highestBid >= takeProfit:  # or highestBid <= stopLoss:
            try:
                conn.sell(pair,
                          highestBid,
                          balances[1])
                holding = False
            except:
                print "Trade execution failed"
                sys.exit(-1)

        time.sleep(5)


def getBalances(pair):
    coins = pair.split("_")
    balances = [conn.returnBalances()[c] for c in coins]
    return balances


def getHistoricPrices(pair, start, end):
    dayChart = conn.api_query("returnChartData",
                              {"currencyPair": pair,
                               "start": start,
                               "end": end,
                               "period": 300})

    prices = [dayChart[dc]["weightedAverage"] for dc in range(len(dayChart))]
    return prices[::-1]


if __name__ == "__main__":
    print "TRADE AT YOUR OWN RISK!!!\n\nI claim absolutely no responsibility for any money you lose\n"
    main(sys.argv[1:])
