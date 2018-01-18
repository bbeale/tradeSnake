import sys, getopt
import urllib2
import time

from botchart import BotChart
from botstrategy import BotStrategy
from botcandlestick import BotCandlestick


def main(args):

    # TODO: Factor transaction fees into buy/sell amounts
    # TODO: Get an idea of trend direction by storing and examining the last 3 (4?) ticks
    # TODO: Fix current MACD indicator or else get it from somewhere else (ta-lib?)
    # TODO: UNIT. FUCKING. TESTS.
    # TODO: Add bollinger bands and RSI indicators to trading strategy

    usage = """
    Usage:

        python bot.py [currency pair] [stop loss] [take profit]

        Stop loss may be zero, take profit may not.

        Valid currency pairs:
        
        BTC                 BTC_ETH
                            BTC_LTC
                            BTC_XRP
                            BTC_BCH
                            BTC_ZEC
                            BTC_DASH
                            BTC_XMR

        ETH                 ETH_REP
                            ETH_BCH
                            ETH_ZEC
        
        XMR (Monero)        XMR_LTC
                            XMR_ZEC
                            XMR_DASH
        
        Tether              USDT_BTC
                            USDT_ETH
                            USDT_XRP
                            USDT_BCH
                            USDT_LTC             
    """

    pairs = ["BTC_ETH", "BTC_LTC", "BTC_XRP", "BTC_BCH", "BTC_ZEC", "BTC_DASH",
             "BTC_XMR", "ETH_REP", "ETH_BCH", "ETH_ZEC", "XMR_LTC", "XMR_ZEC",
             "XMR_DASH", "USDT_BTC", "USDT_ETH", "USDT_XRP", "USDT_BCH", "USDT_LTC"]

    if len(args) != 3:
        print usage
        sys.exit(-1)
    if args[0] not in pairs:
        print usage
        sys.exit(-1)
    if args[2] <= 0:
        print "Take profit must be greater than zero"
        print usage
        sys.exit(-1)
    else:

        period          = 300
        now             = float(time.time())
        pair            = args[0]
        stopLossAmount  = float(args[1])
        takeProfit      = float(args[2])

    chart = BotChart("poloniex", pair, period, now, False)
    strategy = BotStrategy(chart.conn, pair, period, stopLossAmount, takeProfit, now)

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
            strategy.tick(developingCandlestick, balances)
            developingCandlestick = BotCandlestick(period, now)

        time.sleep(int(5))


if __name__ == "__main__":
    main(sys.argv[1:])
