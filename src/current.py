from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
# Import the backtrader platform
import backtrader as bt
import locale
from minRsiWithTresholds import MinRsiWithThresholdsStrategy


class CurrentStrategy(MinRsiWithThresholdsStrategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)

        # print only last days
        if self.datas[0].datetime.date(0) >= datetime.date.today() - datetime.timedelta(days=7):
            print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        self.log("")
        for i in range(len(self.datas)):
            self.log(self.get_ticker_name(self.datas[i]).ljust(4) +
                     " rsi: " + format(self.rsi[i][0], ".2f").ljust(5) +
                     " (price: " + format(self.datas[i][0], ".2f") + ")")

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")

        super().next()

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")


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
            adjclose=False,
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
    cerebro.broker.setcommission(leverage=cashstart, commission=0.00007)  # 0.007% of the operation value

    # Run over everything
    run = cerebro.run()

    # cerebro.plot()
    locale.setlocale(locale.LC_ALL, 'en_US')
