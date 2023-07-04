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
```
python downloader.py
```
### Execute the simulation
```
python minRsiWithTresholds.py
```

## Sample output

```
Annualized return: 29.014496 percent
OrderedDict([('sharperatio',
              1.0745926638137793)])
OrderedDict([('maxdrawdown',
              18.19505371364862),
             ('maxdrawdownperiod', 311)])
OrderedDict([(2015, 0.05019344596513653),
             (2016, 0.35092590323866335),
             (2017, 0.26046061000225484),
             (2018, 0.07378235850410264),
             (2019, 0.3043427221917756),
             (2020, 0.844213615743616),
             (2021, 0.17926578021654582),
             (2022, 0.03501970027711443),
             (2023, 0.2430388111870534)])
```

![plot1](https://github.com/qbajas/backtesting/assets/682591/0cdfd4c0-6929-4308-81ff-a0eab502ae2f)
