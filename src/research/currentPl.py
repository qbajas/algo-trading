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
            self.rsi.append(
                (10 * bt.indicators.RSI_Safe(self.datas[i].close, period=2) +
                 bt.indicators.RSI_Safe(self.datas[i].close, period=3)) / 11
            )

        self.minRsiElement = 0

    def next(self):
        self.previousMinRsiElement = self.minRsiElement

        # --- START effective strategy ---

        self.minRsiElement = self.rsi.index(min(self.rsi))

        # --- END effective strategy ---

        # print only last days
        if self.datas[0].datetime.date(0) < datetime.date.today() - datetime.timedelta(days=7):
            return

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

        if self.previousMinRsiElement != self.minRsiElement:
            self.log("+ BUY %s limit %s " %
                     (self.get_ticker_name(self.datas[self.minRsiElement]),
                      format(self.datas[self.minRsiElement][0] * 1.017, ".2f")))
            self.log("- SELL %s limit %s" %
                     (self.get_ticker_name(self.datas[self.previousMinRsiElement]),
                      format(self.datas[self.previousMinRsiElement][0] * 0.98, ".2f")))

    def get_ticker_name(self, data):
        return data.params.dataname.split("/")[-1].split(".")[0]


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    tickers = [
        "IWMO.L",
        "IWRD.L",
        "VWRL.L",
    ]

    datas = []

    for ticker in tickers:
        # Create a Data Feed
        data = bt.feeds.YahooFinanceCSVData(
            dataname="../../resources/tickers/" + ticker + ".csv",
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
