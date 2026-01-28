import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

url = "https://www.saramin.co.kr/zf_user/search/recruit"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
ppp = []

for i in range(1,100):
    params = {
        "searchType": "search",
        "searchword": "개발자",
        "recruitPage": i,
        "recruitPageCount": 100
    }
    res = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    infos = soup.select(".item_recruit")

    if not infos:
        print(f"페이지 {i} 없음  종료")
        break

    for info in infos:
        title = info.select_one(".job_tit a")["title"]
        link = info.select_one(".job_tit a")["href"]

        company = info.select_one(".corp_name a").get_text(strip=True)
        due = info.select_one(".job_date").get_text(strip=True)

        cond_spans = info.select(".job_condition span")
        loc = cond_spans[0].get_text(strip=True)
        requirements = " ".join(
            span.get_text(strip=True) for span in cond_spans[1:]
        )

        ppp.append([title, company, due, link, loc, requirements])

df = pd.DataFrame(
    ppp,
    columns=["title", "company", "due", "link", "loc", "requirements"]
)
df.to_csv("(사람인) 개발자 채용 데이터.csv", index=False,encoding='utf-8-sig')


