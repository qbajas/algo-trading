import requests

tickers = [
    "SHY",
    "IEF",
    "TLT",
    "AGG",
    "LQD",

    "SPY",
    "SPMO",

    "IWM",

    "QQQ",
    "PTF",

    "EFA",
    "IDMO",

    "EEM",
    "EEMO",

    "VNQ",
    "GLD",
]

for ticker in tickers:
    url = "https://query1.finance.yahoo.com/v7/finance/download/" + ticker + "?period1=0&period2=2689241600&interval=1d&events=history"
    print(url)
    header = {'Connection': 'keep-alive',
              'Expires': '-1',
              'Upgrade-Insecure-Requests': '1',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
              }
    # response = requests.get(url, headers={"cookie":"APID=1A183a548a-9cba-11e9-af7b-1237df373440; B=bjr2kctehmev4&b=3&s=s6; A1=d=AQABBFQFMl4CEL-XFkBopYNV4cYQ6zC-z74FEgABBgG74GHDYu-bb2UB9iMAAAcI5DsbXWdU7Lk&S=AQAAAjaC7NhfDGoHP8J5-6hDPx8; A3=d=AQABBFQFMl4CEL-XFkBopYNV4cYQ6zC-z74FEgABBgG74GHDYu-bb2UB9iMAAAcI5DsbXWdU7Lk&S=AQAAAjaC7NhfDGoHP8J5-6hDPx8; A1S=d=AQABBFQFMl4CEL-XFkBopYNV4cYQ6zC-z74FEgABBgG74GHDYu-bb2UB9iMAAAcI5DsbXWdU7Lk&S=AQAAAjaC7NhfDGoHP8J5-6hDPx8&j=GDPR; GUC=AQABBgFh4Ltiw0IjSQT8; PRF=t=MSFT; cmp=v=22&t=1642433470&j=1; APIDTS=1642526270"})
    # response = requests.get(url)
    response = requests.get(url, headers=header)
    f = open("../resources/tickers/" + ticker + ".csv", "w")
    f.write(response.text)
    f.close()
