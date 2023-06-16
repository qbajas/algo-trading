from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

import pprint

# Create a Stratey
from backtrader.analyzers import SharpeRatio, TimeDrawDown, PeriodStats, AnnualReturn, Returns

day = 0


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
            self.rsi.append(bt.indicators.RSI_Safe(self.datas[i].close, period=14))

        self.sma = []
        for i in range(len(self.datas)):
            self.sma.append(bt.indicators.SMA(self.datas[i].close, period=126))

    def next(self):
        self.log("Positions: %d, cash %d" % (self.positioncount, self.sizer.broker.getcash()))

        global day
        day += 1

        if (day % 5 == 0):
            self.maxRsi = 0
            for i in range(len(self.datas)):
                if self.rsi[i] > 80:
                    self.maxRsi += 1
            self.log("maxRsi: %d" % (self.maxRsi))

            for i in range(len(self.datas)):
                if self.rsi[i] > 80:
                    self.close(data=self.datas[i])

        if (day % 5 == 1):
            self.minRsi = 0
            for i in range(len(self.datas)):
                if self.rsi[i] < 40 and self.sma[i] <= self.datas[i].close:
                    self.minRsi += 1
            self.log("minRsi: %d" % (self.minRsi))

            for i in range(len(self.datas)):
                if self.rsi[i] < 40 and self.sma[i] <= self.datas[i].close:
                    self.buy(data=self.datas[i], size=self.getsizing(self.datas[i]) * 0.9 / self.minRsi)

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.positioncount += 1
                self.log(
                    ' BUY EXECUTED at {}, cost {}, com {}'.format(order.executed.price,
                                                                  order.executed.value,
                                                                  order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.buycom = order.executed.comm
            else:
                self.positioncount -= 1
                self.log(
                    ' SELL EXECUTED at price {}, cost {}, com {}'.format(order.executed.price,
                                                                         order.executed.value,
                                                                         order.executed.comm)
                )
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('WARNING: Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('  OPERATION PROFIT, GROSS {}, NET{}'.format(trade.pnl,
                                                              trade.pnlcomm))


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    cerebro.addanalyzer(SharpeRatio)
    cerebro.addanalyzer(TimeDrawDown)
    cerebro.addanalyzer(PeriodStats)
    cerebro.addanalyzer(AnnualReturn)
    cerebro.addanalyzer(Returns)


    tickers = [
        "SPY",
        "MDY",
        "EWJ",
        "EWC",
        "EWU",
        "EWG",
        "EWL",
        "EWA",
        "EWH",
        "EWQ",
        "EWW",
        "EWI",
        "EWD",
        "EWP",
        "EWS",
        "EWN",
        "EWM",
        "EWO",
        "EWK"
    ]

    datas = []

    for ticker in tickers:
        # Create a Data Feed
        data = bt.feeds.YahooFinanceCSVData(
            dataname="../../resources/tickers/" + ticker + ".csv")
        # Do not pass values before this date
        # fromdate=datetime.datetime(2018, 1, 1),
        # Do not pass values before this date
        # todate=datetime.datetime(2020, 12, 31))

        data.start()

        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

        datas.append(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    run = cerebro.run()

    # cerebro.plot()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    pp = pprint.PrettyPrinter(width=41, compact=True)
    pp.pprint(run[0].analyzers[0].get_analysis())
    pp.pprint(run[0].analyzers[1].get_analysis())
    pp.pprint(run[0].analyzers[2].get_analysis())
    pp.pprint(run[0].analyzers[3].get_analysis())
    pp.pprint(run[0].analyzers[4].get_analysis())
