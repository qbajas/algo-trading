from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class BaseStrategy(bt.Strategy):

    def __init__(self):
        self.positioncount = 0
        self.orders = []

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def get_ticker_name(self, data):
        return data.params.dataname.split("/")[-1].split(".")[0]

    def notify_order(self, order):
        if order not in self.orders:
            self.orders.append(order)
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
        elif order.status in [order.Canceled, order.Expired, order.Margin, order.Rejected]:
            self.log(' WARNING: Order %s Canceled/Expired/Margin/Rejected %s'
                     % (self.get_ticker_name(order.data), order.status))
            self.orders.remove(order)

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('  OPERATION PROFIT, GROSS {}, NET{}'.format(format(trade.pnl, ".2f"),
                                                              format(trade.pnlcomm, ".2f")))

    def cancel_open_orders(self):
        for i in range(len(self.orders)):
            self.log(" cancelling an order " + self.get_ticker_name(self.orders[i].data))
            self.cancel(self.orders[i])


