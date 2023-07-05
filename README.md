# Algotrading strategies for ETFs

## About
- several trading strategies based on indicators such as RSI and SMA
- allows backtesting of the strategies using historical data
- runs on Python 3.10 with backtrader framework

## Installation
- https://www.backtrader.com/docu/installation/
- https://github.com/mementum/backtrader#installation

## Running a simulation
### Download data
Downloads historical prices of ETFs from the defined ETF universe
```
python downloader.py
```
### Execute the simulation
This example strategy invests all capital in the ETF with the lowest RSI(2) score. The RSI is calculated at the market close, the trading is done at the market open.
```
python minRsi.py
```

## Sample output
Information about annualized returns, yearly returns, sharpe ration, max drawdown, executed trades etc

```
2023-06-30, Positions: 1, cash 362572
2023-06-30,   Selected stock: SHY.csv (RSI 33)
2023-06-30,  selling 
2023-06-30,  buying size 4483.393466
2023-07-03,  SELL EXECUTED at price 178.61, cost 358073.83183599793, com 12.63016898182004
2023-07-03,  BUY EXECUTED at 80.82, cost 362347.8599006582, com 12.682175096523036
2023-07-03,   OPERATION PROFIT, GROSS 2788.1390731461133, NET2762.9763200500333
2023-07-03, Positions: 1, cash 365292
2023-07-03,   Selected stock: SHY.csv (RSI 16)
Final Portfolio Value: 368,736
Annualized return: 18.607256 percent
OrderedDict([('sharperatio',
              0.8688111333582026)])
OrderedDict([('maxdrawdown',
              22.0152934121263),
             ('maxdrawdownperiod', 247)])
OrderedDict([(2015, 0.05122567838026293),
             (2016, 0.06276456157714883),
             (2017, 0.22561824592017454),
             (2018,
              -0.015572732841336534),
             (2019, 0.19185511924085952),
             (2020, 0.6097033355248196),
             (2021, 0.2080663609335569),
             (2022,
              -0.03148034329036109),
             (2023, 0.2186399935846095)])
```


![plot1](https://github.com/qbajas/backtesting/assets/682591/d47bc9ed-a20b-4706-8733-6b3de65d986b)


## Support
Ideas? Suggestions? Feel free to contact me at jaskowiecj@gmail.com
