# import pandas as pd 
# import requests
# from bs4 import BeautifulSoup

# res = requests.get("https://en.wikipedia.org/wiki/List_of_S&P_500_companies")
# soup = BeautifulSoup(res.content, "html")
# table = soup.find(id="constituents") #[0]
# print(table)
# # df = pd.read_html(str(table))
# # print(df[0].to_json(orient="records"))

import pandas as pd 
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

site= "https://en.wikipedia.org/wiki/List_of_S&P_500_companies"
hdr = {'User-Agent': 'Mozilla/5.0'}
req = Request(site,headers=hdr)
page = urlopen(req)
soup = BeautifulSoup(page, 'html.parser')

table = soup.find("table") #[0]

df = pd.read_html(str(table))
print(df[0].head())

# table_MN = pd.read_html('https://en.wikipedia.org/wiki/Minnesota')
# print(f'Total tables: {len(table_MN)}')

# table_MN = pd.read_html('https://en.wikipedia.org/wiki/Minnesota', match='Election results from statewide races')
# len(table_MN)