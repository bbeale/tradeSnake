from poloniex import poloniex
import urllib, json, os
from botcandlestick import BotCandlestick


class BotChart(object):
    def __init__(self, exchange, pair, period, backtest, now, earlier=None):

        self.pair = pair
        self.period = period
        self.now = now
        self.p_key = os.environ["POLONIEX_KEY"]
        self.p_secret = os.environ["POLONIEX_SECRET"]

        if earlier is None:
            self.earlier = self.now - (86400 * 27)
        else:
            self.earlier = earlier

        self.historicPrices = []
        self.data = []

        if exchange == "poloniex":
            self.conn = poloniex(self.p_key, self.p_secret)

            if backtest:
                poloData = self.conn.api_query("returnChartData",
                                               {"currencyPair": self.pair,
                                                "start": self.earlier,
                                                "end": self.now,
                                                "period": self.period})

                for datum in poloData:
                    if datum['open'] and datum['close'] and datum['high'] and datum['low']:
                        self.data.append(
                            BotCandlestick(self.period,
                                           datum['date'], datum['open'], datum['close'], datum['high'], datum['low'], backtest))

        if (exchange == "bittrex"):
            if backtest:
                url = "https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=" + self.pair + "&tickInterval=" + self.period + "&_=" + str(
                    self.earlier)
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

    def getLowestAsk(self):

        currentValues = self.conn.api_query("returnTicker")
        lastLowestAsk = {}
        lastLowestAsk = currentValues[self.pair]["lowestAsk"]
        return lastLowestAsk

    def getHighestBid(self):

        currentValues = self.conn.api_query("returnTicker")
        lastHighestBid = {}
        lastHighestBid = currentValues[self.pair]["highestBid"]
        return lastHighestBid

    def getBalances(self, pair):
        coins = pair.split("_")
        balances = []
        for c in coins:
            bal = self.conn.returnBalances()[c]
            balances.append(bal)
        return balances

    def returnTrades(self):
        return self.conn.returnOpenOrders(self.pair)
