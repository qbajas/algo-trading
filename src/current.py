from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects

# Import the backtrader platform
import backtrader as bt
import locale


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.setsizer(bt.sizers.AllInSizer())

        self.positioncount = 0
        self.rsi = []
        for i in range(len(self.datas)):
            self.rsi.append(bt.indicators.RSI_Safe(self.datas[i].close, period=2))

        self.minRsiElement = 0

    def next(self):
        self.previousMinRsiElement = self.minRsiElement

        # --- START effective strategy ---

        # buy if any rsi below 90
        self.doBuy = False
        for i in range(0, len(self.datas)):
            if self.rsi[i] < 90:
                self.doBuy = True

        # buy stocks if any stock rsi below 10
        self.buyStocksOnly = False
        for i in range(5, len(self.datas)):
            if self.rsi[i] < 10:
                self.buyStocksOnly = True

        if self.buyStocksOnly:
            self.startRange = 5
            self.endRange = len(self.datas)
        else:
            self.startRange = 0
            self.endRange = len(self.datas)

        self.minRsiElement = self.startRange
        for i in range(self.startRange, self.endRange):
            if self.rsi[i] <= self.rsi[self.minRsiElement]:
                self.minRsiElement = i
        if self.previousMinRsiElement and self.previousMinRsiElement in range(self.startRange, self.endRange) and (self.rsi[self.previousMinRsiElement]) < 10:
            self.minRsiElement = self.previousMinRsiElement

        # --- END effective strategy ---

        # print only last days
        if self.datas[0].datetime.date(0) < datetime.date.today() - datetime.timedelta(days=7):
            return

        self.log("")
        for i in range(len(self.datas)):
            self.log(self.get_ticker_name(self.datas[i]) +
                     " rsi: " + str(self.rsi[i][0]) +
                     " (price: " + str(self.datas[i][0]) + ")")

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")

        self.log("Selected stock: %s (rsi %d)" %
                 (self.get_ticker_name(self.datas[self.minRsiElement]),
                  self.rsi[self.minRsiElement][0]))

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")

        if self.previousMinRsiElement != self.minRsiElement and self.doBuy:
            self.log("+ BUY %s limit %s " %
                     (self.get_ticker_name(self.datas[self.minRsiElement]),
                      self.datas[self.minRsiElement][0] * 1.02))

        if self.previousMinRsiElement != self.minRsiElement or not self.doBuy:
            self.log("- SELL %s limit %s" %
                     (self.get_ticker_name(self.datas[self.previousMinRsiElement]),
                      self.datas[self.previousMinRsiElement][0] * 0.98))

    def get_ticker_name(self, data):
        return data.params.dataname.split("/")[-1].split(".")[0]


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

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
            fromdate=datetime.date.today() - datetime.timedelta(days=100))
        # Do not pass values before this date
        # todate=datetime.datetime(2015, 12, 31))

        data.start()

        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

        datas.append(data)

    # Set our desired cash start
    cashstart = 100000.0
    cerebro.broker.setcash(cashstart)

    # Run over everything
    run = cerebro.run()

    # cerebro.plot()
    locale.setlocale(locale.LC_ALL, 'en_US')
