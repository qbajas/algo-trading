from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects

# Import the backtrader platform
import backtrader as bt
import locale


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

        self.minRsiElement = 0

    def next(self):
        global day
        day += 1

        self.foundWithinTrend = False
        for i in range(0,len(self.datas)):
            if self.rsi[i] <= self.rsi[self.minRsiElement] and self.sma[i] <= self.datas[i].close:
                self.minRsiElement = i
                self.foundWithinTrend = True

        if not self.foundWithinTrend:
            self.minRsiElement = self.rsi.index(min(self.rsi))

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")

        self.log("Selected stock: %s (RSI %d, SMA %f)" % (self.datas[self.minRsiElement].params.dataname.split("/")[-1], self.rsi[self.minRsiElement][0], self.sma[self.minRsiElement][0]))

        if self.datas[0].datetime.date(0) == datetime.date.today():
            self.log("---------------")


    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.positioncount += 1
                self.log(
                    '  BUY EXECUTED at {}, cost {}, com {}'.format(order.executed.price,
                                                                  order.executed.value,
                                                                  order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.buycom = order.executed.comm
            else:
                self.positioncount -= 1
                self.log(
                    '  SELL EXECUTED at price {}, cost {}, com {}'.format(order.executed.price,
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
        self.log('    OPERATION PROFIT, GROSS {}, NET{}'.format(trade.pnl,
                                                              trade.pnlcomm))


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)


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

        "EWZ",
        "IWM",

    ]

    datas = []

    for ticker in tickers:
        # Create a Data Feed
        data = bt.feeds.YahooFinanceCSVData(
            dataname="../resources/tickers/" + ticker + ".csv",
        # Do not pass values before this date
        fromdate=datetime.date.today() - datetime.timedelta(days=310))
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



# from 2014:
# minRsiFromTrend:
# Final Portfolio Value: 336,177
# Annualized return: 17.496206 percent
# OrderedDict([('sharperatio',
#               0.9282592346858832)])
# OrderedDict([('maxdrawdown',
#               42.530647318311814),
#              ('maxdrawdownperiod', 281)])
#
#
# doubleMinRsiFromTrend:
# Final Portfolio Value: 338,756
# Annualized return: 17.615701 percent
# OrderedDict([('sharperatio',
#               0.9612934930364905)])
# OrderedDict([('maxdrawdown',
#               44.32361203162356),
#
#
# from 2000:
# minRsiFromTrend:
# Final Portfolio Value: 11,142,334
# Annualized return: 25.221267 percent
# OrderedDict([('sharperatio',
#               0.9836698192209045)])
# OrderedDict([('maxdrawdown',
#               42.53064731831191),
#
# doubleMinRsiFromTrend:
# Final Portfolio Value: 4,206,018
# Annualized return: 19.533123 percent
# OrderedDict([('sharperatio',
#               0.9279661749056529)])
# OrderedDict([('maxdrawdown',
#               44.32361203162373),
#
#  doubleMinRsiFromTrend with MORE ETFs
# Final Portfolio Value: 6,535,484
# Annualized return: 22.073628 percent
# OrderedDict([('sharperatio',
#               0.8583002342340326)])
# OrderedDict([('maxdrawdown',
#               56.150983349748635),
#              ('maxdrawdownperiod', 573)])
