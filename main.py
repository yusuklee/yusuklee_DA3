import requests
from bs4 import BeautifulSoup

res = requests.get("https://news.naver.com/")
html = res.text
soup = BeautifulSoup(html, 'html.parser')
title = soup.select("a.cnf_news._cds_link")
for file in title:

    print(file.text)
    print("------------------------------------------------------------------")
