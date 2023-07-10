from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects

# Import the backtrader platform
import backtrader as bt
import locale


# Create a Stratey
class CurrentStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)

        # print only last days
        if self.datas[0].datetime.date(0) >= datetime.date.today() - datetime.timedelta(days=7):
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.setsizer(bt.sizers.AllInSizer())

        self.positioncount = 0
        self.rsi = []
        for i in range(len(self.datas)):
            self.rsi.append(
                (10 * bt.indicators.RSI_Safe(self.datas[i].close, period=2) +
                 bt.indicators.RSI_Safe(self.datas[i].close, period=3)) / 11
            )

        self.minRsiElement = 5

    def next(self):
        self.previousMinRsiElement = self.minRsiElement

        # --- START effective strategy ---

        # buy if any rsi below 70
        self.doBuy = False
        for i in range(0, len(self.datas)):
            if self.rsi[i] < 70:
                self.doBuy = True

        # buy stocks if any stock rsi below 15
        self.buyStocksOnly = False
        for i in range(5, len(self.datas)):
            if self.rsi[i] < 15:
                self.buyStocksOnly = True

        # compute the range
        if self.buyStocksOnly:
            self.startRange = 5
            self.endRange = len(self.datas)
        else:
            self.startRange = 0
            self.endRange = len(self.datas)

        # select the asset from the range
        self.minRsiElement = self.startRange
        for i in range(self.startRange, self.endRange):
            if self.rsi[i] <= self.rsi[self.minRsiElement]:
                self.minRsiElement = i

        # reduce number of trades
        if self.previousMinRsiElement in range(self.startRange, self.endRange):
            if self.rsi[self.previousMinRsiElement][-1] > self.rsi[self.previousMinRsiElement][0] + 1:
                self.minRsiElement = self.previousMinRsiElement

        # --- END effective strategy ---

        self.log("")
        for i in range(len(self.datas)):
            self.log(self.get_ticker_name(self.datas[i]).ljust(4) +
                     " rsi: " + format(self.rsi[i][0], ".2f").ljust(5) +
                     " (price: " + format(self.datas[i][0], ".2f") + ")")

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")

        self.log("Selected stock: %s (rsi %d)" %
                 (self.get_ticker_name(self.datas[self.minRsiElement]),
                  self.rsi[self.minRsiElement][0]))

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")

        if self.previousMinRsiElement != self.minRsiElement and self.doBuy:
            sizing = self.getsizing(self.datas[self.minRsiElement])
            price = self.datas[self.minRsiElement][0]
            self.log("+ BUY %d %s @ %s LIMIT ($%d)" % (
                sizing,
                self.get_ticker_name(self.datas[self.minRsiElement]),
                format(price * 1.017, ".2f"),
                sizing * price))
            # simulate buy at any price to avoid handling edge cases where the order was not executed:
            self.buy(data=self.datas[self.minRsiElement],
                     size=sizing,
                     exectype=bt.Order.Limit,
                     price=(price * 2))

        if self.previousMinRsiElement != self.minRsiElement or not self.doBuy:
            price = self.datas[self.previousMinRsiElement][0]
            self.log("- CLOSE %s %s MIDPRICE" % (
                self.get_ticker_name(self.datas[self.previousMinRsiElement]),
                format(price * 0.983, ".2f")))
            # simulate sell at any price to avoid handling edge cases where the order was not executed:
            self.close(data=self.datas[self.previousMinRsiElement],
                       exectype=bt.Order.Limit,
                       price=price * 0.5)

    def get_ticker_name(self, data):
        return data.params.dataname.split("/")[-1].split(".")[0]


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(CurrentStrategy)

    tickers = [

        # first five need to be bonds
        "SHY",
        "IEF",
        "TLT",
        "AGG",
        "LQD",

        # the rest need to be stocks
        "SPY",
        "SPMO",

        "EFA",
        "IMTM",

        "QQQ",
        "EEM",
        "IWM",
        "VNQ",
        "GLD",
    ]

    datas = []

    for ticker in tickers:
        # Create a Data Feed
        data = bt.feeds.YahooFinanceCSVData(
            dataname="../resources/tickers/" + ticker + ".csv",
            # Do not pass values before this date
            fromdate=datetime.datetime(2022, 11, 10))
        # Do not pass values before this date
        # todate=datetime.datetime(2015, 12, 31))

        data.start()

        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

        datas.append(data)

    # Set our desired cash start
    cashstart = 96000.0
    cerebro.broker.setcash(cashstart)
    cerebro.broker.setcommission(leverage=cashstart, commission=0.000035)  # 0.0035% of the operation value

    # Run over everything
    run = cerebro.run()

    # cerebro.plot()
    locale.setlocale(locale.LC_ALL, 'en_US')
