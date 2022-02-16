from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

import pprint


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        # self.rsi0 = bt.indicators.RSI_Safe(self.datas[0].close, period=14)
        # self.rsi1 = bt.indicators.RSI_Safe(self.datas[1].close, period=14)
        # self.setsizer(bt.sizers.PercentSizerInt(percents=20))
        self.setsizer(bt.sizers.AllInSizer())

        self.positioncount = 0
        self.rsi = []
        for i in range(len(self.datas)):
            self.rsi.append(bt.indicators.RSI_Safe(self.datas[i].close, period=14))

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('RSI0, %.2f' % self.rsi0[0])
        # self.log('RSI1, %.2f' % self.rsi1[0])
        # self.buy(data=self.datas[1], size=self.getsizing(self.datas[1]) * 0.9)
        self.log("Positions: %d, cash %d" % (self.positioncount, self.sizer.broker.getcash()))

        for i in range(len(self.datas)):
            if self.positioncount > 0 and self.rsi[i] > 70 and self.broker.getposition(datas[i]):
                self.close(data=self.datas[i])

        for i in range(len(self.datas)):
            if self.positioncount < 10 and self.rsi[i] < 40 and not self.broker.getposition(datas[i]):
                self.buy(data=self.datas[i], size=self.getsizing(self.datas[i]) * 0.95 / (10 - self.positioncount))

        # if self.positioncount == 0:
        #     for i in range(len(self.datas)):
        #         self.buy(data=self.datas[i], size=self.getsizing(self.datas[i]) * 0.9 / (len(self.datas)))

        # if (self.rsi0[0] < self.rsi1[0]):
        #     if self.broker.getposition(datas[1]):
        #         self.log('SELL DATA1')
        #         self.close(data=self.datas[1])
        #     if not self.broker.getposition(datas[0]):
        #         # BUY, BUY, BUY!!! (with all possible default parameters)
        #         self.log('BUY DATA0, %.2f , size %f, cash %d' % (self.datas[0].close[0], self.getsizing(self.datas[0]), self.sizer.broker.getcash()))
        #         self.buy(data=self.datas[0], size=self.getsizing(self.datas[0]) * 0.9)
        # else:
        #     if self.broker.getposition(datas[0]):
        #         self.log('SELL DATA0')
        #         self.close(data=self.datas[0])
        #     if not self.broker.getposition(datas[1]):
        #         # BUY, BUY, BUY!!! (with all possible default parameters)
        #         self.log('BUY DATA1, %.2f , size %d' % (self.datas[1].close[0], self.getsizing(self.datas[1])))
        #         self.buy(data=self.datas[1], size=self.getsizing(self.datas[1]) * 0.9)

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

    # TODO how to get a historical tickers e.g. companies which do not longer exist

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
            dataname="../resources/tickers/" + ticker + ".csv")
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
    cerebro.run()

    # cerebro.plot()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # for data in datas:
    #     print(data.params.dataname)
    #     print(cerebro.broker.getposition(data))
