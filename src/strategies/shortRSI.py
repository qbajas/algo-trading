from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import locale
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

import pprint


# Create a Stratey
from backtrader.analyzers import PeriodStats, AnnualReturn, Returns


class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.setsizer(bt.sizers.AllInSizer())

        self.buyStock = False
        self.shortStock = False

        self.rsi = bt.indicators.RSI_Safe(self.datas[0].close, period=14)

    def next(self):
        self.log("RSI %d, cash %d" % (self.rsi[0], self.sizer.broker.getcash()))

        if self.shortStock:
            self.sell(data=self.datas[0], size=self.getsizing(self.datas[0]) * 0.95)
            self.shortStock = False

        if self.buyStock:
            self.buy(data=self.datas[0], size=self.getsizing(self.datas[0]) * 0.95)
            self.buyStock = False

        if self.rsi > 80 and self.broker.getposition(datas[0]).size >= 0:
            self.close(data=self.datas[0])
            self.shortStock = True

        if self.rsi < 60 and self.broker.getposition(datas[0]).size <= 0:
            self.close(data=self.datas[0])
            self.buyStock = True

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    ' BUY EXECUTED at {}, cost {}, com {}'.format(order.executed.price,
                                                                  order.executed.value,
                                                                  order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.buycom = order.executed.comm
            else:
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

    cerebro.addanalyzer(PeriodStats)
    cerebro.addanalyzer(AnnualReturn)
    cerebro.addanalyzer(Returns)

    tickers = [
        "EWC",
        # "SHY"
    ]

    datas = []

    for ticker in tickers:
        # Create a Data Feed
        data = bt.feeds.YahooFinanceCSVData(
            dataname="../../resources/tickers/" + ticker + ".csv",
            # Do not pass values before this date
            fromdate=datetime.datetime(1970, 1, 1),
            # Do not pass values before this date
            todate=datetime.datetime(2022, 12, 31))

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

    locale.setlocale(locale.LC_ALL, 'en_US')

    # Print out the final result
    print(locale.format_string("Final Portfolio Value: %d", cerebro.broker.getvalue(), grouping=True))

    pp = pprint.PrettyPrinter(width=41, compact=True)
    # pp.pprint(run[0].analyzers[0].get_analysis())
    # pp.pprint(run[0].analyzers[1].get_analysis())
    pp.pprint(run[0].analyzers[2].get_analysis())