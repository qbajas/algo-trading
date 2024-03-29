from unittest import TestCase

import backtrader as bt
from current import CurrentStrategy


class TestCurrentStrategy(TestCase):

    def setUp(self):
        self.cerebro = bt.Cerebro()
        self.cerebro.addstrategy(CurrentStrategy)
        self.cerebro.broker.setcash(100000.0)
        self.cerebro.broker.setcommission(leverage=100000.0, commission=0.000035)

        self.tickers = [

            "SHY",
            "IEF",
            "TLT",
            "AGG",
            "LQD",

            "SPY",
            "EFA",
            "QQQ",
            "EEM",
            "IWM",
            "VNQ",
            "GLD",

        ]

    def test_buy(self):
        # given
        self.load_data(fromdate=bt.datetime.datetime(2023, 6, 2), todate=bt.datetime.datetime(2023, 6, 8))

        # when
        self.cerebro.run()

        # then
        strategy = self.cerebro.runstrats[0][0]
        self.assert_min_rsi_element(strategy, ticker="QQQ.csv", rsi=2.2)

        # Assertion 2: The buy order is created with maximum available cash and buys the selected ticker
        buy_orders = [order for order in self.cerebro.getbroker().orders if order.isbuy()]
        self.assertEqual(len(buy_orders), 1)  # Ensure only one buy order is created
        buy_order = buy_orders[0]
        self.assertEqual(buy_order.data.params.dataname.split("/")[-1], "QQQ.csv")
        self.assertAlmostEqual(buy_order.price, 354.7, delta=0.1)
        cash = strategy.sizer.broker.getcash()
        price = strategy.datas[strategy.minRsiElement][0]
        self.assertEqual(buy_order.size, cash / price)

    def test_sell(self):
        # given
        self.load_data(fromdate=bt.datetime.datetime(2023, 6, 2), todate=bt.datetime.datetime(2023, 6, 9))

        # when
        self.cerebro.run()

        # then
        strategy = self.cerebro.runstrats[0][0]
        self.assert_min_rsi_element(strategy, ticker="EFA.csv", rsi=45.2)

        # Assertion 2: The sell order is created with maximum available cash and sells the selected ticker
        sell_orders = [order for order in self.cerebro.getbroker().orders if order.issell()]
        self.assertEqual(len(sell_orders), 1)  # Ensure only one sell order is created
        sell_order = sell_orders[0]
        self.assertEqual(sell_order.data.params.dataname.split("/")[-1], "QQQ.csv")
        self.assertAlmostEqual(sell_order.price, 347.1, delta=0.1)
        cash = strategy.sizer.broker.getcash()
        self.assertAlmostEqual(sell_order.size, - cash / sell_orders[0].price, delta=2)

    def test_value(self):
        # given
        self.load_data(fromdate=bt.datetime.datetime(2015, 11, 1), todate=bt.datetime.datetime(2023, 6, 30))

        # when
        self.cerebro.run()

        # then
        self.assertAlmostEqual(474426, self.cerebro.broker.getvalue(), delta=1)

    def test_do_not_change_when_rsi_dropped_by_more_than_1(self):
        # given
        self.load_data(fromdate=bt.datetime.datetime(2023, 6, 9), todate=bt.datetime.datetime(2023, 6, 21))

        # when
        self.cerebro.run()

        # then
        strategy = self.cerebro.runstrats[0][0]
        self.assert_min_rsi_element(strategy, ticker="IWM.csv", rsi=25.1)
        self.assertAlmostEqual(strategy.rsi[strategy.previousMinRsiElement][-1], 37.1, delta=0.1)
        self.assertEqual(strategy.previousMinRsiElement, strategy.minRsiElement)

    # def test_do_not_buy_when_min_rsi_above_70(self):

    # def test_buy_stock_if_any_stock_rsi_below_15(self):

    def assert_min_rsi_element(self, strategy, ticker, rsi):
        # the ticker with the lowest RSI score is selected
        selected_ticker = strategy.datas[strategy.minRsiElement].params.dataname.split("/")[-1]
        lowest_rsi_score = strategy.rsi[strategy.minRsiElement][0]
        self.assertEqual(selected_ticker, ticker)
        self.assertAlmostEqual(lowest_rsi_score, rsi, delta=0.1)

    def load_data(self, fromdate, todate):
        self.datas = []
        for ticker in self.tickers:
            # Create a Data Feed
            data = bt.feeds.YahooFinanceCSVData(
                dataname="../resources/tickers/" + ticker + ".csv",
                adjclose=False,
                fromdate=fromdate,
                todate=todate
            )
            self.cerebro.adddata(data)
            self.datas.append(data)

if __name__ == '__main__':
    unittest.main()