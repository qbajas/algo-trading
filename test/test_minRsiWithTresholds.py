from unittest import TestCase

import backtrader as bt
from minRsiWithTresholds import MinRsiWithThresholdsStrategy


class TestMinRsiWithThresholdsStrategy(TestCase):

    def setUp(self):
        # Create a cerebro entity
        self.cerebro = bt.Cerebro()

        # Add a strategy
        self.cerebro.addstrategy(MinRsiWithThresholdsStrategy)

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

        self.datas = []

        for ticker in tickers:
            # Create a Data Feed
            data = bt.feeds.YahooFinanceCSVData(
                dataname="../resources/tickers/" + ticker + ".csv",
                fromdate=bt.datetime.datetime(2023, 6, 2),
                todate=bt.datetime.datetime(2023, 6, 8)
            )
            self.cerebro.adddata(data)
            self.datas.append(data)

    def test_strategy(self):
        # given
        self.cerebro.broker.setcash(100000.0)
        self.cerebro.broker.setcommission(leverage=100000.0, commission=0.000035)

        # when
        self.cerebro.run()

        # then
        strategy = self.cerebro.runstrats[0][0]
        # Assertion 1: On day one, the ticker with the lowest RSI score is selected
        selected_ticker = strategy.datas[strategy.minRsiElement].params.dataname.split("/")[-1]
        lowest_rsi_score = strategy.rsi[strategy.minRsiElement][0]
        self.assertEqual(selected_ticker, "QQQ.csv")
        self.assertAlmostEqual(lowest_rsi_score, 2.2, delta=0.1)
        # Assertion 2: The buy order is created with maximum available cash and buys the selected ticker
        buy_orders = [order for order in strategy.orders if order.isbuy()]
        self.assertEqual(len(buy_orders), 1)  # Ensure only one buy order is created
        buy_order = buy_orders[0]
        self.assertEqual(buy_order.data.params.dataname.split("/")[-1], "QQQ.csv")
        self.assertAlmostEqual(buy_order.price, 354.2, delta=0.1)
        cash = strategy.sizer.broker.getcash()
        price = strategy.datas[strategy.minRsiElement][0]
        self.assertEqual(buy_order.size, cash / price)

if __name__ == '__main__':
    unittest.main()