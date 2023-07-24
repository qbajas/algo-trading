from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import locale
import pprint

# Import the backtrader platform
import backtrader as bt
from backtrader.analyzers import SharpeRatio, TimeDrawDown, PeriodStats, Returns, AnnualReturn

from base import BaseStrategy

day = 0


# Create a Stratey
class MinRsi(BaseStrategy):

    def __init__(self):
        super().__init__()
        self.setsizer(bt.sizers.AllInSizer())

        self.rsi = []
        for i in range(len(self.datas)):
            self.rsi.append(bt.indicators.RSI_Safe(self.datas[i].close, period=2))
            # self.rsi.append(bt.indicators.WilliamsR(self.datas[i], period=6))

        self.minRsiElement = 0

    def next(self):
        self.log("Positions: %d, cash %d" % (self.positioncount, self.sizer.broker.getcash()))
        global day
        day += 1

        self.minRsiElement = self.rsi.index(min(self.rsi))

        self.log("  Selected stock: %s (RSI %d)" % (
            self.datas[self.minRsiElement].params.dataname.split("/")[-1], self.rsi[self.minRsiElement][0]))

        self.cancel_open_orders()

        for i in range(len(self.datas)):
            if self.broker.getposition(datas[i]) and i != self.minRsiElement:
                self.log(" selling ")
                self.close(data=self.datas[i], exectype=bt.Order.Limit, price=self.datas[i][0] * 0.98)

        if not self.broker.getposition(datas[self.minRsiElement]):
            self.log(" buying size %f" % self.getsizing(self.datas[self.minRsiElement]))
            self.buy(data=self.datas[self.minRsiElement], size=self.getsizing(self.datas[self.minRsiElement]),
                     exectype=bt.Order.Limit, price=self.datas[self.minRsiElement][0] * 1.017)


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(MinRsi)

    cerebro.addanalyzer(SharpeRatio)
    cerebro.addanalyzer(TimeDrawDown)
    cerebro.addanalyzer(PeriodStats)
    cerebro.addanalyzer(AnnualReturn)
    cerebro.addanalyzer(Returns)

    tickers = [
        "SHY",
        "IEF",
        "TLT",
        "AGG",
        "LQD",

        "SPY",
        # "SPMO",
        #
        "EFA",
        # "IMTM",
        #
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

            fromdate=bt.datetime.datetime(2015, 11, 1)
            # fromdate=bt.datetime.datetime(2004, 11, 1),
            # todate=datetime.datetime(2018, 12, 31)
        )

        data.start()

        data.plotinfo.plot = False
        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

        datas.append(data)

    # Set our desired cash start
    cashstart = 100000.0
    cerebro.broker.setcash(cashstart)
    cerebro.broker.setcommission(leverage=100, commission=0.000035)  # 0.0035% of the operation value

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    run = cerebro.run()

    # cerebro.plot()
    locale.setlocale(locale.LC_ALL, 'en_US')

    # Print out the final result
    print(locale.format_string("Final Portfolio Value: %d", cerebro.broker.getvalue(), grouping=True))
    print(locale.format_string("Annualized return: %f percent",
                               100 * (((cerebro.broker.getvalue() / cashstart) ** (1 / (day / 252))) - 1),
                               grouping=True))

    pp = pprint.PrettyPrinter(width=41, compact=True)
    pp.pprint(run[0].analyzers[0].get_analysis())
    pp.pprint(run[0].analyzers[1].get_analysis())
    pp.pprint(run[0].analyzers[3].get_analysis())
    pp.pprint(run[0].analyzers[4].get_analysis())

    cerebro.plot()
