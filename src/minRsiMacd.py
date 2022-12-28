from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import locale
import yfinance as yf
import pprint

from backtrader.analyzers import SharpeRatio, TimeDrawDown, PeriodStats, TimeReturn, Returns, AnnualReturn

day = 0


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
            self.rsi.append(bt.indicators.RSI_Safe(self.datas[i].close, period=12))

        self.macd = []
        for i in range(len(self.datas)):
            self.macd.append(bt.indicators.MACD(self.datas[i].close, period_me1=12, period_me2=26, period_signal=9))

        # self.sma = []
        # for i in range(len(self.datas)):
        #     self.sma.append(bt.indicators.SMA(self.datas[i].close, period=200))

        self.minRsiElement = 0


    def next(self):
        self.log("Positions: %d, cash %d" % (self.positioncount, self.sizer.broker.getcash()))
        global day
        day += 1

        # self.minRsiElement = self.rsi.index(min(self.rsi))

        for i in range(0, len(self.datas)):
            if self.rsi[i] > 70 and self.macd[i].macd < self.macd[i].signal:
                self.close(data=self.datas[i])

        for i in range(0, len(self.datas)):
            if self.rsi[i] < 30 and self.macd[i].macd > self.macd[i].signal and not self.broker.getposition(datas[i]):
                self.buy(data=self.datas[i], size=self.getsizing(self.datas[i]))



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
    cerebro = bt.Cerebro(cheat_on_open=True)

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    cerebro.addanalyzer(SharpeRatio)
    cerebro.addanalyzer(TimeDrawDown)
    cerebro.addanalyzer(PeriodStats)
    cerebro.addanalyzer(AnnualReturn)
    cerebro.addanalyzer(Returns)

    tickers = [
        # "SHY",
        # "IEF",
        # "TLT",
        # "AGG",
        # "LQD",

        "SPY",
        # "SPMO",
        #
        "EFA",
        # "IMTM",
        #
        # "QQQ",
        # "EEM",
        # "IWM",
        # "VNQ",
        "GLD",

    ]

    datas = []

    for ticker in tickers:

        data = bt.feeds.PandasData(
            dataname=yf.download(ticker, '2021-01-21', '2022-12-27', auto_adjust=True, interval="1h" ))

        data.start()

        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

        datas.append(data)

    # Set our desired cash start
    cashstart = 100000.0
    cerebro.broker.setcash(cashstart)
    cerebro.broker.setcommission(leverage=cashstart, commission=0.000005)  # 0.0005% of the operation value

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    run = cerebro.run()

    # cerebro.plot()
    locale.setlocale(locale.LC_ALL, 'en_US')

    # Print out the final result
    print(locale.format_string("Final Portfolio Value: %d", cerebro.broker.getvalue(), grouping=True))
    # print(locale.format_string("Annualized return: %f percent",
    #                            100 * (((cerebro.broker.getvalue() / cashstart) ** (1 / (day / 252))) - 1),
    #                            grouping=True))

    pp = pprint.PrettyPrinter(width=41, compact=True)
    pp.pprint(run[0].analyzers[0].get_analysis())
    pp.pprint(run[0].analyzers[1].get_analysis())
    pp.pprint(run[0].analyzers[3].get_analysis())
    pp.pprint(run[0].analyzers[4].get_analysis())
