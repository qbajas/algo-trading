from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import locale

import pprint

from backtrader.analyzers import SharpeRatio, TimeDrawDown, PeriodStats, TimeReturn, Returns, AnnualReturn

day = 0


# Create a Stratey
class MinRsi(bt.Strategy):

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
        self.orders = []
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
                self.orders.append(
                    self.close(data=self.datas[i], exectype=bt.Order.Limit, price=self.datas[i][0] * 0.98)
                )

        if not self.broker.getposition(datas[self.minRsiElement]):
            self.log(" buying size %f" % self.getsizing(self.datas[self.minRsiElement]))
            self.orders.append(
                self.buy(data=self.datas[self.minRsiElement], size=self.getsizing(self.datas[self.minRsiElement]),
                         exectype=bt.Order.Limit, price=self.datas[self.minRsiElement][0] * 1.017)
            )

    def cancel_open_orders(self):
        for i in range(len(self.orders)):
            self.log(" cancelling an order " + self.get_ticker_name(self.orders[i].data))
            self.cancel(self.orders[i])

    def get_ticker_name(self, data):
        return data.params.dataname.split("/")[-1].split(".")[0]

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
                self.positioncount = 0
                self.log(
                    ' SELL EXECUTED at price {}, cost {}, com {}'.format(order.executed.price,
                                                                         order.executed.value,
                                                                         order.executed.comm)
                )
            self.orders.remove(order)
        elif order.status in [order.Canceled, order.Margin, order.Rejected, order.Expired]:
            self.log('WARNING: Order Canceled/Margin/Rejected/Expired %s' % order.status)
            self.orders.remove(order)

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('  OPERATION PROFIT, GROSS {}, NET{}'.format(trade.pnl,
                                                              trade.pnlcomm))


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro(cheat_on_open=True)

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
