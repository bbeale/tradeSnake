import sys

from src.botchart import BotChart
from src.botstrategy import BotStrategy


def main(args):

    usage = """
        Usage:

            python backtest.py [currency pair] [stop loss]

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
        print(usage)
        sys.exit(-1)
    if args[0] not in pairs:
        print(usage)
        sys.exit(-1)
    else:
        period          = 300
        startTime       = 1513296000
        endTime         = 1513490400

        pair            = args[0]
        stopLossAmount  = float(args[1])
        takeProfit      = float(args[2])

    chart = BotChart("poloniex", pair, period, True, now=endTime, earlier=startTime)
    strategy = BotStrategy(chart.conn, pair, period, stopLossAmount, takeProfit, True, startTime, endTime)

    for candlestick in chart.getPoints():
        amtToTrade = chart.getCurrentPrice()
        strategy.tick(candlestick, amtToTrade)


if __name__ == "__main__":
    main(sys.argv[1:])
