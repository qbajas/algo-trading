from datetime import datetime
import backtrader as bt

# Create a Strategy
class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30   # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average

        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast MA crosses above slow MA
                self.buy()  # enter long position
        else:
            if self.crossover < 0:  # if fast MA crosses below slow MA
                self.close()  # close the position

# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
# strategy = SmaCross()
# cerebro.addstrategy(strategy)
cerebro.addstrategy(SmaCross)

# Load data
data = bt.feeds.YahooFinanceData(dataname='../../resources/tickers/AAPL.csv', fromdate=datetime(2020, 1, 1), todate=datetime(2020, 12, 31))
cerebro.adddata(data)

# Run the backtest
cerebro.run()

# Plot the result
cerebro.plot()