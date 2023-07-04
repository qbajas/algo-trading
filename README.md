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
2023-06-30, Positions: 1, cash 695636
2023-06-30,  Selected stock: SHY.csv (RSI 33, price 80)
2023-06-30,  selling GLD.csv
2023-06-30,  buying SHY.csv
2023-07-03,  SELL GLD EXECUTED at price 178.61, cost 712773.6312497967, com 25.14132731317168
2023-07-03,  BUY SHY EXECUTED at 80.82, cost 695206.686859368, com 24.33223404007788
2023-07-03,   OPERATION PROFIT, GROSS 5550.006269394214, NET5499.917864987299
2023-07-03, Positions: 1, cash 701137
2023-07-03,  Selected stock: SHY.csv (RSI 17, price 80)
Final Portfolio Value: 700,800
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

## Support
Ideas? Suggestions? Fell free to contact me at jaskowiecj@gmail.com
