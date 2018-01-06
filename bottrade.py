from botlog import BotLog
import time, sys


class BotTrade(object):

    def __init__(self, conn, pair, currentPrice, tradeAmount, stopLoss):

        self.conn = conn
        self.tradeOpenTime 	= float(time.time())
        self.tradeCloseTime = None  # don't know if I need this yet
        self.elapsedTime 	= None
        self.output 		= BotLog()
        self.status 		= "OPEN"
        self.fee_buy 		= 0.25
        self.fee_sell 		= 0.15
        self.entryPrice 	= currentPrice
        self.tradeAmount	= tradeAmount
        self.exitPrice 		= ""
        self.output.log("Trade opened at {}".format(str(self.tradeOpenTime)))  # convert this for display
        self.stopLossNumber = stopLoss
        self.pair 			= pair
        self.orderNumber    = 0

        if stopLoss > 0:
            self.stopLoss = currentPrice - self.stopLossNumber
        else:
            self.stopLoss = stopLoss
        self.diff = 0

        try:
            self.orderNumber = self.conn.buy(self.pair, currentPrice, tradeAmount)
            print "Order#:", self.orderNumber
        except:
            self.output.log("Can't connect to API")
            sys.exit(-1)

    def close(self, pair, currentPrice, sellAmount):
        try:
            self.conn.sell(pair, currentPrice, sellAmount)
        except:
            self.output.log("Can't connect to API")
            sys.exit(-1)

        self.status 	= "CLOSED"
        self.exitPrice 	= currentPrice
        self.output.log("Trade closed")
        self.diff 		= self.exitPrice - self.entryPrice

    def cancelOldTrade(self):
        try:
            self.conn.cancel(self.pair, self.orderNumber)
        except:
            self.output.log("Can't connect to API... Please login to exchange and cancel trade manually")
            sys.exit(-1)

        self.status 	= "CANCELED"
        self.output.log("Trade canceled")

    def tick(self, currentPrice):

        now = float(time.time())  # subtract start from now to get
        self.elapsedTime = now - self.tradeOpenTime
        self.output.log("Trade time elapsed:" +str(self.elapsedTime))

        # if self.elapsedTime > 90 and self.status == "OPEN":
        #     self.cancelOldTrade()
        #     return

        if self.stopLoss > 0:

            if self.stopLoss == 0:
                return

            if currentPrice > self.stopLoss:
                self.stopLoss = currentPrice - self.stopLossNumber

    def showTrade(self):
        tradeStatus = "Entry Price: "+str(self.entryPrice)+"\tStatus: "+str(self.status)+" Exit Price: "+str(self.exitPrice)

        if self.status == "CLOSED":
            tradeStatus = tradeStatus + " Profit: "
            if self.exitPrice > self.entryPrice:
                tradeStatus = tradeStatus + "\033[92m"
            else:
                tradeStatus = tradeStatus + "\033[91m"

            tradeStatus = tradeStatus+str(self.exitPrice - self.entryPrice)+"\033[0m"

        self.output.log(tradeStatus)

    def getMargin(self):
        return self.margin
