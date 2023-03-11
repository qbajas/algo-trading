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
        self.rsi3 = []
        for i in range(len(self.datas)):
            self.rsi.append(bt.indicators.RSI_Safe(self.datas[i].close, period=2))
            self.rsi3.append(bt.indicators.RSI_Safe(self.datas[i].close, period=3))

        self.buyStocksOnly = False
        self.buyBondsOnly = False
        self.doBuy = True
        self.previousMinRsiElement = None

    def next(self):
        self.log("Positions: %d, cash %d" % (self.positioncount, self.sizer.broker.getcash()))
        global day
        day += 1

        # buy only if some rsi below 90
        self.doBuy = False
        for i in range(0, len(self.datas)):
            if self.rsi[i] < 90:
                self.doBuy = True

        # buy bonds if all stock rsi over 70
        # self.buyBondsOnly = True
        # for i in range(5, len(self.datas)):
        #     if self.rsi[i] < 70:
        #         self.buyBondsOnly = False

        # buy stocks if any stock rsi below 10
        self.buyStocksOnly = False
        for i in range(5, len(self.datas)):
            if self.rsi[i] < 15:
                self.buyStocksOnly = True

        if self.buyBondsOnly:
            self.startRange = 0
            self.endRange = 5

        if self.buyStocksOnly:
            self.startRange = 5
            self.endRange = len(self.datas)

        if not self.buyBondsOnly and not self.buyStocksOnly:
            self.startRange = 0
            self.endRange = len(self.datas)

        self.minRsiElement = self.startRange
        for i in range(self.startRange, self.endRange):
            if 10 * self.rsi[i] + self.rsi3[i] <= 10 * self.rsi[self.minRsiElement] + self.rsi3[self.minRsiElement]:
                self.minRsiElement = i

        # self.log("  buy: %s %s" % (self.buyBondsOnly, self.buyStocksOnly))
        self.log("  Selected stock: %s (RSI %d, price %d)" % (
            self.datas[self.minRsiElement].params.dataname.split("/")[-1],
            self.rsi[self.minRsiElement][0],
            self.datas[self.minRsiElement][0])
                 )

        if not self.doBuy:
            self.log(" selling ")
            for i in range(len(self.datas)):
                if self.broker.getposition(datas[i]):
                    self.log(" selling " + self.datas[i].params.dataname.split("/")[-1])
                    self.close(data=self.datas[i], exectype=bt.Order.Limit, price=self.datas[i][0] * 0.98,
                               valid=bt.datetime.timedelta(days=1))

        if self.doBuy:
            for i in range(len(self.datas)):
                if self.broker.getposition(datas[i]) and i != self.minRsiElement:
                    self.log(" selling " + self.datas[i].params.dataname.split("/")[-1])
                    self.close(data=self.datas[i], exectype=bt.Order.Limit, price=self.datas[i][0] * 0.98,
                               valid=bt.datetime.timedelta(days=1))

            if not self.broker.getposition(datas[self.minRsiElement]):
                self.log(" buying " + self.datas[self.minRsiElement].params.dataname.split("/")[-1])
                self.buy(data=self.datas[self.minRsiElement], size=self.getsizing(self.datas[self.minRsiElement]),
                         exectype=bt.Order.Limit, price=self.datas[self.minRsiElement][0] * 1.017,
                         valid=bt.datetime.timedelta(days=1))

        self.previousMinRsiElement = self.minRsiElement

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
            fromdate=bt.datetime.datetime(2015, 11, 1)
            # fromdate=bt.datetime.datetime(2014, 10, 5)
        )

        data.start()

        # Add the Data Feed to Cerebro
        data.plotinfo.plot = False
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

    # get rid of warnings from locator.py
    # https://stackoverflow.com/questions/63471764/importerror-cannot-import-name-warnings-from-matplotlib-dates
    cerebro.plot()
