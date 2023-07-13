from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import locale
import pprint

# Import the backtrader platform
import backtrader as bt
from backtrader.analyzers import SharpeRatio, TimeDrawDown, PeriodStats, Returns, AnnualReturn

day = 0


# Create a Stratey
class MinRsiWithThresholdsStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.setsizer(bt.sizers.AllInSizer())

        self.positioncount = 0
        self.orders = []
        self.rsi = []
        for i in range(len(self.datas)):
            self.rsi.append(
                (10 * bt.indicators.RSI_Safe(self.datas[i].close, period=2) +
                 bt.indicators.RSI_Safe(self.datas[i].close, period=3)) / 11
            )

        self.buyStocksOnly = False
        self.buyBondsOnly = False
        self.doBuy = True
        self.minRsiElement = 5
        self.buyRsi = 0

    def next(self):
        self.compute_min_rsi_element()

        self.cancel_open_orders()

        if not self.doBuy:
            for i in range(len(self.datas)):
                if self.broker.getposition(self.datas[i]):
                    self.create_sell_order(i)

        if self.doBuy:
            for i in range(len(self.datas)):
                if self.broker.getposition(self.datas[i]) and i != self.minRsiElement:
                    self.create_sell_order(i)

            if not self.broker.getposition(self.datas[self.minRsiElement]):
                self.create_buy_order()
                self.buyRsi = self.rsi[self.minRsiElement][0]

    def compute_min_rsi_element(self):
        self.previousMinRsiElement = self.minRsiElement
        # self.log("Positions: %d, cash %d" % (self.positioncount, self.sizer.broker.getcash()))
        global day
        day += 1

        # buy only if some rsi below 90
        self.doBuy = False
        for i in range(0, len(self.datas)):
            if self.rsi[i] < 70:
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
            if self.rsi[i] <= self.rsi[self.minRsiElement]:
                self.minRsiElement = i

        # reduce number of trades:
        if self.previousMinRsiElement in range(self.startRange, self.endRange):
            # if rsi of the asset fell by too much compared to previous day, do not change the asset
            if self.rsi[self.previousMinRsiElement][-1] > self.rsi[self.previousMinRsiElement][0] + 1:
                self.minRsiElement = self.previousMinRsiElement

            # if the new asset has rsi too big compared to the current one, do not change it
            # if self.rsi[self.minRsiElement][0] + 2 > self.rsi[self.previousMinRsiElement][0]:
            #     self.minRsiElement = self.previousMinRsiElement

            # if rsi fallen by too much compared to when bought, do not change the asset
            # if self.buyRsi > self.rsi[self.previousMinRsiElement][0]:
            #     self.minRsiElement = self.previousMinRsiElement

            # if rsi lower than 20, do not change the asset
            # if self.rsi[self.previousMinRsiElement][0] < 20:
            #     self.minRsiElement = self.previousMinRsiElement

        self.log("Selected stock: %s (rsi %d)" %
                 (self.get_ticker_name(self.datas[self.minRsiElement]),
                  self.rsi[self.minRsiElement][0]))

    def create_buy_order(self):
        sizing = self.getsizing(self.datas[self.minRsiElement])
        price = self.datas[self.minRsiElement][0]
        self.log("+ BUY %d %s @ %s LIMIT ($%d)" % (
            sizing,
            self.get_ticker_name(self.datas[self.minRsiElement]),
            format(price * 1.017, ".2f"),
            sizing * price)
                 )
        self.orders.append(
            self.buy(data=self.datas[self.minRsiElement], size=self.getsizing(self.datas[self.minRsiElement]),
                     exectype=bt.Order.Limit, price=self.datas[self.minRsiElement][0] * 1.017)
        )

    def create_sell_order(self, i):
        price = self.datas[i][0]
        self.log("- CLOSE %s %s LIMIT" % (
            self.get_ticker_name(self.datas[self.previousMinRsiElement]),
            format(price * 0.983, ".2f"))
                 )
        self.orders.append(
            self.close(data=self.datas[i], exectype=bt.Order.Limit, price=price * 0.983)
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
                    ' BUY {} EXECUTED at {}, cost {}, com {}'.format(
                        self.get_ticker_name(order.data),
                        format(order.executed.price, ".2f"),
                        format(order.executed.value, ".2f"),
                        format(order.executed.comm, ".2f"))
                )
                # self.buyprice = order.executed.price
                # self.buycom = order.executed.comm
            else:
                self.positioncount -= 1
                self.log(
                    ' SELL {} EXECUTED at price {}, cost {}, com {}'.format(
                        self.get_ticker_name(order.data),
                        format(order.executed.price, ".2f"),
                        format(order.executed.value, ".2f"),
                        format(order.executed.comm , ".2f"))
                )
            self.orders.remove(order)
            # self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Expired, order.Margin, order.Rejected]:
            self.log(' WARNING: Order %s Canceled/Expired/Margin/Rejected %s'
                     % (self.get_ticker_name(order.data), order.status))
            self.orders.remove(order)

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('  OPERATION PROFIT, GROSS {}, NET{}'.format(format(trade.pnl, ".2f"),
                                                              format(trade.pnlcomm, ".2f")))


if __name__ == '__main__':
    # Create a cerebro entity
    # cerebro = bt.Cerebro(cheat_on_open=True)
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(MinRsiWithThresholdsStrategy)

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
    cerebro.broker.setcommission(leverage=cashstart, commission=0.000035)  # 0.0035% of the operation value
    # cerebro.broker.setcommission(leverage=cashstart, commission=0.0006)

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
