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
        # print only last days
        if self.datas[0].datetime.date(0) < datetime.date.today() - datetime.timedelta(days=7):
            return

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
            self.minRsiElement = 5
            for i in range(5, len(self.datas)):
                if self.rsi[i] <= self.rsi[self.minRsiElement]:
                    self.minRsiElement = i
        else:
            self.minRsiElement = self.rsi.index(min(self.rsi))

        self.log("")
        for i in range(len(self.datas)):
            self.log(self.datas[i].params.dataname.split("/")[-1] + " " + str(self.rsi[i][0]))

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")

        if self.doBuy:
            self.log("Selected stock: %s (RSI %d)" % (self.datas[self.minRsiElement].params.dataname.split("/")[-1], self.rsi[self.minRsiElement][0]))
        else:
            self.log("Nothing to buy, close all positions")

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")



if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)


    tickers = [

        "SHY",
        "IEF",
        "TLT",
        "AGG",
        "LQD",

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
