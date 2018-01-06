from botlog import BotLog
from botindicators import BotIndicators
from bottrade import BotTrade
import time, sys


class BotStrategy(object):

    def __init__(self, conn, pair, period, stopLoss, backTest, startTime):

        self.conn           = conn
        self.pair           = pair
        self.period         = period
        self.stopLoss       = stopLoss
        self.backTest       = backTest
        self.startTime      = startTime
        self.currentTime    = self.startTime
        self.earlier        = None
        self.indicators     = BotIndicators()
        self.output         = BotLog()
        self.prices         = []
        self.macdPrices     = []
        self.closes         = []  # Needed for Momentum Indicator
        self.macds          = []
        self.trades         = []
        self.numSimulTrades = 1
        self.currentPrice   = 0
        self.currentClose   = 0
        self.lowestAsk      = 0
        self.highestBid     = 0
        self.movingAvg      = 0
        self.maDiff         = 0
        self.macd           = 0
        self.signal         = 0
        self.margin         = 0
        self.tradeProfit    = 0
        self.profit         = 0
        self.amountToTrade  = 0
        self.totalPurchase  = 0
        self.amountToSell   = 0
        self.buy            = False
        self.sell           = False
        self.profitable     = False
        self.buyTrigger     = float(-.2)
        self.sellTrigger    = float(.1)
        self.takeProfit     = float(.45)  # abstract this value

    def tick(self, candlestick, balances):

        self.currentTime    = float(time.time())
        self.earlier        = self.currentTime - (86400 * 30)
        self.macdPrices     = self.getHistoricPrices(self.earlier, self.currentTime)
        self.movingAvg      = self.indicators.movingAverage(self.prices, 15)
        self.currentPrice   = float(candlestick.current)
        self.lowestAsk      = float(candlestick.lowestAsk)
        self.highestBid     = float(candlestick.highestBid)

        self.prices.append(self.currentPrice)

        self.signal         = self.indicators.signal(self.macdPrices, 9)
        p                   = -(27 * 300)
        self.macd           = self.indicators.MACD(self.macdPrices[-(27 * 300):])

        self.macds.append(self.macd)

        print len(self.macdPrices)
        print len(self.macdPrices[-(27 * 300):])

        self.maDiff = self.percentDiff(self.lowestAsk,  # + (self.lowestAsk * .025), # <<== Fee calculation
                                       self.movingAvg)

        self.amountToTrade  = float(balances[0]) / self.currentPrice
        self.amountToSell   = balances[1]

        self.evaluatePositions()
        self.updateOpenTrades()
        self.showPositions()

        self.output.log("Price: " + str(candlestick.current) + "\tMoving Average: " + str(
            self.movingAvg) + "\t Price/MA Variance: " + str(self.maDiff) + "\tMACD: " + str(self.macd[0][2]))

    def evaluatePositions(self):

        # TODO: deprecate that garbage below and use the API to get open trades...
        # ...like we should have from the start...
        #
        # openTrades = []
        # for trade in self.trades:
        #     if trade.status == "OPEN":
        #         openTrades.append(trade)
        #
        # if len(openTrades) < self.numSimulTrades:
        #     if (self.lowestAsk < self.movingAvg) \
        #             and (self.maDiff < self.buyTrigger):
        #
        #         self.trades.append(BotTrade(self.conn,
        #                                     self.pair,
        #                                     self.currentPrice,
        #                                     self.amountToTrade,
        #                                     self.stopLoss))
        #
        # for trade in openTrades:

        # Trying the trades list a different way
        try:
            ot = self.conn.returnOpenOrders(self.pair)
            self.output.log("Orders:\t{}\t{}".format(str(ot), str(len(ot))))
        except:
            self.output.log("Can't connect to API")
            sys.exit(-1)

        while len(ot) < self.numSimulTrades:
            if (self.lowestAsk < self.movingAvg) \
                    and (self.maDiff < self.buyTrigger):
                self.trades.append(BotTrade(self.conn,
                                            self.pair,
                                            self.currentPrice,
                                            self.amountToTrade,
                                            self.stopLoss))

        for trade in ot:

            self.margin = self.percentDiff(self.highestBid,     # - (self.highestBid * .025), # <<== Fee calculation
                                           trade.entryPrice)

            self.profitable = self.margin >= self.takeProfit
            self.output.log("Current/Entry Variance:" + str(self.margin) + "\tTarget:" + str(
                self.takeProfit) + "\tProfitable? " + str(self.profitable))

            if self.margin >= self.takeProfit:
                trade.close(self.pair, self.highestBid, self.amountToSell)

            else:
                self.output.log("HODLing for {}".format(str(trade.elapsedTime)))

            self.profit += trade.diff

        self.output.log("Profit: " + str(self.profit))

    def updateOpenTrades(self):
        for trade in self.trades:
            if trade.status == "OPEN":
                trade.tick(self.currentPrice)

    def showPositions(self):
        for trade in self.trades:
            trade.showTrade()

    def percentDiff(self, new, old):
        if new is not None and old is not None:
            return float(new - old) / float(old) * 100
        else:
            return None

    def getHistoricPrices(self, start, end):
        prices = []
        dayChart = self.conn.api_query("returnChartData",
                                       {"currencyPair": self.pair,
                                        "start": start,
                                        "end": end,
                                        "period": 300})
        for dc in range(len(dayChart)):
            prices.append(dayChart[dc]["weightedAverage"])
        return prices[::-1]
