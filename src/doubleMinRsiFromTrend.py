from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import locale
import pprint

# Import the backtrader platform
import backtrader as bt
from backtrader.analyzers import SharpeRatio, TimeDrawDown, PeriodStats, Returns, AnnualReturn

day = 0


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
        self.sma = []
        for i in range(len(self.datas)):
            self.sma.append(bt.indicators.SMA(self.datas[i].close, period=200))

        self.buyStock = True
        self.minRsiElement = 0
        self.minRsiElement2 = 0
        self.foundWithinTrend = False
        self.foundWithinTrend2 = False

    def next(self):
        self.log("Positions: %d, cash %d" % (self.positioncount, self.sizer.broker.getcash()))
        global day
        day += 1

        self.foundWithinTrend = False
        self.minRsiElement = 0
        for i in range(0,len(self.datas)):
            if self.rsi[i] <= self.rsi[self.minRsiElement] and self.sma[i] <= self.datas[i].close:
                self.minRsiElement = i
                self.foundWithinTrend = True

        if not self.foundWithinTrend:
            self.log("trend not found")
            self.minRsiElement = self.rsi.index(min(self.rsi))

        self.minRsiElement2 = 0
        if self.minRsiElement == 0:
            self.minRsiElement2 = 1

        self.foundWithinTrend2 = False
        for i in range(0,len(self.datas)):
            if self.rsi[i] <= self.rsi[self.minRsiElement2] and self.sma[i] <= self.datas[i].close and i != self.minRsiElement:
                self.minRsiElement2 = i
                self.foundWithinTrend2 = True

        if not self.foundWithinTrend2:
            self.log("trend not found")
            for i in range(0,len(self.datas)):
                if self.rsi[i] <= self.rsi[self.minRsiElement2] and i != self.minRsiElement:
                    self.minRsiElement2 = i

        self.log("  Selected stock: %s (RSI %d, SMA %d)" % (self.datas[self.minRsiElement].params.dataname.split("/")[-1], self.rsi[self.minRsiElement][0], self.sma[self.minRsiElement][0]))
        self.log("  Selected stock: %s (RSI %d, SMA %d)" % (self.datas[self.minRsiElement2].params.dataname.split("/")[-1], self.rsi[self.minRsiElement2][0], self.sma[self.minRsiElement2][0]))

        # --- version 1
        if not self.broker.getposition(datas[self.minRsiElement]) or not self.broker.getposition(datas[self.minRsiElement2]):
            sizing1 = self.getsizing(self.datas[self.minRsiElement])
            if not self.broker.getposition(datas[self.minRsiElement]):
                sizing1 = sizing1 / 2
            sizing2 = self.getsizing(self.datas[self.minRsiElement2])
            if not self.broker.getposition(datas[self.minRsiElement2]):
                sizing2 = sizing2 / 2

            self.log(" selling ")
            for i in range(len(self.datas)):
                self.close(data=self.datas[i])

            self.log(" buying ")
            self.buy(data=self.datas[self.minRsiElement], size=sizing1)
            self.buy(data=self.datas[self.minRsiElement2], size=sizing2)
        # --- end version 1

        # --- version 2
        # if not self.broker.getposition(datas[self.minRsiElement]):
        #     sizing1 = self.getsizing(self.datas[self.minRsiElement]) / 2
        #
        #     self.log(" selling 1")
        #     for i in range(len(self.datas)):
        #         if i != self.minRsiElement2:
        #             self.close(data=self.datas[i])
        #
        #     self.log(" buying 1")
        #     self.buy(data=self.datas[self.minRsiElement], size=sizing1)
        #
        # if not self.broker.getposition(datas[self.minRsiElement2]):
        #     sizing2 = self.getsizing(self.datas[self.minRsiElement2]) / 2
        #
        #     if self.broker.getposition(datas[self.minRsiElement]):
        #         self.log(" selling 2")
        #         for i in range(len(self.datas)):
        #             if i != self.minRsiElement:
        #                 self.close(data=self.datas[i])
        #
        #     self.log(" buying 2")
        #     self.buy(data=self.datas[self.minRsiElement2], size=sizing2)
        # --- end version 2


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
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('WARNING: Order Canceled/Margin/Rejected %s' % order.status)
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('  OPERATION PROFIT, GROSS {}, NET{}'.format(trade.pnl,
                                                              trade.pnlcomm))


if __name__ == '__main__':
    # Create a cerebro entity
    # cerebro = bt.Cerebro(cheat_on_open=True)
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

        "XLU",
        "XLE",
        "XLV",
        "XLB",
        "XLF",
        "XLI",
        "XLK",
        "XLP",
        "XLY",

        # "EWW",
        # "EWI",
        # "EWD",
        # "EWP",
        # "EWS",
        # "EWN",
        # "EWM",
        # "EWO",
        # "EWK",

        "EWZ",

        # "QQQ",
        "IWM",

        # "IWMO.L",
        # "MVOL.L",

    ]

    datas = []

    for ticker in tickers:
        # Create a Data Feed
        data = bt.feeds.YahooFinanceCSVData(
            dataname="../resources/tickers/" + ticker + ".csv",
            # Do not pass values before this date
            fromdate=bt.datetime.datetime(2000, 1, 1)
            # fromdate=bt.datetime.datetime(2014, 10, 5)
        )

        data.start()

        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

        datas.append(data)

    # Set our desired cash start
    cashstart = 100000.0
    cerebro.broker.setcash(cashstart)
    cerebro.broker.setcommission(leverage=100, commission=0.000005)  # 0.0005% of the operation value

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

