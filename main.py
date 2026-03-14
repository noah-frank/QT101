
import pandas as pd 
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

def get_sp500_tickers():
    site= "https://en.wikipedia.org/wiki/List_of_S&P_500_companies"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(site,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table") #[0]
    df = pd.read_html(str(table))
    tickers = list(df[0].Symbol)
    return tickers

tickers = get_sp500_tickers()

def get_history(ticker, period_start, period_end, granularity="1d"):
    import yfinance

    df = yfinance.Ticker(ticker).history(
        start=period_start, 
        end=period_end, 
        interval=granularity, 
        auto_adjust=True
    ).reset_index()
    df = df.rename(columns={
        "Date": "datetime", 
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close", 
        "Volume": "volume"
    })

    # input(df.head())

    if df.empty:
        return pd.DataFrame()

    df["datetime"] = df["datetime"].dt.tz_convert(pytz.utc)
    df = df.drop(columns=["Dividends", "Stock Splits"])
    df = df.set_index("datetime", drop=True)
    return df

from datetime import datetime
import pytz

period_start = datetime(2016, 1, 1, tzinfo=pytz.utc)
period_end = datetime(2026, 1, 1, tzinfo=pytz.utc)

# print(period_start)
# print(period_end)
# get_history("MMM", period_start, period_end, "1d")

i = 0

for ticker in tickers:
    df = get_history(ticker, period_start, period_end)
    print(ticker, df)

    i += 1

    if i >= 5:
        break
