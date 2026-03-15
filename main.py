
import pandas as pd 
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime
import pytz
import threading

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

def get_history(ticker, period_start, period_end, granularity="1d", tries=0):
    import yfinance
    try:
        df = yfinance.Ticker(ticker).history(
            start=period_start, 
            end=period_end, 
            interval=granularity, 
            auto_adjust=True
        ).reset_index()
    except Exception as err:
        if tries < 5:
            return get_history(ticker, period_start, period_end, granularity, tries+1)
        return pd.DataFrame()

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


def get_histories(tickers, period_starts, period_ends, granularity="1d"):
    dfs = [None] * len(tickers)
    def _helper(i):
        print(tickers[i])
        df = get_history(
            tickers[i], 
            period_starts[i], 
            period_ends[i], 
            granularity=granularity
        )
        dfs[i] = df
    threads = [threading.Thread(target=_helper, args=(i,)) for i in range(len(tickers))]
    [thread.start() for thread in threads]
    # If we don't do this, the rest of the function 
    # will execute before the threads are complete 
    [thread.join() for thread in threads] 
    tickers = [tickers[i] for i in range(len(tickers)) if not dfs[i].empty]
    dfs = [df for df in dfs if not df.empty]
    return tickers, dfs

def get_tickers_dfs(start, end):
    from utils import load_pickle, save_pickle
    try:
        tickers, ticker_dfs = load_pickle("dataset.obj")
    except Exception as err:
        tickers = get_sp500_tickers()
        starts = [start]*len(tickers)
        ends = [end]*len(tickers)
        tickers,dfs = get_histories(tickers, starts, ends, granularity="1d")
        ticker_dfs = {ticker:df for ticker,df in zip(tickers, dfs)}
        save_pickle("dataset.obj", (tickers, ticker_dfs))
    return tickers, ticker_dfs


period_start = datetime(2010, 1, 1, tzinfo=pytz.utc)
period_end = datetime.now(pytz.utc)

tickers, ticker_dfs = get_tickers_dfs(period_start, period_end)
print(ticker_dfs)
